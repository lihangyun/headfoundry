import unittest

import numpy as np

from headfoundry.camera import estimate_projection_dlt, project, synthetic_camera_check


class CameraTests(unittest.TestCase):
    def test_synthetic_camera_is_subpixel(self) -> None:
        result = synthetic_camera_check()
        self.assertTrue(result.passed)
        self.assertLess(result.p95_reprojection_px, 0.05)

    def test_rejects_too_few_correspondences(self) -> None:
        with self.assertRaises(ValueError):
            estimate_projection_dlt(np.zeros((5, 3)), np.zeros((5, 2)))

    def test_project_preserves_principal_point(self) -> None:
        intrinsic = np.array(
            [[1000.0, 0.0, 320.0], [0.0, 1000.0, 240.0], [0.0, 0.0, 1.0]]
        )
        camera = intrinsic @ np.column_stack([np.eye(3), np.array([[0.0], [0.0], [3.0]])])
        result = project(camera, np.array([[0.0, 0.0, 0.0]]))
        np.testing.assert_allclose(result, [[320.0, 240.0]])


if __name__ == "__main__":
    unittest.main()
