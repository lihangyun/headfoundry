import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from headfoundry.camera import project
from direct_geometry_capacity_0236 import (RESIZE, camera_structure, evaluate_camera_only,
    projection_result, relative_pose_errors, unproject_samples)
from scan_motion_truth_0230 import look_at_origin


class DirectGeometryCapacityTests(unittest.TestCase):
    def fixture(self):
        points = np.random.default_rng(236).uniform([-.6, -.6, -.25], [.6, .6, .25], (600, 3))
        e = np.array([look_at_origin([0, 0, 6]), look_at_origin([1., 0, 5.9]),
            look_at_origin([-1., 0, 5.9]), look_at_origin([0, .8, 5.9])])
        k = np.broadcast_to(np.array([[1083., 0, 359.5], [0, 1083, 639.5], [0, 0, 1]]), (4, 3, 3)).copy()
        pixels = np.array([project(a @ b, points) for a, b in zip(k, e)])
        known = {'pixels': pixels + .5, 'visible': np.ones((4, 600), bool),
            'point_ids': np.arange(600), 'view_names': np.array(['front', 'yaw-10', 'other', 'pitch'])}
        return known, points, k, e

    def test_exact_camera_replay_and_scale_gauge(self):
        known, _, k, e = self.fixture()
        report, arrays = evaluate_camera_only(known, k, e)
        self.assertEqual(report['status'], 'TECHNICAL_CHECK_PASSED')
        self.assertLess(max(a['errors'].max() for a in arrays.values()), 1e-8)
        scaled = e.copy()
        scaled[:, :, 3] *= 17.
        self.assertEqual(evaluate_camera_only(known, k, scaled)[0]['status'], 'TECHNICAL_CHECK_PASSED')
        bad = e.copy()
        bad[2, 1, 3] += .2
        self.assertEqual(evaluate_camera_only(known, k, bad)[0]['status'], 'REJECT')
        self.assertGreater(relative_pose_errors(bad, e)[1]['translation_direction_deg'], 1.)

    def test_native_resize_and_positive_depth_unprojection(self):
        known, _, k, e = self.fixture()
        p = known['pixels'][0, :10] - .5
        resized = np.c_[p, np.ones(len(p))] @ RESIZE.T
        np.testing.assert_allclose(resized[:, :2], (p + .5) * .525 - .5)
        depth = np.full((672, 378), 5.)
        world = unproject_samples(depth, RESIZE @ k[0], e[0], resized[:, :2])
        result, pixels, _ = projection_result(world, k[0], e[0], p)
        self.assertTrue(result['passed'])
        np.testing.assert_allclose(pixels, p, atol=1e-12)
        unsupported = unproject_samples(depth, RESIZE @ k[0], e[0], [[-1., -1.]])
        score, _, errors = projection_result(unsupported, k[0], e[0], [[2., 3.]])
        self.assertFalse(score['passed'])
        self.assertEqual(score['invalid_count'], 1)
        self.assertTrue(np.isinf(errors).all())
        with self.assertRaises(ValueError):
            unproject_samples(-depth, k[0], e[0], p)

    def test_malformed_and_behind_camera_cannot_pass(self):
        known, points, k, e = self.fixture()
        self.assertTrue(camera_structure(k, e)['passed'])
        bad = e.copy()
        bad[:, 0, :3] *= -1
        self.assertFalse(camera_structure(k, bad)['passed'])
        bad_k = k.copy()
        bad_k[:, 0, 0] = 10000
        self.assertFalse(camera_structure(bad_k, e)['passed'])
        with self.assertRaises(ValueError):
            camera_structure(k[:, :2], e)
        behind = e[0].copy()
        behind[2, 3] = -10
        score, _, error = projection_result(points, k[0], behind, known['pixels'][0] - .5)
        self.assertFalse(score['passed'])
        self.assertEqual(score['positive_depth_fraction'], 0.)
        self.assertTrue(np.isinf(error).all())


if __name__ == '__main__':
    unittest.main()
