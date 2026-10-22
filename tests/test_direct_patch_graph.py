import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from direct_patch_graph import residual
from direct_patch_camera import residual as complete_residual


class DirectPatchGraphTest(unittest.TestCase):
    def setUp(self):
        yy,xx=np.mgrid[:1280,:720]
        self.poses=np.repeat(np.eye(4)[None],4,axis=0)
        self.poses[:,:3,3]=[[0,0,0],[.12,-.04,.03],[-.08,.06,-.02],[.02,.1,.04]]
        self.a=np.log([1.,1.1,.95,1.04]);self.b=np.array([0.,.02,.01,-.01])
        images=[]
        # Independent inverse homography from each view back to world plane Z=4.
        for pose,a,b in zip(self.poses,self.a,self.b):
            tx,ty,tz=pose[:3,3]
            u=(xx-359.5)*(4+tz)/4-1000*tx/4+359.5
            v=(yy-639.5)*(4+tz)/4-1000*ty/4+639.5
            images.append(np.exp(a)*(.1+.0002*u+.0001*v)+b)
        self.images=np.stack(images)
        self.hosts=np.array([2,0,3,1])
        centers=np.array([[270.,500.],[420.,600.],[370.,750.],[330.,900.]])
        offsets=np.array([[0.,0.],[1.,0.],[0.,1.],[-1.,0.]])
        self.pixels=centers[:,None,:]+offsets
        self.rho=1/(4+self.poses[self.hosts,2,3])
        self.edges=np.array([[2,1],[0,3],[3,0],[1,2],[0,1],[2,0]])

    def call(self,**kw):
        args=dict(images=self.images,pixels=self.pixels,hosts=self.hosts,observations=self.edges,
                  inverse_depth=self.rho,poses=self.poses,log_gains=self.a,biases=self.b,log_focal=np.log(1000.))
        args.update(kw);return residual(**args)

    def test_sparse_exposures_order_and_gauges(self):
        values,warps=self.call()
        self.assertEqual(values.shape,(6,4));self.assertEqual(warps.shape,(6,4,2))
        np.testing.assert_allclose(values,0,atol=2e-15)
        shuffle=np.array([5,1,3,0,4,2])
        v,w=self.call(observations=self.edges[shuffle])
        np.testing.assert_array_equal(v,values[shuffle]);np.testing.assert_array_equal(w,warps[shuffle])
        transform=np.eye(4);transform[:3,:3]=cv2.Rodrigues(np.array([.07,-.03,.02]))[0]
        transform[:3,3]=[.1,-.2,.3]
        for changes in [dict(poses=self.poses@np.linalg.inv(transform)),
                        dict(log_gains=self.a+.2,biases=self.b+np.exp(self.a)*.01)]:
            v,w=self.call(**changes)
            np.testing.assert_allclose(v,values,atol=2e-15)
            np.testing.assert_allclose(w,warps,atol=1e-10)

    def test_complete_graph_equivalence(self):
        edges=np.array([[point,target] for target in range(1,4) for point in range(4)])
        rho=np.full(4,.25)
        v,w=self.call(hosts=np.zeros(4,dtype=int),observations=edges,inverse_depth=rho)
        old,warp=complete_residual(self.images,self.pixels,rho,self.poses,self.a,self.b,np.log(1000.))
        np.testing.assert_allclose(v,old.reshape(12,4),atol=1e-14)
        np.testing.assert_allclose(w,warp.reshape(12,4,2),atol=1e-10)

    def test_noncommuting_global_poses_opencv_oracle(self):
        poses=self.poses.copy()
        for pose,vector in zip(poses,[[.01,-.03,.005],[-.02,.02,.01],[.025,.01,-.015],[-.01,-.025,.02]]):
            pose[:3,:3]=cv2.Rodrigues(np.array(vector))[0]
        xyz=np.array([[-.3,-.4,4.],[.2,-.1,4.3],[.1,.35,3.8],[-.1,.6,4.1]])
        k=np.array([[1000.,0,359.5],[0,1000.,639.5],[0,0,1.]])
        pixels=[];rho=[]
        for point,host in enumerate(self.hosts):
            pose=poses[host]
            pixels.append(cv2.projectPoints(xyz[point:point+1],cv2.Rodrigues(pose[:3,:3])[0],pose[:3,3],k,None)[0].reshape(1,2))
            rho.append(1/(pose[:3,:3]@xyz[point]+pose[:3,3])[2])
        _,warps=self.call(pixels=np.array(pixels),inverse_depth=np.array(rho),poses=poses)
        oracle=[]
        for point,target in self.edges:
            pose=poses[target]
            oracle.append(cv2.projectPoints(xyz[point:point+1],cv2.Rodrigues(pose[:3,:3])[0],pose[:3,3],k,None)[0].reshape(1,2))
        np.testing.assert_allclose(warps,oracle,atol=1e-10)

    def test_bad_graph_or_included_support_rejected(self):
        off=self.pixels.copy();off[0,0,0]=-1
        behind=self.poses.copy();behind[0,2,3]=-10
        reflection=self.poses.copy();reflection[0,0,0]=-1
        unused=np.stack([*self.poses,np.eye(4)]);unused[-1,0,0]=2
        changes=[dict(hosts=self.hosts.astype(float)),dict(observations=self.edges.astype(float)),
                 dict(hosts=np.array([2,0,3,-1])),dict(observations=np.array([[0,4]])),
                 dict(observations=np.array([[0,2]])),dict(observations=self.edges[:2]),
                 dict(observations=np.vstack([self.edges,self.edges[0]])),dict(observations=np.empty((0,2),int)),
                 dict(pixels=off),dict(poses=behind),dict(poses=reflection),
                 dict(inverse_depth=np.array([0.,.25,.25,.25])),dict(log_gains=np.array([0.,1000.,0.,0.])),
                 dict(biases=np.array([-1.,0.,0.,0.])),dict(log_focal=1000.),
                 dict(log_gains=np.array([0.,np.nan,0.,0.])),
                 dict(images=np.concatenate([self.images,self.images[:1]]),poses=unused,
                      log_gains=np.r_[self.a,0.],biases=np.r_[self.b,0.])]
        for change in changes:
            with self.subTest(change=tuple(change)):
                with self.assertRaises(ValueError):self.call(**change)
