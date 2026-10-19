"""Coordinate-only gauge mathematics;not an identity predictor or scan aligner."""
import numpy as np


def compensate_camera(extrinsic, transform):
    e, t = np.asarray(extrinsic, float), np.asarray(transform, float)
    if e.shape != (3, 4) or t.shape != (4, 4) or not np.isfinite(e).all() or not np.isfinite(t).all():
        raise ValueError('Finite proper camera and similarity required')
    s = float(np.linalg.norm(t[:3, :3], axis=1).mean())
    if s <= 0 or not np.allclose(t[3], [0, 0, 0, 1]) or not np.allclose(t[:3, :3]@t[:3, :3].T, np.eye(3)*s*s, atol=1e-12):
        raise ValueError('Positive uniform similarity required')
    q = t[:3, :3]/s
    if not np.isclose(np.linalg.det(q), 1.) or not np.allclose(e[:, :3]@e[:, :3].T, np.eye(3), atol=1e-10) or not np.isclose(np.linalg.det(e[:, :3]), 1.):
        raise ValueError('Proper rotations required,no reflection')
    r = e[:, :3]@q.T
    return np.c_[r, s*e[:, 3]-r@t[:3, 3]]


def canonicalize_centroid_radius(vertices, directions, reference, skin):
    v, b, ref, ids = np.asarray(vertices, float), np.asarray(directions, float), np.asarray(reference, float), np.asarray(skin)
    if (v.ndim != 2 or v.shape[1:] != (3,) or ref.shape != v.shape or b.ndim != 3 or b.shape[:2] != v.shape
            or ids.ndim != 1 or len(ids) < 3 or not np.issubdtype(ids.dtype, np.integer)
            or (ids < 0).any() or (ids >= len(v)).any() or len(np.unique(ids)) != len(ids)
            or not all(np.isfinite(a).all() for a in (v, b, ref))):
        raise ValueError('Matching finite geometry,field and unique skin indices required')
    center, ref_center = v[ids].mean(0), ref[ids].mean(0)
    local, ref_local = v-center, ref-ref_center
    radius = float(np.sqrt(np.mean(np.sum(local[ids]**2, axis=1))))
    ref_radius = float(np.sqrt(np.mean(np.sum(ref_local[ids]**2, axis=1))))
    if min(radius, ref_radius) <= 1e-12:
        raise ValueError('Nondegenerate radius required')
    centered_basis = b-b[ids].mean(0)
    derivative = np.einsum('vi,vik->k', local[ids], centered_basis[ids])/len(ids)/radius
    scale = ref_radius/radius
    result = ref_center+scale*local
    jacobian = scale*(centered_basis-local[:, :, None]*derivative[None, None, :]/radius)
    transform = np.diag([scale, scale, scale, 1.])
    transform[:3, 3] = ref_center-scale*center
    return result, jacobian, transform


def split_similarity_fields(reference, directions):
    ref, b = np.asarray(reference, float), np.asarray(directions, float)
    if (ref.ndim != 2 or ref.shape[1:] != (3,) or b.ndim != 3 or b.shape[:2] != ref.shape
            or not all(np.isfinite(a).all() for a in (ref, b))):
        raise ValueError('Finite native reference and matching basis required')
    centered = ref-ref.mean(0)
    generators = np.empty((len(ref), 3, 7))
    generators[:, :, :3] = np.eye(3)[None]
    for i in range(3):
        generators[:, :, i+3] = np.cross(np.eye(3)[i], centered)
    generators[:, :, 6] = centered
    matrix = generators.reshape(-1, 7)
    if np.linalg.matrix_rank(matrix, tol=1e-10) != 7:
        raise ValueError('Seven independent similarity generators required')
    orthogonal = np.linalg.qr(matrix, mode='reduced')[0]
    flat = b.reshape(-1, b.shape[-1])
    global_map = orthogonal.T@flat
    return orthogonal, global_map, flat-orthogonal@global_map
