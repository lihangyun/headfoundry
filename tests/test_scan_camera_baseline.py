import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from tools.calibrate_scan_camera_0217 import initial_pose, lift_source, project


class ScanCameraBaselineTests(unittest.TestCase):
    def test_orthographic_lift_selects_front_surface_after_display_roll(self):
        front = np.array([[0, 0, 1], [.5, 0, 1], [0, .5, 1]])
        vertices = np.r_[front, front - [0, 0, 1]]
        matrix = np.eye(4)
        matrix[:3, 3] = [0, 0, 4]
        record = {"display_center_source_units": [0, 0, 0], "display_radius_source_units": 1,
                  "camera_world_matrix": matrix.tolist()}
        points, ids, weights, error = lift_source(vertices, np.array([[0, 1, 2], [3, 4, 5]]),
                                                 np.array([[246., 266.]]), record)
        np.testing.assert_allclose(points, [[.046875, .046875, 1]], atol=1e-12)
        np.testing.assert_array_equal(ids, [0])
        self.assertAlmostEqual(float(weights.sum()), 1.)
        self.assertLess(error, 1e-10)

    def test_metric_pose_recovery_from_known_nonplanar_points(self):
        points = np.random.default_rng(217).uniform(-.5, .5, (12, 3))
        pose = np.array([.1, .2, -.1, .05, -.08, 5.])
        rotation = Rotation.from_rotvec(pose[:3]).as_matrix()
        camera = points @ rotation.T + pose[3:]
        # Analytic reference projection is independent of the tested helper.
        expected = camera[:, :2] / camera[:, 2:3] * 1000 + [360, 640]
        np.testing.assert_allclose(project(points, pose, 1000), expected, atol=1e-10)
        recovered = initial_pose(points, expected)
        np.testing.assert_allclose(recovered, pose, atol=1e-7)


if __name__ == "__main__":
    unittest.main()
