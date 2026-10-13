import unittest
import numpy as np
from headfoundry.raster import render,lift_pixels,occluding_edges


class RasterTests(unittest.TestCase):
    def test_occluding_edges_require_separate_visibility_check(self):
        v=np.array([[-1,-1,2],[1,-1,2],[1,1,2],[-1,1,2],
                    [-1,-1,4],[1,-1,4],[1,1,4],[-1,1,4]],float)
        f=np.array([[0,3,2],[0,2,1],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                    [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
        e=np.c_[np.eye(3),np.zeros(3)]
        expected=np.array([[0,1],[0,3],[1,2],[2,3]])
        np.testing.assert_array_equal(occluding_edges(v,f,e),expected)
        # Reordering triangles does not change contour topology.
        np.testing.assert_array_equal(occluding_edges(v,f[::-1],e),expected)
        angle=.4
        rotation=np.array([[np.cos(angle),-np.sin(angle),0],
                           [np.sin(angle),np.cos(angle),0],[0,0,1]])
        offset=np.array([.2,-.3,.1])
        transformed=v @ rotation.T+offset
        moved_camera=np.c_[rotation.T,-rotation.T @ offset]
        np.testing.assert_array_equal(occluding_edges(transformed,f,moved_camera),expected)
        # A second shell behind the first has the same projection, but is not
        # visible. Normal-facing transitions alone cannot certify support.
        mesh=np.r_[v,v*2];faces=np.r_[f,f+len(v)]
        edges=occluding_edges(mesh,faces,e)
        points=mesh[edges].mean(1);pixels=points[:,:2]/points[:,2:]
        ids,w=lift_pixels(mesh,faces,e,np.eye(3),pixels)
        hits=np.einsum('ni,nij->nj',w,mesh[faces[ids]])
        visible=np.linalg.norm(points-hits,axis=1)<1e-9
        np.testing.assert_array_equal(visible,edges[:,0]<len(v))
        np.testing.assert_array_equal(occluding_edges(v,f[:1],e),np.empty((0,2),int))
        for bad_vertices,bad_faces,bad_camera in [
                (v,f,np.eye(3)),(v,f.astype(float),e),(v,np.r_[f,f[:1]],e),
                (v,np.r_[f[:1],f[1:2,::-1],f[2:]],e),
                (v,np.array([[0,0,1]]),e),(v*[-1,1,-1],f,e),
                (v,np.array([[0,1,len(v)]]),e)]:
            with self.assertRaises(ValueError):
                occluding_edges(bad_vertices,bad_faces,bad_camera)

    def test_component_filter_does_not_see_through_occluders(self):
        v=np.array([[0.,0,1],[8,0,2],[0,8,2]])
        vertices=np.r_[v*2,v];faces=np.array([[0,1,2],[3,4,5]])
        e=np.c_[np.eye(3),np.zeros(3)]
        for allowed,expected in [([True,False],-1),([False,True],1),([False,False],-1)]:
            ids,w=lift_pixels(vertices,faces,e,np.eye(3),[[.5,.5]],allowed_faces=allowed)
            self.assertEqual(ids[0],expected)
            self.assertEqual(bool(np.isnan(w).all()),expected==-1)
        for bad in [[1,0],[True],[[True,False]]]:
            with self.assertRaises(ValueError):
                lift_pixels(vertices,faces,e,np.eye(3),[[.5,.5]],allowed_faces=bad)

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

    def test_perspective_correct_vertex_color(self):
        v=np.array([[0,0,1],[8,0,2],[0,8,2]],float)
        rgb=np.array([[0,0,0],[200,0,0],[0,0,0]],float)
        image,_,_=render(v,[[0,1,2]],np.c_[np.eye(3),np.zeros(3)],np.eye(3),(5,5),vertex_colors=rgb)
        self.assertAlmostEqual(float(image[0,0,0]),200*(.125/2)/.875,delta=1)
        with self.assertRaises(ValueError):
            render(v,[[0,1,2]],np.c_[np.eye(3),np.zeros(3)],np.eye(3),(5,5),vertex_colors=rgb[:2])

    def test_near_plane_rejected(self):
        with self.assertRaises(ValueError):
            render([[0,0,-1],[1,0,1],[0,1,1]],[[0,1,2]],np.c_[np.eye(3),np.zeros(3)],np.eye(3),(8,8))
