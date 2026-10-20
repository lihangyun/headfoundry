import unittest
import numpy as np
from headfoundry.da3 import depth_to_world, original_intrinsics

class DepthProjectionTests(unittest.TestCase):
    def test_depth_roundtrip_with_camera_translation_rotation_and_resize(self):
        angle=.4;c,s=np.cos(angle),np.sin(angle)
        r=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        e=np.array([np.c_[r,[.2,-.1,.3]],np.c_[np.eye(3),[-.3,.1,0]]])
        k=np.array([[[100.,0,1],[0,120,1],[0,0,1]]]*2)
        depth=np.arange(12,dtype=float).reshape(2,2,3)/10+2
        world=depth_to_world(depth,e,k)
        camera=np.einsum('vij,vhwj->vhwi',e[:,:,:3],world)+e[:,None,None,:,3]
        np.testing.assert_allclose(camera[...,2],depth)
        pixels=np.einsum('vij,vhwj->vhwi',k,camera)
        y,x=np.mgrid[:2,:3];expected=np.stack([x,y],axis=-1)
        np.testing.assert_allclose(pixels[...,:2]/pixels[...,2:],np.broadcast_to(expected,(2,2,3,2)),atol=1e-12)
        scaled=original_intrinsics(k,[2,3],[[20,30],[4,9]])
        np.testing.assert_allclose(scaled[0],np.diag([10,10,1])@k[0])
        np.testing.assert_allclose(scaled[1],np.diag([3,2,1])@k[1])
        with self.assertRaises(ValueError):depth_to_world(-depth,e,k)
        with self.assertRaises(ValueError):depth_to_world(depth,e[:,:2],k)
        bad=e.copy();bad[:,0,:3]*=-1
        with self.assertRaises(ValueError):depth_to_world(depth,bad,k)
        with self.assertRaises(ValueError):original_intrinsics(k,[0,3],[[2,3],[2,3]])
