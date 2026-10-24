"""WebP thumbnail encoding and one-way migration of the existing JPEG cache.

Run a bulk migration without starting the server:
    python -m Dashboard.thumbnail_cache [thumbnail-directory]
"""

import argparse
from contextlib import nullcontext
import os
from pathlib import Path
import re
import tempfile
import threading

from PIL import Image, ImageOps


_encoders = threading.BoundedSemaphore(2)
# Remote covers are untrusted. Pillow's default decompression-bomb threshold
# allows much larger images than a thumbnail needs and initially only warns.
MAX_SOURCE_PIXELS = 32_000_000
THUMBNAIL_SIZE = (960, 960)


def _check_image_size(image):
    width, height = image.size
    if width <= 0 or height <= 0 or width * height > MAX_SOURCE_PIXELS:
        raise ValueError('Thumbnail source exceeds the pixel limit')


def write_webp(source, destination):
    """Publish a verified image atomically; never expose a partial cache file."""
    destination = Path(destination)
    temporary = None
    try:
        with _encoders:
            with Image.open(source) as original:
                _check_image_size(original)
                # Shrink before EXIF transpose/RGB conversion: those operations
                # otherwise allocate additional full-resolution pixel buffers.
                # JPEG thumbnail() can also use the decoder's draft reduction.
                # Palette/1-bit inputs need RGB first to retain LANCZOS filtering.
                working = (original.convert('RGB')
                           if original.mode in ('1', 'P') else original)
                try:
                    working.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    with ImageOps.exif_transpose(working) as oriented:
                        with oriented.convert('RGB') as image:
                            fd, temporary = tempfile.mkstemp(
                                prefix='.webp-', suffix='.tmp', dir=destination.parent)
                            with os.fdopen(fd, 'wb') as handle:
                                image.save(handle, format='WEBP', quality=82, method=4)
                            with Image.open(temporary) as check:
                                check.load()
                                if check.format != 'WEBP' or check.size != image.size:
                                    raise ValueError('Invalid WebP output')
                finally:
                    if working is not original:
                        working.close()
            os.replace(temporary, destination)
    finally:
        if temporary and os.path.exists(temporary):
            os.remove(temporary)


def convert_jpeg(source):
    """Delete a JPEG only after its replacement has been successfully decoded."""
    source = Path(source)
    destination = source.with_suffix('.webp')
    reusable = False
    if destination.exists() and destination.stat().st_mtime_ns >= source.stat().st_mtime_ns:
        try:
            with Image.open(destination) as check:
                _check_image_size(check)
                if (check.format == 'WEBP' and
                        check.width <= THUMBNAIL_SIZE[0] and
                        check.height <= THUMBNAIL_SIZE[1]):
                    check.load()
                    reusable = True
        except (OSError, ValueError):
            pass
    if not reusable:
        write_webp(source, destination)
    saved = source.stat().st_size - destination.stat().st_size
    source.unlink()
    return saved


def migrate_directory(directory, lock_for=None):
    """Convert only thumbnail cache JPEGs, sequentially, and retain failed inputs."""
    directory = Path(directory).resolve()
    result = {'converted': 0, 'failed': 0, 'bytes_saved': 0}
    if not directory.is_dir():
        return result
    for source in directory.iterdir():
        if (source.is_symlink() or not source.is_file() or
                not re.fullmatch(r'[0-9A-Za-z]+\.(?:jpg|jpeg)', source.name, re.I)):
            continue
        with lock_for(source.stem) if lock_for else nullcontext():
            if not source.exists():
                continue  # A request already converted this entry.
            try:
                result['bytes_saved'] += convert_jpeg(source)
                result['converted'] += 1
            except Exception:
                result['failed'] += 1
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?',
                        default=Path(__file__).resolve().parents[1] / 'thumbnails')
    result = migrate_directory(parser.parse_args().directory)
    print(result)
    raise SystemExit(1 if result['failed'] else 0)
