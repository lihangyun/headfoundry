"""Whiten paired image observations without hiding native pixel errors.

Covariances must come from declared measurement evidence, not fitted residuals.
This operation does not certify material correspondence or model uncertainty.
"""
import numpy as np


def whiten_observations(residual, covariance, jacobian=None):
    """Return whitened residual/Jacobian and unchanged Euclidean pixel errors.

    Each covariance is a positive definite 2x2 matrix in pixel-squared units.
    Within-point xy correlation is supported; cross-point independence remains
    an assumption of any downstream sum-of-squares objective.
    """
    r = np.asarray(residual, dtype=float)
    c = np.asarray(covariance, dtype=float)
    if (r.ndim != 2 or r.shape[1] != 2 or not len(r)
            or c.shape != (len(r), 2, 2)
            or not np.isfinite(r).all() or not np.isfinite(c).all()
            or not np.allclose(c, c.transpose(0, 2, 1), atol=1e-12, rtol=1e-12)):
        raise ValueError('Finite Nx2 residuals and symmetric Nx2x2 covariances required')
    try:
        factor = np.linalg.cholesky(c)
    except np.linalg.LinAlgError as error:
        raise ValueError('Strictly positive definite covariances required') from error
    weighted = np.linalg.solve(factor, r[..., None])[..., 0]
    derivative = None
    if jacobian is not None:
        j = np.asarray(jacobian, dtype=float)
        if j.ndim != 3 or j.shape[:2] != r.shape or not j.shape[2] or not np.isfinite(j).all():
            raise ValueError('Finite Nx2xP Jacobian required')
        derivative = np.linalg.solve(factor, j)
    return weighted, derivative, np.linalg.norm(r, axis=1)
