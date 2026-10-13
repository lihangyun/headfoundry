import unittest
import numpy as np
from headfoundry.profile_fit import curve_residuals,curve_residual_jacobian


class CurveDistanceTests(unittest.TestCase):
    def test_piecewise_jacobian_matches_independent_point_perturbations(self):
        line=np.array([[0.,0],[1,0],[1,1],[1,1]])
        points=np.array([[.5,.8],[-.2,.2],[1.3,.5],[1.2,1.4]])
        residual,jacobian=curve_residual_jacobian(points,line)
        np.testing.assert_array_equal(residual,curve_residuals(points,line))
        for axis in range(2):
            delta=np.zeros_like(points);delta[:,axis]=1e-6
            numeric=(curve_residuals(points+delta,line)-curve_residuals(points-delta,line))/2e-6
            np.testing.assert_allclose(jacobian[:,:,axis],numeric,atol=1e-9)
        empty,jac=curve_residual_jacobian(np.empty((0,2)),line)
        self.assertEqual(empty.shape,(0,2));self.assertEqual(jac.shape,(0,2,2))

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
