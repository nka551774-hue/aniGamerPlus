"""Offline media protocol regressions; upstream traffic stays on loopback."""

import gzip
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from fastapi.testclient import TestClient

import Dashboard.Server as server
from test_fastapi_server import make_settings


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    settings = make_settings()
    settings['temp_dir'] = str(tmp_path / 'temp')
    monkeypatch.setattr(server, '_get_current_settings', lambda: settings)
    monkeypatch.setattr(server, '_sync_plugin_manager', lambda force=False: settings)
    monkeypatch.setattr(server.Config, 'read_settings', lambda *a, **k: settings)
    monkeypatch.setattr(server.Config, 'get_working_dir', lambda: str(tmp_path))
    monkeypatch.setattr(server, 'load_user_data', lambda: {'users': []})
    monkeypatch.setattr(server.plugin_manager, 'resolve_playback_source', lambda info: None)
    monkeypatch.setattr(server, '_stream_dict_cache', {})
    monkeypatch.setattr(server, '_stream_media_cache', {})
    return settings


@pytest.fixture
def client():
    return TestClient(server.app)


@pytest.fixture
def video(monkeypatch, tmp_path):
    path = tmp_path / 'episode.mp4'
    path.write_bytes(b'0123456789' * 10)
    monkeypatch.setattr(server, '_find_video_path', lambda sn, resolution=None: str(path))
    return path


@pytest.fixture
def upstream():
    routes = {}
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            calls.append(self.path)
            status, headers, body = routes.get(self.path, (404, {}, b'not found'))
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            chunked = headers.get('Transfer-Encoding') == 'chunked'
            if not chunked:
                self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try:
                if chunked:
                    for start in range(0, len(body), 4096):
                        chunk = body[start:start + 4096]
                        self.wfile.write(('%x\r\n' % len(chunk)).encode() + chunk + b'\r\n')
                    self.wfile.write(b'0\r\n\r\n')
                else:
                    self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # A body limit intentionally closes the upstream connection.

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield 'http://127.0.0.1:%d' % httpd.server_port, routes, calls
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize('if_range', ['"outdated-version"', 'Wed, 21 Oct 2015 07:28:00 GMT'])
def test_stale_if_range_restarts_download_instead_of_splicing_versions(client, video, if_range):
    response = client.get('/get_video.mp4?id=123',
                          headers={'Range': 'bytes=50-', 'If-Range': if_range})
    assert response.status_code == 200
    assert response.content == video.read_bytes()
    assert 'content-range' not in response.headers


def test_current_if_range_permits_resume_and_weak_validator_does_not(client, video):
    original = client.head('/get_video.mp4?id=123')
    for validator in (original.headers['etag'], original.headers['last-modified']):
        resumed = client.get('/get_video.mp4?id=123',
                             headers={'Range': 'bytes=50-', 'If-Range': validator})
        assert resumed.status_code == 206
        assert resumed.content == video.read_bytes()[50:]
    weak = client.get('/get_video.mp4?id=123', headers={
        'Range': 'bytes=50-', 'If-Range': 'W/' + original.headers['etag']})
    assert weak.status_code == 200
    assert weak.content == video.read_bytes()


@pytest.mark.parametrize('route', ['/get_video.mp4?id=123', '/video_list.json'])
def test_etag_takes_precedence_over_same_second_modified_date(client, video, tmp_path, route):
    path = video
    if route == '/video_list.json':
        path = tmp_path / 'video_list.json'
        path.write_text('{"videos": []}', encoding='utf-8')
    original = client.get(route)
    stamp = path.stat().st_mtime_ns
    # File contents and ETag change inside the same HTTP-date second.
    path.write_bytes(path.read_bytes() + b' ')
    os.utime(path, ns=(stamp, stamp))
    refreshed = client.get(route, headers={
        'If-None-Match': original.headers['etag'],
        'If-Modified-Since': original.headers['last-modified'],
    })
    assert refreshed.status_code == 200
    assert refreshed.content == path.read_bytes()


@pytest.mark.parametrize('validator_type', ['list', 'weak', 'wildcard'])
def test_conditional_get_accepts_standard_etag_forms(client, video, validator_type):
    etag = client.head('/get_video.mp4?id=123').headers['etag']
    assert etag.startswith('"') and etag.endswith('"')
    value = {'list': '"old", ' + etag, 'weak': 'W/' + etag, 'wildcard': '*'}[validator_type]
    response = client.get('/get_video.mp4?id=123', headers={'If-None-Match': value})
    assert response.status_code == 304
    assert response.content == b''


def test_oversized_range_integer_returns_416_instead_of_500(client, video):
    response = client.get('/get_video.mp4?id=123', headers={'Range': 'bytes=' + '9' * 5000 + '-'})
    assert response.status_code == 416
    assert response.headers['content-range'] == 'bytes */100'


def playlist(segment='chunk.ts', key='enc.key', sequence=0):
    return ('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n'
            '#EXT-X-MEDIA-SEQUENCE:%d\n#EXT-X-KEY:METHOD=AES-128,URI="%s"\n'
            '#EXTINF:10,\n%s\n#EXT-X-ENDLIST\n' % (sequence, key, segment)).encode()


@pytest.mark.parametrize('segment', ['/root/chunk.ts?sig=1', '../chunk.ts?sig=1', '//HOST/chunk.ts?sig=1'])
def test_proxy_resolves_relative_segment_against_redirected_playlist(
        client, monkeypatch, upstream, segment):
    origin, routes, calls = upstream
    segment = segment.replace('HOST', origin.split('//', 1)[1])
    resolved_path = '/root/chunk.ts?sig=1' if segment.startswith('/root') else '/chunk.ts?sig=1'
    routes['/original.m3u8'] = (302, {'Location': '/redirected/list.m3u8'}, b'')
    routes['/redirected/list.m3u8'] = (200, {}, playlist(segment=segment, key='../enc.key?sig=1'))
    routes[resolved_path] = (200, {}, b'segment-payload')
    routes['/enc.key?sig=1'] = (200, {}, b'0123456789abcdef')
    monkeypatch.setattr(server, '_stream_allowed', lambda sn: True)
    monkeypatch.setattr(server, '_stream_dict', lambda sn: {'720': origin + '/original.m3u8'})
    response = client.get('/stream/segment.ts?id=123&res=720&n=0')
    assert response.status_code == 200
    assert response.content == b'segment-payload'
    key = client.get('/stream/key.bin?id=123&res=720')
    assert key.content == b'0123456789abcdef'
    assert resolved_path in calls
    assert '/enc.key?sig=1' in calls


def test_proxy_preserves_nonzero_sequence_for_implicit_aes_iv():
    from Crypto.Cipher import AES

    source = playlist(sequence=43).decode()
    parsed = server._stream_parse_media(source)
    rendered = server._stream_render('123', '720', parsed)
    sequence = int(next(line.split(':')[1] for line in rendered.splitlines()
                        if line.startswith('#EXT-X-MEDIA-SEQUENCE:')))
    key = b'0123456789abcdef'
    plaintext = b'correct-segment!'
    ciphertext = AES.new(key, AES.MODE_CBC, iv=(43).to_bytes(16, 'big')).encrypt(plaintext)
    assert AES.new(key, AES.MODE_CBC, iv=sequence.to_bytes(16, 'big')).decrypt(ciphertext) == plaintext


def test_parallel_key_requests_only_fetch_upstream_once(monkeypatch):
    calls = []
    start = threading.Barrier(8)

    def fetch(*args, **kwargs):
        calls.append(True)
        time.sleep(0.05)
        return type('Reply', (), {'status_code': 200, 'content': b'0123456789abcdef'})()

    monkeypatch.setattr(server, '_bahamut_get', fetch)
    media = {'key': None, 'base': 'https://example.invalid/list.m3u8',
             'parsed': server._stream_parse_media(playlist().decode())}

    def get_key(_):
        start.wait(timeout=5)
        return server._stream_key('123', '720', media)

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(get_key, range(8)))
    assert values == [b'0123456789abcdef'] * 8
    assert len(calls) == 1


def test_temporary_resolution_failure_does_not_disable_playback_for_half_an_hour(monkeypatch):
    now = [100.0]
    calls = []
    monkeypatch.setattr(server.time, 'monotonic', lambda: now[0])

    def resolve(sn):
        calls.append(sn)
        if len(calls) == 1:
            raise RuntimeError('temporary network failure')
        return {'720': 'https://example.invalid/list.m3u8'}

    monkeypatch.setattr(server, '_stream_resolve_blocking', resolve)
    assert server._stream_dict('123') == {}
    assert server._stream_dict('123') == {}  # immediate retries remain coalesced
    now[0] += 31
    assert server._stream_dict('123') == {'720': 'https://example.invalid/list.m3u8'}
    assert len(calls) == 2


@pytest.mark.parametrize('encoding', ['identity', 'gzip', 'chunked'])
def test_upstream_size_limit_applies_while_receiving_and_after_decompression(upstream, encoding):
    origin, routes, _ = upstream
    body = b'x' * (128 * 1024)
    headers = {}
    if encoding == 'gzip':
        body = gzip.compress(body)
        headers['Content-Encoding'] = 'gzip'
    elif encoding == 'chunked':
        headers['Transfer-Encoding'] = 'chunked'
    routes['/large'] = (200, headers, body)
    with pytest.raises(ValueError, match='response.*limit'):
        server._bahamut_get(origin + '/large', max_bytes=32 * 1024)


def test_bounded_upstream_keeps_normal_json_response_usable(upstream):
    origin, routes, _ = upstream
    routes['/small'] = (200, {'Content-Type': 'application/json'}, b'{"ok": true}')
    reply = server._bahamut_get(origin + '/small', max_bytes=32 * 1024)
    assert reply.json() == {'ok': True}


def test_body_limit_disconnects_upstream_before_large_response_finishes():
    finished = threading.Event()
    sent = []
    total = 64 * 1024 * 1024

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Length', str(total))
            self.end_headers()
            count = 0
            try:
                while count < total:
                    self.wfile.write(b'x' * 4096)
                    self.wfile.flush()
                    count += 4096
                    time.sleep(0.001)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            finally:
                sent.append(count)
                finished.set()

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(ValueError, match='response.*limit'):
            server._bahamut_get('http://127.0.0.1:%d/large' % httpd.server_port,
                               max_bytes=1024)
        assert finished.wait(5), 'the response must be actively disconnected'
        assert sent and sent[0] < total
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=3)
