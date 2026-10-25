/// A single HTTP byte range with a known complete representation length.
class ByteContentRange {
  const ByteContentRange(this.start, this.end, this.total);

  final int start;
  final int end;
  final int total;

  int get length => end - start + 1;

  static final _pattern = RegExp(r'^bytes ([0-9]+)-([0-9]+)/([0-9]+)$');

  static ByteContentRange? parse(String? value) {
    final match = _pattern.firstMatch(value?.trim() ?? '');
    if (match == null) return null;
    final start = int.tryParse(match.group(1)!);
    final end = int.tryParse(match.group(2)!);
    final total = int.tryParse(match.group(3)!);
    if (start == null ||
        end == null ||
        total == null ||
        start < 0 ||
        end < start ||
        end >= total) {
      return null;
    }
    return ByteContentRange(start, end, total);
  }

  static int? unsatisfiedTotal(String? value) {
    final match =
        RegExp(r'^bytes \*/([0-9]+)$').firstMatch(value?.trim() ?? '');
    return match == null ? null : int.tryParse(match.group(1)!);
  }
}
