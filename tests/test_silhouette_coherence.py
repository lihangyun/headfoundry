"""Generic interval/known-camera controls,not reconstruction acceptance."""
from pathlib import Path
import sys
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from check_silhouette_focal_0254 import arc_samples, coherence, self_check
from scan_motion_truth_0230 import look_at_origin


class SilhouetteCoherenceTests(unittest.TestCase):
    def test_holes_rigid_cube_negative_camera_and_scale_gauge(self):
        self.assertTrue(all(self_check().values()))
        vertices = np.array([[x, y, z] for x in (-1., 1.)
            for y in (-1., 1.) for z in (-1., 1.)])
        k = np.array([[600., 0, 320], [0, 600, 240], [0, 0, 1]])
        cameras = np.array([look_at_origin(c) for c in
            ([0., 0, 6], [3., 0, 5.2], [0, 2., 5.7])])
        contours, samples = [], []
        for ext in cameras:
            h = vertices@ext[:, :3].T+ext[:, 3]
            h = h@k.T
            polygon = cv2.convexHull((h[:, :2]/h[:, 2:]).astype(np.float32))[:, 0].astype(float)
            contours.append([polygon])
            center = polygon.mean(0)
            samples.append(arc_samples([center+(polygon-center)*.99], 64))
        score, flags = coherence(k, cameras, contours, samples)
        self.assertEqual(score, 1.)
        wrong = cameras.copy()
        wrong[1, 0, 3] += 3.
        score, flags = coherence(k, wrong, contours, samples)
        self.assertLess(score, .99)
        wrong[:, :, 3] *= .125
        replay, scaled = coherence(k, wrong, contours, samples)
        self.assertEqual(score, replay)
        np.testing.assert_array_equal(flags, scaled)
