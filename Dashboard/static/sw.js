/* ---------------------------------------------------------------------------
   aniGamerPlus+ service worker
   Just enough to make the app launchable from the iOS home screen: the shell
   is cached so a cold standalone start paints instantly, while everything
   that is actually live data goes straight to the network.
   --------------------------------------------------------------------------- */
'use strict';

var CACHE = 'agp-shell-v16';
var OFFLINE = './static/offline.html';

/* Bare paths on purpose: the ?v= tokens in the templates move whenever an asset
   changes, and a list that pinned them would drift out of step unnoticed. These
   copies are the offline fallback; the runtime cache holds the versioned ones.

   Session-rendered HTML must never enter CacheStorage: it survives logout and
   could expose the previous user's name and account state while offline. */
var SHELL = [
    OFFLINE,
    './static/css/agp.css',
    './static/css/home.css',
    './static/css/catalog.css',
    './static/css/watch.css',
    './static/js/agp-shell.js',
    './static/js/home.js',
    './static/js/catalog.js',
    './static/js/userapi.js',
    './static/img/aniGamerPlus.ico',
    './static/img/pwa/icon-192.png',
    './static/img/pwa/apple-touch-icon.png',
    './manifest.webmanifest'
];

self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE).then(function (cache) {
            /* One missing entry must not fail the whole install, so each asset
               is added on its own and allowed to lose. */
            return Promise.all(SHELL.map(function (url) {
                return cache.add(new Request(url, { cache: 'reload' })).catch(function () { });
            }));
        }).then(function () { return self.skipWaiting(); })
    );
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(keys.map(function (key) {
                return key !== CACHE && key.indexOf('agp-shell-') === 0 ? caches.delete(key) : null;
            }));
        }).then(function () { return self.clients.claim(); })
    );
});

/* Anything below is per-user, live, or range-requested. Serving a stale or
   whole-file response for these would break resume positions and iOS video
   seeking outright. Posters join them: the server answers those with an ETag
   and a Cache-Control lifetime, and CacheStorage would ignore both. */
var BYPASS = [
    '/get_video.mp4',
    '/get_danmu.ass',
    '/thumbnail.webp',
    '/video_list.json',
    '/watch/time',
    '/login',
    '/logout',
    '/register',
    '/user',
    '/config',
    '/sn_list',
    '/catalog',
    '/msg',
    /* 邊看邊下載. hls.js 重抓 playlist 用的是普通 fetch, 沒有 range 標頭, 所以上面那道
       range 檢查攔不到它 -- 一份被快取住的清單會讓播放器永遠停在當初那幾片. */
    '/hls/'
];

/* Only a versioned asset may be answered from CacheStorage: its ?v= token
   changes with the file, so a stale body cannot outlive its URL. CacheStorage
   ignores HTTP freshness headers, so anything else kept here would be pinned to
   its first response for the life of the cache. */
function isVersionedAsset(url) {
    return url.pathname.indexOf('/static/') === 0 && /[?&]v=/.test(url.search);
}

function shouldBypass(url, request) {
    if (request.headers.has('range')) { return true; }
    /* Every token above names a root-level route, but the scan below is a plain
       substring test: without this line '/user' also fires on userapi.js, which
       would leave a precached asset permanently unreachable. */
    if (url.pathname.indexOf('/static/') === 0) { return false; }
    for (var i = 0; i < BYPASS.length; i++) {
        if (url.pathname.indexOf(BYPASS[i]) !== -1) { return true; }
    }
    return false;
}

function cached(request, options) {
    return caches.open(CACHE).then(function (cache) { return cache.match(request, options); });
}

function cacheAsset(event, request, response, onlyIfMissing) {
    var copy = response.clone();
    event.waitUntil(caches.open(CACHE).then(function (cache) {
        return (onlyIfMissing ? cache.match(request) : Promise.resolve(null)).then(function (stored) {
            if (!stored) { return cache.put(request, copy); }
        });
    }).catch(function () { /* A full cache must not interrupt playback or navigation. */ }));
}

self.addEventListener('fetch', function (event) {
    var request = event.request;
    if (request.method !== 'GET') { return; }

    var url;
    try {
        url = new URL(request.url);
    } catch (error) {
        return;
    }
    if (url.origin !== self.location.origin) { return; }
    if (shouldBypass(url, request)) { return; }

    /* The offline fallback contains no account data or session bootstrap. */
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(function () {
                return cached(OFFLINE).then(function (hit) {
                    return hit || new Response('Offline', { status: 503 });
                });
            })
        );
        return;
    }

    if (isVersionedAsset(url)) {
        event.respondWith(
            cached(request).then(function (hit) {
                if (hit) { return hit; }
                return fetch(request).then(function (response) {
                    if (response && response.ok && response.type === 'basic') {
                        cacheAsset(event, request, response, false);
                    }
                    return response;
                }).catch(function () {
                    /* Offline holding a token this cache has never seen: the
                       shell copy stored under the bare path is the same file,
                       and a possibly-older script beats no script at all. */
                    return cached(request, { ignoreSearch: true }).then(function (fallback) {
                        return fallback || Response.error();
                    });
                });
            })
        );
        return;
    }

    /* Unversioned assets and every live endpoint go to the network. The vendored
       libraries under /static/ are copied in on the way past so a cold offline
       start still has them; nothing else is stored, because CacheStorage ignores
       freshness and would pin a live response for the life of the cache. */
    event.respondWith(
        fetch(request).then(function (response) {
            if (response && response.ok && response.type === 'basic' &&
                url.pathname.indexOf('/static/') === 0) {
                cacheAsset(event, request, response, true);
            }
            return response;
        }).catch(function () {
            return cached(request).then(function (hit) {
                return hit || Response.error();
            });
        })
    );
});
