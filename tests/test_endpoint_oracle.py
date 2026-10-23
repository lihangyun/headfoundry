import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from endpoint_oracle import oracle_controls

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
