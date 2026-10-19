import sys
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from semantic_material_stability_0242 import forbid_patient_data, error_summary, PARENT, PILOT, TASK


class SemanticMaterialFixtureTests(unittest.TestCase):
    def test_generic_only_guard_and_complete_error_summary(self):
        for path in (TASK, PARENT / 'generic-bindings.npz', PARENT / 'controls.json', PARENT / 'generic-neutral-only.png'):
            forbid_patient_data(path)
        for path in (PILOT / 'manifest.json', PARENT / 'frame-000000.png',
                PARENT / 'fit/numerical-result.npz', ROOT / 'outside.STL'):
            with self.assertRaises(PermissionError):
                forbid_patient_data(path)
        errors = np.r_[np.zeros(9), 100.]
        result = error_summary(errors)
        self.assertEqual(result['count'], 10)
        self.assertAlmostEqual(result['p95_px'], 55.)
        self.assertEqual(result['maximum_px'], 100.)
        for bad in ([1, np.nan], [-1], []):
            with self.assertRaises(ValueError):
                error_summary(bad)
