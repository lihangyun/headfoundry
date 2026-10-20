"""Pre-inference convention controls;no checkpoint or human data required."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


class RecurrentMaterialControls(unittest.TestCase):
    def test_asymmetric_xy_half_pixel_and_warp_inverse(self):
        path = Path(__file__).resolve().parents[1] / "tools/check_recurrent_material_0258.py"
        spec = importlib.util.spec_from_file_location("recurrent0258", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.controls()
        import numpy as np
        points = np.array([[13.25, 167.75], [699.5, 637.25]])
        self.assertTrue(np.allclose(module.from_model(module.to_model(points, (720, 640)),
                                                     (720, 640)), points, atol=1e-12))
        optimized = subprocess.run([sys.executable, "-O", str(path), "controls"],
                                   capture_output=True, text=True, timeout=10)
        self.assertNotEqual(optimized.returncode, 0)
        self.assertIn("run without -O", optimized.stderr)


if __name__ == "__main__":
    unittest.main()
