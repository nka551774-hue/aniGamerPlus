"""Compare thumbnail encoders from a Git revision and the current checkout.

Run from the repository with its Python environment, for example::

    python tools/benchmark_thumbnail.py --baseline-ref <commit> --runs 3

Each measurement runs in a fresh process. Input generation and source loading
are outside the timed section. The baseline module is executed from the selected
Git revision; use a revision whose code you trust. Only temporary files are used.
"""

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path


def _peak_resident_bytes():
    if sys.platform == 'win32':
        import ctypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ('cb', ctypes.c_ulong),
                ('PageFaultCount', ctypes.c_ulong),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        current_process = ctypes.windll.kernel32.GetCurrentProcess
        current_process.restype = ctypes.c_void_p
        get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
        get_memory.argtypes = [ctypes.c_void_p, ctypes.POINTER(ProcessMemoryCounters),
                              ctypes.c_ulong]
        if not get_memory(current_process(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError()
        return counters.PeakWorkingSetSize

    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak if sys.platform == 'darwin' else peak * 1024


def _worker(source, image, output):
    module = types.ModuleType('thumbnail_benchmark')
    exec(compile(source.read_text(encoding='utf-8'), str(source), 'exec'), module.__dict__)
    started = time.perf_counter()
    module.write_webp(image, output)
    elapsed = time.perf_counter() - started
    return {'seconds': elapsed, 'peak_resident_mib': _peak_resident_bytes() / 1024**2,
            'output_bytes': output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref', required=True,
                        help='Git commit containing the previous thumbnail encoder')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--width', type=int, default=6000)
    parser.add_argument('--height', type=int, default=4000)
    args = parser.parse_args()
    if min(args.runs, args.width, args.height) < 1:
        parser.error('runs and image dimensions must be positive')

    from PIL import Image, __version__ as pillow_version

    root = Path(__file__).resolve().parents[1]
    baseline_commit = subprocess.check_output(
        ['git', 'rev-parse', '--verify', '--end-of-options', args.baseline_ref + '^{commit}'],
        cwd=root, text=True).strip()
    baseline = subprocess.check_output(
        ['git', 'show', baseline_commit + ':Dashboard/thumbnail_cache.py'], cwd=root)
    results = {}
    with tempfile.TemporaryDirectory(prefix='agp-thumbnail-benchmark-') as folder:
        directory = Path(folder)
        source_image = directory / 'input.jpg'
        with Image.new('RGB', (args.width, args.height), 'navy') as image:
            image.save(source_image, 'JPEG')
        (directory / 'baseline.py').write_bytes(baseline)
        (directory / 'current.py').write_bytes(
            (root / 'Dashboard/thumbnail_cache.py').read_bytes())
        for version in ('baseline', 'current'):
            samples = []
            for index in range(args.runs):
                output = subprocess.check_output([
                    sys.executable, str(Path(__file__).resolve()), '--worker',
                    str(directory / (version + '.py')), str(source_image),
                    str(directory / (version + '-' + str(index) + '.webp')),
                ], text=True)
                samples.append(json.loads(output))
            results[version] = {
                'samples': samples,
                'median_seconds': statistics.median(row['seconds'] for row in samples),
                'median_peak_resident_mib': statistics.median(
                    row['peak_resident_mib'] for row in samples),
            }
    return {
        'baseline_commit': baseline_commit,
        'python': sys.version,
        'pillow': pillow_version,
        'platform': sys.platform,
        'image': {'width': args.width, 'height': args.height, 'color': 'navy', 'format': 'JPEG'},
        'memory_metric': 'PeakWorkingSetSize' if sys.platform == 'win32' else 'ru_maxrss',
        'results': results,
    }


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--worker':
        result = _worker(*(Path(value) for value in sys.argv[2:]))
    else:
        result = main()
    print(json.dumps(result, ensure_ascii=True, indent=2))
