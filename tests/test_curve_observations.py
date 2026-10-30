import unittest
import numpy as np
from headfoundry.curve_observations import point_to_polyline


class CurveObservationTests(unittest.TestCase):
    def test_sliding_and_endpoint(self):
        r,j,_,_,ambiguous=point_to_polyline([[2.,3.],[7.,3.],[-2.,3.]],[[0.,0.],[10.,0.]])
        np.testing.assert_allclose(r,[[0.,3.],[0.,3.],[-2.,3.]])
        np.testing.assert_allclose(j[:2],np.tile([[0.,0.],[0.,1.]],(2,1,1)))
        np.testing.assert_allclose(j[2],np.eye(2))
        self.assertFalse(ambiguous.any())

    def test_local_jacobian(self):
        p=np.array([[2.,4.],[-2.,-3.],[12.,6.]])
        q=np.array([[0.,0.],[8.,2.],[10.,10.]])
        _,j,_,_,ambiguous=point_to_polyline(p,q)
        self.assertFalse(ambiguous.any())
        for axis in range(2):
            d=np.zeros_like(p);d[:,axis]=1e-6
            numerical=(point_to_polyline(p+d,q)[0]-point_to_polyline(p-d,q)[0])/2e-6
            np.testing.assert_allclose(numerical,j[:,:,axis],atol=1e-9)

    def test_segment_switch_and_invalid(self):
        _,_,_,_,flags=point_to_polyline([[1.,1.],[0.,0.]],[[0.,0.],[2.,0.],[2.,2.]])
        self.assertTrue(flags.all())
        for q in [[[0.,0.],[0.,0.]],[[0.,0.],[np.nan,1.]]]:
            with self.assertRaises(ValueError):point_to_polyline([[1.,1.]],q)
