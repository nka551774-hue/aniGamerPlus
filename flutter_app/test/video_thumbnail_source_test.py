"""Offline ownership regressions for the bundled thumbnail native sources."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
OBJC = ROOT / "flutter_app/packages/video_thumbnail/ios/Classes/VideoThumbnailPlugin.m"
JAVA = ROOT / (
    "flutter_app/packages/video_thumbnail/android/src/main/java/"
    "xyz/justsoft/video_thumbnail/VideoThumbnailPlugin.java"
)


class VideoThumbnailNativeSourceTest(unittest.TestCase):
    def test_webp_ownership_and_mutable_copy_are_explicit(self) -> None:
        source = OBJC.read_text(encoding="utf-8")
        self.assertIn("CFDataCreateMutableCopy", source)
        self.assertIn("CFDataGetMutableBytePtr", source)
        self.assertIn("CGImageRelease(cgImage);", source)
        self.assertIn("WebPFree(output);", source)
        self.assertNotIn("CGDataProviderRelease(dataProvider)", source)
        self.assertNotIn("CGColorSpaceRelease(colorSpace)", source)
        self.assertRegex(source, r"colorSpace == NULL \|\| CGColorSpaceGetModel")

    def test_android_file_descriptor_is_closed_after_set_data_source(self) -> None:
        source = JAVA.read_text(encoding="utf-8")
        match = re.search(
            r"private static void setDataSource\(.*?\n    \}",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        method = match.group(0)
        self.assertIn("try (FileInputStream inputStream", method)
        self.assertIn("retriever.setDataSource(inputStream.getFD())", method)


if __name__ == "__main__":
    unittest.main()
