import unittest
import numpy as np
from headfoundry.raster import render


class RasterTests(unittest.TestCase):
    def test_occlusion_independent_of_triangle_order(self):
        v=np.array([[0,0,2],[12,0,2],[0,12,2],[0,0,1],[6,0,1],[0,6,1]],float)
        e=np.c_[np.eye(3),np.zeros(3)]
        for f in (np.array([[0,1,2],[3,4,5]]),np.array([[3,4,5],[0,1,2]])):
            _,depth,_=render(v,f,e,np.eye(3),(8,8))
            self.assertEqual(depth[1,1],1.)
            self.assertTrue(np.isinf(depth[7,7]))

    def test_perspective_correct_uv(self):
        v=np.array([[0,0,1],[8,0,2],[0,8,2]],float)
        tex=np.zeros((9,9,3));tex[:,:,0]=np.arange(9)[None,:]*20
        image,_,_=render(v,[[0,1,2]],np.c_[np.eye(3),np.zeros(3)],np.eye(3),(5,5),[[0,0],[8,0],[0,8]],tex)
        # At (.5,.5), screen weights .75,.125,.125; reciprocal-depth sum .875.
        self.assertAlmostEqual(float(image[0,0,0]),20*.5/.875,delta=1)

    def test_near_plane_rejected(self):
        with self.assertRaises(ValueError):
            render([[0,0,-1],[1,0,1],[0,1,1]],[[0,1,2]],np.c_[np.eye(3),np.zeros(3)],np.eye(3),(8,8))
