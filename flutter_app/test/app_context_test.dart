import 'dart:async';
import 'dart:io';

import 'package:agp_mobile/src/api/client.dart';
import 'package:agp_mobile/src/api/models.dart';
import 'package:agp_mobile/src/state/app_state.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'support/temp_dir.dart';

class Paths extends PathProviderPlatform {
  Paths(this.path);
  final String path;
  Completer<String?>? supportResult;
  Completer<void>? supportStarted;
  @override
  Future<String?> getApplicationDocumentsPath() async => path;
  @override
  Future<String?> getApplicationSupportPath() async {
    final result = supportResult;
    if (result == null) return path;
    if (supportStarted?.isCompleted == false) supportStarted!.complete();
    return result.future;
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late Directory temp;
  late AppState state;
  late Paths paths;
  late Future<http.Response> Function(http.Request) reply;

  setUp(() async {
    temp = await Directory.systemTemp.createTemp('agp-account-test-');
    paths = Paths(temp.path);
    PathProviderPlatform.instance = paths;
    SharedPreferences.setMockInitialValues({});
    reply = (request) async => http.Response('{}', 200);
    final api = AgpClient(
        baseUrl: 'https://old.invalid',
        token: 'old-token',
        httpClient: MockClient((request) => reply(request)));
    state = await AppState.boot(client: api);
    await state.prefs.setServer('https://old.invalid');
    await state.prefs.setToken('old-token');
  });

  tearDown(() async {
    await state.flushWatchTimesToDisk();
    state.downloadNetwork.dispose();
    state.downloadBackground.dispose();
    state.downloads.dispose();
    state.discord.dispose();
    state.client.close();
    await deleteTempDir(temp);
  });

  test('changing servers clears the persisted token before the next boot',
      () async {
    await state.setServer('https://new.invalid');
    expect(state.client.token, isNull);
    expect(state.prefs.token, isEmpty);
    expect(state.prefs.server, 'https://new.invalid');
  });

  test('anonymous remote setup cannot retain another server token on disk',
      () async {
    await state.applyRemoteSetup(server: 'https://new.invalid');
    expect(state.client.token, isNull);
    expect(state.prefs.token, isEmpty);
  });

  test('late logout cannot erase a newer account token on disk', () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    reply = (request) async {
      if (request.url.path == '/logout') {
        started.complete();
        return response.future;
      }
      return http.Response('{}', 200);
    };
    final logout = state.logout();
    await started.future;
    state.client.token = 'new-token';
    await state.prefs.setToken('new-token');
    response.complete(http.Response('{}', 200));
    await logout;
    expect(state.client.token, 'new-token');
    expect(state.prefs.token, 'new-token');
  });

  test('stale library rejection cannot replace a newer account library',
      () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    reply = (request) async {
      if (request.url.path == '/video_list.json') {
        started.complete();
        return response.future;
      }
      return http.Response('{}', 200);
    };
    final loading = state.refreshLibrary();
    await started.future;
    state.client.baseUrl = 'https://new.invalid';
    state.library = [VideoItem(sn: '999', title: 'new account')];
    state.lastError = '';
    response.complete(http.Response('[]', 200));
    await loading;
    expect(state.library.single.sn, '999');
    expect(state.lastError, isEmpty);
  });

  test('stale watch response is rejected without merging into a newer account',
      () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    state.serverInfo = ServerInfo(userControl: true);
    state.currentUser = CurrentUser(username: 'old-user');
    reply = (request) async {
      if (request.url.path == '/watch/time') {
        started.complete();
        return response.future;
      }
      return http.Response('{}', 200);
    };
    final loading = state.refreshWatchTimes();
    await started.future;
    state.client.token = 'new-token';
    state.watchTimes = {'999': WatchTime(time: 42, timestamp: 100)};
    response.complete(http.Response('{"123":{"time":7,"timestamp":200}}', 200));
    await loading;
    expect(state.watchTimes.keys, ['999']);
  });

  test('logout waiting for a file path cannot delete new account watch data',
      () async {
    paths.supportStarted = Completer<void>();
    paths.supportResult = Completer<String?>();
    final logout = state.logout();
    await paths.supportStarted!.future;
    state.client.token = 'new-token';
    await state.prefs.setToken('new-token');
    final watch = File('${temp.path}/watch-times.json');
    await watch.writeAsString('{"999":{"time":42}}');
    paths.supportResult!.complete(temp.path);
    await logout;
    expect(await watch.exists(), isTrue);
    expect(await watch.readAsString(), contains('999'));
  });

  test('late watch deletion cannot erase a new account entry', () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    reply = (request) async {
      if (request.method == 'POST' && request.url.path == '/watch/time') {
        started.complete();
        return response.future;
      }
      return http.Response('{}', 200);
    };
    state.watchTimes = {'123': WatchTime(time: 7)};
    final deleting = state.forgetWatchTime('123');
    await started.future;
    state.client.token = 'new-token';
    state.noteWatchTime('123', WatchTime(time: 42), pending: true);
    response.complete(http.Response('{}', 200));
    await deleting;
    expect(state.watchTimeOf('123')?.time, 42);
    expect(state.isWatchTimePending('123'), isTrue);
  });

  test('delayed watch save cannot overwrite a new account file', () async {
    paths.supportStarted = Completer<void>();
    paths.supportResult = Completer<String?>();
    state.watchTimes = {'123': WatchTime(time: 7)};
    final saving = state.flushWatchTimesToDisk();
    await paths.supportStarted!.future;
    state.client.token = 'new-token';
    state.watchTimes = {'999': WatchTime(time: 42)};
    final watch = File('${temp.path}/watch-times.json');
    await watch.writeAsString('{"999":{"time":42}}');
    paths.supportResult!.complete(temp.path);
    await saving;
    expect(await watch.readAsString(), contains('999'));
    expect(await watch.readAsString(), isNot(contains('123')));
  });

  test('delayed watch load cannot merge data into a new account', () async {
    final watch = File('${temp.path}/watch-times.json');
    await watch.writeAsString('{"123":{"time":7,"dirty":true}}');
    paths.supportStarted = Completer<void>();
    paths.supportResult = Completer<String?>();
    final loading = state.refreshWatchTimes();
    await paths.supportStarted!.future;
    state.client.token = 'new-token';
    state.watchTimes = {'999': WatchTime(time: 42)};
    paths.supportResult!.complete(temp.path);
    await loading;
    expect(state.watchTimes.keys, ['999']);
    expect(state.hasPendingWatchTimes, isFalse);
  });

  test('watch sync acknowledgement preserves progress updated in flight',
      () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    state.serverInfo = ServerInfo(userControl: true);
    state.currentUser = CurrentUser(username: 'old-user');
    reply = (request) async {
      if (request.method == 'POST' && request.url.path == '/watch/time') {
        started.complete();
        return response.future;
      }
      return http.Response('{}', 200);
    };
    state.noteWatchTime('123', WatchTime(time: 7), pending: true);
    final syncing = state.flushPendingWatchTimes();
    await started.future;
    state.noteWatchTime('123', WatchTime(time: 42), pending: true);
    response.complete(http.Response('{}', 200));
    await syncing;
    expect(state.watchTimeOf('123')?.time, 42);
    expect(state.isWatchTimePending('123'), isTrue);
  });

  test('watch sync stops submitting its old batch after an account change',
      () async {
    final started = Completer<void>();
    final response = Completer<http.Response>();
    final posts = <http.Request>[];
    state.serverInfo = ServerInfo(userControl: true);
    state.currentUser = CurrentUser(username: 'old-user');
    reply = (request) async {
      if (request.method == 'POST' && request.url.path == '/watch/time') {
        posts.add(request);
        if (posts.length == 1) {
          started.complete();
          return response.future;
        }
      }
      return http.Response('{}', 200);
    };
    state.noteWatchTime('123', WatchTime(time: 7), pending: true);
    state.noteWatchTime('456', WatchTime(time: 8), pending: true);
    final syncing = state.flushPendingWatchTimes();
    await started.future;
    state.client.token = 'new-token';
    state.noteWatchTime('456', WatchTime(time: 42), pending: true);
    response.complete(http.Response('{}', 200));
    await syncing;
    expect(posts, hasLength(1));
    expect(state.isWatchTimePending('456'), isTrue);
  });
}
