"""Browser regressions for cache privacy, repeated work and settings races."""

from urllib.parse import parse_qs, urlparse
from pathlib import Path

from test_web_ui import browser, page, server, open_control  # noqa: F401
from ui_harness import HarnessServer
from playwright.sync_api import expect


def test_watch_name_map_is_parsed_once_and_not_stale(page, server):
    page.goto(server.url)
    result = page.evaluate("""() => {
        const entries = {};
        for (let i = 0; i < 2000; i++) entries['perf-' + i] = {name: 'Show ' + i, episode: '3'};
        localStorage.setItem('agp-watch-names', JSON.stringify(entries));
        const original = JSON.parse;
        let parses = 0;
        JSON.parse = function (text) { parses++; return original(text); };
        try {
            for (let i = 0; i < 2000; i++) AGP.watchName('perf-' + i);
            const bulkParses = parses;
            AGP.rememberNames({'perf-0': {name: 'Changed', episode: '4'}});
            const changed = AGP.watchName('perf-0');
            localStorage.setItem('agp-watch-names', '{"perf-0":{"name":"Other tab"}}');
            return {bulkParses, changed, external: AGP.watchName('perf-0')};
        } finally { JSON.parse = original; }
    }""")
    assert result['bulkParses'] == 1
    assert result['changed']['name'] == 'Changed'
    assert result['external']['name'] == 'Other tab'


def test_watch_index_is_reused_and_invalidates_when_names_change(page, server):
    times = {f'perf-{i}': {'time': 120, 'timestamp': i + 1, 'duration': 1000}
             for i in range(2000)}
    page.route('**/watch/time?type=get', lambda route: route.fulfill(json=times))
    page.add_init_script("""(() => {
        const entries = {};
        for (let i = 0; i < 2000; i++) entries['perf-' + i] = {name: 'Show ' + i, episode: '3'};
        localStorage.setItem('agp-watch-names', JSON.stringify(entries));
        const keys = Object.keys;
        window.historyScans = 0;
        Object.keys = function (value) {
            if (value && value['perf-0'] && value['perf-0'].time === 120) window.historyScans++;
            return keys(value);
        };
    })();""")
    page.goto(server.url)
    page.wait_for_function("() => window.AGP && AGP.lastWatchedFor && AGP.lastWatchedFor('Show 0')")
    result = page.evaluate("""() => {
        window.historyScans = 0;
        for (let i = 0; i < 1000; i++) AGP.lastWatchedFor('Show ' + i);
        const scans = window.historyScans;
        const label = AGP.watchedLabel('Show 0');
        AGP.rememberNames({'perf-0': {name: 'Renamed', episode: '5'}});
        return {scans, label, newLabel: AGP.watchedLabel('Renamed'), old: AGP.lastWatchedFor('Show 0')};
    }""")
    assert result == {'scans': 0, 'label': '看到第 3 集', 'newLabel': '看到第 5 集', 'old': None}


def test_missing_history_episode_does_not_starve_later_episodes(page, server):
    page.route('**/watch/time?type=get', lambda route: route.fulfill(json={
        'missing-1': {'time': 100, 'timestamp': 20},
        'available-2': {'time': 200, 'timestamp': 10},
    }))
    calls = []

    def series(route):
        sn = parse_qs(urlparse(route.request.url).query)['id'][0]
        calls.append(sn)
        if sn == 'missing-1':
            route.fulfill(json={})  # A successful HTTP response with no usable episode.
        else:
            route.fulfill(json={'title': 'Recovered', 'groups': [{'episodes': [
                {'videoSn': 'available-2', 'episode': '2'}]}]})

    page.route('**/watch/series.json?*', series)
    page.goto(server.url + '/?tab=history')
    page.wait_for_function("() => window.AGP && AGP.lastWatchedFor && AGP.lastWatchedFor('Recovered')")
    assert calls == ['missing-1', 'available-2']
    assert page.errors == []


def test_reloading_settings_renders_the_new_response(page):
    with HarnessServer(proxy='') as running:
        open_control(page, running)
        running.settings['config']['check_frequency'] = 27
        page.evaluate('reloadSetting()')
        expect(page.locator('#check_frequency')).to_have_value('27')
        assert page.errors == []


def test_offline_fallback_never_contains_a_previous_login(page, server):
    page.goto(server.url)
    page.evaluate("""async () => {
        await navigator.serviceWorker.ready;
        const old = await caches.open('agp-shell-v15');
        await old.put('./', new Response('PRIVATE PREVIOUS USER'));
        const other = await caches.open('unrelated-application');
        await other.put('./unrelated', new Response('keep'));
    }""")
    page.wait_for_function('() => navigator.serviceWorker.controller !== null')
    # The current worker only reads its own neutral offline page, even if an
    # old authenticated home page remains in another cache during an upgrade.
    page.context.set_offline(True)
    try:
        page.goto(server.url + '/?offline=1')
        expect(page.get_by_role('heading')).to_have_text('暫時無法連上伺服器')
        assert 'PRIVATE PREVIOUS USER' not in page.content()
        assert page.evaluate("() => caches.has('unrelated-application')")
    finally:
        page.context.set_offline(False)


def test_monitor_uses_one_patched_jquery_and_renders_progress_safely(page, server):
    template = Path(__file__).resolve().parents[1] / 'Dashboard/templates/monitor.html'
    page.route('**/monitor', lambda route: route.fulfill(
        content_type='text/html', body=template.read_text(encoding='utf-8')))
    page.add_init_script("""window.WebSocket = class {
        constructor() { window.monitorSocket = this; }
        close() {}
    };""")
    loaded = []
    page.on('request', lambda request: loaded.append(request.url))
    page.goto(server.url + '/monitor')
    page.wait_for_function('() => window.monitorSocket && window.monitorSocket.onmessage')
    page.evaluate("""() => monitorSocket.onmessage({data: JSON.stringify({
        '123': {filename: '<img src=x onerror=alert(1)>', status: 'Downloading', rate: 42}
    })})""")
    expect(page.locator('#header123')).to_have_text('<img src=x onerror=alert(1)>')
    expect(page.locator('#header123 img')).to_have_count(0)
    expect(page.locator('[lay-filter="123"] .layui-progress-text')).to_have_text('42%')
    assert page.evaluate('() => layui.$ === window.jQuery && jQuery.fn.jquery') == '3.7.1'
    assert not any('/lay/modules/jquery.js' in url for url in loaded)
    assert page.errors == []
