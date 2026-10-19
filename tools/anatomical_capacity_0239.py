"""Small NumPy-only proper-similarity, constrained linear-fit and mesh checks."""
import numpy as np


def fit_similarity(source, target, weights):
    x, y, w = map(lambda a: np.asarray(a, float), (source, target, weights))
    if (x.ndim != 2 or x.shape[1:] != (3,) or y.shape != x.shape or len(x) < 3
            or w.shape != (len(x),) or not all(np.isfinite(a).all() for a in (x, y, w)) or (w <= 0).any()):
        raise ValueError('Finite weighted paired3D points required')
    w = w / w.sum()
    cx, cy = w @ x, w @ y
    a, b = x - cx, y - cy
    if np.linalg.matrix_rank(a) < 2:
        raise ValueError('Noncollinear similarity support required')
    u, singular, vt = np.linalg.svd(a.T @ (w[:, None] * b))
    correction = np.diag([1., 1., np.linalg.det(vt.T @ u.T)])
    rotation = vt.T @ correction @ u.T
    scale = float(np.sum(singular * np.diag(correction)) / np.sum(w * np.sum(a * a, axis=1)))
    if scale <= 0 or not np.isfinite(scale):
        raise ValueError('Positive similarity scale required')
    result = np.eye(4)
    result[:3, :3] = scale * rotation
    result[:3, 3] = cy - scale * rotation @ cx
    return result


def box_quadratic(hessian, linear, initial=None):
    """Primal active-set box QP; fixed objective, bound and KKT/iteration ceiling."""
    h, g = np.asarray(hessian, float), np.asarray(linear, float)
    if (g.ndim != 1 or not len(g) or h.shape != (len(g), len(g))
            or not np.isfinite(h).all() or not np.isfinite(g).all()
            or not np.allclose(h, h.T, rtol=1e-10, atol=1e-10)):
        raise ValueError('Finite symmetric quadratic required')
    eigen = np.linalg.eigvalsh(h)
    if eigen[0] <= 0:
        raise ValueError('Positive definite regularized quadratic required')
    x = np.zeros(len(g)) if initial is None else np.asarray(initial, float).copy()
    if x.shape != g.shape or not np.isfinite(x).all() or (abs(x) > 3).any():
        raise ValueError('Finite bounded initialization required')
    active = np.zeros(len(g), np.int8)
    active[x <= -3 + 1e-10], active[x >= 3 - 1e-10] = -1, 1
    ratio = np.inf
    for step in range(2000):
        free, fixed = np.flatnonzero(active == 0), np.flatnonzero(active != 0)
        proposal = x.copy()
        if len(free):
            proposal[free] = np.linalg.solve(h[np.ix_(free, free)], g[free] - h[np.ix_(free, fixed)] @ x[fixed])
        direction = proposal - x
        alpha = 1.
        above, below = (proposal > 3) & (direction > 0), (proposal < -3) & (direction < 0)
        if above.any():
            alpha = min(alpha, float(((3 - x[above]) / direction[above]).min()))
        if below.any():
            alpha = min(alpha, float(((-3 - x[below]) / direction[below]).min()))
        # Feasible line step, not acceptance of clipped unconstrained weights.
        x = np.clip(x + alpha * direction, -3., 3.)
        active[(active == 0) & (x <= -3 + 1e-10)] = -1
        active[(active == 0) & (x >= 3 - 1e-10)] = 1
        gradient = h @ x - g
        projected = gradient.copy()
        low, high = x <= -3 + 1e-10, x >= 3 - 1e-10
        projected[low] = np.minimum(projected[low], 0)
        projected[high] = np.maximum(projected[high], 0)
        ratio = float(abs(projected).max() / max(1., abs(g).max()))
        if ratio <= 1e-6:
            break
        if alpha < 1.:
            continue
        # At the free-subspace optimum, release the worst active KKT violation.
        violation = np.zeros(len(g))
        violation[active == -1] = np.maximum(-gradient[active == -1], 0)
        violation[active == 1] = np.maximum(gradient[active == 1], 0)
        if violation.max() <= 0:
            break
        active[int(np.argmax(violation))] = 0
    return x, {'iterations': step + 1, 'relative_projected_KKT': ratio, 'converged': ratio <= 1e-6}


def barycentric_closest(points, triangles):
    a, b, c = np.moveaxis(triangles, 1, 0)
    ab, ac, ap = b - a, c - a, points - a
    aa, bb, cc = (np.einsum('ni,ni->n', p, q) for p, q in ((ab, ab), (ab, ac), (ac, ac)))
    d, e = (np.einsum('ni,ni->n', p, ap) for p in (ab, ac))
    denominator = aa * cc - bb * bb
    if (denominator <= 1e-20).any():
        raise ValueError('Degenerate closest triangle')
    v, w = (cc * d - bb * e) / denominator, (aa * e - bb * d) / denominator
    bary = np.c_[1 - v - w, v, w]
    if bary.min() < -1e-3 or bary.max() > 1 + 1e-3:
        raise ValueError('Closest point outside its reported triangle')
    # Blender's float32 nearest coordinates can lie microscopically off an edge.
    bary = np.clip(bary, 0, 1)
    bary /= bary.sum(axis=1)[:, None]
    if np.linalg.norm(np.einsum('ni,nij->nj', bary, triangles) - points, axis=1).max() > .001:
        raise ValueError('Closest-point barycentric numeric replay failed')
    return bary


def mesh_guard(vertices, base, faces):
    old = np.cross(base[faces[:, 1]] - base[faces[:, 0]], base[faces[:, 2]] - base[faces[:, 0]])
    new = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]], vertices[faces[:, 2]] - vertices[faces[:, 0]])
    denominator = np.linalg.norm(old, axis=1)
    if (denominator <= 0).any():
        raise ValueError('Degenerate baseline face')
    ratio = np.linalg.norm(new, axis=1) / denominator
    record = {'finite': bool(np.isfinite(vertices).all()), 'min_area_ratio': float(ratio.min()),
        'max_area_ratio': float(ratio.max()), 'normal_reversals': int((np.einsum('ni,ni->n', old, new) <= 0).sum())}
    record['passed'] = bool(record['finite'] and record['min_area_ratio'] >= .2
        and record['max_area_ratio'] <= 5 and record['normal_reversals'] == 0)
    return record
