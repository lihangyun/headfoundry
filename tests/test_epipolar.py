import unittest
import numpy as np
from headfoundry.epipolar import fundamental, sampson_distance, calibrated_pose


class EpipolarTests(unittest.TestCase):
    def test_independent_points_and_corrupted_validation(self):
        rng=np.random.default_rng(42)
        points=rng.uniform(-1,1,(50,3));points[:,2]+=5
        first=points[:,:2]/points[:,2:]*900+500
        moved=points+np.array([.8,.1,0])
        second=moved[:,:2]/moved[:,2:]*900+500
        f=fundamental(first[:35],second[:35])
        self.assertLess(sampson_distance(f,first[35:],second[35:]).max(),1e-8)
        wrong=second[35:]+np.array([0,50])
        self.assertGreater(sampson_distance(f,first[35:],wrong).min(),30)
        self.assertEqual(np.linalg.matrix_rank(f),2)
        with self.assertRaises(ValueError):fundamental(first[:7],second[:7])
        with self.assertRaises(ValueError):fundamental(np.zeros((10,2)),np.zeros((10,2)))

    def test_calibrated_pose_recovers_rotation_and_translation_direction(self):
        rng=np.random.default_rng(7)
        points=rng.uniform(-1,1,(80,3));points[:,2]+=5
        angle=.3
        r=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
        t=np.array([.8,.1,.05]);other=points@r.T+t
        k=np.array([[900.,0,500],[0,900,500],[0,0,1]])
        a=points[:,:2]/points[:,2:]*900+500
        b=other[:,:2]/other[:,2:]*900+500
        result=calibrated_pose(a,b,k,k);e=np.array(result['extrinsic'])
        np.testing.assert_allclose(e[:,:3],r,atol=1e-8)
        np.testing.assert_allclose(e[:,3],t/np.linalg.norm(t),atol=1e-8)
        self.assertEqual(result['positive_depth_fraction'],1.)
        self.assertEqual(result['status'],'UNVERIFIED')
