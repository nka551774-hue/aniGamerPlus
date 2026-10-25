"""Packaging must not turn an entire checkout, including its secrets, into data."""
import importlib.util
import os
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('workflow', ['Python-build.yml', 'Release-build.yml'])
def test_workflow_does_not_bundle_the_checkout_as_data(workflow):
    text = (ROOT / '.github/workflows' / workflow).read_text(encoding='utf-8')
    assert not re.search(r'--add-data\s+["\']?(?:%cd%|\./|\.)(?:;|:)', text), (
        'Collecting the checkout includes .git, cookies, configuration and build output'
    )


def _builder():
    path = ROOT / '.github/scripts/build-executable.py'
    spec = importlib.util.spec_from_file_location('agp_build_executable', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bundle_inputs_preserve_runtime_assets_and_exclude_private_files(tmp_path):
    public = {
        'Dashboard/templates/index.html', 'Dashboard/static/js/app.js',
        'Dashboard/static/img/aniGamerPlus.ico', 'DanmuTemplate.ass',
    }
    private = {
        '.git/config', '.env', 'cookie.txt', 'config.json', 'Dashboard/userdata.json',
        'Dashboard/sslkey/server.key', 'build/old.exe', 'flutter_app/signing.jks',
    }
    for name in public | private | {'aniGamerPlus.py'}:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('synthetic fixture', encoding='utf-8')
    command = _builder().build_command(tmp_path)
    collected = set()
    for index, part in enumerate(command):
        if part != '--add-data':
            continue
        source, _destination = command[index + 1].rsplit(os.pathsep, 1)
        source = Path(source)
        inputs = source.rglob('*') if source.is_dir() else [source]
        collected.update(path.relative_to(tmp_path).as_posix() for path in inputs if path.is_file())
    assert collected == public
    assert not collected & private


def test_builder_propagates_build_failure(monkeypatch):
    module = _builder()
    calls = []

    def failed(command, **kwargs):
        calls.append((command, kwargs))
        return type('Result', (), {'returncode': 7})()

    monkeypatch.setattr(module.subprocess, 'run', failed)
    assert module.main() == 7
    assert calls[0][1]['cwd'] == ROOT
