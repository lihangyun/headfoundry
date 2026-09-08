import unittest
import numpy as np
from headfoundry.fusion import fuse_grid,extract_surface,_sample_depth


class FusionTest(unittest.TestCase):
    def test_bilinear_affine_depth_and_mask_boundary(self):
        y,x=np.mgrid[:5,:5]; depth=1+.2*x+.3*y
        uv=np.array([[1.2,2.7],[.5,.5],[4.,2.],[-.1,2.]])
        mask=np.ones((5,5),bool)
        indices,sampled=_sample_depth(depth,mask,uv,True)
        np.testing.assert_array_equal(indices,[0,1])
        np.testing.assert_allclose(sampled,1+.2*uv[:2,0]+.3*uv[:2,1])
        mask[3,2]=False
        indices,_=_sample_depth(depth,mask,uv,True)
        np.testing.assert_array_equal(indices,[1])

    def test_free_space_is_known_but_hidden_space_is_not(self):
        depth=np.ones((1,8,8)); e=np.eye(4)[None,:3]
        k=np.array([[[10,0,4],[0,10,4],[0,0,1]]])
        args=(depth,e,k,np.ones_like(depth,bool),[-.01,-.01,.5],[.01,.01,1.5],5,.1)
        _,field,count=fuse_grid(*args,free_space=True)
        self.assertTrue((field[:,:,0]==1).all())
        self.assertTrue((count[:,:,0]==1).all())
        self.assertTrue((count[:,:,-1]==0).all())
        _,_,old_count=fuse_grid(*args)
        self.assertTrue((old_count[:,:,0]==0).all())

    def test_closed_sphere_shared_edges(self):
        axis=np.linspace(-1,1,14)
        xyz=np.stack(np.meshgrid(axis,axis,axis,indexing='ij'),-1)
        values=np.linalg.norm(xyz,axis=-1)-.71
        v,f=extract_surface(xyz,values,np.ones_like(values,bool))
        edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1)
        _,counts=np.unique(edges,axis=0,return_counts=True)
        self.assertTrue((counts==2).all())
        normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
        self.assertTrue(((normal*v[f].mean(1)).sum(1)>0).all())

    def test_plane_and_unknown_space(self):
        depth=np.ones((2,16,16)); e=np.repeat(np.eye(4)[None,:3],2,0)
        e[1,0,3]=.025
        k=np.repeat(np.array([[20,0,8],[0,20,8],[0,0,1]])[None],2,0)
        xyz,field,count=fuse_grid(depth,e,k,np.ones_like(depth,bool),[-.1,-.1,.91],[.1,.1,1.08],9,.2)
        v,f=extract_surface(xyz,field,count>0)
        self.assertGreater(len(f),0)
        np.testing.assert_allclose(v[:,2],1,atol=1e-12)
        normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
        self.assertTrue((normal[:,2]<0).all())
        self.assertEqual(len(extract_surface(xyz,field,np.zeros_like(count,bool))[1]),0)
        self.assertEqual(int(count.min()),2)
        with self.assertRaises(ValueError):fuse_grid(depth,e,k,np.ones_like(depth,bool),[0,0,0],[0,1,1])
