import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from headfoundry.rigid_surface import fit_locally_rigid


class RigidSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.rest = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        self.faces = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])

    def test_rigid_rotation_translation_is_a_zero_energy_fixed_point(self):
        target = self.rest @ Rotation.from_rotvec([.6, -.4, .7]).as_matrix().T+[3., 1., -2.]
        actual, report = fit_locally_rigid(self.rest, self.faces, target, np.ones(4), initial=target)
        np.testing.assert_allclose(actual, target, atol=2e-12)
        self.assertLess(report["energy"][-1], 1e-22)
        self.assertGreater(report["minimum_rotation_determinant"], 1-1e-12)

    def test_translation_and_nonrigid_energy_descent(self):
        translated = self.rest+[2., -1., 3.]
        actual, _ = fit_locally_rigid(self.rest, self.faces, translated, np.ones(4))
        np.testing.assert_allclose(actual, translated, atol=2e-12)
        target = translated.copy()
        target[1] += [.2, .1, -.1]
        actual, report = fit_locally_rigid(self.rest, self.faces, target, np.ones(4))
        self.assertTrue(np.isfinite(actual).all())
        self.assertTrue(np.all(np.diff(report["energy"]) <= 1e-10))
        self.assertLess(report["energy"][-1], report["energy"][0])

    def test_rejects_unanchored_or_invalid_input(self):
        with self.assertRaises(ValueError):
            fit_locally_rigid(self.rest, self.faces, self.rest, np.zeros(4))
        with self.assertRaises(ValueError):
            fit_locally_rigid(self.rest, np.array([[0, 0, 1]]), self.rest, np.ones(4))
        with self.assertRaises(ValueError):
            fit_locally_rigid(self.rest, self.faces, np.full((4, 3), np.nan), np.ones(4))

    def test_missing_data_propagates_rigid_motion_without_fake_positions(self):
        target = np.full_like(self.rest, 999.)
        target[0] = self.rest[0]+[.2, -.1, .3]
        actual, _ = fit_locally_rigid(self.rest, self.faces, target, [1., 0., 0., 0.],
                                     weight_normalizer=3.25)
        np.testing.assert_allclose(actual, self.rest+[.2, -.1, .3], atol=2e-12)

    def test_disconnected_unobserved_component_fails_closed(self):
        rest = np.vstack([self.rest, self.rest+[3., 0., 0.]])
        faces = np.vstack([self.faces, self.faces+4])
        with self.assertRaises(ValueError):
            fit_locally_rigid(rest, faces, rest, np.r_[np.ones(4), np.zeros(4)])


if __name__ == "__main__":
    unittest.main()
