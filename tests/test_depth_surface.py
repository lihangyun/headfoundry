import unittest
import numpy as np
from headfoundry.depth_surface import triangulate_grid


class DepthSurfaceTest(unittest.TestCase):
    def test_mask_discontinuity_and_compaction(self):
        y, x = np.mgrid[:3, :3]
        p = np.stack([x, y, np.ones_like(x)], -1).astype(float)
        mask = np.ones((3, 3), bool)
        v, f, used = triangulate_grid(p, mask, 1.5)
        self.assertEqual(f.shape, (8, 3))
        np.testing.assert_array_equal(v, p.reshape(-1, 3)[used])
        mask[1, 1] = False
        v, f, used = triangulate_grid(p, mask, 1.5)
        self.assertNotIn(4, used)
        self.assertEqual(len(f), 2)
        p[0, 0, 2] = 100
        v, f, used = triangulate_grid(p, np.ones((3, 3), bool), 1.5)
        self.assertNotIn(0, used)
        with self.assertRaises(ValueError):
            triangulate_grid(p, mask, float('nan'))
