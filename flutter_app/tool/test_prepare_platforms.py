"""Regression tests for the embedded platform-manifest patcher."""

from __future__ import annotations

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID = "http://schemas.android.com/apk/res/android"
TOOLS = "http://schemas.android.com/tools"
SCRIPT = Path(__file__).with_name("prepare_platforms.sh")
REMOVE_PERMISSIONS = (
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_AUDIO",
)


def _load_patch_manifest():
    source = SCRIPT.read_text(encoding="utf-8")
    heredoc = 'APP_LABEL="$APP_LABEL" "$PYTHON" - <<\'PYTHON\'\n'
    _, _, body = source.partition(heredoc)
    if not body:
        raise AssertionError("prepare_platforms.sh Python heredoc not found")
    body, _, _ = body.partition("\npatch_manifest(")
    namespace: dict[str, object] = {}
    exec(compile(body, str(SCRIPT), "exec"), namespace)  # noqa: S102
    return namespace["patch_manifest"]


class PreparePlatformsManifestTest(unittest.TestCase):
    def test_existing_and_missing_storage_permissions_are_removed(self) -> None:
        manifest = ET.Element("manifest", {
            "xmlns:android": ANDROID,
            "xmlns:tools": TOOLS,
        })
        ET.SubElement(manifest, "uses-permission", {
            f"{{{ANDROID}}}name": "android.permission.INTERNET",
        })
        # These two are already in a newer scaffold; the other two are absent.
        for permission in REMOVE_PERMISSIONS[:2]:
            ET.SubElement(manifest, "uses-permission", {
                f"{{{ANDROID}}}name": permission,
            })
        application = ET.SubElement(manifest, "application")
        activity = ET.SubElement(application, "activity")
        intent = ET.SubElement(activity, "intent-filter")
        ET.SubElement(intent, "action", {
            f"{{{ANDROID}}}name": "android.intent.action.MAIN",
        })

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "AndroidManifest.xml"
            ET.ElementTree(manifest).write(path, encoding="utf-8", xml_declaration=True)
            _load_patch_manifest()(str(path))
            result = ET.parse(path).getroot()

        permissions = result.findall("uses-permission")
        by_name = {}
        for node in permissions:
            name = node.get(f"{{{ANDROID}}}name")
            if name in REMOVE_PERMISSIONS:
                by_name.setdefault(name, []).append(node)

        self.assertEqual(set(by_name), set(REMOVE_PERMISSIONS))
        for nodes in by_name.values():
            self.assertEqual(len(nodes), 1)
            self.assertEqual(nodes[0].get(f"{{{TOOLS}}}node"), "remove")

        internet = next(
            node for node in permissions
            if node.get(f"{{{ANDROID}}}name") == "android.permission.INTERNET"
        )
        self.assertIsNone(internet.get(f"{{{TOOLS}}}node"))


if __name__ == "__main__":
    unittest.main()
