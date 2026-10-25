import 'dart:async';

import 'package:agp_mobile/src/api/client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('switching servers removes the old credential before the next request',
      () async {
    final requests = <http.Request>[];
    final client = AgpClient(
        baseUrl: 'https://first.invalid',
        token: 'first-token',
        httpClient: MockClient((request) async {
          requests.add(request);
          return http.Response('{}', 200);
        }));
    addTearDown(client.close);
    client.baseUrl = 'https://second.invalid';
    await client.seriesJson('123');
    expect(client.token, isNull);
    expect(requests.single.url.host, 'second.invalid');
    expect(requests.single.headers['cookie'], isNull);
  });

  test('a pending response cannot populate a different account cache',
      () async {
    final pending = Completer<http.Response>();
    var requests = 0;
    final client = AgpClient(
        baseUrl: 'https://first.invalid',
        token: 'old',
        httpClient: MockClient((request) {
          if (++requests == 1) return pending.future;
          return Future.value(http.Response('{"owner":"new"}', 200));
        }));
    addTearDown(client.close);
    final old = client.seriesJson('123');
    final rejected = expectLater(old, throwsA(isA<ApiException>()));
    await pumpEventQueue();
    client.token = 'new';
    pending.complete(http.Response('{"owner":"old"}', 200));
    await rejected;
    expect((await client.seriesJson('123'))['owner'], 'new');
    expect(requests, 2);
  });

  test('clearMemo also invalidates a request still in flight', () async {
    final pending = Completer<http.Response>();
    var requests = 0;
    final client = AgpClient(
        baseUrl: 'https://first.invalid',
        httpClient: MockClient((request) {
          if (++requests == 1) return pending.future;
          return Future.value(http.Response('{"fresh":true}', 200));
        }));
    addTearDown(client.close);
    final old = client.seriesJson('123');
    await pumpEventQueue();
    client.clearMemo();
    pending.complete(http.Response('{"fresh":false}', 200));
    await old;
    expect((await client.seriesJson('123'))['fresh'], isTrue);
    expect(requests, 2);
  });

  test('the newest login wins even when the first finishes last', () async {
    final replies = <Completer<http.Response>>[];
    final client = AgpClient(
        baseUrl: 'https://first.invalid',
        httpClient: MockClient((request) {
          final reply = Completer<http.Response>();
          replies.add(reply);
          return reply.future;
        }));
    addTearDown(client.close);
    final first = client.login('first', 'password');
    final rejected = expectLater(first, throwsA(isA<ApiException>()));
    await pumpEventQueue();
    final second = client.login('second', 'password');
    await pumpEventQueue();
    replies[1].complete(
        http.Response('', 302, headers: {'set-cookie': 'token=second'}));
    expect(await second, 'second');
    replies[0].complete(
        http.Response('', 302, headers: {'set-cookie': 'token=first'}));
    await rejected;
    expect(client.token, 'second');
  });

  test('an old logout response cannot clear a newer login', () async {
    final pending = Completer<http.Response>();
    final client = AgpClient(
        baseUrl: 'https://first.invalid',
        token: 'old',
        httpClient: MockClient((request) => pending.future));
    addTearDown(client.close);
    final logout = client.logout();
    await pumpEventQueue();
    client.token = 'new';
    pending.complete(http.Response('', 200));
    await logout;
    expect(client.token, 'new');
  });
}
