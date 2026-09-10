import unittest
import numpy as np
from headfoundry.target_asset import parse_target


class TargetAssetTests(unittest.TestCase):
    def test_sparse_ids_zero_fill_and_comments(self):
        result=parse_target('# data\n2 .1 -.2 0\n0 0 0 0 # valid zero\n',4)
        np.testing.assert_allclose(result,[[0,0,0],[0,0,0],[.1,-.2,0],[0,0,0]])

    def test_fail_closed_invalid_targets(self):
        for text in ['', '# only comment','0 1 2','0 1 2 3\n0 3 2 1','-1 0 0 0','4 0 0 0','1 nan 0 0','1.5 0 0 0']:
            with self.assertRaises(ValueError):parse_target(text,4)
        for count in [0,-1,True,2.5]:
            with self.assertRaises(ValueError):parse_target('0 0 0 0',count)
