import unittest
import numpy as np
from headfoundry.profile_fit import fit_profile_step


class ProfileFitTest(unittest.TestCase):
    def test_bounded_move_and_missing_rows(self):
        v=np.array([[0,0,1],[.1,0,1],[0,.1,1],[.1,.1,1.]])
        f=np.array([[0,2,1],[1,2,3]])
        p=np.array([[[100,0,0,0],[0,100,0,0],[0,0,1,0]]])
        result,report=fit_profile_step(v,f,p,[np.array([[11,0],[11,10]])],[1],.001)
        self.assertGreater(report['maximum_displacement'],0)
        self.assertLessEqual(report['maximum_displacement'],.001+1e-12)
        unchanged,_=fit_profile_step(v,f,p,[np.array([[11,100]])],[1])
        np.testing.assert_array_equal(unchanged,v)
