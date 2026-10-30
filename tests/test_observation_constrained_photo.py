"""Constraint arithmetic and biased-input limitation, not reconstruction tests."""
import sys
import unittest
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dense_photo_0332 import camera_values
from observation_constrained_photo import constraints, geometry
from short_track_camera import intrinsics, project


class ObservationConstraintTests(unittest.TestCase):
    def setUp(self):
        self.source = np.array([[280.,550.],[360.,620.],[440.,710.],[325.,690.]])
        k = intrinsics(np.log(1200.)); poses = np.repeat(np.eye(4)[None],3,axis=0)
        poses[1,:3,:3] = cv2.Rodrigues(np.array([.03,.12,-.01]))[0]
        poses[1,:3,3] = [1.,0,0]
        poses[2,:3,:3] = cv2.Rodrigues(np.array([-.06,-.1,.02]))[0]
        poses[2,:3,3] = [-.7,.2,.1]
        self.values = np.r_[camera_values(k,poses),np.zeros(4),np.log(1/np.array([4.,5.,6.,4.5]))]
        k,p,x = geometry(self.values,self.source)
        rows = np.array([[c,i,0,0] for c in (1,2) for i in range(4)])
        self.targets = project(k,p,x,rows)[0].reshape(2,4,2)

    def test_exact_bias_and_large_mismatch(self):
        slack,_ = constraints(self.values,self.source,self.targets)
        np.testing.assert_allclose(slack,9.,atol=1e-9)
        for shift,expected in ((3.,0.),(6.,-27.),(50.,-2491.)):
            biased = self.targets.copy(); biased[0,0,0] += shift
            slack,_ = constraints(self.values,self.source,biased)
            self.assertAlmostEqual(slack[0],expected,places=8)
        # The real geometry is rejected when its supplied observation is biased.
        # Thus feasibility must never be interpreted as physical accuracy.

    def test_all_parameter_derivatives(self):
        targets = self.targets+np.array([.7,-.4])
        _,analytic = constraints(self.values,self.source,targets)
        numeric = np.zeros_like(analytic)
        for column in range(len(self.values)):
            left=self.values.copy();right=self.values.copy();step=1e-6
            left[column]-=step;right[column]+=step
            numeric[:,column]=(constraints(right,self.source,targets)[0]-constraints(left,self.source,targets)[0])/(2*step)
        error=float(np.max(abs(analytic-numeric)/(1+abs(numeric))))
        self.assertLess(error,1e-5)
        print('observation constraint derivative max normalized error:',error)
        np.testing.assert_array_equal(analytic[:,12:16],0.)

    def test_invalid_domains(self):
        bad=self.values.copy();bad[11]=-20
        with self.assertRaises(ValueError):constraints(bad,self.source,self.targets)
        bad=self.values.copy();bad[16]=1000
        with self.assertRaises(ValueError):constraints(bad,self.source,self.targets)
        with self.assertRaises(ValueError):constraints(self.values,self.source,self.targets[:1])
        bad=self.targets.copy();bad[0,0,0]=np.nan
        with self.assertRaises(ValueError):constraints(self.values,self.source,bad)


if __name__=='__main__':unittest.main()
