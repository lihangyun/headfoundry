import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from mapanything_geometry_0249 import resize_transform, sample_points, convention_report


class MapGeometryTests(unittest.TestCase):
    def test_actual_axis_rounding_and_pixel_centers(self):
        a, resized, crop = resize_transform((720, 1280), (294, 518))
        self.assertEqual(resized, (294, 522))
        self.assertEqual(crop, (0, 2))
        self.assertAlmostEqual(a[1, 1], 522/1280)
        np.testing.assert_allclose(a@[-.5, -.5, 1], [-.5, -2.5, 1])
        np.testing.assert_allclose(np.linalg.inv(a)@a, np.eye(3))

    def test_bilinear_retains_invalid_population(self):
        yy, xx = np.indices((4, 5))
        points = np.stack([xx, yy, xx+2*yy], axis=-1)
        result = sample_points(points, [[1.2, 2.4], [-1, 1], [4, 2]])
        np.testing.assert_allclose(result[0], [1.2, 2.4, 6])
        self.assertTrue(np.isnan(result[1:]).all())

    def test_c2w_not_inverse_and_pinhole_checks(self):
        yy, xx = np.indices((4, 5))
        cam = np.broadcast_to(np.stack([xx, yy, np.ones_like(xx)], axis=-1), (6, 4, 5, 3)).copy()
        poses = np.repeat(np.eye(4)[None], 6, axis=0)
        poses[:, :3, 3] = [2, -3, 4]
        data = dict(intrinsics=np.repeat(np.eye(3)[None], 6, axis=0), camera_poses=poses,
            pts3d_cam=cam, pts3d=cam+[2, -3, 4], ray_directions=cam.copy())
        self.assertTrue(convention_report(data)['passed'])
        data['camera_poses'] = np.linalg.inv(poses)
        self.assertFalse(convention_report(data)['passed'])
        data['camera_poses'] = poses
        data['ray_directions'][0, :, :, 0] += 2
        self.assertFalse(convention_report(data)['passed'])
