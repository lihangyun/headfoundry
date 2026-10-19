import unittest

import numpy as np

from tools.measure_real_profiles_0218 import color_boundary


class RealProfileObservationTests(unittest.TestCase):
    def test_subpixel_boundary_and_detached_color_noise(self):
        rgb = np.full((5, 10, 3), 100.)
        rgb[:, :, 0] += np.array([20, 16, 12, 8, 4, -4, -8, -12, -16, -20])
        rgb[0, 9, 0] = 120  # Detached one-pixel island must not move the face edge.
        result = color_boundary(rgb, (0, 0, 10, 5), 1)
        np.testing.assert_allclose(result[:, 0], 5.)
        np.testing.assert_allclose(result[:, 1], np.arange(5) + .5)
        mirrored = color_boundary(rgb[:, ::-1], (0, 0, 10, 5), -1)
        np.testing.assert_allclose(mirrored, result)

    def test_missing_or_clipped_observation_rejected(self):
        for rgb in (np.zeros((4, 8, 3)), np.full((4, 8, 3), [200, 100, 80])):
            with self.assertRaises(ValueError):
                color_boundary(rgb, (0, 0, 8, 4), 1)


if __name__ == "__main__":
    unittest.main()
