import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from anycalib_adapter import native_intrinsics


class AnyCalibCoordinates(unittest.TestCase):
    def test_edge_to_native_preserves_two_focals(self):
        np.testing.assert_array_equal(native_intrinsics([1200,1250,347.5,631.5]),
            [[1200,0,347],[0,1250,631],[0,0,1]])
        for params in ([0,1,2,3],[-1,2,3,4],[1,np.inf,2,3],[1,2,np.nan,3],[1,2,3]):
            with self.assertRaises(ValueError):native_intrinsics(params)
