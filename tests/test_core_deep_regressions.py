"""Second-pass core regressions: transactions, completed files and retries."""

import copy
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import threading
import types
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

import pytest
import requests

import Anime as anime_module
import aniGamerPlus as agp
import Catalog
import Danmu as danmu_module
import Loginer


@pytest.fixture
def quiet(monkeypatch):
    monkeypatch.setattr(anime_module, 'err_print', lambda *a, **k: None)
    monkeypatch.setattr(agp, 'err_print', lambda *a, **k: None)
    monkeypatch.setattr(danmu_module, 'err_print', lambda *a, **k: None)


def anime_record(size=10):
    return types.SimpleNamespace(
        get_sn=lambda: 123, get_title=lambda: 'Episode', get_bangumi_name=lambda: 'Series',
        get_episode=lambda: '1', video_size=size, video_resolution=720,
        local_video_path='', upload_succeed_flag=False)


@pytest.mark.parametrize('operation', ['insert_db', 'update_db'])
def test_failed_commit_closes_connection_and_releases_database_gate(monkeypatch, operation, quiet):
    gate = threading.Semaphore(1)
    closed = []

    class Connection:
        def cursor(self):
            return types.SimpleNamespace(execute=lambda *a: None, close=lambda: None)

        def commit(self):
            raise sqlite3.OperationalError('offline simulated disk full during commit')

        def close(self):
            closed.append(True)

    monkeypatch.setattr(agp, 'db_locker', gate)
    monkeypatch.setattr(agp.sqlite3, 'connect', lambda *a: Connection())
    with pytest.raises(sqlite3.OperationalError, match='disk full'):
        getattr(agp, operation)(anime_record())
    assert closed == [True]
    assert gate.acquire(blocking=False), 'A failed commit must not freeze every later DB operation'


@pytest.mark.parametrize('operation', ['read_db', 'read_db_all', 'insert_db', 'update_db'])
def test_cursor_cleanup_failure_still_closes_connection_and_releases_gate(monkeypatch, operation, quiet):
    gate = threading.Semaphore(1)
    closed = []
    row = (123, 'Title', 'Series', '1', 1, 0, 720, 10, '', '2026-01-01 00:00:00')

    def fail_close():
        raise sqlite3.OperationalError('offline cursor close failure')

    connection = types.SimpleNamespace(
        cursor=lambda: types.SimpleNamespace(execute=lambda *a: None,
                                             fetchall=lambda: [row], close=fail_close),
        commit=lambda: None, close=lambda: closed.append(True))
    monkeypatch.setattr(agp, 'db_locker', gate)
    monkeypatch.setattr(agp.sqlite3, 'connect', lambda *a: connection)
    args = [] if operation == 'read_db_all' else [123 if operation == 'read_db' else anime_record()]
    with pytest.raises(sqlite3.OperationalError, match='cursor close failure'):
        getattr(agp, operation)(*args)
    assert closed == [True]
    assert gate.acquire(blocking=False)


@pytest.mark.parametrize('operation', ['insert_db', 'update_db'])
def test_failed_statement_is_not_committed(monkeypatch, operation, quiet):
    commits = []

    def fail_execute(*args):
        raise sqlite3.OperationalError('offline failed statement')

    connection = types.SimpleNamespace(
        cursor=lambda: types.SimpleNamespace(execute=fail_execute, close=lambda: None),
        commit=lambda: commits.append(True), close=lambda: None)
    monkeypatch.setattr(agp, 'db_locker', threading.Semaphore(1))
    monkeypatch.setattr(agp.sqlite3, 'connect', lambda *a: connection)
    with pytest.raises(sqlite3.OperationalError, match='failed statement'):
        getattr(agp, operation)(anime_record())
    assert commits == []


@pytest.fixture
def public_anime(tmp_path, monkeypatch, quiet):
    anime = anime_module.Anime.__new__(anime_module.Anime)
    library, temporary = tmp_path / 'library', tmp_path / 'temporary'
    library.mkdir()
    temporary.mkdir()
    anime._sn, anime._title, anime._episode = 123, 'Series [1]', '1'
    anime._bangumi_name = 'Series'
    anime._working_dir = str(tmp_path)
    anime._bangumi_dir, anime._temp_dir = str(library), str(temporary)
    anime._settings = {
        'bangumi_dir': str(library), 'download_resolution': '720',
        'classify_season': False, 'segment_download_mode': True,
        'lock_resolution': False, 'multi_downloading_segment': 2,
        'segment_max_retry': 0, 'faststart_movflags': False,
        'audio_language': False, 'use_copyfile_method': False,
        'coolq_notify': False, 'telebot_notify': False, 'discord_notify': False,
        'plex_refresh': False, 'save_m3u8': False, 'm3u8': False,
    }
    anime.video_size, anime.video_resolution = 0, 0
    anime.local_video_path, anime._video_filename = '', ''
    anime.upload_succeed_flag = False
    anime._danmu = False
    anime.season_title_filter = re.compile(r'第[零一二三四五六七八九十]{1,3}季$')
    anime.extra_title_filter = re.compile(r'\[(特別篇|中文配音)\]$')
    anime._m3u8_dict = {'720': 'https://fixture.invalid/playlist.m3u8'}
    anime._Anime__get_m3u8_dict = lambda: None
    anime._Anime__get_filename = lambda *a, **k: 'episode.mp4'
    anime._Anime__get_temp_filename = lambda *a, **k: 'merge.mp4'
    anime._Anime__segment_download_mode = lambda resolution: None
    monkeypatch.setattr(anime_module.Config, 'tasks_progress_rate', {})
    monkeypatch.setattr(anime_module.shutil, 'which', lambda executable: 'offline-ffmpeg')
    monkeypatch.setattr(anime_module.subprocess, 'Popen', lambda *a, **k: types.SimpleNamespace(
        stdout=types.SimpleNamespace(readlines=lambda: [b'offline ffmpeg help'])))
    return anime


def test_retry_reuses_the_library_root_instead_of_nesting_series_directories(public_anime):
    anime = public_anime
    anime.download(bangumi_tag='Season')
    first_directory = anime._bangumi_dir
    anime.download(bangumi_tag='Season')
    assert anime._bangumi_dir == first_directory
    assert Path(first_directory) == Path(anime._settings['bangumi_dir']) / 'Season' / 'Series'


def test_failed_attempt_does_not_retain_previous_success_or_send_completion_notifications(
        public_anime, monkeypatch):
    anime = public_anime
    anime.video_size = 100
    anime.local_video_path = 'previous.mp4'
    anime.download_succeeded = True
    anime._settings['discord_notify'] = True
    anime._settings['discord_token'] = 'offline-not-a-real-webhook'
    calls = []
    monkeypatch.setattr(anime_module.requests, 'post', lambda *a, **k: calls.append(True))
    anime.download()
    assert anime.video_size == 0
    assert anime.local_video_path == ''
    assert anime.download_succeeded is False
    assert calls == []
    assert 123 not in anime_module.Config.tasks_progress_rate


def test_resolution_mismatch_clears_attempt_progress(public_anime):
    anime = public_anime
    anime._settings['lock_resolution'] = True
    anime.download(resolution='1080')
    assert 123 not in anime_module.Config.tasks_progress_rate


@pytest.fixture
def local_database(tmp_path, monkeypatch):
    path = tmp_path / 'library.sqlite'
    with sqlite3.connect(path) as conn:
        conn.execute('''CREATE TABLE anime (
            sn INTEGER PRIMARY KEY, title TEXT, anime_name TEXT, episode TEXT,
            status INTEGER DEFAULT 0, remote_status INTEGER DEFAULT 0,
            resolution INTEGER, file_size REAL, local_file_path TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP)''')
    monkeypatch.setattr(agp, 'db_path', str(path))
    monkeypatch.setattr(agp, 'db_locker', threading.Semaphore(1))
    return path


def test_exactly_five_megabytes_is_not_success_to_worker_but_failure_to_database(
        local_database, quiet):
    anime = anime_record(size=5)
    agp.insert_db(anime)
    agp.update_db(anime)
    assert agp.read_db(123)['status'] == 1


@pytest.fixture
def danmu_env(tmp_path, monkeypatch, quiet):
    output = tmp_path / 'episode.ass'
    output.write_text('existing valid subtitles', encoding='utf-8')
    (tmp_path / 'DanmuTemplate.ass').write_text('[Script Info]\n', encoding='utf-8')
    monkeypatch.setattr(danmu_module.Config, 'read_settings', lambda: {'ua': 'offline'})
    monkeypatch.setattr(danmu_module.Config, 'get_working_dir', lambda: str(tmp_path))
    state = types.SimpleNamespace(
        body=[{'text': 'hello', 'time': 10, 'color': '#FFFFFF', 'position': 1}],
        keywords=[{'keyword': 'blocked'}])

    def request(method, *args, **kwargs):
        value = state.body if method == 'POST' else state.keywords
        return types.SimpleNamespace(status_code=200, text=json.dumps(value))

    monkeypatch.setattr(danmu_module.Config, 'bahamut_request', request)
    return danmu_module.Danmu(123, str(output), {}), state, output


def test_invalid_danmu_record_does_not_truncate_previous_subtitles(danmu_env):
    danmu, state, output = danmu_env
    state.body = [{'text': 'missing time/color/position'}]
    with pytest.raises((KeyError, ValueError)):
        danmu.download([])
    assert output.read_text(encoding='utf-8') == 'existing valid subtitles'


def test_downloading_danmu_does_not_grow_the_configured_filter_list(danmu_env):
    danmu, state, output = danmu_env
    filters = ['configured']
    danmu.download(filters)
    danmu.download(filters)
    assert filters == ['configured']
    assert 'Dialogue:' in output.read_text(encoding='utf-8')


def test_online_keywords_are_literal_not_untrusted_regex_patterns(danmu_env):
    danmu, state, output = danmu_env
    state.keywords = [{'keyword': '['}]
    danmu.download([])
    assert 'hello' in output.read_text(encoding='utf-8')


def test_small_published_video_is_complete_but_failed_attempt_never_is(local_database, tmp_path, quiet):
    path = tmp_path / 'short.mp4'
    path.write_bytes(b'short successfully published fixture')
    anime = anime_record(size=0)
    anime.download_succeeded = True
    anime.local_video_path = str(path)
    agp.insert_db(anime)
    agp.update_db(anime)
    assert agp.read_db(123)['status'] == 1
    anime.download_succeeded = False
    agp.update_db(anime)
    assert agp.read_db(123)['status'] == 0


def test_separate_episode_instances_share_one_download_lock(monkeypatch):
    barrier = threading.Barrier(8)
    guard = threading.Lock()
    active = peak = 0

    def download(instance, *args):
        nonlocal active, peak
        with guard:
            active += 1
            peak = max(peak, active)
        time.sleep(0.01)
        with guard:
            active -= 1

    monkeypatch.setattr(anime_module.Anime, '_download', download)

    def work(_):
        anime = anime_module.Anime.__new__(anime_module.Anime)
        anime._sn = 123
        anime._settings = {'bangumi_dir': 'unused'}
        barrier.wait(timeout=5)
        anime.download()

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(work, range(8)))
    assert peak == 1


def test_telegram_failure_never_logs_bot_token_or_chat_id(public_anime,
                                                           monkeypatch):
    anime = public_anime
    output = Path(anime._bangumi_dir) / 'episode.mp4'

    def publish(_resolution):
        output.write_bytes(b'published video')
        anime.local_video_path = str(output)
        anime._video_filename = output.name
        anime.video_size = 1
        anime.download_succeeded = True

    anime._Anime__segment_download_mode = publish
    anime._settings.update({
        'telebot_notify': True,
        'telebot_token': 'offline-secret-bot-token',
        'telebot_use_chat_id': True,
        'telebot_chat_id': 'offline-secret-chat-id',
    })
    monkeypatch.setattr(
        anime_module.requests, 'post',
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError('offline')))
    logs = []
    monkeypatch.setattr(anime_module, 'err_print',
                        lambda *a, **k: logs.append(' '.join(map(str, a))))

    anime.download()

    rendered = '\n'.join(logs)
    assert 'offline-secret-bot-token' not in rendered
    assert 'offline-secret-chat-id' not in rendered


def test_ftp_upload_does_not_change_process_wide_socket_timeout(
        public_anime, monkeypatch, tmp_path):
    anime = public_anime
    video = tmp_path / 'episode.mp4'
    video.write_bytes(b'fixture')
    anime.local_video_path = str(video)
    anime._video_filename = video.name
    anime._settings['ftp'] = {
        'tls': False, 'server': 'offline.invalid', 'port': 21,
        'user': 'user', 'pwd': 'password', 'cwd': '',
        'show_error_detail': False, 'max_retry_num': 0,
    }

    class OfflineFtp:
        def connect(self, *args, **kwargs):
            raise RuntimeError('offline')

    monkeypatch.setattr(anime_module, 'FTP', OfflineFtp)
    monkeypatch.setattr(
        anime_module.socket, 'setdefaulttimeout',
        lambda _timeout: (_ for _ in ()).throw(
            AssertionError('must not mutate the process-wide socket timeout')))

    assert anime.upload() is False


def test_export_my_anime_stops_after_http_failure(monkeypatch, tmp_path, quiet):
    calls = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(agp.Config, 'read_cookie', lambda: {'BAHARUNE': 'offline'})

    def request(*args, **kwargs):
        calls.append(True)
        if len(calls) > 1:
            raise AssertionError('HTTP failure must not start an unbounded page loop')
        return types.SimpleNamespace(status_code=503, text='offline')

    monkeypatch.setattr(agp, 'do_request', request)
    agp.export_my_anime()
    assert calls == [True]
    assert not (tmp_path / 'my_anime.txt').exists()


@pytest.mark.parametrize('value, expected', [
    ('true', True), ('TRUE', True), ('1', True), ('yes', True),
    ('false', False), ('FALSE', False), ('0', False), ('no', False),
])
def test_login_cli_boolean_arguments_are_parsed_by_value(value, expected):
    assert Loginer._parse_bool_arg(value) is expected


def test_login_cli_boolean_arguments_reject_ambiguous_values():
    with pytest.raises(ValueError, match='true/false'):
        Loginer._parse_bool_arg('definitely')


def test_catalog_plain_text_decodes_named_and_numeric_html_entities():
    assert Catalog.plain_text(
        '<p>Tom &apos;N&apos; Jerry &#x1F600; &#39;ok&#39;&nbsp;</p>'
    ) == "Tom 'N' Jerry 😀 'ok'"


@pytest.mark.skipif(os.name != 'nt', reason='Windows ANSI CA path compatibility')
def test_unicode_ca_bundle_retains_the_trusted_certificates(tmp_path):
    path = tmp_path / '\u52d5\u756b\u6191\u8b49.pem'
    path.write_bytes(b'public test CA bundle')
    adapted = anime_module.Config.curl_ca_bundle(str(path))
    assert Path(adapted).read_bytes() == path.read_bytes()
    assert adapted == anime_module.Config.curl_ca_bundle(str(path))
