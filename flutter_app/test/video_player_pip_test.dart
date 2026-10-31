import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:video_player_pip/index.dart';
import 'package:video_player_pip/video_player_pip_method_channel.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('video_player_pip');
  final calls = <String>[];
  late bool previousSupported;

  setUp(() {
    previousSupported = VideoPlayerPip.supported;
    VideoPlayerPipPlatform.instance = MethodChannelVideoPlayerPip();
    channel.setMockMethodCallHandler((call) async {
      calls.add(call.method);
      return true;
    });
  });

  tearDown(() {
    calls.clear();
    VideoPlayerPip.supported = previousSupported;
    channel.setMockMethodCallHandler(null);
  });

  test('unsupported platforms short-circuit every PiP API', () async {
    VideoPlayerPip.supported = false;
    final controller = VideoPlayerController.networkUrl(
      Uri.parse('https://example.test/video.mp4'),
    );

    expect(await VideoPlayerPip.isPipSupported(), isFalse);
    expect(await VideoPlayerPip.enterPipMode(controller), isFalse);
    expect(await VideoPlayerPip.exitPipMode(), isFalse);
    expect(await VideoPlayerPip.isInPipMode(), isFalse);
    expect(
      await VideoPlayerPip.updatePip(autoEnter: false, playing: false),
      isFalse,
    );
    expect(calls, isEmpty);
  });

  test('supported calls retain the current method-channel contract', () async {
    VideoPlayerPip.supported = true;

    expect(await VideoPlayerPip.isPipSupported(), isTrue);
    expect(await VideoPlayerPip.exitPipMode(), isTrue);
    expect(await VideoPlayerPip.isInPipMode(), isTrue);
    expect(
      await VideoPlayerPip.updatePip(autoEnter: true, playing: true),
      isTrue,
    );
    expect(
      calls,
      containsAll(<String>[
        'isPipSupported',
        'exitPipMode',
        'isInPipMode',
        'updatePip',
      ]),
    );
  });
}
