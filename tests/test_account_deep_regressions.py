"""Fail closed on damaged account storage, without touching operator files."""

import builtins
import errno
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import Dashboard.Server as server
from test_fastapi_server import make_settings


@pytest.fixture
def account_store(tmp_path, monkeypatch):
    settings = make_settings()
    settings['dashboard']['user_control'].update(enabled=True, allow_register=True)
    path = tmp_path / 'userdata.json'
    monkeypatch.setattr(server, 'userdata_path', str(path))
    monkeypatch.setattr(server.Config, 'read_settings', lambda *args, **kwargs: settings)
    monkeypatch.setattr(server, '_get_current_settings', lambda: settings)
    return path, settings


@pytest.mark.parametrize('content', [
    b'{"users": [', b'\xff\xfeinvalid', b'[]', b'null', b'{}', b'{"users": {}}',
    b'{"users": [null]}', b'{"users": [{"username":""}]}',
    b'{"users":[{"username":"Alice"},{"username":"alice"}]}',
], ids=['truncated', 'invalid-encoding', 'array', 'null', 'missing-users',
        'wrong-users-type', 'invalid-record', 'missing-username', 'duplicate-users'])
def test_damaged_store_is_never_replaced_with_default_accounts(account_store, content):
    path, _ = account_store
    path.write_bytes(content)
    with TestClient(server.app) as client:
        response = client.post('/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 503
    assert response.headers['cache-control'] == 'no-store'
    assert 'token=' not in response.headers.get('set-cookie', '')
    assert path.read_bytes() == content
    assert not list(path.parent.glob('.userdata-*.tmp'))


@pytest.mark.parametrize('code', [errno.EACCES, errno.EIO])
def test_unreadable_store_does_not_reset_passwords(account_store, monkeypatch, code):
    path, _ = account_store
    before = b'{"users": [{"username":"admin","password":"changed-password"}]}'
    path.write_bytes(before)
    original_open = builtins.open

    def denied(filename, mode='r', *args, **kwargs):
        if str(filename) == str(path) and mode == 'r':
            raise OSError(code, 'simulated read failure')
        return original_open(filename, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', denied)
    with pytest.raises(server.UserDataUnavailable):
        server.load_user_data()
    assert path.read_bytes() == before


def test_first_run_still_creates_defaults_and_legacy_users_still_migrate(account_store):
    path, _ = account_store
    created = server.load_user_data()['users'][0]
    assert server._verify_password(created, 'admin')
    assert path.is_file() and 'password' not in created
    path.write_text(json.dumps({'revision': 7, 'users': [
        {'name': 'legacy', 'password': 'old-password', 'role': 'user'}]}), encoding='utf-8')
    migrated = server.load_user_data()
    assert migrated['revision'] == 7
    legacy = next(user for user in migrated['users'] if user['username'] == 'legacy')
    assert server._verify_password(legacy, 'old-password')
    assert 'password' not in legacy


@pytest.mark.parametrize('code', [errno.ENOSPC, errno.EIO])
def test_failed_file_sync_preserves_previous_accounts(account_store, monkeypatch, code):
    path, _ = account_store
    old = server.load_user_data()
    before = path.read_bytes()

    def fail_sync(fd):
        raise OSError(code, 'simulated delayed write failure')

    monkeypatch.setattr(server.os, 'fsync', fail_sync)
    with pytest.raises(server.UserDataUnavailable):
        server.save_user_data({'users': []})
    assert path.read_bytes() == before
    assert server.load_user_data() == old
    assert not list(path.parent.glob('.userdata-*.tmp'))


@pytest.mark.parametrize('code', [errno.EINVAL, errno.ENOSYS, errno.ENOTSUP])
def test_storage_without_fsync_support_can_still_publish(account_store, monkeypatch, code):
    path, settings = account_store
    settings['dashboard']['user_control']['default_user'] = []

    def unsupported(fd):
        raise OSError(code, 'fsync unsupported')

    monkeypatch.setattr(server.os, 'fsync', unsupported)
    server.save_user_data({'users': []})
    assert json.loads(path.read_text(encoding='utf-8')) == {'users': []}
