import unittest

import cv2
import numpy as np

from tools.localize_reserved_frames_0222 import estimate_reserved_pose


class ReservedFrameLocalizationTests(unittest.TestCase):
    def test_validation_errors_cannot_change_training_pose(self):
        points = np.random.default_rng(222).uniform(-.6, .6, (160, 3))
        intrinsic = np.array([[950., 0, 360], [0, 950, 640], [0, 0, 1]])
        rotation, _ = cv2.Rodrigues(np.array([.08, -.12, .04]))
        camera = points @ rotation.T + [.1, -.05, 4.]
        h = camera @ intrinsic.T
        pixels = h[:, :2] / h[:, 2:]
        ids = np.arange(len(points))
        original = intrinsic.copy()
        pose, _, first = estimate_reserved_pose(points, pixels, ids, intrinsic, points)
        changed = pixels.copy()
        changed[ids % 2 == 1] += [10, 0]
        changed_pose, _, second = estimate_reserved_pose(points, changed, ids, intrinsic, points)
        self.assertEqual(first["status"], "TECHNICAL_CHECK_PASSED")
        self.assertEqual(second["status"], "REJECT")
        np.testing.assert_allclose(pose, changed_pose, atol=1e-10)
        self.assertGreater(second["validation_p95_px"], 9.99)
        np.testing.assert_array_equal(intrinsic, original)

    def test_missing_support_stops_without_pose(self):
        points = np.ones((10, 3))
        pose, _, report = estimate_reserved_pose(points, np.ones((10, 2)), np.arange(10), np.eye(3), points)
        self.assertIsNone(pose)
        self.assertEqual(report["reason"], "insufficient_frozen_track_support")


if __name__ == "__main__":
    unittest.main()
