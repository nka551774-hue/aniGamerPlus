"""Run the real publisher against shell fakes; never contact GitHub or push tags."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.github/scripts/publish-nightly.sh'


def _bash():
    if os.name == 'nt':
        for candidate in (r'C:\Program Files\Git\bin\bash.exe', r'C:\msys64\usr\bin\bash.exe'):
            if Path(candidate).is_file():
                return candidate
        pytest.skip('Git Bash or MSYS2 bash is required')
    return shutil.which('bash') or pytest.skip('bash is required')


def _run(tmp_path, scenario='success', files=True):
    hook = tmp_path / 'fake-commands.sh'
    hook.write_text(r'''
git() {
  printf 'git %s\n' "$*" >> "$CALL_LOG"
  return 0
}
gh() {
  printf 'gh %s\n' "$*" >> "$CALL_LOG"
  case "$1 $2" in
    'release view'|'api repos/'*)
      if [[ "$SCENARIO" == missing_release ]]; then
        echo 'HTTP 404: Not Found' >&2
        return 1
      fi
      if [[ "$*" == *'--json body'* || "$1" == api ]]; then
        if [[ "$SCENARIO" == notes_failure ]]; then
          echo 'HTTP 503: temporarily unavailable' >&2
          return 1
        fi
        printf 'Preserved introduction\n- **App**: existing app\n- **Server**: old server\n'
      fi
      ;;
    'release upload')
      [[ "$SCENARIO" != upload_failure ]] || return 7
      ;;
    'release edit')
      local previous=''
      for argument in "$@"; do
        if [[ "$previous" == --notes-file ]]; then cp -- "$argument" "$PUBLISHED_NOTES"; fi
        previous="$argument"
      done
      ;;
  esac
  return 0
}
''', encoding='utf-8')
    artifact = tmp_path / 'server.zip'
    if files:
        artifact.write_bytes(b'test release artifact')
    notes = tmp_path / 'notes.md'
    notes.write_text('An unrelated local document\n', encoding='utf-8')
    env = os.environ.copy()
    env.update({
        'BASH_ENV': hook.as_posix(), 'CALL_LOG': (tmp_path / 'calls.log').as_posix(),
        'PUBLISHED_NOTES': (tmp_path / 'published.txt').as_posix(), 'SCENARIO': scenario,
        'GITHUB_SHA': '1' * 40, 'GITHUB_SERVER_URL': 'https://github.com',
        'GITHUB_REPOSITORY': 'example/test', 'GITHUB_RUN_ID': '123',
        'RUNNER_TEMP': tmp_path.as_posix(),
    })
    result = subprocess.run(
        [_bash(), SCRIPT.as_posix(), 'Server', 'v25.2', artifact.as_posix()],
        cwd=tmp_path, env=env, capture_output=True, text=True, encoding='utf-8', timeout=20,
    )
    calls = (tmp_path / 'calls.log').read_text(encoding='utf-8') if (tmp_path / 'calls.log').exists() else ''
    return result, calls


def test_failed_notes_read_cannot_overwrite_existing_release_notes(tmp_path):
    result, calls = _run(tmp_path, 'notes_failure')
    assert result.returncode != 0, result.stdout + result.stderr
    assert 'release edit' not in calls
    assert 'release upload' not in calls
    assert 'git push' not in calls


def test_failed_upload_does_not_move_the_verified_release_tag(tmp_path):
    result, calls = _run(tmp_path, 'upload_failure')
    assert result.returncode != 0
    assert 'git tag' not in calls
    assert 'git push' not in calls
    assert 'release edit' not in calls


def test_publish_preserves_other_component_and_local_notes(tmp_path):
    result, calls = _run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    published = (tmp_path / 'published.txt').read_text(encoding='utf-8')
    assert 'Preserved introduction' in published
    assert '- **App**: existing app' in published
    assert '- **Server**: v25.2' in published
    assert 'old server' not in published
    assert (tmp_path / 'notes.md').read_text(encoding='utf-8') == 'An unrelated local document\n'
    assert calls.index('release upload') < calls.index('git push')


def test_missing_artifact_is_rejected_before_external_mutation(tmp_path):
    result, calls = _run(tmp_path, files=False)
    assert result.returncode != 0
    assert calls == ''


def test_missing_release_is_created_at_the_requested_commit(tmp_path):
    result, calls = _run(tmp_path, 'missing_release')
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'release create nightly' in calls
    assert '--target ' + '1' * 40 in calls
