import 'package:agp_mobile/src/state/http_range.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('a range describes offsets within one complete representation', () {
    final range = ByteContentRange.parse('bytes 10-19/100')!;
    expect(range.start, 10);
    expect(range.end, 19);
    expect(range.total, 100);
    expect(range.length, 10);
    expect(ByteContentRange.unsatisfiedTotal('bytes */100'), 100);
  });

  test('invalid, reversed and overflowing ranges are rejected', () {
    for (final value in [
      null,
      '',
      'bytes 20-10/100',
      'bytes 0-100/100',
      'bytes 0-0/0',
      'bytes 0-1/*',
      'bytes 99999999999999999999999-2/100',
      'items 0-1/100',
      'bytes -1-1/100',
      'bytes 0-1/100, 2-3/100'
    ]) {
      expect(ByteContentRange.parse(value), isNull, reason: '$value');
    }
  });
}
