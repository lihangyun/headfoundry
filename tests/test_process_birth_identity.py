"""Generic resource-monitor regression for stale Windows parent process IDs."""
import sys
from pathlib import Path
import unittest
import os
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from bounded_process import descendant_ids, run


class ProcessBirthIdentity(unittest.TestCase):
    def test_stale_parent_links_are_not_descendants(self):
        rows = [(10, 1, 100), (20, 10, 50), (21, 20, 110),
                (30, 10, 101), (31, 30, 102)]
        self.assertEqual(descendant_ids(rows, 10, 100), {10, 30, 31})

    def test_exited_launcher_still_has_new_children(self):
        self.assertEqual(descendant_ids([(30, 10, 101), (31, 30, 102)], 10, 100), {10, 30, 31})

    @unittest.skipUnless(os.name == "nt", "Windows process budget")
    def test_live_worker_measurement_and_time_limit(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root / "assets/private", prefix="process-control-") as tmp:
            folder = Path(tmp)
            command = [sys.executable, "-c", "import time; time.sleep(0.4)"]
            good = run(command, root, os.environ.copy(), folder / "good.log", folder / "good.json", 5, 1024**3)
            self.assertEqual(good["status"], "TECHNICAL_CHECK_PASSED")
            self.assertGreater(good["peak_working_set"], 0)
            limited = run(command, root, os.environ.copy(), folder / "limit.log", folder / "limit.json", .05, 1024**3)
            self.assertEqual(limited["status"], "REJECT")
            self.assertIn("budget exceeded", limited["failure"])
