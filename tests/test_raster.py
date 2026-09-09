import unittest
import numpy as np
from headfoundry.raster import render,lift_pixels


class RasterTests(unittest.TestCase):
    def test_exact_lifting_weights_miss_and_occlusion(self):
        v=np.array([[0.,0,1],[8,0,2],[0,8,2]])
        e=np.c_[np.eye(3),np.zeros(3)]
        ids,w=lift_pixels(v,np.array([[0,1,2]]),e,np.eye(3),[[.5,.5],[10,10]])
        np.testing.assert_array_equal(ids,[0,-1])
        np.testing.assert_allclose(w[0],[6/7,1/14,1/14])
        self.assertTrue(np.isnan(w[1]).all())
        vertices=np.r_[v*2,v];faces=np.array([[0,1,2],[3,4,5]])
        ids,w=lift_pixels(vertices,faces,e,np.eye(3),[[.5,.5]])
        self.assertEqual(ids[0],1)
        point=w[0]@vertices[faces[ids[0]]]
        np.testing.assert_allclose(point[:2]/point[2],[.5,.5])
    def test_smooth_clay_changes_only_shading(self):
        v=np.array([[0.,0,2],[1,0,2],[0,1,2],[1,1,3]])
        original=v.copy();f=np.array([[0,1,2],[1,3,2]])
        e=np.c_[np.eye(3),np.zeros(3)];k=np.diag([30.,30.,1.])
        flat,depth,ids=render(v,f,e,k,(20,20))
        smooth,new_depth,new_ids=render(v,f,e,k,(20,20),smooth_shading=True)
        np.testing.assert_array_equal(v,original)
        np.testing.assert_array_equal(new_depth,depth)
        np.testing.assert_array_equal(new_ids,ids)
        self.assertGreater(np.abs(flat.astype(int)-smooth.astype(int)).max(),5)
        one,_,_=render(v,f[:1],e,k,(20,20))
        one_smooth,_,_=render(v,f[:1],e,k,(20,20),smooth_shading=True)
        np.testing.assert_allclose(one,one_smooth,atol=1)
        with self.assertRaises(ValueError):
            render(v,f,e,k,(20,20),np.zeros((4,2)),np.zeros((2,2,3)),smooth_shading=True)
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
