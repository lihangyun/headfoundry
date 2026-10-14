import unittest

import numpy as np

from headfoundry.local_residual import geodesic_patches, fit_patch_residual


class LocalResidualTests(unittest.TestCase):
    def setUp(self):
        y, x = np.mgrid[:8, :8]
        self.v = np.c_[x.ravel(), y.ravel(), np.zeros(x.size)].astype(float)
        self.f = np.array([face for j in range(7) for i in range(7)
                          for face in ((j*8+i, j*8+i+1, (j+1)*8+i),
                                       (j*8+i+1, (j+1)*8+i+1, (j+1)*8+i))])

    def test_partition_determinism_and_dense_oracle(self):
        patches = geodesic_patches(self.v, self.f, (4, 12))
        again = geodesic_patches(self.v, self.f, (4, 12))
        for (w, nodes, radius), other in zip(patches, again):
            np.testing.assert_allclose(w.sum(1), 1., atol=1e-14)
            self.assertTrue(np.all(w >= 0))
            np.testing.assert_array_equal(nodes, other[1])
            self.assertEqual(radius, other[2])
            self.assertEqual(len(np.unique(nodes)), len(nodes))
        np.testing.assert_array_equal(patches[0][1], patches[1][1][:4])
        target = self.v + [0.1, -0.2, 0.3]
        fitted, coefficients = fit_patch_residual(self.v, target, patches, np.ones(64))
        self.assertLess(np.linalg.norm(fitted-target), 1e-5)
        replay = self.v + sum(p[0] @ c for p, c in zip(patches, coefficients))
        np.testing.assert_allclose(fitted, replay, atol=1e-14)
        unchanged, _ = fit_patch_residual(self.v, self.v, patches, np.ones(64))
        np.testing.assert_array_equal(unchanged, self.v)

    def test_disconnected_invalid_and_degenerate_fail_closed(self):
        for faces, counts in ((self.f[:1], (2,)), (self.f, (4, 4)),
                              (self.f, (64,)), (self.f.astype(float), (4,))):
            with self.assertRaises(ValueError):
                geodesic_patches(self.v, faces, counts)
        v = self.v.copy()
        v[1] = v[0]
        with self.assertRaises(ValueError):
            geodesic_patches(v, self.f, (4,))
        p = geodesic_patches(self.v, self.f, (4,))
        for target, mass, ridge in ((self.v*np.nan, np.ones(64), 1e-6),
                                    (self.v, np.zeros(64), 1e-6),
                                    (self.v, np.ones(64), 0)):
            with self.assertRaises(ValueError):
                fit_patch_residual(self.v, target, p, mass, ridge)


if __name__ == "__main__":
    unittest.main()
