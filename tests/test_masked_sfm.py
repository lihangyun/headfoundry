import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from headfoundry.manifest import sha256_file
from tools.run_masked_sfm import prepare

try:
    from PIL import Image
except ImportError:
    Image = None


class MaskedSfmTests(unittest.TestCase):
    def test_missing_consent_rejects_before_runtime_or_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "run.json"
            manifest.write_text(json.dumps({"schema_version": 1, "purpose": "local_head_reconstruction_validation", "inputs": [{}]}))
            with patch("tools.run_masked_sfm.importlib.metadata.distribution") as loader:
                with self.assertRaisesRegex(ValueError, "consent"):
                    prepare(manifest, root, root / "out", root / "missing-lock.json")
                loader.assert_not_called()
                self.assertFalse((root / "out").exists())

    @unittest.skipIf(Image is None, "optional Pillow required for image boundary check")
    def test_masks_runtime_and_non_overwrite_preflight(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            masks = root / "masks"
            masks.mkdir()
            assets = []
            for index, yaw in enumerate((-90, -30, 0, 30, 90)):
                name = f"{index}.png"
                Image.new("RGB", (1024, 1024), (index, 70, 90)).save(root / name)
                mask = Image.new("L", (1024, 1024), 0)
                mask.paste(255, (200, 200, 800, 800))
                mask.save(masks / (name + ".png"))
                assets.append({"id": str(index), "path": name, "sha256": sha256_file(root / name),
                               "width_px": 1024, "height_px": 1024, "clarity_score": .9, "yaw_degrees": yaw,
                               "source": "own synthetic test", "license_id": "CC0-1.0",
                               "allowed_uses": ["local_head_reconstruction_validation"], "retention_until": "test end",
                               "deletion_process": "temporary directory cleanup",
                               "consent": {"subject_id": "synthetic", "record_id": "test", "granted_at": "2026-09-12", "biometric_processing": True}})
            manifest = root / "run.json"
            manifest.write_text(json.dumps({"schema_version": 1, "purpose": "local_head_reconstruction_validation", "inputs": assets}))
            (root / "core.bin").write_bytes(b"synthetic runtime")
            lock = root / "runtime.json"
            lock.write_text(json.dumps({"distribution": "pycolmap", "version": "4.2.0", "files": {"core.bin": sha256_file(root / "core.bin")}}))
            runtime = SimpleNamespace(version="4.2.0", locate_file=lambda name: root / name)
            with patch("tools.run_masked_sfm.importlib.metadata.distribution", return_value=runtime):
                _, output, _, records = prepare(manifest, masks, root / "out", lock)
                self.assertEqual(len(records), 5)
                self.assertFalse(output.exists())
                # Documented spelling and the verified upstream fallback both resolve.
                (masks / "0.png.png").rename(masks / "0.png")
                self.assertEqual(prepare(manifest, masks, output, lock)[3][0]["mask"].name, "0.png")
                (masks / "0.png").unlink()
                with self.assertRaisesRegex(ValueError, "Missing mask"):
                    prepare(manifest, masks, output, lock)
                Image.new("L", (32, 32), 255).save(masks / "0.png")
                with self.assertRaisesRegex(ValueError, "size mismatch"):
                    prepare(manifest, masks, output, lock)
                Image.new("L", (1024, 1024), 255).save(masks / "0.png")
                with self.assertRaisesRegex(ValueError, "included and excluded"):
                    prepare(manifest, masks, output, lock)
                (root / "core.bin").write_bytes(b"drift")
                with self.assertRaisesRegex(ValueError, "hash drift"):
                    prepare(manifest, masks, output, lock)
                output.mkdir()
                with self.assertRaisesRegex(ValueError, "already exists"):
                    prepare(manifest, masks, output, lock)
                self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
