"""Offline regressions for bounded downloads, playlist input and publication."""

import errno
import json
import threading
import types
from pathlib import Path

import pytest
import requests

import Anime as anime_module
import aniGamerPlus as agp


PLAYLIST_URL = 'https://example.invalid/show/chunklist.m3u8'
KEY_URL = 'https://example.invalid/show/key.bin'


def response(content=b'', status=200):
    result = requests.Response()
    result.status_code = status
    result._content = content
    result.encoding = 'utf-8'
    result.url = PLAYLIST_URL
    return result


def playlist(count=5, names=None, extra=''):
    names = names if names is not None else ['media_b1_%d.ts' % i for i in range(count)]
    return ('#EXTM3U\n#EXT-X-TARGETDURATION:10\n'
            '#EXT-X-KEY:METHOD=AES-128,URI="key.bin",IV=0x00000000000000000000000000000001\n'
            + extra + ''.join('#EXTINF:10,\n%s\n' % name for name in names)
            + '#EXT-X-ENDLIST\n').encode()


@pytest.fixture
def downloader(tmp_path, monkeypatch):
    anime = anime_module.Anime.__new__(anime_module.Anime)
    anime._sn = 123
    anime._title = 'Offline test'
    anime._settings = {'multi_downloading_segment': 3, 'segment_max_retry': 0,
                       'faststart_movflags': False, 'audio_language': False,
                       'use_copyfile_method': False}
    anime._bangumi_dir = str(tmp_path / 'library')
    anime._temp_dir = str(tmp_path / 'temp')
    Path(anime._bangumi_dir).mkdir()
    Path(anime._temp_dir).mkdir()
    anime._m3u8_dict = {'1080': PLAYLIST_URL}
    anime._ffmpeg_path = 'offline-ffmpeg'
    anime.video_size = 0
    anime.local_video_path = ''
    anime.realtime_show_file_size = False
    anime.get_filename = lambda: 'episode.mp4'
    anime._Anime__get_filename = lambda resolution: 'episode.mp4'
    anime._Anime__get_temp_filename = lambda resolution, temp_suffix: 'merge.mp4'
    state = types.SimpleNamespace(playlist=playlist(), calls=[], merge_calls=[],
                                  merge_status=0, merge_error=b'', merged_playlist='')

    def request(url, **kwargs):
        state.calls.append(url)
        if url == PLAYLIST_URL:
            return response(state.playlist)
        if url == KEY_URL:
            return response(b'0123456789abcdef')
        return response(b'ts segment')

    def popen(command, **kwargs):
        state.merge_calls.append(command)
        state.merged_playlist = Path(command[command.index('-i') + 1]).read_text(encoding='utf-8')
        (Path(anime._temp_dir) / 'merge.mp4').write_bytes(b'new output')
        return types.SimpleNamespace(returncode=state.merge_status,
                                     communicate=lambda: (b'', state.merge_error))

    monkeypatch.setattr(anime, '_Anime__request', request)
    monkeypatch.setattr(anime_module.subprocess, 'Popen', popen)
    monkeypatch.setattr(anime_module, 'err_print', lambda *a, **k: None)
    monkeypatch.setattr(anime_module.Config, 'tasks_progress_rate', {})
    return anime, state


def test_segment_workers_are_reused_and_localisation_keeps_query_and_iv(downloader, monkeypatch):
    anime, state = downloader
    # A path substring in a query must not be rewritten into a local path.
    state.playlist = playlist(names=['media_b1_%d.ts?next=media_b1_1.ts' % i for i in range(120)])
    threads = []
    real_thread = threading.Thread

    def new_thread(*args, **kwargs):
        thread = real_thread(*args, **kwargs)
        threads.append(thread)
        return thread

    monkeypatch.setattr(anime_module.threading, 'Thread', new_thread)
    anime._Anime__segment_download_mode('1080')

    assert len(threads) == 3
    assert all(not thread.is_alive() for thread in threads)
    assert len(state.calls) == 122
    assert 'IV=0x00000000000000000000000000000001' in state.merged_playlist
    assert '?next=' not in state.merged_playlist
    assert len([line for line in state.merged_playlist.splitlines() if line.endswith('.ts')]) == 120
    assert Path(anime.local_video_path).read_bytes() == b'new output'
    assert anime_module.Config.tasks_progress_rate[123]['rate'] == 100


@pytest.mark.parametrize('name', [
    '../media_b1_0.ts', 'media_b/../../outside.ts', r'media_b\..\outside.ts',
    'media_b1_0.ts/../../outside.ts', 'media_b%2f..%2foutside.ts',
    'https://example.invalid/media_b1_0.ts', 'file:///media_b1_0.ts',
])
def test_untrusted_playlist_cannot_choose_a_local_path(downloader, name):
    anime, state = downloader
    state.playlist = playlist(names=[name])
    with pytest.raises(ValueError, match='segment filename'):
        anime._Anime__segment_download_mode('1080')
    assert state.calls == [PLAYLIST_URL]
    assert not state.merge_calls


def test_playlist_rejects_extra_file_resources(downloader):
    anime, state = downloader
    state.playlist = playlist(extra='#EXT-X-MAP:URI="file:///private.txt"\n')
    with pytest.raises(ValueError, match='playlist resource'):
        anime._Anime__segment_download_mode('1080')
    assert state.calls == [PLAYLIST_URL]


def test_playlist_rejects_a_second_key_uri(downloader):
    anime, state = downloader
    state.playlist = playlist().replace(b'URI="key.bin"', b'URI="key.bin",URI="file:///private.txt"')
    with pytest.raises(ValueError, match='segment encryption'):
        anime._Anime__segment_download_mode('1080')
    assert state.calls == [PLAYLIST_URL]


@pytest.mark.parametrize('content,status', [(b'upstream error', 503), (b'', 200)])
def test_bad_segment_is_not_published_or_merged(downloader, monkeypatch, content, status):
    anime, state = downloader
    anime._settings['multi_downloading_segment'] = 1
    original_request = anime._Anime__request

    def request(url, **kwargs):
        if url not in (PLAYLIST_URL, KEY_URL):
            state.calls.append(url)
            return response(content, status)
        return original_request(url, **kwargs)

    monkeypatch.setattr(anime, '_Anime__request', request)
    anime._Anime__segment_download_mode('1080')
    assert len(state.calls) == 3  # No remaining segments are started after failure.
    assert not list(Path(anime._temp_dir).rglob('*.ts'))
    assert not list(Path(anime._temp_dir).rglob('*.part'))
    assert not state.merge_calls
    assert anime.video_size == 0


def test_failure_waits_for_inflight_writer_before_allowing_retry(downloader, monkeypatch):
    anime, state = downloader
    anime._settings['multi_downloading_segment'] = 2
    first_started, failure_seen, release_first, returned = [threading.Event() for _ in range(4)]
    original_request = anime._Anime__request

    def request(url, **kwargs):
        if url.endswith('media_b1_0.ts'):
            first_started.set()
            assert release_first.wait(5)
        elif url.endswith('media_b1_1.ts'):
            assert first_started.wait(5)
            return response(b'error', 503)
        return original_request(url, **kwargs)

    def report(sn, label, *args, **kwargs):
        if label == '下載狀態':
            failure_seen.set()

    def download():
        try:
            anime._Anime__segment_download_mode('1080')
        finally:
            returned.set()

    monkeypatch.setattr(anime, '_Anime__request', request)
    monkeypatch.setattr(anime_module, 'err_print', report)
    owner = threading.Thread(target=download, daemon=True)
    owner.start()
    try:
        assert failure_seen.wait(5)
        assert not returned.wait(0.05), 'Returning here lets a retry race the old writer'
    finally:
        release_first.set()
        owner.join(5)
    assert not owner.is_alive()
    assert not state.merge_calls


def test_sibling_failure_interrupts_unlimited_network_retries(downloader, monkeypatch):
    anime, state = downloader
    anime._settings['multi_downloading_segment'] = 2
    anime._settings['segment_max_retry'] = -1
    anime._req_header, anime._cookies = {}, {}
    retry_started = threading.Event()
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        if url == PLAYLIST_URL:
            return response(state.playlist)
        if url == KEY_URL:
            return response(b'0123456789abcdef')
        if url.endswith('media_b1_0.ts'):
            retry_started.set()
            raise requests.exceptions.ConnectionError('offline network outage')
        assert retry_started.wait(5)
        return response(b'failed segment', 503)

    anime._session = types.SimpleNamespace(get=get, cookies={})
    monkeypatch.setattr(anime, '_Anime__request',
                        types.MethodType(anime_module.Anime._Anime__request, anime))
    owner = threading.Thread(target=anime._Anime__segment_download_mode, args=('1080',), daemon=True)
    owner.start()
    owner.join(2)
    assert not owner.is_alive(), 'Unlimited retries must stop when another segment fails'
    assert len(calls) == 4
    assert not state.merge_calls
    assert anime.video_size == 0


@pytest.mark.parametrize('status,error', [(1, b'conversion failed'), (0, b'Failed to open segment')])
def test_failed_merge_preserves_existing_video_and_segments(downloader, status, error):
    anime, state = downloader
    state.merge_status, state.merge_error = status, error
    existing = Path(anime._bangumi_dir) / 'episode.mp4'
    existing.write_bytes(b'previous complete video')
    anime._Anime__segment_download_mode('1080')
    assert existing.read_bytes() == b'previous complete video'
    assert len(list(Path(anime._temp_dir).rglob('*.ts'))) == 5
    assert anime.video_size == 0
    assert anime.local_video_path == ''


@pytest.mark.parametrize('copy_file', [False, True])
def test_successful_publication_replaces_old_video_and_then_removes_source(tmp_path, copy_file):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')
    anime_module._publish_video(str(source), str(destination), copy_file=copy_file)
    assert destination.read_bytes() == b'complete new video'
    assert not source.exists()
    assert not list(tmp_path.glob('*.part'))


@pytest.mark.parametrize('copy_file', [False, True])
def test_publication_failure_keeps_old_video_and_source(tmp_path, monkeypatch, copy_file):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')

    def fail_replace(src, dst):
        raise OSError('offline simulated publication failure')

    monkeypatch.setattr(anime_module.os, 'replace', fail_replace)
    with pytest.raises(OSError, match='publication failure'):
        anime_module._publish_video(str(source), str(destination), copy_file=copy_file)
    assert destination.read_bytes() == b'previous complete video'
    assert source.read_bytes() == b'complete new video'
    assert not list(tmp_path.glob('*.part'))


@pytest.mark.parametrize('copy_file', [False, True])
def test_partial_copy_failure_keeps_old_video_and_source(tmp_path, monkeypatch, copy_file):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')
    real_replace = anime_module.os.replace

    def cross_device_replace(src, dst):
        if src == str(source):
            raise OSError(errno.EXDEV, 'offline simulated cross-device move')
        return real_replace(src, dst)

    def partial_copy(src, staged):
        assert Path(staged).parent == destination.parent
        Path(staged).write_bytes(b'partial')
        raise OSError('offline simulated full disk')

    monkeypatch.setattr(anime_module.os, 'replace', cross_device_replace)
    monkeypatch.setattr(anime_module.shutil, 'copyfile', partial_copy)
    with pytest.raises(OSError, match='full disk'):
        anime_module._publish_video(str(source), str(destination), copy_file=copy_file)
    assert destination.read_bytes() == b'previous complete video'
    assert source.read_bytes() == b'complete new video'
    assert not list(tmp_path.glob('*.part'))


def test_cross_device_copy_is_verified_before_atomic_publication(tmp_path, monkeypatch):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')
    real_replace = anime_module.os.replace
    final_replacements = []

    def cross_device_replace(src, dst):
        if src == str(source):
            raise OSError(errno.EXDEV, 'offline simulated cross-device move')
        assert source.read_bytes() == b'complete new video'
        assert destination.read_bytes() == b'previous complete video'
        assert Path(src).read_bytes() == b'complete new video'
        final_replacements.append(src)
        return real_replace(src, dst)

    monkeypatch.setattr(anime_module.os, 'replace', cross_device_replace)
    anime_module._publish_video(str(source), str(destination))
    assert len(final_replacements) == 1
    assert destination.read_bytes() == b'complete new video'
    assert not source.exists()


def test_silent_short_copy_is_not_published(tmp_path, monkeypatch):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')
    monkeypatch.setattr(anime_module.shutil, 'copyfile', lambda src, dst: Path(dst).write_bytes(b'partial'))
    with pytest.raises(OSError, match='Incomplete video copy'):
        anime_module._publish_video(str(source), str(destination), copy_file=True)
    assert destination.read_bytes() == b'previous complete video'
    assert source.read_bytes() == b'complete new video'
    assert not list(tmp_path.glob('*.part'))


def test_delayed_disk_full_during_flush_keeps_old_video(tmp_path, monkeypatch):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')
    destination.write_bytes(b'previous complete video')

    def disk_full(fd):
        raise OSError(errno.ENOSPC, 'offline simulated delayed full disk')

    monkeypatch.setattr(anime_module.os, 'fsync', disk_full)
    with pytest.raises(OSError, match='delayed full disk'):
        anime_module._publish_video(str(source), str(destination), copy_file=True)
    assert destination.read_bytes() == b'previous complete video'
    assert source.read_bytes() == b'complete new video'
    assert not list(tmp_path.glob('*.part'))


def test_copy_mode_supports_mount_without_fsync(tmp_path, monkeypatch):
    source, destination = tmp_path / 'merged.mp4', tmp_path / 'episode.mp4'
    source.write_bytes(b'complete new video')

    def unsupported(fd):
        raise OSError(errno.ENOTSUP, 'offline simulated unsupported mount operation')

    monkeypatch.setattr(anime_module.os, 'fsync', unsupported)
    anime_module._publish_video(str(source), str(destination), copy_file=True)
    assert destination.read_bytes() == b'complete new video'
    assert not source.exists()


def request_anime():
    anime = anime_module.Anime.__new__(anime_module.Anime)
    anime._sn = 123
    anime._req_header = {'User-Agent': 'test'}
    anime._cookies = {}
    anime._proxies = {}
    anime._settings = {}
    return anime


def test_extra_headers_do_not_leak_to_later_requests():
    anime = request_anime()
    seen = []

    def get(url, **kwargs):
        seen.append(dict(kwargs['headers']))
        return response(b'{}')

    anime._session = types.SimpleNamespace(cookies={}, get=get)
    anime._Anime__request('https://example.invalid/one', addition_header={'X-Request': 'one'})
    anime._Anime__request('https://example.invalid/two')
    assert seen == [{'User-Agent': 'test', 'X-Request': 'one'}, {'User-Agent': 'test'}]


def test_fingerprint_transport_retries_and_json_is_decoded(monkeypatch):
    anime = request_anime()
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise anime_module.curl_requests.RequestsError('offline timeout')
        return response(b'{"ready": true}')

    anime._fingerprint_session = types.SimpleNamespace(get=get)
    anime._session = types.SimpleNamespace(cookies={})
    monkeypatch.setattr(anime_module.time, 'sleep', lambda seconds: None)
    result = anime._Anime__request_json('https://example.invalid/test', verify_fingerprint=True,
                                      max_retry=1, show_fail=False)
    assert result == {'ready': True}
    assert len(calls) == 2


@pytest.mark.parametrize('fails', [False, True])
def test_bahamut_request_closes_its_session(monkeypatch, fails):
    closed = []

    def request(*args, **kwargs):
        if fails:
            raise anime_module.curl_requests.RequestsError('offline timeout')
        return response(b'body remains readable')

    monkeypatch.setattr(agp.Config, 'read_settings', lambda: {'ua': 'test'})
    monkeypatch.setattr(agp.Config.curl_requests, 'Session', lambda **kwargs: types.SimpleNamespace(
        request=request, close=lambda: closed.append(True)))
    if fails:
        with pytest.raises(requests.exceptions.RequestException):
            agp.Config.bahamut_request('GET', 'https://example.invalid/test')
    else:
        assert agp.Config.bahamut_request('GET', 'https://example.invalid/test').content == b'body remains readable'
    assert closed == [True]


def test_library_snapshot_survives_failed_publication(tmp_path, monkeypatch):
    path = tmp_path / 'video_list.json'
    old = {'videos': [{'sn': '123'}]}
    path.write_text(json.dumps(old), encoding='utf-8')
    monkeypatch.setattr(agp, 'working_dir', str(tmp_path))
    monkeypatch.setattr(agp, 'read_db_all', lambda: [])
    monkeypatch.setattr(agp.Config, 'read_settings', lambda: {'bangumi_dir': str(tmp_path / 'empty')})

    def full_disk(source, destination):
        raise OSError('offline simulated full disk')

    monkeypatch.setattr(agp.Config.os, 'replace', full_disk)
    with pytest.raises(OSError, match='full disk'):
        agp.updatelist()
    assert json.loads(path.read_text(encoding='utf-8')) == old
    assert not list(tmp_path.glob('*.tmp'))


def test_concurrent_library_rebuilds_do_not_publish_an_old_snapshot_last(tmp_path, monkeypatch):
    first_read, second_read, release_first = [threading.Event() for _ in range(3)]
    reads = []
    errors = []
    video = tmp_path / 'episode.mp4'
    video.write_bytes(b'test video')

    def read_db():
        reads.append(True)
        call_number = len(reads)
        if call_number == 1:
            first_read.set()
            assert release_first.wait(5)
        else:
            second_read.set()
        return [{'sn': call_number, 'title': 'test', 'anime_name': 'test',
                 'episode': call_number, 'resolution': 1080,
                 'local_file_path': str(video), 'timestamp': call_number}]

    def rebuild():
        try:
            agp.updatelist()
        except BaseException as error:
            errors.append(error)

    monkeypatch.setattr(agp, 'read_db_all', read_db)
    monkeypatch.setattr(agp, 'working_dir', str(tmp_path))
    monkeypatch.setattr(agp.Config, 'read_settings', lambda: {'bangumi_dir': str(tmp_path / 'empty')})
    monkeypatch.setattr(agp.plugin_manager, 'has_remote', lambda video_data: False)
    first = threading.Thread(target=rebuild, daemon=True)
    second = threading.Thread(target=rebuild, daemon=True)
    first.start()
    assert first_read.wait(5)
    second.start()
    try:
        assert not second_read.wait(0.05), 'A second snapshot must wait for the first publisher'
    finally:
        release_first.set()
        first.join(5)
        second.join(5)
    assert not errors
    assert not first.is_alive() and not second.is_alive()
    assert second_read.is_set()
    data = json.loads((tmp_path / 'video_list.json').read_text(encoding='utf-8'))
    assert [entry['sn'] for entry in data['videos']] == ['2']
