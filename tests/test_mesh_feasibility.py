import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from mesh_feasibility_0240 import constraints, violated_faces


class MeshFeasibilityTests(unittest.TestCase):
    def test_exact_jacobian_and_unchanged_final_guards(self):
        rng = np.random.default_rng(240)
        base = np.array([[[0., 0., 0.], [2., 0., 0.], [0., 3., 0.]],
            [[1., 1., 1.], [3., 1., 1.], [1., 4., 1.]]])
        field = rng.normal(0, .03, (*base.shape, 5))
        x = rng.normal(0, .2, 5)
        value, jac = constraints(x, base, field)
        numerical = np.empty_like(jac)
        for i in range(5):
            delta = np.zeros(5)
            delta[i] = 1e-6
            numerical[:, i] = (constraints(x + delta, base, field)[0] - constraints(x - delta, base, field)[0]) / 2e-6
        np.testing.assert_allclose(jac, numerical, rtol=1e-6, atol=1e-8)
        self.assertTrue((value > 0).all())
        tri = base[:1]
        direction = np.zeros((*tri.shape, 1))
        direction[0, 2, 1, 0] = -6
        bad, _ = constraints([1.], tri, direction)
        self.assertLess(bad[0], 0)
        vertices = tri[0] + direction[0, :, :, 0]
        np.testing.assert_array_equal(violated_faces(vertices, tri[0], np.array([[0, 1, 2]])), [0])

    def test_constraints_do_not_require_scan_units_or_alignment(self):
        rng = np.random.default_rng(241)
        base = np.array([[[0., 0., 0.], [2., 0., 0.], [0., 3., 0.]]])
        field = rng.normal(0, .03, (*base.shape, 4))
        x = rng.normal(0, .2, 4)
        original, jac = constraints(x, base, field)
        linear = 1000 * np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
        transformed = base @ linear.T + [30., -400., 200.]
        directions = np.einsum('ij,nvjk->nvik', linear, field)
        actual, transformed_jac = constraints(x, transformed, directions)
        np.testing.assert_allclose(actual, original, atol=1e-12)
        np.testing.assert_allclose(transformed_jac, jac, atol=1e-12)
