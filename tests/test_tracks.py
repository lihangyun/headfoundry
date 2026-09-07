import unittest
import numpy as np
from headfoundry.tracks import join_three_views


class TrackTests(unittest.TestCase):
    def test_cycles_preserve_observations_and_reject_ambiguity(self):
        ab=np.array([[10.,20,30,40],[100,120,130,140]])
        ac=np.array([[10.5,20,50,60],[100,120,150,160]])
        bc=np.array([[30,40.5,50,60],[130,140,250,260]])
        observations,indices=join_three_views(ab,ac,bc)
        np.testing.assert_array_equal(indices,[[0,0,0]])
        np.testing.assert_array_equal(observations,[[[10,20],[30,40],[50,60]]])
        duplicate=np.vstack([ac,ac[0]])
        self.assertEqual(len(join_three_views(ab,duplicate,bc)[0]),0)
        self.assertEqual(join_three_views(np.empty((0,4)),ac,bc)[0].shape,(0,3,2))
        with self.assertRaises(ValueError):join_three_views(ab,ac,bc,tolerance_px=0)
