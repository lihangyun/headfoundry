import unittest

import cv2
import numpy as np

from tools.temporal_video_sfm_0220 import resolve_keyframe_hashes, track_step


class TemporalVideoTrackTests(unittest.TestCase):
    def test_known_translation_and_occlusion(self):
        image = np.random.default_rng(220).integers(0, 256, (512, 512), dtype=np.uint8)
        image = cv2.GaussianBlur(image, (5, 5), 1)
        mask = np.zeros_like(image)
        # Keep the known-motion check clear of the coarsest pyramid's border.
        mask[120:392, 120:392] = 255
        points = cv2.goodFeaturesToTrack(image, 80, .01, 8, mask=mask).reshape(-1, 2)
        moved = cv2.warpAffine(image, np.float32([[1, 0, 2], [0, 1, -1]]), (512, 512))
        predicted, keep, fb, _ = track_step(image, moved, points)
        self.assertGreater(keep.sum(), .9 * len(points))
        self.assertLess(np.linalg.norm(predicted[keep] - points[keep] - [2, -1], axis=1).max(), .15)
        self.assertLess(fb[keep].max(), .15)
        self.assertEqual(int(track_step(image, np.zeros_like(image), points)[1].sum()), 0)

    def test_invalid_or_empty_input(self):
        image = np.zeros((20, 20), np.uint8)
        self.assertEqual(len(track_step(image, image, np.empty((0, 2)))[0]), 0)
        with self.assertRaises(ValueError):
            track_step(image, image, np.array([[np.nan, 3.]]))

    def test_exact_sequential_frame_identity_and_ambiguity(self):
        expected = {0: "a", 12: "b", 24: "c"}
        self.assertEqual(resolve_keyframe_hashes(expected, [(0, "a"), (13, "b"), (25, "c")]),
                         {0: 0, 12: 13, 24: 25})
        for decoded in ([(0, "a"), (12, "b")],
                        [(0, "a"), (1, "a"), (12, "b"), (24, "c")],
                        [(0, "a"), (15, "b"), (24, "c")]):
            with self.assertRaises(ValueError):
                resolve_keyframe_hashes(expected, decoded)


if __name__ == "__main__":
    unittest.main()
