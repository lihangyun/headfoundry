import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from direct_patch_camera import residual


class DirectPatchCameraTest(unittest.TestCase):
    def setUp(self):
        yy,xx=np.mgrid[:1280,:720]
        self.reference=.1+.0002*xx+.0001*yy
        self.pixels=np.array([[[200.,400.],[201.,400.],[200.,401.]],
                              [[500.,900.],[501.,900.],[500.,901.]]])
        self.rho=np.array([.25,.25])
        self.poses=np.repeat(np.eye(4)[None],2,axis=0)
        self.poses[1,:3,3]=[.12,-.04,.03]
        self.gain=np.array([0.,np.log(1.1)]);self.bias=np.array([0.,.02])
        self.f=1000.;z=4.;tx,ty,tz=self.poses[1,:3,3]
        scale=z/(z+tz)
        # Independent inverse image homography for a translated Z=4 plane.
        sx=(xx-359.5-self.f*tx/(z+tz))/scale+359.5
        sy=(yy-639.5-self.f*ty/(z+tz))/scale+639.5
        target=1.1*(.1+.0002*sx+.0001*sy)+.02
        self.images=np.stack([self.reference,target])

    def call(self,**kw):
        args=dict(images=self.images,pixels=self.pixels,inverse_depth=self.rho,poses=self.poses,
                  log_gains=self.gain,biases=self.bias,log_focal=np.log(self.f))
        args.update(kw);return residual(**args)

    def test_affine_image_oracle_and_exposure_derivatives(self):
        r,warp=self.call()
        self.assertEqual(r.shape,(1,2,3));self.assertEqual(warp.shape,(1,2,3,2))
        np.testing.assert_allclose(r,0,atol=2e-15)
        for key,expected in [('biases',-np.ones_like(r)),('log_gains',-1.1*(.1+.0002*self.pixels[...,0]+.0001*self.pixels[...,1])[None])]:
            value=self.bias if key=='biases' else self.gain
            first,second=value.copy(),value.copy();first[1]+=1e-5;second[1]-=1e-5
            derivative=(self.call(**{key:first})[0]-self.call(**{key:second})[0])/2e-5
            np.testing.assert_allclose(derivative,expected,atol=1e-10)
        self.assertGreater(np.max(abs(self.call(log_focal=np.log(1200.))[0])),1e-4)
        self.assertGreater(np.max(abs(self.call(inverse_depth=self.rho*1.2)[0])),1e-4)

    def test_nonidentity_projection_opencv_replay(self):
        poses=self.poses.copy();vector=np.array([.01,-.02,.005])
        poses[1,:3,:3]=cv2.Rodrigues(vector)[0]
        _,warp=self.call(poses=poses)
        flat=self.pixels.reshape(-1,2)
        xyz=np.c_[(flat-[359.5,639.5])/self.f,np.ones(len(flat))]*4
        k=np.array([[self.f,0,359.5],[0,self.f,639.5],[0,0,1.]])
        oracle=cv2.projectPoints(xyz,vector,poses[1,:3,3],k,None)[0].reshape(self.pixels.shape)
        np.testing.assert_allclose(warp[0],oracle,atol=1e-10)

    def test_invalid_state_never_clamps_or_prunes(self):
        off=self.pixels.copy();off[0,0,0]=-1
        reflected=self.poses.copy();reflected[1,0,0]=-1
        behind=self.poses.copy();behind[1,2,3]=-5
        nan=self.images.copy();nan[0,0,0]=np.nan
        for changes in [dict(inverse_depth=np.array([0.,.25])),dict(pixels=off),dict(poses=reflected),
                        dict(poses=behind),dict(images=nan),dict(log_gains=np.array([0.,1000.])),
                        dict(biases=np.array([0.,-1.])),dict(pixels=self.pixels[:0])]:
            with self.assertRaises(ValueError):self.call(**changes)
        near=self.poses.copy();near[1,:3,3]=[0,0,-4+5e-10]
        with self.assertRaises(ValueError):
            self.call(pixels=np.array([[[359.5,639.5]]]),inverse_depth=np.array([.25]),poses=near)
