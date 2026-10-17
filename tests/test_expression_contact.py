import unittest
import sys
from pathlib import Path

import numpy as np

from headfoundry.expression_contact import fit_contact_expression
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experiment_0211 import proper_crossings


class ExpressionContactTests(unittest.TestCase):
    def setUp(self):
        self.v = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        self.f = np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]])
        self.b = np.zeros((4, 3, 1))
        self.b[0, 1, 0], self.b[2, 1, 0] = .5, -.5

    def test_contact_and_replay_without_topology_claim(self):
        v, coefficients, report = fit_contact_expression(self.v, self.f, self.b, [0], [2],
                                                         contact_sigma=1e-4, motion_sigma=1.)
        self.assertLess(report["maximum_gap"], 1e-6)
        np.testing.assert_allclose(v, self.v+np.einsum("vck,k->vc", self.b, coefficients))
        # This toy contact collapses an edge: numerical fitting must not claim anatomy.
        self.assertIn("separate", report["limits"])

    def test_bounds_and_invalid_pairing_fail_closed(self):
        _, c, report = fit_contact_expression(self.v, self.f, self.b*.01, [0], [2],
                                             contact_sigma=1e-4, motion_sigma=1., coefficient_bound=.5)
        self.assertLessEqual(abs(c[0]), .5)
        self.assertGreater(report["maximum_gap"], .9)
        for up, low, sigma in (([0], [0], 1.), ([0], [2], 0.), ([0.], [2.], 1.)):
            with self.assertRaises(ValueError):
                fit_contact_expression(self.v, self.f, self.b, up, low,
                                       contact_sigma=sigma, motion_sigma=1.)

    def test_section_crossing_and_declared_contact_tolerance(self):
        a = np.array([[[-1., -1.], [1., 1.]]])
        b = np.array([[[-1., 1.], [1., -1.]]])
        self.assertEqual(proper_crossings(a, b, np.array([2., 2.])), 1)
        self.assertEqual(proper_crossings(a, b, np.array([0., 0.])), 0)


if __name__ == "__main__":
    unittest.main()
