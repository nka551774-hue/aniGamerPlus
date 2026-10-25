import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:agp_mobile/src/api/client.dart';
import 'package:agp_mobile/src/state/thumbnails.dart';
import 'package:agp_mobile/src/widgets/common.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'support/temp_dir.dart';

class _Store extends ThumbnailStore {
  _Store(super.client);

  File? hit;
  Completer<File?> pending = Completer<File?>();

  @override
  File? cached(String sn, {bool poster = false, String? fallbackUrl}) => hit;

  @override
  String? urlFor(String sn, {bool poster = false}) => null;

  @override
  Future<File?> resolve(String sn,
          {bool poster = false, String? fallbackUrl}) =>
      pending.future;
}

void main() {
  for (final notify in [true, false]) {
    testWidgets('server switch clears visible old cover (notify=$notify)',
        (tester) async {
      final directory = Directory.systemTemp.createTempSync('agp-cover-scope-');
      final file = File('${directory.path}/pixel.png')
        ..writeAsBytesSync(base64Decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg=='));
      final client = AgpClient(baseUrl: 'http://old.invalid');
      final store = _Store(client)..hit = file;
      addTearDown(() async {
        store.dispose();
        client.close();
        await deleteTempDir(directory);
      });

      Widget cover() => MaterialApp(
            home: SizedBox(
              width: 320,
              child: CoverImage(name: 'Same title', sn: '12', cache: store),
            ),
          );
      await tester.pumpWidget(cover());
      expect(find.byType(Image), findsOneWidget);

      // The AppState keeps the same store and the new host may use the same SN.
      client.baseUrl = 'http://new.invalid';
      store.hit = null;
      if (notify) {
        store.notifyListeners();
        await tester.pump();
      } else {
        await tester.pumpWidget(cover());
      }
      expect(find.byType(Image), findsNothing);
      store.pending.complete(null);
      await tester.pump();
      expect(find.byType(Image), findsNothing);
      await tester.pumpWidget(const SizedBox.shrink());
    });
  }
}
