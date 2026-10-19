import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "tools"))
from direct_video_matches_0224 import component_gate, chronological_adjacent_counts


class DirectVideoGraphTests(unittest.TestCase):
    def test_noncontiguous_image_ids_and_transitive_component(self):
        self.assertEqual(component_gate([2,5,9,12],[(5,9),(2,5)]),[2,5,9])

    def test_no_edges_does_not_manufacture_connectivity(self):
        self.assertEqual(component_gate([2,5,9],[]),[2])

    def test_database_ids_are_not_frame_order_and_pairs_are_normalized(self):
        names = {1:'frame-000000.png',2:'frame-000024.png',3:'frame-000012.png'}
        counts = {(1,3):71,(2,3):83,(1,2):2}
        self.assertEqual(chronological_adjacent_counts(names,counts),[71,83])


if __name__ == "__main__":
    unittest.main()
