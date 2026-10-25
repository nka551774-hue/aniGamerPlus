import 'package:agp_mobile/src/util/format.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('cover initials preserve emoji and combining characters', () {
    expect(initials('😀 Adventure'), '😀A');
    expect(initials('👨‍👩‍👧‍👦 Family'), '👨‍👩‍👧‍👦F');
    expect(initials('e\u0301clair Story'), 'E\u0301S');
    expect(initials('中😀文'), '中😀');
    expect(initials('進擊的巨人'), '進擊');
    expect(initials(null), '?');
  });

  test('numeric episode labels do not lose precision or overflow', () {
    expect(episodeLabel('9007199254740993'), '第 9007199254740993 集');
    final enormous = List.filled(400, '9').join();
    expect(episodeLabel(enormous), '第 $enormous 集');
    expect(episodeLabel('0012.000'), '第 12 集');
    expect(episodeLabel('000'), '第 0 集');
    expect(episodeLabel('12.5'), '第 12.5 集');
    expect(episodeLabel('OVA'), 'OVA');
  });

  test('fallback cover colors match existing dashboard fixtures', () {
    // These hue pairs were obtained from Dashboard/static/js/agp-shell.js.
    for (final fixture in <(String, double, double)>[
      ('進擊的巨人', 151, 220),
      ('😀 Adventure', 16, 70),
      ('aniGamerPlus', 309, 16),
      ('', 341, 40),
    ]) {
      expect(artFor(fixture.$1).colors, [
        HSLColor.fromAHSL(1, fixture.$2, 0.58, 0.26).toColor(),
        HSLColor.fromAHSL(1, fixture.$3, 0.62, 0.15).toColor(),
      ]);
    }
  });
}
