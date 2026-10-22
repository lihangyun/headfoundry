import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from bundle_stationarity import audit
from short_track_camera import project


class BundleStationarityTest(unittest.TestCase):
    def test_stationary_truth_and_wrong_pose_without_refit(self):
        k = np.array([[1200., 0, 359.5], [0, 1200., 639.5], [0, 0, 1.]])
        poses = np.repeat(np.eye(4)[None], 3, axis=0)
        poses[1, :3, 3] = [1., 0, 0]
        poses[2, :3, 3] = [0, 1., .2]
        xyz = np.random.default_rng(305).uniform([-1, -1, 3], [1, 1, 6], (8, 3))
        rows = np.array([[camera, point, 0, 0] for camera in range(3) for point in range(8)], dtype=float)
        rows[:, 2:] = project(k, poses, xyz, rows)[0]
        before = poses.copy()
        truth = audit(k, poses, xyz, rows, 0, 1)
        self.assertLess(truth['column_normalized_gradient_inf'], 1e-7)
        wrong = poses.copy()
        wrong[2, 0, 3] += .05
        negative = audit(k, wrong, xyz, rows, 0, 1)
        self.assertGreater(negative['column_normalized_gradient_inf'], 1.)
        self.assertTrue(np.array_equal(poses, before))
        self.assertTrue(truth['no_step_applied'] and negative['no_step_applied'])
