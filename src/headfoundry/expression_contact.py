"""Bounded expression-space contact solve; caller must validate actual anatomy."""
import numpy as np


def fit_contact_expression(vertices, faces, basis, upper, lower, *, contact_sigma,
                           motion_sigma, coefficient_bound=3.):
    """Minimize paired3D gaps, area-weighted motion and a coefficient prior.

    Linear model only. No topology edit, semantic decoder, camera or acceptance
    decision. Units of both sigmas must match the supplied geometry.
    """
    from scipy.linalg import cholesky, solve_triangular
    from scipy.optimize import lsq_linear

    v, f, b = np.asarray(vertices, float), np.asarray(faces), np.asarray(basis, float)
    up, low = np.asarray(upper), np.asarray(lower)
    if (v.ndim != 2 or v.shape[1:] != (3,) or not len(v)
            or f.ndim != 2 or f.shape[1:] != (3,) or not len(f)
            or not np.issubdtype(f.dtype, np.integer) or np.any(f < 0) or np.any(f >= len(v))
            or b.ndim != 3 or b.shape[:2] != v.shape or not b.shape[2]
            or up.ndim != 1 or not len(up) or low.shape != up.shape
            or not np.issubdtype(up.dtype, np.integer) or not np.issubdtype(low.dtype, np.integer)
            or np.any(up < 0) or np.any(low < 0) or np.any(up >= len(v)) or np.any(low >= len(v))
            or len(np.unique(np.r_[up, low])) != 2*len(up)
            or not all(np.isfinite(a).all() for a in (v, b))
            or not all(np.isfinite(s) and s > 0 for s in (contact_sigma, motion_sigma, coefficient_bound))):
        raise ValueError("finite mesh/basis, disjoint pair IDs and positive scales required")
    tri = v[f]
    area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)/6
    mass = np.zeros(len(v))
    for corner in range(3):
        np.add.at(mass, f[:, corner], area)
    if np.any(area <= 0) or np.any(mass <= 0):
        raise ValueError("nondegenerate triangles must cover every vertex")
    mass /= mass.sum()
    flat = b.reshape(-1, b.shape[2])
    contact = (b[up]-b[low]).reshape(-1, b.shape[2])/contact_sigma
    gap = (v[up]-v[low]).ravel()/contact_sigma
    weighted = flat*np.repeat(np.sqrt(mass), 3)[:, None]/motion_sigma
    hessian = contact.T @ contact + weighted.T @ weighted + np.eye(b.shape[2])/coefficient_bound**2
    rhs = -(contact.T @ gap)
    factor = cholesky(hessian, lower=True)
    result = lsq_linear(factor.T, solve_triangular(factor, rhs, lower=True),
                        bounds=(-coefficient_bound, coefficient_bound), method="bvls", max_iter=200)
    if not result.success or not np.isfinite(result.x).all():
        raise ValueError("bounded expression solve failed")
    displacement = np.einsum("vck,k->vc", b, result.x)
    candidate = v+displacement
    distances = np.linalg.norm(candidate[up]-candidate[low], axis=1)
    return candidate, result.x, {
        "maximum_gap": float(distances.max()), "median_gap": float(np.median(distances)),
        "area_weighted_rms_motion": float(np.sqrt(np.sum(mass*np.sum(displacement**2, axis=1)))),
        "maximum_motion": float(np.linalg.norm(displacement, axis=1).max()),
        "maximum_absolute_coefficient": float(np.abs(result.x).max()),
        "active_bounds": int(np.count_nonzero(result.active_mask)),
        "limits": "Paired linear contact objective only; final mesh/contact/anatomy checks are separate."}
