import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))


class ShortTrackObservabilityTests(unittest.TestCase):
    def test_local_counterexample_and_disconnection(self):
        from check_short_track_observability import check
        result=check()
        self.assertEqual(result["rank"],result["parameters"])
        self.assertLess(result["disconnected_rank"],result["parameters"])
        self.assertFalse(result["point_visible_first_and_last"])
