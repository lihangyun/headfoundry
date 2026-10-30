"""Local image-curve factors for sliding observations, not material IDs."""
import numpy as np


def point_to_polyline(points, curve):
    """Residual, local Jacobian, segment index, fraction and ambiguous-tie flag.

    Jacobian differentiates residual with respect to points while curve is fixed.
    At ties the first segment is chosen deterministically; the returned flag
    warns callers that a unique smooth derivative is not established there.
    Curves are open; close explicitly by repeating the first vertex if desired.
    """
    p, q = np.asarray(points, float), np.asarray(curve, float)
    if (p.ndim != 2 or p.shape[1] != 2 or not len(p)
            or q.ndim != 2 or q.shape[1] != 2 or len(q) < 2
            or not np.isfinite(p).all() or not np.isfinite(q).all()):
        raise ValueError('Finite nonempty Nx2 points and ordered Mx2 curve required')
    edge = np.diff(q, axis=0)
    length2 = np.sum(edge*edge, axis=1)
    if (length2 <= 0).any() or not np.isfinite(length2).all():
        raise ValueError('Every curve segment must have positive finite length')
    # ponytail: dense NxM search for small facial curves; spatial indexing only
    # if a measured larger workload requires it.
    fraction = np.einsum('nmi,mi->nm', p[:,None]-q[:-1], edge)/length2
    clamped = np.clip(fraction, 0., 1.)
    delta = p[:,None]-q[:-1]-clamped[...,None]*edge
    distance2 = np.sum(delta*delta, axis=2)
    segment = np.argmin(distance2, axis=1)
    row = np.arange(len(p))
    chosen = fraction[row,segment]
    derivative = np.broadcast_to(np.eye(2), (len(p),2,2)).copy()
    interior = (chosen > 0) & (chosen < 1)
    direction = edge[segment[interior]]
    derivative[interior] -= np.einsum('ni,nj->nij', direction, direction)/length2[segment[interior],None,None]
    tied = np.sum(np.isclose(distance2, distance2[row,segment,None], rtol=1e-12, atol=1e-12), axis=1)>1
    # Exact clamp transitions also lack a two-sided residual Jacobian.
    ambiguous = tied | (chosen == 0) | (chosen == 1)
    return delta[row,segment], derivative, segment, clamped[row,segment], ambiguous
