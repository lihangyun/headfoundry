import unittest

import numpy as np

from headfoundry.synthetic_identity import paired_controls, synthesize


class SyntheticIdentityTests(unittest.TestCase):
    def test_bilateral_pairs_and_deterministic_safe_sampling(self):
        names = ["cheek/l-volume-decr.target", "cheek/l-volume-incr.target",
                 "cheek/r-volume-decr.target", "cheek/r-volume-incr.target",
                 "mouth/mouth-open-decr.target", "mouth/mouth-open-incr.target"]
        deltas = np.zeros((len(names), 4, 3))
        deltas[:4, :, 2] = [[-.01], [.01], [-.01], [.01]]
        controls = paired_controls(names, deltas)
        self.assertEqual([item.name for item in controls], ["cheek/volume"])
        vertices = np.asarray([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
        faces = np.asarray([[0, 1, 2], [0, 2, 3]])
        first = synthesize(vertices, faces, controls, count=3, seed=7, active_controls=1)
        second = synthesize(vertices, faces, controls, count=3, seed=7, active_controls=1)
        np.testing.assert_allclose(first[0], second[0])
        np.testing.assert_allclose(first[1], second[1])
        self.assertTrue(all(item["normal_reversals"] == 0 for item in first[2]))


if __name__ == "__main__":
    unittest.main()
