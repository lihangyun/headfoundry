import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from bundle_stationarity import linearize as numeric
from native_camera_jacobian import linearize
from short_track_camera import intrinsics,project


class NativeCameraJacobianTest(unittest.TestCase):
    def test_independent_finite_differences_and_invalid_gauges(self):
        poses=np.repeat(np.eye(4)[None],3,axis=0)
        poses[1,:3,:3]=cv2.Rodrigues(np.array([.02,-.04,.01]))[0]
        poses[2,:3,:3]=cv2.Rodrigues(np.array([-.03,.01,.025]))[0]
        poses[1,:3,3]=np.array([.8,-.4,.2])/np.linalg.norm([.8,-.4,.2]);poses[2,:3,3]=[-.3,.2,.1]
        points=np.random.default_rng(329).uniform([-.3,-.5,3],[.3,.5,4],(8,3));k=intrinsics(np.log(1200.))
        rows=np.array([[camera,point,0,0] for camera in range(3) for point in range(8)],float)
        rows[:,2:]=project(k,poses,points,rows)[0]
        residual,jac,replay=linearize(k,poses,points,rows,0,1)
        old,finite,_,_=numeric(k,poses,points,rows,0,1)
        self.assertLess(replay,1e-9);np.testing.assert_allclose(residual,old,atol=1e-9)
        self.assertLess(np.linalg.norm(jac-finite)/np.linalg.norm(finite),1e-7)
        bad=poses.copy();bad[1,:3,3]*=2
        with self.assertRaises(ValueError):linearize(k,bad,points,rows,0,1)
        wrong=rows.copy();wrong[0,0]=.5
        with self.assertRaises(ValueError):linearize(k,poses,points,wrong,0,1)
