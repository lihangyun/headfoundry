import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from headfoundry.template_pose import fit_template_pose


class TemplatePoseTest(unittest.TestCase):
    def test_known_pose_and_invalid_inputs(self):
        points=np.array([[-1,-1,0],[1,-1,0],[-.5,.5,-.4],[.5,.5,-.4],[0,0,-.8],[0,1,.2]])
        k=np.array([[1000.,0,500],[0,1000,500],[0,0,1]])
        truth=np.array([.08,-.6,.02,.1,-.2,6.])
        initial=np.array([0,-.5,0,0,0,6.])
        bounds=(initial-[.3,.3,.3,1,1,2],initial+[.3,.3,.3,1,1,2])
        r=Rotation.from_rotvec(truth[:3]).as_matrix()
        h=(points@r.T+truth[3:])@k.T;pixels=h[:,:2]/h[:,2:]
        original=points.copy()
        e,report=fit_template_pose(points,pixels,k,initial,bounds)
        np.testing.assert_allclose(e,np.column_stack([r,truth[3:]]),atol=1e-6)
        np.testing.assert_array_equal(points,original)
        self.assertLess(max(report['fit_errors_px']),1e-5)
        self.assertEqual(report['status'],'UNVERIFIED')
        for bad_points,bad_pixels in [(points*0,pixels),(points,pixels*0),(points*np.nan,pixels)]:
            with self.assertRaises(ValueError):fit_template_pose(bad_points,bad_pixels,k,initial,bounds)
        bad=k.copy();bad[0,0]=-1
        with self.assertRaises(ValueError):fit_template_pose(points,pixels,bad,initial,bounds)
