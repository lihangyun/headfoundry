import unittest
import numpy as np
from headfoundry.profile_fit import fit_profile_step,envelope_edge


class ProfileFitTest(unittest.TestCase):
    def test_perspective_correct_continuous_edge_and_horizontal(self):
        v=np.array([[1.,0,1],[4,4,2]])
        p=np.array([[100,0,0,0],[0,100,0,0],[0,0,1,0.]])
        ids,w,pixel=envelope_edge(v,np.array([[0,1]]),p,100,1)
        np.testing.assert_allclose(w,[2/3,1/3])
        h=p@np.r_[w@v[ids],1]
        np.testing.assert_allclose(h[:2]/h[2],pixel)
        self.assertIsNone(envelope_edge(v,np.array([[0,1]]),p,300,1))
        v[:,1]=0
        _,w,pixel=envelope_edge(v,np.array([[0,1]]),p,0,-1)
        np.testing.assert_allclose(pixel,[100,0]);np.testing.assert_array_equal(w,[1,0])

    def test_bounded_move_and_missing_rows(self):
        v=np.array([[0,0,1],[.1,0,1],[0,.1,1],[.1,.1,1.]])
        f=np.array([[0,2,1],[1,2,3]])
        p=np.array([[[100,0,0,0],[0,100,0,0],[0,0,1,0]]])
        result,report=fit_profile_step(v,f,p,[np.array([[11,0],[11,10]])],[1],.001)
        self.assertGreater(report['maximum_displacement'],0)
        self.assertLessEqual(report['maximum_displacement'],.001+1e-12)
        unchanged,_=fit_profile_step(v,f,p,[np.array([[11,100]])],[1])
        np.testing.assert_array_equal(unchanged,v)

    def test_frontal_ray_constraint_survives_bounded_step(self):
        v=np.array([[0,0,1],[.1,0,1],[0,.1,1],[.1,.1,1.]])
        f=np.array([[0,2,1],[1,2,3]])
        front=np.array([[100,0,0,0],[0,100,0,0],[0,0,1,0.]])
        side=front.copy();side[0,3]=-20
        result,report=fit_profile_step(v,f,side[None],[np.array([[-9,0],[-9,10]])],[1],.001,
                                       frontal_projection=front)
        def uv(mesh):
            h=np.c_[mesh,np.ones(len(mesh))]@front.T
            return h[:,:2]/h[:,2:]
        self.assertGreater(report['maximum_displacement'],0)
        self.assertLessEqual(report['maximum_displacement'],.001+1e-12)
        np.testing.assert_allclose(uv(result),uv(v),atol=1e-10)
        continuous,continuous_report=fit_profile_step(v,f,side[None],[np.array([[-9,5]])],[1],.001,
                                                      frontal_projection=front,continuous=True)
        self.assertEqual(continuous_report['selected_per_view'],[1])
        self.assertGreater(continuous_report['maximum_displacement'],0)
        np.testing.assert_allclose(uv(continuous),uv(v),atol=1e-10)
        with self.assertRaises(ValueError):
            fit_profile_step(v,f,side[None],[np.array([[-9,0]])],[1],frontal_projection=front*0)
