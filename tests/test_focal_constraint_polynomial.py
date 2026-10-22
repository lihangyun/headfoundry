import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from focal_constraint_polynomial import demazure_coefficients


class FocalConstraintPolynomialTest(unittest.TestCase):
    def test_critical_and_noncritical_fixed_motion(self):
        rotation=cv2.Rodrigues(np.array([0,np.deg2rad(18),0]))[0]@cv2.Rodrigues(np.array([np.deg2rad(15),0,0]))[0]
        pivot=np.array([0,0,3.]);translation=pivot-rotation@pivot
        cross=lambda t:np.array([[0,-t[2],t[1]],[t[2],0,-t[0]],[-t[1],t[0],0]])
        critical=cross(translation)@rotation
        coefficients=demazure_coefficients(critical)
        self.assertLess(abs(coefficients).max(),1e-12)
        self.assertEqual(np.linalg.matrix_rank(critical),2)
        # A fixed radial displacement breaks this identity;not a solver rerun.
        moved=cross(translation+[0,0,.3])@rotation
        polynomial=demazure_coefficients(moved)
        self.assertGreater(abs(polynomial).max(),1e-4)
        # Independent numeric cubic evaluation checks every polynomial entry.
        s=.7;diagonal=np.diag([s,s,1.]);e=diagonal@(moved/np.linalg.norm(moved))@diagonal
        cubic=2*e@e.T@e-np.trace(e@e.T)*e
        value=np.sum(polynomial*s**np.arange(7),axis=2)
        np.testing.assert_allclose(value,cubic,atol=1e-15)
        for factor in [-1.,1e200,1e-200]:
            np.testing.assert_allclose(demazure_coefficients(moved*factor),polynomial*np.sign(factor),atol=1e-15)
        for bad in [np.zeros((3,3)),np.ones((2,3)),np.full((3,3),np.nan)]:
            with self.assertRaises(ValueError):demazure_coefficients(bad)
