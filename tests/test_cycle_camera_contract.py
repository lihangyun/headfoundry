from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))


class CycleCameraContractTests(unittest.TestCase):
    def test_corrupted_short_tracks_recover_unknown_cameras_without_held_fit(self):
        from check_cycle_camera_contract import check
        base = Path(__file__).resolve().parents[1]/'tmp'
        with tempfile.TemporaryDirectory(dir=base) as folder:
            path = Path(folder).resolve()
            self.assertTrue(path.is_relative_to(base.resolve()))
            result = check(path/'control')
            self.assertEqual(result['status'], 'TECHNICAL_CHECK_PASSED')
            self.assertEqual(result['selected_tracks'], 141)
            self.assertEqual(result['purity'], 1.)
            self.assertTrue(result['proper_cameras'])
            self.assertLess(result['held_GT_p95_px'], 1.)

