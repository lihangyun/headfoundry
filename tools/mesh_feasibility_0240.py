"""Exact cross-product inequality/Jacobian on original prior triangles."""
import numpy as np


def constraints(coefficients, base_triangles, triangle_directions):
    x, base, field = map(lambda a: np.asarray(a, float),
        (coefficients, base_triangles, triangle_directions))
    if (x.ndim != 1 or base.ndim != 3 or base.shape[1:] != (3, 3)
            or field.shape != (*base.shape, len(x)) or not len(base)
            or not all(np.isfinite(a).all() for a in (x, base, field))):
        raise ValueError('Finite original triangles and matching identity fields required')
    a, b, c = np.moveaxis(base, 1, 0)
    da, db, dc = np.moveaxis(field, 1, 0)
    du, dv = db - da, dc - da
    u0, v0 = b - a, c - a
    old = np.cross(u0, v0)
    denominator = np.einsum('ni,ni->n', old, old)
    if (denominator <= 0).any():
        raise ValueError('Degenerate original face')
    u = u0 + np.einsum('nck,k->nc', du, x)
    v = v0 + np.einsum('nck,k->nc', dv, x)
    normal = np.cross(u, v)
    derivative = np.cross(du.transpose(0, 2, 1), v[:, None]) + np.cross(u[:, None], dv.transpose(0, 2, 1))
    signed = np.einsum('ni,ni->n', normal, old) / denominator
    squared = np.einsum('ni,ni->n', normal, normal) / denominator
    signed_jac = np.einsum('nki,ni->nk', derivative, old) / denominator[:, None]
    squared_jac = 2 * np.einsum('nki,ni->nk', derivative, normal) / denominator[:, None]
    values = np.r_[signed - 1e-6, squared - .20001 ** 2, 4.99999 ** 2 - squared]
    jacobian = np.concatenate([signed_jac, squared_jac, -squared_jac])
    return values, jacobian


def violated_faces(vertices, base, faces):
    old = np.cross(base[faces[:, 1]] - base[faces[:, 0]], base[faces[:, 2]] - base[faces[:, 0]])
    new = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]])
    denominator = np.einsum('ni,ni->n', old, old)
    if (denominator <= 0).any():
        raise ValueError('Degenerate original face')
    signed = np.einsum('ni,ni->n', new, old) / denominator
    squared = np.einsum('ni,ni->n', new, new) / denominator
    # Fixed arithmetic tolerance is smaller than the conservative margins; the
    # caller must still check the original strict .2..5/zero-reversal guards.
    return np.flatnonzero((signed < 1e-6 - 1e-7) | (squared < .20001 ** 2 - 1e-7)
        | (squared > 4.99999 ** 2 + 1e-7))
