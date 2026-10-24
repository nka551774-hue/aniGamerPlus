"""Bounded catalogue work and safe thumbnail/skip metadata processing."""

import io

import pytest
from PIL import Image, ImageOps

import Catalog
import OpeningSkip
from Dashboard import thumbnail_cache


@pytest.mark.parametrize('html,expected', [
    ('no pagination', 1),
    ('?page=0 ?page=2 ?page=63', 63),
    ('?page=0002 ?page=12', 12),
    ('?page=' + str(Catalog.MAX_CATALOG_PAGES), Catalog.MAX_CATALOG_PAGES),
])
def test_catalogue_page_count_handles_normal_pagination(html, expected):
    assert Catalog.total_pages(html) == expected


@pytest.mark.parametrize('digits', [str(Catalog.MAX_CATALOG_PAGES + 1), '9' * 5000])
def test_catalogue_page_count_rejects_unbounded_crawls(digits):
    with pytest.raises(ValueError, match='implausible catalogue page count'):
        Catalog.total_pages('?page=2 ?page=' + digits)


def test_thumbnail_rejects_oversized_header_before_decode(tmp_path, monkeypatch):
    source = io.BytesIO()
    with Image.new('RGB', (11, 10), 'navy') as original:
        original.save(source, 'JPEG')
    source.seek(0)
    destination = tmp_path / '123.webp'
    destination.write_bytes(b'existing cache')
    monkeypatch.setattr(thumbnail_cache, 'MAX_SOURCE_PIXELS', 100)

    def unexpected_decode(*args, **kwargs):
        pytest.fail('Oversized source must be rejected before pixel decoding')

    monkeypatch.setattr(Image.Image, 'load', unexpected_decode)
    with pytest.raises(ValueError, match='pixel limit'):
        thumbnail_cache.write_webp(source, destination)
    assert destination.read_bytes() == b'existing cache'
    assert not list(tmp_path.glob('.webp-*.tmp'))


def test_thumbnail_shrinks_before_copying_and_preserves_orientation(tmp_path, monkeypatch):
    source = tmp_path / '123.jpg'
    with Image.new('RGB', (1600, 800), 'red') as original:
        original.paste('blue', (800, 0, 1600, 800))
        exif = Image.Exif()
        exif[274] = 6  # Rotate 90 degrees clockwise.
        original.save(source, 'JPEG', exif=exif)

    real_transpose = ImageOps.exif_transpose
    copied_sizes = []

    def transpose(image, *args, **kwargs):
        copied_sizes.append(image.size)
        return real_transpose(image, *args, **kwargs)

    monkeypatch.setattr(thumbnail_cache.ImageOps, 'exif_transpose', transpose)
    destination = tmp_path / '123.webp'
    thumbnail_cache.write_webp(source, destination)
    assert copied_sizes == [(960, 480)]
    with Image.open(destination) as result:
        assert result.format == 'WEBP' and result.size == (480, 960)
        red, _, blue = result.getpixel((240, 120))
        assert red > 200 and blue < 30
        red, _, blue = result.getpixel((240, 840))
        assert blue > 200 and red < 30
        assert result.getexif().get(274, 1) == 1


@pytest.mark.parametrize('mode', ['1', 'P', 'RGBA', 'L', 'CMYK'])
def test_thumbnail_supports_existing_image_modes(tmp_path, mode):
    source = io.BytesIO()
    with Image.new(mode, (1024, 512)) as original:
        original.save(source, 'JPEG' if mode == 'CMYK' else 'PNG')
    source.seek(0)
    destination = tmp_path / '123.webp'
    thumbnail_cache.write_webp(source, destination)
    with Image.open(destination) as result:
        result.load()
        assert result.format == 'WEBP' and result.size == (960, 480)


def test_jpeg_migration_replaces_oversized_existing_thumbnail(tmp_path):
    source = tmp_path / '123.jpg'
    destination = tmp_path / '123.webp'
    with Image.new('RGB', (120, 80), 'red') as original:
        original.save(source, 'JPEG')
    with Image.new('RGB', (1000, 1000), 'blue') as oversized:
        oversized.save(destination, 'WEBP')
    thumbnail_cache.convert_jpeg(source)
    assert not source.exists()
    with Image.open(destination) as result:
        assert result.size == (120, 80)
        red, _, blue = result.getpixel((60, 40))
        assert red > 200 and blue < 30


class _Response:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class _Session:
    def __init__(self, episodes):
        self.episodes = episodes

    def post(self, url, **kwargs):
        return _Response({'data': {'shows': [{'episodes': self.episodes}]}})


class _CountedTimestamp(float):
    subtractions = 0

    def __sub__(self, other):
        type(self).subtractions += 1
        return super().__sub__(other)


def _recording(start=100, end=190):
    return {'season': '1', 'number': '1', 'baseDuration': 1440,
            'timestamps': [
                {'at': _CountedTimestamp(start), 'type': {'name': 'Intro'}},
                {'at': _CountedTimestamp(end), 'type': {'name': 'Canon'}},
            ]}


def test_duplicate_opening_recordings_require_linear_comparisons():
    episodes = [_recording() for _ in range(1000)]
    _CountedTimestamp.subtractions = 0
    interval = OpeningSkip.anime_skip_op(
        {'anilistId': 1}, 1, 1440, session=_Session(episodes))
    assert interval == (100, 190)
    # A provider can supply many recordings of one episode. Comparing every
    # pair performs two million subtractions for this otherwise tiny payload.
    assert _CountedTimestamp.subtractions <= 4 * len(episodes)


@pytest.mark.parametrize('start,end,expected', [
    (103, 193, (100, 190)),
    (103.001, 193, None),
    (100, 193.001, None),
    (96.999, 190, None),
])
def test_opening_recording_conflicts_keep_existing_tolerance(start, end, expected):
    episodes = [_recording(), _recording(start, end)]
    assert OpeningSkip.anime_skip_op(
        {'anilistId': 1}, 1, 1440, session=_Session(episodes)) == expected
