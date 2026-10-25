"""Security regressions using local, isolated request and userdata fixtures."""

import copy
import gc
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

import Dashboard.Server as server
from test_fastapi_server import make_settings, make_userdata


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    settings = make_settings()
    monkeypatch.setattr(server, '_get_current_settings', lambda: settings)
    monkeypatch.setattr(server.Config, 'read_settings', lambda *a, **kw: settings)
    return settings


@pytest.fixture(autouse=True)
def userdata(monkeypatch):
    data = make_userdata()
    monkeypatch.setattr(server, 'load_user_data', lambda: copy.deepcopy(data))

    def save(updated):
        data.clear()
        data.update(copy.deepcopy(updated))

    monkeypatch.setattr(server, 'save_user_data', save)
    return data


@pytest.fixture
def client():
    return TestClient(server.app)


@pytest.mark.parametrize('headers', [
    {'Origin': 'https://attacker.example'},
    {'Origin': 'null'},
    {'Origin': 'http://testserver.attacker.example'},
    {'Origin': 'http://attacker@testserver'},
    {'Origin': 'https://testserver'},
    {'Origin': 'http://testserver:81'},
    {'Referer': 'https://attacker.example/form'},
    {'Sec-Fetch-Site': 'cross-site'},
    {'Sec-Fetch-Site': 'same-site'},
])
def test_foreign_browser_cannot_write_even_with_authentication_disabled(
        client, settings, monkeypatch, headers):
    writes = []
    monkeypatch.setattr(server.Config, 'write_sn_list', writes.append)
    response = client.post('/sn_list', content='123', headers=headers)
    assert response.status_code == 403
    assert writes == []


@pytest.mark.parametrize('headers', [
    {},  # Flutter and CLI clients do not send browser-origin headers.
    {'Origin': 'http://testserver'},
    {'Origin': 'http://testserver:80', 'Sec-Fetch-Site': 'same-origin'},
    {'Referer': 'http://testserver/control'},
])
def test_native_and_same_origin_requests_can_still_write(
        client, settings, monkeypatch, headers):
    writes = []
    monkeypatch.setattr(server.Config, 'write_sn_list', writes.append)
    response = client.post('/sn_list', content='123', headers=headers)
    assert response.status_code == 200
    assert writes == ['123']


@pytest.mark.parametrize('path', [
    '/checknow', '/logout', '/watch/time?type=set&sn=123&time=3',
    '/watch/time?type=del&sn=123',
])
def test_legacy_get_mutations_reject_cross_site_navigation(
        client, settings, monkeypatch, path):
    calls = []
    monkeypatch.setattr(server, 'checknow', lambda: calls.append(True))
    response = client.get(path, headers={'Sec-Fetch-Site': 'cross-site'},
                          follow_redirects=False)
    assert response.status_code == 403
    assert calls == []


@pytest.mark.parametrize('path', [
    '/agp/checknow', '/agp/logout',
    '/agp/watch/time?type=set&sn=123&time=3',
    '/agp/watch/time?type=del&sn=123',
    '/agp/%63hecknow', '/agp%2Fchecknow', '/agp/watch/time?type=%64el&sn=123',
])
def test_mounted_get_mutations_reject_cross_site_navigation(
        settings, userdata, monkeypatch, path):
    calls = []
    settings['dashboard']['user_control']['enabled'] = True
    monkeypatch.setattr(server, 'checknow', lambda: calls.append(True))
    client = TestClient(server.app, root_path='/agp')
    client.cookies.set('token', 'admintoken123')
    response = client.get(path, headers={
        'Origin': 'https://attacker.example', 'Sec-Fetch-Site': 'cross-site',
    }, follow_redirects=False)
    assert response.status_code == 403
    assert calls == []


def test_mounted_native_get_mutation_still_works(settings, monkeypatch):
    calls = []
    monkeypatch.setattr(server, 'checknow', lambda: calls.append(True))
    client = TestClient(server.app, root_path='/agp')
    assert client.get('/agp/checknow').status_code == 200
    assert calls == [True]


@pytest.mark.parametrize('path', ['/agp-other/checknow', '/AGP/checknow', '/agp/CHECKNOW'])
def test_csrf_path_matching_preserves_router_boundaries_and_case(settings, monkeypatch, path):
    calls = []
    monkeypatch.setattr(server, 'checknow', lambda: calls.append(True))
    client = TestClient(server.app, root_path='/agp')
    response = client.get(path, headers={'Sec-Fetch-Site': 'cross-site'},
                          follow_redirects=False)
    assert response.status_code == 404
    assert calls == []


def test_csrf_guard_precedes_body_parsing(client, settings, monkeypatch):
    async def unexpected_body(_request):
        raise AssertionError('Untrusted browser request body was parsed')

    monkeypatch.setattr(server.Request, 'json', unexpected_body)
    response = client.post('/manualTask', content='{}',
                           headers={'Origin': 'https://attacker.example'})
    assert response.status_code == 403


@pytest.mark.parametrize('path', ['/login', '/register', '/console/command', '/sn_list/add'])
def test_streamed_oversized_body_returns_413_even_in_forgiving_parsers(
        client, settings, path):
    settings['dashboard']['user_control']['enabled'] = True
    settings['dashboard']['user_control']['allow_register'] = True
    client.cookies.set('token', 'admintoken123')
    response = client.post(path,
                           content=iter([b'x' * server.MAX_REQUEST_BODY_BYTES, b'x']),
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 413


@pytest.mark.parametrize('ticket', [
    '9' * 5000 + '.aaaaaaaaaaaaaaaa.' + 'b' * 32,
    '².aaaaaaaaaaaaaaaa.' + 'b' * 32,
    '9999999999.你好.' + 'b' * 32,
    '9999999999.aaaaaaaaaaaaaaaa.你好',
], ids=['oversized-expiry', 'unicode-digit', 'unicode-tag', 'unicode-signature'])
def test_malformed_cast_ticket_is_denied_without_loading_accounts(
        client, settings, monkeypatch, ticket):
    settings['dashboard']['online_watch_requires_login'] = True

    def unexpected_read():
        raise AssertionError('Malformed ticket must be rejected before account I/O')

    monkeypatch.setattr(server, 'load_user_data', unexpected_read)
    response = client.get('/get_video.mp4', params={'id': '123', 'ct': ticket})
    assert response.status_code == 403


@pytest.mark.parametrize('new_password_format', ['hashed', 'plaintext', 'deleted'])
def test_legacy_login_cannot_receive_token_after_concurrent_password_reset(
        client, settings, userdata, monkeypatch, new_password_format):
    settings['dashboard']['user_control']['enabled'] = True
    original_update = server.update_user_data

    def update_after_reset(mutator):
        target = userdata['users'][1]
        target['token'] = 'token-issued-by-password-reset'
        if new_password_format == 'hashed':
            target.pop('password')
            target['password_hash'] = server._hash_password('replacement-password')
        elif new_password_format == 'plaintext':
            target['password'] = 'replacement-password'
        else:
            userdata['users'].remove(target)
        return original_update(mutator)

    monkeypatch.setattr(server, 'update_user_data', update_after_reset)
    response = client.post('/login', json={'username': 'tester', 'password': 'testerpw'},
                           follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'].endswith('login?error=1')
    assert 'set-cookie' not in response.headers


def test_non_ascii_wrong_password_is_a_login_failure(client, settings, userdata):
    settings['dashboard']['user_control']['enabled'] = True
    response = client.post('/login', json={'username': 'tester', 'password': '錯誤密碼'},
                           follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'].endswith('login?error=1')


@pytest.mark.parametrize('unsafe_segment', [
    'media_bfolder/../../secret.ts',
    r'media_bfolder\..\..\secret.ts',
    'media_b%2f..%2fsecret.ts',
    'https://example.invalid/media_b123_0.ts',
    'https:media_b123_0.ts',
    '../media_b123_0.ts',
    'media_b123_0.ts:private.ts',
])
def test_hls_playlist_rejects_unsafe_paths_instead_of_skipping_segments(unsafe_segment):
    from test_hls_playlist import remote_playlist

    playlist = remote_playlist(2).replace('media_b1500000_1.ts', unsafe_segment)
    assert server._hls_parse_playlist(playlist) is None


def test_hls_query_string_does_not_become_a_local_filename():
    from test_hls_playlist import remote_playlist

    playlist = remote_playlist(1).replace(
        'media_b1500000_0.ts', 'media_b1500000_0.ts?signature=a.ts&x=1#fragment')
    parsed = server._hls_parse_playlist(playlist)
    assert parsed['segments'][0]['name'] == 'media_b1500000_0.ts'


def test_idle_keyed_locks_do_not_accumulate_for_arbitrary_resolution_values():
    names = ['security-test-stream-media-123/%d' % n for n in range(256)]
    try:
        for name in names:
            with server._keyed_lock(name):
                pass
        gc.collect()
        assert not any(name in server._keyed_locks for name in names)
    finally:
        for name in names:
            server._keyed_locks.pop(name, None)


def test_reclaimed_keyed_locks_still_serialize_contending_requests():
    active = 0
    peak = 0
    counter_guard = threading.Lock()
    start = threading.Barrier(4)

    def worker():
        nonlocal active, peak
        start.wait(timeout=5)
        for _ in range(4):
            with server._keyed_lock('security-test-shared-resource'):
                with counter_guard:
                    active += 1
                    peak = max(peak, active)
                time.sleep(0.002)
                with counter_guard:
                    active -= 1

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: worker(), range(4)))
    assert peak == 1


@pytest.mark.parametrize('fail', [False, True])
def test_upstream_session_closes_on_success_and_failure(monkeypatch, fail):
    closed = []
    result = object()

    class Session:
        def request(self, *args, **kwargs):
            if fail:
                raise RuntimeError('upstream failed')
            return result

        def close(self):
            closed.append(True)

    monkeypatch.setattr(server.curl_requests, 'Session', lambda **kw: Session())
    if fail:
        with pytest.raises(RuntimeError, match='upstream failed'):
            server._curl_perform({}, 'https://example.invalid', {})
    else:
        assert server._curl_perform({}, 'https://example.invalid', {}) is result
    assert closed == [True]


@pytest.mark.parametrize('resolution', ['²', '9' * 5000], ids=['unicode', 'oversized'])
def test_invalid_video_resolution_uses_existing_video_instead_of_500(
        client, settings, monkeypatch, tmp_path, resolution):
    video = tmp_path / 'episode.mp4'
    video.write_bytes(b'test-video')
    monkeypatch.setattr(server, '_sync_plugin_manager', lambda: settings)
    monkeypatch.setattr(server.plugin_manager, 'resolve_playback_source', lambda info: None)
    monkeypatch.setattr(server, '_find_video_path', lambda sn, res: str(video))
    response = client.get('/get_video.mp4', params={'id': '123', 'res': resolution})
    assert response.status_code == 200
    assert response.content == b'test-video'


@pytest.mark.parametrize('sn', [None, '', '   ', ['123'], 'x' * 129])
def test_watch_time_set_rejects_missing_or_unbounded_video_ids(
        client, settings, userdata, sn):
    settings['dashboard']['user_control']['enabled'] = True
    client.cookies.set('token', 'admintoken123')
    payload = {'type': 'set', 'time': 3}
    if sn is not None:
        payload['sn'] = sn

    response = client.post('/watch/time', json=payload)

    assert response.status_code == 400
    assert userdata['users'][0]['videotimes'] == {}


def test_watch_time_set_accepts_bounded_plugin_video_ids(
        client, settings, userdata):
    settings['dashboard']['user_control']['enabled'] = True
    client.cookies.set('token', 'admintoken123')

    response = client.post('/watch/time', json={
        'type': 'set', 'sn': 'plugin:series-1_episode.2', 'time': 3})

    assert response.status_code == 200
    assert userdata['users'][0]['videotimes'][
        'plugin:series-1_episode.2']['time'] == 3
