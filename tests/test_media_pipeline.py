"""A real, entirely local encrypted-HLS download/merge/decode round trip."""

from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

import pytest
import requests

import Anime as anime_module


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='needs ffmpeg for real encrypted HLS')
def test_real_encrypted_segments_merge_and_decode(tmp_path, monkeypatch):
    ffmpeg = shutil.which('ffmpeg')
    upstream = tmp_path / 'upstream'
    upstream.mkdir()
    key = upstream / 'key.bin'
    key.write_bytes(b'0123456789abcdef')
    key_info = upstream / 'key-info.txt'
    key_info.write_text('key.bin\n' + key.as_posix() + '\n' + '0' * 31 + '1\n', encoding='utf-8')
    playlist = upstream / 'playlist.m3u8'
    subprocess.run([
        ffmpeg, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=64x64:r=10',
        '-t', '2', '-an', '-c:v', 'libx264', '-g', '10', '-hls_time', '1',
        '-hls_playlist_type', 'vod', '-hls_key_info_file', str(key_info),
        '-hls_segment_filename', str(upstream / 'media_b1_%d.ts'), str(playlist),
    ], check=True, capture_output=True, timeout=30)

    anime = anime_module.Anime.__new__(anime_module.Anime)
    anime._sn, anime._title = 123, 'Local encrypted fixture'
    anime._settings = {'multi_downloading_segment': 3, 'segment_max_retry': 0,
                       'faststart_movflags': True, 'audio_language': False,
                       'use_copyfile_method': False}
    anime._bangumi_dir, anime._temp_dir = str(tmp_path / 'library'), str(tmp_path / 'temp')
    Path(anime._bangumi_dir).mkdir()
    Path(anime._temp_dir).mkdir()
    anime._m3u8_dict = {'1080': 'https://fixture.invalid/playlist.m3u8'}
    anime._ffmpeg_path = ffmpeg
    anime.video_size, anime.local_video_path = 0, ''
    anime.realtime_show_file_size = False
    anime.get_filename = lambda: 'episode.mp4'
    anime._Anime__get_filename = lambda resolution: 'episode.mp4'
    anime._Anime__get_temp_filename = lambda resolution, temp_suffix: 'merge.mp4'

    def request(url, **kwargs):
        parsed = urlsplit(url)
        assert parsed.hostname == 'fixture.invalid'
        name = parsed.path.lstrip('/')
        assert '/' not in name and '\\' not in name
        result = requests.Response()
        result.status_code, result.encoding = 200, 'utf-8'
        result._content = (upstream / name).read_bytes()
        return result

    monkeypatch.setattr(anime, '_Anime__request', request)
    monkeypatch.setattr(anime_module.Config, 'tasks_progress_rate', {})
    anime._Anime__segment_download_mode('1080')
    output = Path(anime.local_video_path)
    assert output.is_file() and output.stat().st_size > 0
    assert not list(Path(anime._temp_dir).iterdir())
    subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-i', str(output), '-f', 'null', '-'],
                   check=True, capture_output=True, timeout=30)
