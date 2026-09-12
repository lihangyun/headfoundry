import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

spec = importlib.util.spec_from_file_location("mapanything_runner", Path(__file__).resolve().parents[1] / "tools/run_mapanything.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class MapAnythingRunnerTests(unittest.TestCase):
    def test_assumed_focal_resize_preserves_pixel_projection(self):
        matrices = runner.assumed_intrinsics(1800, [[1254, 1254], [1024, 1024]])
        self.assertEqual(matrices.shape, (2, 3, 3))
        ray = np.array([.1, -.2, 1.])
        for matrix, size in zip(matrices, [1254, 1024]):
            expected = np.array([180 + size / 2, -360 + size / 2]) * 518 / size
            np.testing.assert_allclose((matrix @ ray)[:2], expected, atol=1e-5)
        for value in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                runner.assumed_intrinsics(value, [[1254, 1254]])
        for sizes in ([], [[0, 1254]], [[1254]], [[float("nan"), 1254]]):
            with self.assertRaises(ValueError):
                runner.assumed_intrinsics(1800, sizes)

    def test_only_local_dino_architecture_request_is_allowed(self):
        original = Mock(return_value="local architecture")
        directory = Path("reviewed-dino")
        load = runner.local_dino_loader(original, directory)
        self.assertEqual(load("facebookresearch/dinov2", "dinov2_vitg14", pretrained=False, force_reload=True), "local architecture")
        original.assert_called_once_with(str(directory), "dinov2_vitg14", source="local", pretrained=False)
        for repo, model, kwargs in (("facebookresearch/dinov2", "dinov2_vitg14", {}),
                                    ("facebookresearch/dinov2", "dinov2_vitg14", {"pretrained": True}),
                                    ("other", "dinov2_vitg14", {"pretrained": False}),
                                    ("facebookresearch/dinov2", "other", {"pretrained": False})):
            with self.assertRaisesRegex(ValueError, "Unreviewed"):
                load(repo, model, **kwargs)
        self.assertEqual(original.call_count, 1)

    def test_rights_and_wrong_checkpoint_fail_before_model_loading(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"purpose": "local_head_reconstruction_validation"}))
            with self.assertRaisesRegex(ValueError, "input rights"):
                runner.verify(manifest, root, root, root)
            lock = root / "lock.json"
            with patch.object(runner, "LOCK_PATH", lock), patch.object(runner, "validate_input_assets", return_value=[]), patch.object(runner, "validate_multiview", return_value={"status": "TECHNICAL_CHECK_PASSED"}):
                manifest.write_text(json.dumps({"purpose": "local_head_reconstruction_validation", "inputs": []}))
                lock.write_text(json.dumps({"asset_id": "facebook/map-anything", "license_id": "Apache-2.0"}))
                with self.assertRaisesRegex(ValueError, "reviewed Apache"):
                    runner.verify(manifest, root, root, root)
                lock.write_text(json.dumps({"asset_id": "facebook/map-anything-apache", "license_id": "Apache-2.0", "model_sha256": {"model.safetensors": "wrong"}}))
                (root / "model.safetensors").write_bytes(b"unreviewed bytes")
                with self.assertRaisesRegex(ValueError, "Model asset hash"):
                    runner.verify(manifest, root, root, root)


if __name__ == "__main__":
    unittest.main()
