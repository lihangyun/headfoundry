import unittest
import numpy as np
from headfoundry.fusion import fuse_grid,extract_surface


class FusionTest(unittest.TestCase):
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
