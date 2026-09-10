import unittest
import numpy as np
from headfoundry.target_fit import fit_target_points


class TargetFitTests(unittest.TestCase):
    def fixture(self):
        prior=np.array([[-.3,0,3],[.2,.2,3.2],[0,-.3,2.8]])
        delta=np.array([[[.2,0,.05],[0,.1,0],[-.1,0,.1]]])
        k=np.diag([500.,500.,1.]);p=np.array([k@np.c_[np.eye(3),[0,0,0]],k@np.c_[np.eye(3),[-.5,0,0]]])
        points=prior+.3*delta[0];h=np.einsum('vij,nj->vni',p,np.c_[points,np.ones(3)])
        return prior,delta,p,h[:,:,:2]/h[:,:,2:],np.ones((2,3),bool),np.full((2,3),3.)

    def test_known_shape_and_explicit_exclusion(self):
        args=list(self.fixture());args[4][1,2]=False;args[3][1,2]=np.nan;args[5][1,2]=np.nan
        weights,report=fit_target_points(*args,regularization=0)
        np.testing.assert_allclose(weights,[.3],atol=1e-6)
        self.assertEqual(report['status'],'UNVERIFIED');self.assertEqual(report['eligible_observations'],5)
        self.assertLess(report['after']['mean_error_px'],1e-5)
        args[3][1,2]=1e9
        second,_=fit_target_points(*args,regularization=0)
        np.testing.assert_allclose(weights,second,atol=1e-10)

    def test_reject_invalid_and_enforce_bound(self):
        args=list(self.fixture());weights,report=fit_target_points(*args,maximum_weight=.1,regularization=0)
        self.assertLessEqual(weights[0],.1);self.assertEqual(report['active_bounds'],[1])
        for replacement in [0,np.nan,-1]:
            bad=list(self.fixture());bad[5][0,0]=replacement
            with self.assertRaises(ValueError):fit_target_points(*bad)
        bad=list(self.fixture());bad[4][:]=False
        with self.assertRaises(ValueError):fit_target_points(*bad)
        bad=list(self.fixture());bad[0][:,2]=-3
        with self.assertRaises(ValueError):fit_target_points(*bad)
        bad=list(self.fixture());bad[2][0,0]=0
        with self.assertRaises(ValueError):fit_target_points(*bad)

    def test_supplied_uncertainty_changes_influence(self):
        args=list(self.fixture());prior,delta,p=args[:3]
        for view,weight in enumerate([.1,.4]):
            points=prior+weight*delta[0];h=np.c_[points,np.ones(3)]@p[view].T
            args[3][view]=h[:,:2]/h[:,2:]
        args[5][0]=1;args[5][1]=10
        first,_=fit_target_points(*args,regularization=0)
        args[5][0]=10;args[5][1]=1
        second,_=fit_target_points(*args,regularization=0)
        self.assertLess(first[0],.15);self.assertGreater(second[0],.35)
