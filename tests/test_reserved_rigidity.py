import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_reserved_localization_0222 import epipolar_validation


class ReservedRigidityTests(unittest.TestCase):
    def test_known_geometry_and_validation_do_not_change_essential_fit(self):
        points = np.random.default_rng(222).uniform(-1, 1, (160, 3)) + [0, 0, 5]
        camera = np.array([[950., 0, 360], [0, 950., 640], [0, 0, 1]])
        rotation = cv2.Rodrigues(np.array([.04, -.12, .01]))[0]
        def project(x):
            h = x @ camera.T
            return h[:, :2] / h[:, 2:]
        first, second = project(points), project(points @ rotation.T + [.2, .01, .02])
        ids = np.arange(len(points))
        result = epipolar_validation(first, second, ids, camera)
        self.assertEqual(result["status"], "TECHNICAL_CHECK_PASSED")
        changed = second.copy()
        changed[ids % 2 != 0] += [0, 20]
        rejected = epipolar_validation(first, changed, ids, camera)
        self.assertEqual(rejected["status"], "REJECT")
        np.testing.assert_array_equal(rejected["essential_matrix"], result["essential_matrix"])

    def test_missing_partition_stops(self):
        result = epipolar_validation(np.ones((10, 2)), np.ones((10, 2)), np.arange(10), np.eye(3))
        self.assertEqual(result["status"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
