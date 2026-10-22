import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))


class CycleConsensusTests(unittest.TestCase):
    def test_bridge_ambiguity_and_structural_limits(self):
        from cycle_consensus import select_tracks
        tracks = [tuple((f, p) for f in range(4)) for p in range(2)]
        edges = {tuple(pair) for track in tracks for pair in itertools.combinations(track, 2)}
        edges.add(((0, 0), (1, 1)))
        selected, report = select_tracks(edges)
        self.assertEqual(set(selected), set(tracks))
        self.assertEqual(report['selected_observations'], 8)
        ambiguous = [((0, 0), (1, 0), (2, 0)), ((0, 0), (1, 0), (3, 0))]
        edges = {tuple(pair) for track in ambiguous for pair in itertools.combinations(track, 2)}
        self.assertEqual(select_tracks(edges)[0], [])
        # Even a wrong semantic identity can be a complete clique;never certify truth here.
        wrong = ((0, 0), (1, 0), (2, 1))
        self.assertEqual(select_tracks(set(itertools.combinations(wrong, 2)))[0], [wrong])
        self.assertEqual(select_tracks(set())[0], [])
        with self.assertRaises(ValueError):
            select_tracks({((0, 0), (0, 1))})
