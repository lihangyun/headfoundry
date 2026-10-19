import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from video_model_0241 import camera, residual_jacobian, project, visible_support


class VideoModelProjectionTests(unittest.TestCase):
    def test_all_projection_derivatives_and_residual_order(self):
        rng = np.random.default_rng(241)
        base = rng.normal(size=(20, 3)) * .03
        field = rng.normal(size=(20, 3, 7)) * .003
        initial = np.array([[3., .1, -.2, .02, -.03, .7], [2.8, -.4, .3, -.01, .02, .8]])
        views = np.repeat([0, 1], 10)
        observed = rng.normal(size=(20, 2)) * 10 + [360, 640]
        state = rng.normal(size=20) * .1
        residual, analytic = residual_jacobian(state, base, field, observed, views, initial)
        numerical = np.empty_like(analytic)
        for column in range(len(state)):
            d = np.eye(len(state))[column] * 1e-6
            numerical[:, column] = (residual_jacobian(state + d, base, field, observed, views, initial)[0]
                - residual_jacobian(state - d, base, field, observed, views, initial)[0]) / 2e-6
        np.testing.assert_allclose(analytic, numerical, rtol=1e-5, atol=8e-8)
        points = base + np.einsum('nck,k->nc', field, state[:7])
        intrinsic = np.diag([1000 * np.exp(.3 * state[-1])] * 2 + [1.])
        intrinsic[:2, 2] = [360, 640]
        for view in (0, 1):
            r, t, _ = camera(state[7 + view * 6:13 + view * 6], initial[view])
            chosen = views == view
            expected = (project(points[chosen], np.c_[r, t], intrinsic) - observed[chosen]) / 4
            np.testing.assert_allclose(residual[:-7].reshape(-1, 2)[chosen], expected, atol=1e-12)
        np.testing.assert_array_equal(residual[-7:], state[:7])

    def test_negative_depth_is_rejected(self):
        with self.assertRaises(ValueError):
            camera(np.zeros(6), np.array([0, 0, 0, 0, 0, -1.]))
        with self.assertRaises(ValueError):
            project(np.zeros((1, 3)), np.c_[np.eye(3), [0, 0, -1]], np.eye(3))

    def test_visibility_accepts_shared_edge_but_not_hidden_or_disallowed_surface(self):
        front = np.array([[-1., -1, 2], [1, -1, 2], [1, 1, 2], [-1, 1, 2]])
        back = front.copy()
        back[:, 2] = 3
        vertices = np.vstack([front, back])
        faces = np.array([[0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7]])
        points = np.array([[0., 0, 2], [0, 0, 3]])
        extrinsic = np.c_[np.eye(3), np.zeros(3)]
        visible, gap = visible_support(vertices, faces, points, extrinsic, np.eye(3), np.ones(4, bool))
        np.testing.assert_array_equal(visible, [True, False])
        np.testing.assert_allclose(gap, [0, 1], atol=1e-12)
        visible, _ = visible_support(vertices, faces, points, extrinsic, np.eye(3), np.array([False, False, True, True]))
        self.assertFalse(visible.any())
