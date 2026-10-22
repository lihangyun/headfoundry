"""Candidate-only CLI status check;no network/weight/data access."""
from pathlib import Path
import json
import runpy
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))


class AnyCalibAssetEntry(unittest.TestCase):
    def test_public_lock_matches_fixed_installer(self):
        root=Path(__file__).resolve().parents[1]
        constants=runpy.run_path(str(root/'tools/acquire_anycalib_0323.py'),run_name='candidate_asset_constants')
        lock=json.loads((root/'examples/anycalib-edit-asset-lock.json').read_text())
        self.assertEqual(lock['model_id'],'anycalib_edit')
        self.assertEqual(lock['checkpoint']['name'],constants['NAME'])
        self.assertEqual(lock['checkpoint']['bytes'],constants['SIZE'])
        self.assertEqual(lock['checkpoint']['sha256'],constants['SHA'])
        self.assertEqual(lock['checkpoint']['url'],constants['URL'])
        self.assertEqual(lock['license_id'],'Apache-2.0')
        self.assertTrue(lock['no_fallback'])

    def test_worker_failure_cannot_exit_success(self):
        script=Path(__file__).resolve().parents[1]/'tools/acquire_anycalib_0323.py'
        for status,code in [('REJECT',1),('TECHNICAL_CHECK_PASSED',0)]:
            with self.subTest(status=status),patch.object(sys,'argv',[str(script)]),\
                 patch('pathlib.Path.mkdir'),patch('bounded_process.run',return_value={'status':status}),\
                 patch('builtins.print'),self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(script),run_name='__main__')
            self.assertEqual(stopped.exception.code,code)
