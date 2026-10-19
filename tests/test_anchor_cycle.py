import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from anchor_cycle_localization_0223 import closed_observations


class AnchorCycleTests(unittest.TestCase):
    def test_id_join_and_eligibility_do_not_depend_on_input_order_or_3d(self):
        ids = np.array([20, 21, 22, 23])
        direct = np.array([[0.,0], [10,10], [20,20], [30,30]])
        sequential_ids = np.array([23, 20, 22, 21])
        sequential = np.array([[30.,30], [.5,0], [21,20], [10,10]])
        rows, distances, keep = closed_observations(ids, direct, np.array([True,False,True,True]), sequential_ids, sequential)
        np.testing.assert_array_equal(rows, [3,0])
        np.testing.assert_array_equal(keep, [True,True,False,False])
        np.testing.assert_allclose(distances, [0,.5,1,0])

    def test_duplicate_identity_rejected(self):
        with self.assertRaises(ValueError):
            closed_observations(np.array([1,1]), np.zeros((2,2)), np.ones(2, bool), np.array([1]), np.zeros((1,2)))


if __name__ == "__main__":
    unittest.main()
