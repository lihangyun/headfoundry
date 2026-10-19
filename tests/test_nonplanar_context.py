import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from headfoundry.camera import project
from scan_motion_truth_0230 import look_at_origin
from nonplanar_context_0231 import fit_context_fundamental,symmetric_line_errors


class NonplanarContextTests(unittest.TestCase):
    def test_context_only_fit_and_independent_known_measurements(self):
        points=np.random.default_rng(231).uniform(-.8,.8,(120,3))
        k=np.array([[1000.,0,360],[0,1000.,640],[0,0,1.]])
        a=project(k@look_at_origin([0,0,6]),points)
        b=project(k@look_at_origin([1.,-.4,5.9]),points)
        matrix,_,report=fit_context_fundamental(a[:60],b[:60])
        self.assertEqual(report['status'],'TECHNICAL_CHECK_PASSED')
        self.assertLess(symmetric_line_errors(matrix,a[60:],b[60:]).max(),1e-3)
        self.assertGreater(np.percentile(symmetric_line_errors(matrix,a[60:],b[60:]+[0,20]),95),3)

    def test_unspread_context_fails_closed(self):
        with self.assertRaises(ValueError):
            fit_context_fundamental(np.ones((12,2)),np.ones((12,2)))


if __name__=='__main__':
    unittest.main()
