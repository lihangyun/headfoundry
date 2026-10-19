import unittest

import cv2
import numpy as np

from tools.parallax_initialization_0221 import homography_fraction, select_initial_pair


class ParallaxInitializationTests(unittest.TestCase):
    def test_real_nonplanar_projection_beats_more_planar_support(self):
        rng = np.random.default_rng(221)
        points = rng.uniform([-1, -.6, 0], [1, .6, 1.2], (200, 3))
        rotation, _ = cv2.Rodrigues(np.array([0., .15, 0.]))
        def observations(world):
            first = world + [0, 0, 4]
            second = world @ rotation.T + [.4, 0, 4]
            return [p[:, :2] / p[:, 2:3] * 900 + [360, 640] for p in (first, second)]
        nonplanar = homography_fraction(*observations(points))
        points[:, 2] = .4
        planar = homography_fraction(*observations(points))
        self.assertGreater(planar, .99)
        self.assertLess(nonplanar, .8)
        plane = {"image_ids": [1, 2], "inliers": 400, "homography_fraction": planar}
        depth = {"image_ids": [2, 3], "inliers": 200, "homography_fraction": nonplanar}
        self.assertEqual(select_initial_pair([plane, depth])["image_ids"], [2, 3])
        with self.assertRaises(ValueError):
            select_initial_pair([plane])


if __name__ == "__main__":
    unittest.main()
