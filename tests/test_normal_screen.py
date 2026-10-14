import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experiment_0209 import normal_errors, material_samples
from headfoundry.raster import render


class NormalScreenTests(unittest.TestCase):
    def test_invalid_observations_are_not_dropped(self):
        truth = np.tile([0., 0., -1.], (4, 1))
        prediction = np.array([[0, 0, -2.], [0, 0, 1.], [np.nan, 0, 0], [0, 0, 0]])
        error, valid = normal_errors(prediction, truth, np.ones(4, bool))
        np.testing.assert_allclose(error, [0, 180, 180, 180])
        np.testing.assert_array_equal(valid, [True, True, False, False])
        error, valid = normal_errors(prediction[:1], truth[:1], [False])
        self.assertEqual(error[0], 180)
        self.assertFalse(valid[0])

    def test_perspective_material_sampling_reprojects_pixel_centers(self):
        v = np.array([[-2., -2., 3.], [2., -2., 4.], [0., 2., 5.]])
        f = np.array([[0, 1, 2]])
        e = np.c_[np.eye(3), np.zeros(3)]
        k = np.array([[40., 0, 32.], [0, 40., 32.], [0, 0, 1.]])
        _, _, hit = render(v, f, e, k, (64, 64))
        y, x, ids, weights = material_samples(v, f, e, k, hit)
        self.assertGreater(len(x), 20)
        xyz = np.einsum("ni,nij->nj", weights, v[f[ids]])
        h = xyz @ k.T
        np.testing.assert_allclose(h[:, :2]/h[:, 2:], np.c_[x+.5, y+.5], atol=1e-12)
        np.testing.assert_allclose(weights.sum(1), 1.)


if __name__ == "__main__":
    unittest.main()
