package uz.flutterwithakmaljon.video_player_pip

import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import kotlin.test.Test
import org.mockito.Mockito

internal class VideoPlayerPipPluginTest {
  @Test
  fun updatePip_withoutActivity_returnsFalse() {
    val plugin = VideoPlayerPipPlugin()
    val call = MethodCall(
      "updatePip",
      mapOf("playerId" to 1, "autoEnter" to true, "playing" to true),
    )
    val result = Mockito.mock(MethodChannel.Result::class.java)

    plugin.onMethodCall(call, result)

    Mockito.verify(result).success(false)
  }

  @Test
  fun unknownMethod_isNotImplemented() {
    val plugin = VideoPlayerPipPlugin()
    val result = Mockito.mock(MethodChannel.Result::class.java)

    plugin.onMethodCall(MethodCall("unknown", null), result)

    Mockito.verify(result).notImplemented()
  }
}
