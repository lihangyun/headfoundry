"""Rigid pose of a fixed anatomical template; not a camera acceptance test."""
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def fit_template_pose(points, pixels, intrinsic, initial, bounds, sigma_px=5.):
    points, pixels, k, initial = [np.asarray(a, float) for a in
                                 (points, pixels, intrinsic, initial)]
    lower, upper = [np.asarray(a, float) for a in bounds]
    if (points.ndim != 2 or points.shape[1:] != (3,) or len(points) < 4
            or pixels.shape != (len(points), 2) or k.shape != (3, 3)
            or any(a.shape != (6,) for a in (initial, lower, upper))
            or not all(np.isfinite(a).all() for a in (points, pixels, k, initial, lower, upper))
            or not np.isfinite(sigma_px) or sigma_px <= 0):
        raise ValueError('finite correspondences, camera and six-parameter bounds required')
    if (not np.allclose(k[2], [0, 0, 1]) or k[1, 0] != 0
            or min(k[0, 0], k[1, 1]) <= 0
            or np.any(lower >= upper) or np.any(initial <= lower) or np.any(initial >= upper)
            or np.linalg.matrix_rank(points-points.mean(0)) < 3
            or len(np.unique(pixels, axis=0)) != len(pixels)):
        raise ValueError('invalid intrinsics, bounds or degenerate correspondences')

    def camera(x):
        return points @ Rotation.from_rotvec(x[:3]).as_matrix().T + x[3:]

    if np.any(camera(initial)[:, 2] <= 0):
        raise ValueError('initial landmarks behind camera')

    def residual(x):
        cam = camera(x)
        h = cam @ k.T
        # Reject negative-depth solutions after optimization; penalize trial crossings.
        uv = h[:, :2] / np.maximum(h[:, 2:], 1e-6)
        return np.r_[((uv-pixels)/sigma_px).ravel(), 100*np.minimum(cam[:, 2]-.01, 0)]

    solved = least_squares(residual, initial, bounds=(lower, upper),
                           loss='soft_l1', max_nfev=300)
    cam = camera(solved.x)
    if not solved.success or np.any(cam[:, 2] <= 0):
        raise ValueError('pose solve failed or landmarks behind camera')
    h = cam @ k.T
    error = np.linalg.norm(h[:, :2]/h[:, 2:]-pixels, axis=1)
    e = np.column_stack([Rotation.from_rotvec(solved.x[:3]).as_matrix(), solved.x[3:]])
    return e, dict(status='UNVERIFIED', fit_errors_px=error.tolist(),
                   active_bounds=solved.active_mask.tolist(),
                   rotation_vector=solved.x[:3].tolist(),
                   limitation='Training residuals only; fixed template and assumed intrinsics, no held-out camera or identity acceptance.')
