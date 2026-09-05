import unittest
import numpy as np
from headfoundry.epipolar import fundamental, sampson_distance


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
