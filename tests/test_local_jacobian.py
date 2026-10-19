import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from local_jacobian_0235 import local_jacobian, refine_local_geometry


class LocalJacobianTests(unittest.TestCase):
    def test_slope_discards_context_intercept_and_rejects_bad_geometry(self):
        source = np.random.default_rng(235).uniform(80, 420, (50, 2))
        matrix = np.array([[1.1, .12], [-.05, .95]])
        target = source @ matrix.T + [80., -43.]
        slope, neighbors, condition = local_jacobian(source, target, [256., 256.])
        np.testing.assert_allclose(slope, matrix, atol=1e-12)
        self.assertEqual(len(neighbors), 12)
        self.assertLess(condition, 1000)
        self.assertIsNone(local_jacobian(source, source * 3., [256., 256.])[0])
        line = np.c_[np.arange(12.), np.arange(12.)]
        self.assertIsNone(local_jacobian(line, line, [6., 6.])[0])

    def test_image_not_wrong_context_translation_determines_endpoint(self):
        random = np.random.default_rng(236)
        image = cv2.GaussianBlur(random.integers(0, 256, (512, 512), dtype=np.uint8), (5, 5), 1)
        matrix = np.array([[1.06, .06], [-.04, .97]])
        translation = np.array([7.3, 12.7])
        moved = cv2.warpAffine(image, np.c_[matrix, translation], (512, 512))
        context_source = random.uniform(90, 400, (80, 2))
        # Consistent contextual plane, intentionally incorrect translation.
        # Its slope is useful; its intercept must never become the measurement.
        context_target = context_source @ matrix.T + translation + [25., -20.]
        points = np.array([[170., 170.], [260., 210.], [210., 290.], [290., 280.]])
        truth = points @ matrix.T + translation
        result = refine_local_geometry(image, moved, context_source, context_target,
            points, truth + [.7, -.6])
        self.assertTrue(result['eligible'].all(), result.get('refinement_failure'))
        self.assertLess(np.linalg.norm(result['pixels'] - truth, axis=1).max(), .35)
        np.testing.assert_array_equal(result['failure_code'], 0)

    def test_missing_context_and_invalid_inputs_fail_closed(self):
        image = np.zeros((80, 80), np.uint8)
        result = refine_local_geometry(image, image, np.ones((12, 2)),
            np.ones((12, 2)), [[40., 40.]], [[40., 40.]])
        self.assertFalse(result['eligible'].any())
        self.assertIn('refinement_failure', result)
        with self.assertRaises(ValueError):
            refine_local_geometry(image, image, [], [], [[np.nan, 1]], [[1., 1.]])
        empty = refine_local_geometry(image, image, [], [], np.empty((0, 2)), np.empty((0, 2)))
        self.assertEqual(len(empty['eligible']), 0)


if __name__ == '__main__':
    unittest.main()
