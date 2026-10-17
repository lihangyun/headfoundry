import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experiment_0212 import shape_audit


class NativeExteriorAuditTests(unittest.TestCase):
    def test_displacement_does_not_hide_area_or_orientation_failure(self):
        mean = np.array([[0., 0., 0.], [.01, 0., 0.], [0., .01, 0.]])
        faces = np.array([[0, 1, 2]])
        self.assertTrue(shape_audit(mean, mean, faces, 1.)["passed"])
        compressed = mean.copy()
        compressed[2, 1] = .002
        result = shape_audit(mean, compressed, faces, 1.)
        self.assertAlmostEqual(result["minimum_area_ratio"], .2)
        self.assertLess(result["maximum_shape_displacement_world"], .06)
        self.assertFalse(result["passed"])
        flipped = mean.copy()
        flipped[2, 1] *= -1
        self.assertEqual(shape_audit(mean, flipped, faces, 1.)["normal_reversals"], 1)


if __name__ == "__main__":
    unittest.main()
