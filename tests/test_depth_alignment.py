import unittest
import numpy as np
from headfoundry.depth_alignment import refine_depth_cameras


class DepthAlignmentTest(unittest.TestCase):
    def test_known_scale_translation_and_anchor(self):
        from scipy.spatial.transform import Rotation
        rng=np.random.default_rng(22)
        world=rng.uniform([-.2,-.2,.8],[.2,.2,1.2],(40,3))
        e=np.repeat(np.eye(4)[None,:3],2,0);e[1,:,3]=[.1,0,.05]
        q=np.stack([world,(world+e[1,:,3])/1.04])
        start=e.copy();start[1,:,3]+=[.02,-.01,.015]
        start[1,:,:3]=Rotation.from_rotvec([.03,.01,-.02]).as_matrix()
        result,scale,report=refine_depth_cameras(q,start)
        np.testing.assert_array_equal(result[0],start[0])
        np.testing.assert_allclose(result,e,atol=1e-5)
        np.testing.assert_allclose(scale,[1,1.04],atol=1e-5)
        self.assertTrue(report['converged'])
        k=np.repeat(np.array([[[1000,0,500],[0,1000,500],[0,0,1]]]),2,axis=0)
        joint,joint_scale,joint_report=refine_depth_cameras(q,start,k)
        np.testing.assert_allclose(joint,e,atol=1e-5)
        np.testing.assert_allclose(joint_scale,[1,1.04],atol=1e-5)
        self.assertTrue(joint_report['pixel_term'])
        self.assertEqual(joint_report['active_parameters'],[])
        self.assertTrue(np.isfinite(joint_report['depth_pixel_costs']).all())
        with self.assertRaises(ValueError):refine_depth_cameras(q[:,:2],start)
        with self.assertRaises(ValueError):refine_depth_cameras(np.ones((2,8,3)),start)
