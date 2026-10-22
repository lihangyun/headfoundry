import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from check_bootstapir_0307 import validate_lock


class SoftwareEntryLockTest(unittest.TestCase):
    def test_public_lock_and_transcription_or_rights_rejection_without_assets(self):
        lock = json.loads((ROOT/'examples/bootstapir-0307.asset-lock.json').read_text())
        validate_lock(lock)
        corrupt = copy.deepcopy(lock)
        corrupt['weights_sha256'] += '0'
        with self.assertRaises(ValueError):
            validate_lock(corrupt)
        corrupt = copy.deepcopy(lock)
        corrupt['commercial_use'] = False
        with self.assertRaises(ValueError):
            validate_lock(corrupt)
