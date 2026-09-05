import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from headfoundry.bundle import project
from headfoundry.dense_camera import refine


class DenseCameraTests(unittest.TestCase):
    def fixture(self):
        x,y=np.meshgrid(np.linspace(-.8,.8,5),np.linspace(-.8,.8,5))
        shape=np.c_[x.ravel(),y.ravel(),(-.2*np.exp(-3*(x*x+y*y))).ravel()]
        faces=[]
        for row in range(4):
            for col in range(4):
                a=row*5+col;faces.extend([[a,a+1,a+5],[a+1,a+6,a+5]])
        protected=np.array([i for i in range(25) if i//5 in (0,4) or i%5 in (0,4)])
        k=np.tile([[900.,0,500],[0,900,500],[0,0,1]],(3,1,1))
        r=Rotation.from_rotvec([[0,0,0],[0,-.4,0],[0,.4,0]]).as_matrix()
        t=np.tile([0.,0.,5.],(3,1)); e=np.concatenate([r,t[:,:,None]],axis=2)
        obs=project(shape,r,t,k)
        held=np.zeros((3,25),bool);held[1,12]=True;held[2,13]=True
        return shape,obs,k,e,np.array(faces),protected,~held,held

    def test_validation_does_not_change_fit_or_masks(self):
        args=list(self.fixture());before=args[-2].copy()
        expected=refine(*args,iterations=2)
        args[1]=args[1].copy();args[1][args[-1]]+=100
        corrupted=refine(*args,iterations=2)
        np.testing.assert_allclose(expected['shape'],corrupted['shape'],atol=1e-10)
        np.testing.assert_allclose(expected['extrinsics'],corrupted['extrinsics'],atol=1e-10)
        np.testing.assert_array_equal(args[-2],before)
        self.assertLess(expected['validation_p95_px'],.01)
        self.assertGreater(corrupted['validation_p95_px'],100)
