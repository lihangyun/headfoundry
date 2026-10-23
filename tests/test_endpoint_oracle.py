import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from endpoint_oracle import oracle_controls
from check_dense_grid_contract import bilinear

class EndpointOracleTest(unittest.TestCase):
    def test_nondyadic_pixel_roundoff_is_not_physical_error(self):
        q=np.column_stack((np.linspace(.1,700,257),np.linspace(.7,1200,257)))
        self.assertTrue(np.any(np.linalg.norm(q+[40,0]-q,axis=1)!=40))
        report=oracle_controls(q)
        self.assertEqual(report['zero_max_px'],0)
        self.assertGreater(report['wrong40_max_roundoff_px'],0)
        self.assertLessEqual(report['wrong40_max_roundoff_px'],report['roundoff_bound_px'])
        self.assertLess(report['roundoff_bound_px'],1e-10)

    def test_invalid_or_empty_oracle_rejected(self):
        for q in (np.empty((0,2)),np.array([[np.nan,0.]]),np.zeros((3,3))):
            with self.assertRaises(ValueError):oracle_controls(q)

    def test_cycle_closure_does_not_certify_physical_endpoints(self):
        # Independent visible affine truth;no estimator,clinical points or masks.
        import json
        y,x=np.mgrid[:96,:128]
        grid=np.stack((x,y),axis=-1).astype(float)
        a=np.diag([1.25,.8]);inverse=np.linalg.inv(a);t=np.array([8.,12.])
        q=np.stack(np.meshgrid(np.linspace(24,64,12),np.linspace(24,56,8)),axis=-1).reshape(-1,2)
        forward=grid@a.T+t-grid
        backward=(grid-t)@inverse.T-grid
        reports=[]
        for ef,eb,expected_cycle,expected_count in (
                ([0.,0.],[0.,0.],0.,96),
                ([1.,0.],[1.,0.],1.8,0),
                ([16.,0.],[-12.8,0.],0.,96)):
            with self.subTest(forward_bias=ef,backward_bias=eb):
                target=q+bilinear(forward+ef,q,[128,96])
                returned=target+bilinear(backward+eb,target,[128,96])
                self.assertTrue(np.all((returned>=0)&(returned<=[127,95])))
                errors=np.linalg.norm(target-(q@a.T+t),axis=1)
                back_errors=np.linalg.norm(returned-(target-t)@inverse.T,axis=1)
                closure=np.linalg.norm(returned-q,axis=1)
                np.testing.assert_allclose(errors,np.linalg.norm(ef),atol=1e-10,rtol=0)
                np.testing.assert_allclose(back_errors,np.linalg.norm(eb),atol=1e-10,rtol=0)
                np.testing.assert_allclose(closure,expected_cycle,atol=1e-10,rtol=0)
                count=int(np.count_nonzero(closure<=.75))
                self.assertEqual(count,expected_count)
                reports.append({'forward_p95_px':float(np.percentile(errors,95)),
                    'backward_p95_px':float(np.percentile(back_errors,95)),
                    'cycle_p95_px':float(np.percentile(closure,95)),
                    'cycle_admits':count,'population':len(q)})
        first=np.arange(96)<48;second=~first
        self.assertEqual((int(first.sum()),int(second.sum()),int((first&second).sum())),(48,48,0))
        print('Independent cycle witnesses: '+json.dumps(reports))

    def test_pixel_budget_is_not_a_metric_depth_guarantee(self):
        focal,baseline,depth=1200.,100.,1000. # owned rectified geometry,mm
        disparity=focal*baseline/depth
        reconstructed=focal*baseline/(disparity-2.)
        self.assertEqual(disparity,120.)
        self.assertLess(2.,3.)
        self.assertAlmostEqual(reconstructed-depth,16.9491525423729,places=10)
        self.assertGreater(reconstructed-depth,2.)
