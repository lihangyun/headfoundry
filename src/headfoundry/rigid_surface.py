"""Opt-in positive-cotangent ARAP fit; not a collision/anatomy certificate.

Independent local/global formulation following Sorkine and Alexa, SGP2007.
No external implementation is used. Positions and proper rotations alternate.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu


def fit_locally_rigid(rest, faces, target, weights, *, initial=None, strength=.05, iterations=20):
    """Fit soft3D controls while preserving rest one-ring edge geometry.

    All vertices need positive finite data weights, anchoring every component.
    Callers must separately guard each accepted geometry update and actual export.
    """
    rest, target, weights = np.asarray(rest, float), np.asarray(target, float), np.asarray(weights, float)
    faces = np.asarray(faces)
    current = rest.copy() if initial is None else np.asarray(initial, float).copy()
    if (rest.ndim != 2 or rest.shape[1:] != (3,) or not len(rest) or target.shape != rest.shape
            or current.shape != rest.shape or weights.shape != (len(rest),)
            or not all(np.isfinite(x).all() for x in (rest, target, current, weights))
            or np.any(weights <= 0) or not np.isfinite(strength) or strength <= 0
            or not isinstance(iterations, int) or iterations < 1
            or faces.ndim != 2 or faces.shape[1:] != (3,) or not len(faces)
            or not np.issubdtype(faces.dtype, np.integer) or np.any(faces < 0) or np.any(faces >= len(rest))):
        raise ValueError("finite matching triangular surfaces, positive data weights and iterations required")
    tri = rest[faces]
    twice_area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)
    if np.any(twice_area <= 1e-14):
        raise ValueError("degenerate rest triangle")
    all_edges, all_weights = [], []
    for a, b, opposite in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        all_edges.append(np.sort(faces[:, [a, b]], axis=1))
        all_weights.append(np.einsum("ij,ij->i", tri[:, a]-tri[:, opposite], tri[:, b]-tri[:, opposite])/twice_area/2)
    edges, inverse = np.unique(np.concatenate(all_edges), axis=0, return_inverse=True)
    edge_weight = np.bincount(inverse, weights=np.concatenate(all_weights))
    clipped = int(np.sum(edge_weight < 1e-8))
    edge_weight = np.maximum(edge_weight, 1e-8)
    edge_weight /= np.median(edge_weight)
    i, j = edges.T
    if len(np.unique(edges)) != len(rest):
        raise ValueError("every vertex must have an incident rest edge")
    rest_edge = rest[i]-rest[j]
    laplacian = sparse.coo_matrix((np.r_[edge_weight, edge_weight, -edge_weight, -edge_weight],
                                  (np.r_[i, j, i, j], np.r_[i, j, j, i])), shape=(len(rest), len(rest))).tocsc()
    data_weight = weights/weights.mean()*strength
    solve = splu(laplacian+sparse.diags(data_weight, format="csc"))

    def rotations(points):
        edge = points[i]-points[j]
        products = edge_weight[:, None, None]*rest_edge[:, :, None]*edge[:, None, :]
        covariance = np.zeros((len(rest), 3, 3))
        np.add.at(covariance, i, products)
        np.add.at(covariance, j, products)
        u, _, vt = np.linalg.svd(covariance)
        v = vt.transpose(0, 2, 1)
        sign = np.linalg.det(v @ u.transpose(0, 2, 1))
        v[:, :, -1] *= np.where(sign < 0, -1., 1.)[:, None]
        return v @ u.transpose(0, 2, 1)

    def energy(points, rotation):
        edge = points[i]-points[j]
        a = edge-np.einsum("nij,nj->ni", rotation[i], rest_edge)
        b = edge-np.einsum("nij,nj->ni", rotation[j], rest_edge)
        return float(np.sum(edge_weight*(np.sum(a*a, axis=1)+np.sum(b*b, axis=1))*.5)
                     + np.sum(data_weight[:, None]*(points-target)**2))

    rotation, history = rotations(current), []
    history.append(energy(current, rotation))
    for _ in range(iterations):
        desired_edge = np.einsum("nij,nj->ni", (rotation[i]+rotation[j])*.5, rest_edge)*edge_weight[:, None]
        rhs = data_weight[:, None]*target
        np.add.at(rhs, i, desired_edge)
        np.add.at(rhs, j, -desired_edge)
        current = solve.solve(rhs)
        rotation = rotations(current)
        value = energy(current, rotation)
        if not np.isfinite(current).all() or value > history[-1]+1e-10*max(1., history[-1]):
            raise ValueError("local/global energy increased or became nonfinite")
        history.append(value)
    return current, {"energy": history, "clipped_edge_count": clipped, "edge_count": len(edges),
                     "minimum_rotation_determinant": float(np.linalg.det(rotation).min())}
