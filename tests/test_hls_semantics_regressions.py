"""Keep HLS encryption and timeline semantics intact, or decline the playlist."""

import pytest

import Dashboard.Server as server


def playlist(extra='', key='#EXT-X-KEY:METHOD=AES-128,URI="key.bin"'):
    return ('#EXTM3U\n#EXT-X-TARGETDURATION:10\n#EXT-X-MEDIA-SEQUENCE:42\n'
            + key + '\n#EXTINF:10,\nmedia_b1_0.ts\n' + extra
            + '#EXTINF:10,\nmedia_b1_1.ts\n#EXT-X-ENDLIST\n')


def test_local_event_playlist_preserves_implicit_iv_sequence():
    parsed = server._hls_parse_playlist(playlist())
    assert parsed is not None
    rendered = server._hls_render('123', parsed, ready=2, complete=True)
    assert '#EXT-X-MEDIA-SEQUENCE:42\n' in rendered


@pytest.mark.parametrize('parser', [server._hls_parse_playlist, server._stream_parse_media])
@pytest.mark.parametrize('extra', [
    '#EXT-X-KEY:METHOD=AES-128,URI="another.bin"\n',
    '#EXT-X-KEY:METHOD=NONE\n',
    '#EXT-X-MAP:URI="init.mp4"\n',
    '#EXT-X-BYTERANGE:10@0\n',
    '#EXT-X-DISCONTINUITY\n',
])
def test_unsupported_semantics_are_rejected_instead_of_silently_rewritten(parser, extra):
    assert parser(playlist(extra)) is None


@pytest.mark.parametrize('parser', [server._hls_parse_playlist, server._stream_parse_media])
@pytest.mark.parametrize('duration', ['nan', 'inf', '-1'])
def test_invalid_durations_are_declined(parser, duration):
    assert parser(playlist().replace('#EXTINF:10,', '#EXTINF:%s,' % duration)) is None
