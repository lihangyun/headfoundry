import unittest
import numpy as np
from headfoundry.observation_uncertainty import whiten_observations


class ObservationUncertaintyTests(unittest.TestCase):
    def test_correlated_mahalanobis_and_derivative(self):
        residual = np.array([[3., 4.], [-2., 1.]])
        covariance = np.array([[[4., 1.], [1., 9.]], [[2., -.5], [-.5, 1.]]])
        jacobian = np.arange(12, dtype=float).reshape(2, 2, 3) / 10
        weighted, derivative, pixels = whiten_observations(residual, covariance, jacobian)
        expected = np.einsum('ni,nij,nj->n', residual, np.linalg.inv(covariance), residual)
        np.testing.assert_allclose(np.sum(weighted**2, axis=1), expected)
        np.testing.assert_allclose(pixels, [5., np.sqrt(5)])
        for k in range(3):
            plus = whiten_observations(residual + 1e-6*jacobian[:,:,k], covariance)[0]
            minus = whiten_observations(residual - 1e-6*jacobian[:,:,k], covariance)[0]
            np.testing.assert_allclose((plus-minus)/2e-6, derivative[:,:,k], atol=1e-9)

    def test_old_scale_is_reproducible_and_errors_stay_native(self):
        residual = np.array([[30., 40.]])
        weighted, _, pixels = whiten_observations(residual, 16*np.eye(2)[None])
        np.testing.assert_allclose(weighted, residual/4)
        self.assertEqual(pixels[0], 50.)
        _, _, larger = whiten_observations(residual, 1600*np.eye(2)[None])
        np.testing.assert_array_equal(pixels, larger)

    def test_invalid_measurements_fail(self):
        for covariance in [np.zeros((1,2,2)), -np.eye(2)[None],
                           np.array([[[1.,2.],[0.,1.]]]), np.full((1,2,2), np.nan)]:
            with self.assertRaises(ValueError):
                whiten_observations([[1.,2.]], covariance)
        with self.assertRaises(ValueError):
            whiten_observations([[1.,2.]], np.eye(2)[None], np.zeros((1,3,2)))
