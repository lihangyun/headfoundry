import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from anatomical_capacity_0239 import fit_similarity, box_quadratic, barycentric_closest, mesh_guard
from scan_surface_metric_0237 import apply_similarity


class AnatomicalCapacityTests(unittest.TestCase):
    def test_proper_global_similarity_and_true_box_solution(self):
        points = np.random.default_rng(239).normal(size=(40, 3))
        matrix = np.array([[0., -2., 0., 4.], [2., 0., 0., -5.], [0., 0., 2., 6.], [0., 0., 0., 1.]])
        recovered = fit_similarity(points, apply_similarity(points, matrix), np.ones(40))
        np.testing.assert_allclose(recovered, matrix, atol=1e-12)
        x, report = box_quadratic([[2., 1.], [1., 2.]], [10., 1.])
        self.assertTrue(report['converged'])
        np.testing.assert_allclose(x, [3., -1.], atol=1e-5)
        with self.assertRaises(ValueError):
            box_quadratic([[1., 0.], [0., -1.]], [0., 0.])
        with self.assertRaises(ValueError):
            fit_similarity(np.zeros((3, 3)), np.zeros((3, 3)), np.ones(3))

    def test_ill_conditioned_and_active_optima(self):
        rng = np.random.default_rng(239)
        q, _ = np.linalg.qr(rng.normal(size=(40, 40)))
        h = (q * np.geomspace(1., 1e5, 40)) @ q.T
        expected = rng.uniform(-.5, .5, 40)
        x, report = box_quadratic(h, h @ expected)
        self.assertTrue(report['converged'])
        np.testing.assert_allclose(x, expected, atol=1e-8)
        h = q @ np.diag(np.linspace(1., 20., 40)) @ q.T
        expected[[0, 1, 2, 3]] = [-3, 3, -3, 3]
        g = h @ expected
        g[[0, 1, 2, 3]] += [-2, 2, -2, 2]
        x, report = box_quadratic(h, g)
        self.assertTrue(report['converged'])
        np.testing.assert_allclose(x, expected, atol=1e-5)

    def test_barycentric_replay_and_whole_mesh_reversal_guard(self):
        triangle = np.array([[[0., 0., 0.], [10., 0., 0.], [0., 10., 0.]]])
        bary = barycentric_closest(np.array([[2., 3., 0.]]), triangle)
        np.testing.assert_allclose(bary, [[.5, .2, .3]])
        base = triangle[0]
        faces = np.array([[0, 1, 2]])
        self.assertTrue(mesh_guard(base, base, faces)['passed'])
        self.assertFalse(mesh_guard(base[[0, 2, 1]], base, faces)['passed'])
        self.assertFalse(mesh_guard(base * 3, base, faces)['passed'])


if __name__ == '__main__':
    unittest.main()
