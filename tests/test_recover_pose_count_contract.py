"""recoverPose support count is not a pure cheirality count."""
import unittest

import cv2
import numpy as np


class RecoverPoseCountContract(unittest.TestCase):
    def test_far_positive_points_are_not_reported_as_support(self):
        k = np.array([[1200., 0, 360], [0, 1200., 640], [0, 0, 1]])
        t = np.array([1., 0, 0])
        essential = np.array([[0., 0, 0], [0, 0, -1], [0, 1, 0]])
        counts = []
        for depth in (20., 100.):
            # Original exact points, not photographs or a fitted human shape.
            x, y = np.meshgrid(np.linspace(-1, 1, 4), np.linspace(-1, 1, 4))
            points = np.c_[x.ravel(), y.ravel(), depth + .1*np.arange(16)]
            other = points + t
            self.assertTrue((points[:, 2] > 0).all() and (other[:, 2] > 0).all())
            first = points[:, :2]/points[:, 2, None]*1200 + [360, 640]
            second = other[:, :2]/other[:, 2, None]*1200 + [360, 640]
            count, _, _, mask = cv2.recoverPose(essential, first, second, k)
            self.assertEqual(count, np.count_nonzero(mask))
            counts.append(count)
        self.assertEqual(counts, [16, 0])
        print({'opencv': cv2.__version__, 'known_positive_counts': [16, 16],
               'recoverPose_counts': counts, 'scope': 'synthetic API semantics only'})


if __name__ == '__main__':
    unittest.main()
