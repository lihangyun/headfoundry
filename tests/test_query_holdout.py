import hashlib
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from short_track_camera import split_observations


class QueryHoldoutTest(unittest.TestCase):
    def test_legacy_split_is_unchanged_and_supplied_query_cannot_be_held(self):
        frames = [10,20,30,40]
        track = [(frame,7) for frame in frames]
        data = {'frames':frames, 'xy':{vertex:np.array([vertex[0]+.25,17.5]) for vertex in track}}
        original = min(track, key=lambda v:hashlib.sha256(f'300/hold/{v[0]}/{v[1]}'.encode()).digest())
        train, held = split_observations(data,[track])
        self.assertTrue(np.array_equal(held,[[frames.index(original[0]),0,*data['xy'][original]]]))
        expected = [[frames.index(v[0]),0,*data['xy'][v]] for v in track if v!=original]
        self.assertTrue(np.array_equal(train,expected))
        eligible = set(track)-{original}
        train, held = split_observations(data,[track],eligible)
        self.assertNotEqual(int(held[0,0]),frames.index(original[0]))
        self.assertTrue(any(int(row[0])==frames.index(original[0]) for row in train))
        with self.assertRaises(ValueError):
            split_observations(data,[track],set())
