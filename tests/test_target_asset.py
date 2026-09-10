import unittest
import json, tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
from headfoundry.target_asset import parse_target


class TargetAssetTests(unittest.TestCase):
    def test_explicit_lock_mapping_and_digest_rejection(self):
        from headfoundry.manifest import sha256_file
        from tools.prepare_makehuman_targets import main
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'base.obj';target=root/'shape.target'
            base.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\n')
            target.write_text('1 .1 .2 .3\n')
            base_lock=root/'base.json';lock=root/'targets.json'
            base_lock.write_text(json.dumps({'license_id':'CC0-1.0','revision':'test','sha256':{'base.obj':sha256_file(base)}}))
            lock.write_text(json.dumps({'license_id':'CC0-1.0','revision':'test','base_asset_lock':str(base_lock),'sha256':{'shape.target':sha256_file(target)}}))
            output=root/'out'
            with patch('sys.argv',['prepare',str(root),str(root),str(output),'--lock',str(lock)]), patch('tools.prepare_makehuman_targets.extract_head',return_value=(np.zeros((3,3)),np.array([[0,1,2]]),np.array([2,1,0]))):
                main()
                with np.load(output/'targets.npz') as data:
                    np.testing.assert_allclose(data['deltas'][0],[[0,0,0],[.1,-.2,-.3],[0,0,0]])
                target.write_text('1 .9 .2 .3\n')
                with self.assertRaisesRegex(ValueError,'digest mismatch'):main()

    def test_sparse_ids_zero_fill_and_comments(self):
        result=parse_target('# data\n2 .1 -.2 0\n0 0 0 0 # valid zero\n',4)
        np.testing.assert_allclose(result,[[0,0,0],[0,0,0],[.1,-.2,0],[0,0,0]])

    def test_fail_closed_invalid_targets(self):
        for text in ['', '# only comment','0 1 2','0 1 2 3\n0 3 2 1','-1 0 0 0','4 0 0 0','1 nan 0 0','1.5 0 0 0']:
            with self.assertRaises(ValueError):parse_target(text,4)
        for count in [0,-1,True,2.5]:
            with self.assertRaises(ValueError):parse_target('0 0 0 0',count)
