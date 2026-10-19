import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gradient_profile_0243 import gradient_profile, known_boundary_fixture


class GradientProfileTests(unittest.TestCase):
    def test_fixed_noisy_mirrored_subpixel_boundaries(self):
        for direction in (-1, 1):
            rgb, truth = known_boundary_fixture(direction)
            for sigma in (.75, 1., 1.25):
                curve, strength = gradient_profile(rgb, (0, 0, 190, 213), sigma)
                errors = abs(curve[:, 0]-truth[:, 0])
                self.assertLessEqual(np.percentile(errors, 95), 1.)
                self.assertLessEqual(errors.max(), 2.)
                self.assertTrue((strength >= 2).all())
                np.testing.assert_array_equal(curve[:, 1], truth[:, 1])

    def test_missing_clipped_or_unregistered_measurements_fail_closed(self):
        for rgb, box, sigma in [(np.zeros((8, 8, 3)), (0, 0, 8, 8), 1.),
                (np.zeros((8, 8, 3)), (-1, 0, 8, 8), 1.),
                (np.zeros((8, 8, 3)), (0, 0, 8, 8), 2.)]:
            with self.assertRaises(ValueError):
                gradient_profile(rgb, box, sigma)
