import 'dart:io';

import 'package:agp_mobile/src/api/client.dart';
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
  @override
  Future<String?> getApplicationDocumentsPath() async => path;
  @override
  Future<String?> getApplicationSupportPath() async => path;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late Directory temp;
  late AppState state;

  setUp(() async {
    temp = await Directory.systemTemp.createTemp('agp-account-test-');
    PathProviderPlatform.instance = Paths(temp.path);
    SharedPreferences.setMockInitialValues({});
    final api = AgpClient(
        baseUrl: 'https://old.invalid',
        token: 'old-token',
        httpClient: MockClient((request) async => http.Response('{}', 200)));
    state = await AppState.boot(client: api);
    await state.prefs.setServer('https://old.invalid');
    await state.prefs.setToken('old-token');
  });

  tearDown(() async {
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
}
