"""Build the server executable with explicit runtime data, never the checkout."""
from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def build_command(root=ROOT):
    root = Path(root).resolve()
    command = [
        sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile', '--console',
        '--distpath', str(root), '--workpath', str(root / 'build/pyinstaller'),
        '--specpath', str(root / 'build/pyinstaller-spec'),
    ]
    # Config.working_dir still resolves beside the executable: the release also
    # ships Dashboard and DanmuTemplate.ass there. Keep only runtime resources
    # in the internal bundle, excluding .git, credentials, tests and old builds.
    for source, destination in (
        ('Dashboard/templates', 'Dashboard/templates'),
        ('Dashboard/static', 'Dashboard/static'),
        ('DanmuTemplate.ass', '.'),
    ):
        command += ['--add-data', str(root / source) + os.pathsep + destination]
    if os.name == 'nt':
        command += ['--icon', str(root / 'Dashboard/static/img/aniGamerPlus.ico')]
    command.append(str(root / 'aniGamerPlus.py'))
    return command


def main():
    return subprocess.run(build_command(), cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
