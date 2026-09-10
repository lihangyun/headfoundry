import unittest
import numpy as np
from headfoundry.profile_fit import curve_residuals


class CurveDistanceTests(unittest.TestCase):
    def test_interior_endpoints_repetition_and_orientation(self):
        line=np.array([[0.,0],[0,0],[0,2]])
        points=np.array([[1.,1],[0,3],[0,-1]])
        expected=[[-1,0],[0,-1],[0,1]]
        np.testing.assert_allclose(curve_residuals(points,line),expected)
        np.testing.assert_allclose(curve_residuals(points,line[::-1]),expected)
        np.testing.assert_allclose(curve_residuals([[1,2]],[[0,0],[0,0]]),[[-1,-2]])
        self.assertEqual(curve_residuals(np.empty((0,2)),line).shape,(0,2))

    def test_curve_rejects_invalid_coordinates(self):
        for line in [[[0,0]],[[0,0],[np.nan,1]],[[0,0,0],[1,1,1]]]:
            with self.assertRaises(ValueError):curve_residuals([[1,1]],line)
