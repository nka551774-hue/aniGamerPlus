import 'dart:io';

import 'package:agp_mobile/src/api/client.dart';
import 'package:agp_mobile/src/api/models.dart';
import 'package:agp_mobile/src/state/downloads.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';

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
  HttpOverrides.global = null;
  late Directory temp;
  late HttpServer server;
  late AgpClient client;
  late DownloadStore store;
  late Future<void> Function(HttpRequest) reply;
  final requests = <HttpRequest>[];

  setUp(() async {
    requests.clear();
    temp = await Directory.systemTemp.createTemp('agp-range-test-');
    PathProviderPlatform.instance = Paths(temp.path);
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((request) async {
      if (request.uri.path != '/get_video.mp4') {
        request.response.statusCode = 404;
        await request.response.close();
        return;
      }
      requests.add(request);
      await reply(request);
    });
    client = AgpClient(baseUrl: 'http://127.0.0.1:${server.port}');
    store = DownloadStore(client);
    await store.init();
    store.concurrency = 0;
  });

  tearDown(() async {
    await store.remove('123', deleteFiles: false);
    store.dispose();
    client.close();
    await server.close(force: true);
    await deleteTempDir(temp);
  });

  Future<DownloadEntry> seed() async {
    final entry = await store.enqueue(VideoItem(sn: '123', episode: '1'),
        withDanmaku: false);
    await store.partFile(entry).writeAsBytes([1, 2, 3]);
    entry.sourceUrl = client.videoUrl('123').toString();
    entry.resumeValidator = '"old-video"';
    return entry;
  }

  Future<void> run(DownloadEntry entry) async {
    store.concurrency = 1;
    for (var count = 0; count < 200; count++) {
      if (entry.status == DownloadStatus.done ||
          entry.status == DownloadStatus.failed) {
        return;
      }
      await Future<void>.delayed(const Duration(milliseconds: 10));
    }
    fail('download did not settle');
  }

  test('mismatched 416 cannot publish a truncated partial file', () async {
    final entry = await seed();
    reply = (request) async {
      request.response.statusCode = 416;
      request.response.headers.set('Content-Range', 'bytes */6');
      await request.response.close();
    };
    await run(entry);
    expect(entry.status, DownloadStatus.failed);
    expect(await store.videoFile(entry).exists(), isFalse);
    expect(await store.partFile(entry).readAsBytes(), [1, 2, 3]);
  });

  test('wrong 206 offset cannot append bytes to an existing partial file',
      () async {
    final entry = await seed();
    reply = (request) async {
      request.response.statusCode = 206;
      request.response.headers.set('Content-Range', 'bytes 0-2/6');
      request.response.add([4, 5, 6]);
      await request.response.close();
    };
    await run(entry);
    expect(entry.status, DownloadStatus.failed);
    expect(await store.partFile(entry).readAsBytes(), [1, 2, 3]);
  });

  test('If-Range replacement restarts instead of mixing old and new bytes',
      () async {
    final entry = await seed();
    reply = (request) async {
      request.response.headers.set(HttpHeaders.etagHeader, '"new-video"');
      request.response.add([4, 5, 6, 7]);
      await request.response.close();
    };
    await run(entry);
    expect(requests.single.headers.value(HttpHeaders.ifRangeHeader),
        '"old-video"');
    expect(entry.status, DownloadStatus.done);
    expect(await store.videoFile(entry).readAsBytes(), [4, 5, 6, 7]);
  });

  test('a legacy partial file without a validator is restarted safely',
      () async {
    final entry = await seed();
    entry.resumeValidator = '';
    reply = (request) async {
      request.response.add([4, 5, 6]);
      await request.response.close();
    };
    await run(entry);
    expect(requests.single.headers.value(HttpHeaders.rangeHeader), isNull);
    expect(entry.status, DownloadStatus.done);
    expect(await store.videoFile(entry).readAsBytes(), [4, 5, 6]);
  });
}
