import unittest
from unittest.mock import patch
import numpy as np
from headfoundry.profile_fit import (fit_profile_step,envelope_edge,envelope_edges,
                                    envelope_edges_with_jacobian,project_with_basis_jacobian)


class ProfileFitTest(unittest.TestCase):
    def test_projection_basis_jacobian_and_invalid_geometry(self):
        v=np.array([[1.,.5,2],[-.5,1,3]])
        b=np.arange(18,dtype=float).reshape(2,3,3)/100
        p=np.array([[120.,3,20,.1],[0,110,30,-.1],[0,0,1,0]])
        uv,jac=project_with_basis_jacobian(v,b,p)
        for dimension in range(3):
            plus=np.c_[v+1e-5*b[:,:,dimension],np.ones(2)] @ p.T
            minus=np.c_[v-1e-5*b[:,:,dimension],np.ones(2)] @ p.T
            numeric=(plus[:,:2]/plus[:,2:]-minus[:,:2]/minus[:,2:])/2e-5
            np.testing.assert_allclose(jac[:,:,dimension],numeric,atol=1e-8)
        self.assertEqual(uv.shape,(2,2))
        for bad in (b[:1],np.full_like(b,np.nan)):
            with self.assertRaises(ValueError):project_with_basis_jacobian(v,bad,p)
        with self.assertRaises(ValueError):project_with_basis_jacobian(-v,b,p)

    def test_envelope_jacobian_matches_full_row_reprojection(self):
        v=np.array([[1.,0,2],[4,4,3],[-1,0,2],[-2,4,3]])
        b=np.arange(36,dtype=float).reshape(4,3,3)/100
        p=np.array([[100.,0,0,0],[0,100,0,0],[0,0,1,0]])
        edges=np.array([[0,1],[2,3]]);rows=[25.,65,90]
        for direction in (-1,1):
            support,jac=envelope_edges_with_jacobian(v,edges,p,rows,direction,b)
            for dimension in range(3):
                plus=envelope_edges(v+1e-5*b[:,:,dimension],edges,p,rows,direction)
                minus=envelope_edges(v-1e-5*b[:,:,dimension],edges,p,rows,direction)
                numeric=np.array([(a[2][0]-c[2][0])/2e-5 for a,c in zip(plus,minus)])
                np.testing.assert_allclose(jac[:,dimension],numeric,atol=1e-8)
            self.assertEqual(len(support),len(rows))
        _,jac=envelope_edges_with_jacobian(v,edges,p,[],1,b)
        self.assertEqual(jac.shape,(0,3))
        with self.assertRaises(ValueError):envelope_edges_with_jacobian(v,edges,p,[300],1,b)
        horizontal=v[:2].copy();horizontal[:,1]=0
        xbasis=np.zeros((2,3,1));xbasis[:,0,0]=1
        _,jac=envelope_edges_with_jacobian(horizontal,np.array([[0,1]]),p,[0],1,xbasis)
        np.testing.assert_allclose(jac,[[100/3]])
        xbasis[:,1,0]=1
        with self.assertRaises(ValueError):envelope_edges_with_jacobian(horizontal,np.array([[0,1]]),p,[0],1,xbasis)

    def test_batch_envelope_matches_independent_projected_segments(self):
        v=np.array([[1.,0,1],[4,4,2],[0,0,1],[0,4,2]])
        edges=np.array([[0,1],[2,3]])
        p=np.array([[100,0,0,0],[0,100,0,0],[0,0,1,0.]])
        for direction in (-1,1):
            batch=envelope_edges(v,edges,p,[0,50,100,200,250],direction)
            for row,item in zip([0,50,100,200,250],batch):
                if row==250:self.assertIsNone(item);continue
                ids,w,pixel=item
                h=p @ np.r_[w @ v[ids],1]
                np.testing.assert_allclose(h[:2]/h[2],pixel)
                expected=0. if direction==-1 else 100.+row/2
                np.testing.assert_allclose(pixel,[expected,row])
            self.assertEqual(envelope_edges(v,edges,p,[],direction),[])
        for bad in ([[1]], [np.nan]):
            with self.assertRaises(ValueError):envelope_edges(v,edges,p,bad,1)

    def test_continuous_fit_projects_once_for_many_rows(self):
        v=np.array([[0,0,1],[.1,0,1],[0,.1,1],[.1,.1,1.]])
        f=np.array([[0,2,1],[1,2,3]])
        p=np.array([[[100,0,0,0],[0,100,0,0],[0,0,1,0]]])
        rows=np.array([[11,0],[11,5],[11,10]])
        with patch('headfoundry.profile_fit.envelope_edges', wraps=envelope_edges) as batch:
            fit_profile_step(v,f,p,[rows],[1],.001,continuous=True)
        self.assertEqual(batch.call_count,1)
        np.testing.assert_array_equal(batch.call_args.args[3],rows[:,1])

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
        excluded,excluded_report=fit_profile_step(v,f,p,[np.array([[11,0],[11,10]])],[1],
                                                  continuous=True,contour_face_mask=np.zeros(2,bool))
        np.testing.assert_array_equal(excluded,v)
        self.assertEqual(excluded_report['selected_per_view'],[0])
        fixed,fixed_report=fit_profile_step(v,f,p,[np.array([[11,0],[11,10]])],[1],.001,
                                            continuous=True,protected_vertices=[0,1])
        np.testing.assert_array_equal(fixed[:2],v[:2])
        self.assertGreater(fixed_report['maximum_displacement'],0)
        with self.assertRaises(ValueError):
            fit_profile_step(v,f,p,[np.array([[11,0]])],[1],protected_vertices=[.5])

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
