import sys
from pathlib import Path
import unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from visible_profile_model_0244 import envelope, frontal_constraints


class VisibleProfileModelTests(unittest.TestCase):
    def test_identity_and_all_pose_derivatives_reassociate_visible_envelopes(self):
        vertices = np.array([[-1., -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])*.05
        faces = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4], [3, 7, 6], [3, 6, 2], [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5]])
        rng = np.random.default_rng(244)
        field = rng.normal(size=(8, 3, 4))*.0003
        state = rng.normal(size=10)*.03
        initial = np.array([.1, .7, .1, .02, -.01, .6])
        k = np.array([[937., 0, 360], [0, 937., 640], [0, 0, 1.]])
        args = (vertices, field, faces, np.arange(8), initial, k, np.array([621.7, 645.1, 666.3]), 1, 0)
        values, analytic, _, _ = envelope(state, *args)
        numerical = np.empty_like(analytic)
        for j in range(len(state)):
            delta = np.eye(len(state))[j]*1e-6
            numerical[:, j] = (envelope(state+delta, *args)[0]-envelope(state-delta, *args)[0])/2e-6
        np.testing.assert_allclose(analytic, numerical, atol=1e-7, rtol=1e-5)
        self.assertTrue(np.isfinite(values).all())

    def test_frontal_squared_drift_constraint_derivative(self):
        rng = np.random.default_rng(245)
        base = rng.normal(size=(15, 3))*.02+[0, 0, 1]
        field = rng.normal(size=(15, 3, 4))*.001
        projection = np.array([[900., 0, 360, 0], [0, 900, 640, 0], [0, 0, 1, 0]])
        target = (np.c_[base, np.ones(15)]@projection.T)
        target = target[:, :2]/target[:, 2:]
        beta = np.ones(4)*.2
        values, analytic = frontal_constraints(beta, base, field, projection, target)
        numerical = np.empty_like(analytic)
        for j in range(4):
            delta = np.eye(4)[j]*1e-6
            numerical[:, j] = (frontal_constraints(beta+delta, base, field, projection, target)[0]
                - frontal_constraints(beta-delta, base, field, projection, target)[0])/2e-6
        np.testing.assert_allclose(analytic, numerical, atol=2e-7, rtol=1e-5)
        np.testing.assert_allclose(frontal_constraints(np.zeros(4), base, field, projection, target)[0], 4.)
