import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from acquire_geocalib_0314 import REF,URL,validate_plan,verify_locked_asset

class GeoCalibAssetEntryTest(unittest.TestCase):
    def test_frozen_hash_is_required_and_bytes_fail_closed(self):
        lock=json.loads((Path(__file__).resolve().parents[1]/'examples/geocalib-pinhole.asset-lock.json').read_text())
        bad=copy.deepcopy(lock);del bad['checkpoint']['sha256']
        with self.assertRaises(ValueError):verify_locked_asset(bad,Path(__file__))
        bad=copy.deepcopy(lock);del bad['weight_license']
        with self.assertRaises(ValueError):verify_locked_asset(bad,Path(__file__))
        with self.assertRaises(ValueError):verify_locked_asset(lock,Path(__file__))

    def test_exact_selection_and_missing_rights_reject(self):
        plan=dict(source_ref=REF,rights=dict(code_license='Apache-2.0',weight_license='CC-BY-4.0',
            code_notice=dict(sha256='a'*64,url=f'https://raw.githubusercontent.com/cvg/GeoCalib/{REF}/LICENSE'),
            weight_notice=dict(sha256='b'*64,url=f'https://raw.githubusercontent.com/cvg/GeoCalib/{REF}/LICENSE-WEIGHTS')),
            checkpoint=dict(id=191236355,name='geocalib-pinhole.tar',size=116074121,browser_download_url=URL))
        validate_plan(plan)
        variants=[]
        for field in ['code_license','weight_license']:
            bad=copy.deepcopy(plan);del bad['rights'][field];variants.append(bad)
        bad=copy.deepcopy(plan);bad['checkpoint']['name']='geocalib-distorted.tar';variants.append(bad)
        bad=copy.deepcopy(plan);bad['source_ref']='main';variants.append(bad)
        bad=copy.deepcopy(plan);del bad['rights']['weight_notice']['sha256'];variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):validate_plan(bad)
