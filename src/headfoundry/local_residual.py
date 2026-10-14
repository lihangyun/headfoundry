"""Opt-in mesh-connected patch residuals; no image inference or anatomy claim."""

import numpy as np


def geodesic_patches(vertices, faces, node_counts=(64, 192)):
    """Return (partition weights, node IDs, support radius) at fixed scales.

    Edge-path distances deliberately do not shortcut spatially close opposing
    surfaces. Interpolating the shared vertex field yields one continuous mesh;
    it does not prevent intersections, folds or implausible anatomy.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components, dijkstra

    v, f = np.asarray(vertices, float), np.asarray(faces)
    if (v.ndim != 2 or v.shape[1:] != (3,) or not len(v)
            or not np.isfinite(v).all() or f.ndim != 2 or f.shape[1:] != (3,)
            or not len(f) or not np.issubdtype(f.dtype, np.integer)
            or np.any(f < 0) or np.any(f >= len(v))
            or not node_counts or any(not isinstance(n, (int, np.integer))
                                      or n < 1 or n >= len(v) for n in node_counts)
            or tuple(sorted(set(node_counts))) != tuple(node_counts)):
        raise ValueError("finite triangular mesh and increasing node counts required")
    edges = np.unique(np.sort(np.concatenate(
        [f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1), axis=0)
    lengths = np.linalg.norm(v[edges[:, 0]] - v[edges[:, 1]], axis=1)
    area = np.linalg.norm(np.cross(v[f[:, 1]] - v[f[:, 0]],
                                   v[f[:, 2]] - v[f[:, 0]]), axis=1)
    if np.any(lengths <= 0) or np.any(area <= 0):
        raise ValueError("degenerate mesh")
    graph = coo_matrix((np.r_[lengths, lengths],
                        (np.r_[edges[:, 0], edges[:, 1]],
                         np.r_[edges[:, 1], edges[:, 0]])),
                       shape=(len(v), len(v))).tocsr()
    if connected_components(graph, directed=False, return_labels=False) != 1:
        raise ValueError("patch mesh must be connected, including every vertex")
    nearest = np.full(len(v), np.inf)
    node = int(np.argmax(np.linalg.norm(v - v.mean(0), axis=1)))
    distances, nodes, result = [], [], []
    for count in range(1, max(node_counts) + 1):
        nodes.append(node)
        distance = dijkstra(graph, directed=False, indices=node)
        distances.append(distance)
        nearest = np.minimum(nearest, distance)
        if count in node_counts:
            radius = 2 * float(nearest.max())
            q = np.minimum(np.array(distances).T / radius, 1.)
            weights = (1 - q) ** 4 * (4 * q + 1)
            weights /= weights.sum(1, keepdims=True)
            result.append((weights, np.array(nodes), radius))
        node = int(np.argmax(nearest))
    return result


def fit_patch_residual(prior, target, patches, vertex_weights, ridge=1e-6):
    """Two/fixed-scale dense-3D oracle, not a photo fitting API.

    Area weights sum to one so ridge has a reproducible scale. Caller must
    independently gate the final exported surface; unsafe fits are not repaired
    or accepted here. Target coefficients and target-generating bases are absent.
    """
    from scipy.linalg import cho_factor, cho_solve

    prior, target = np.asarray(prior, float), np.asarray(target, float)
    mass = np.asarray(vertex_weights, float)
    if (prior.ndim != 2 or prior.shape[1:] != (3,) or not len(prior)
            or target.shape != prior.shape or mass.shape != (len(prior),)
            or not all(np.isfinite(x).all() for x in (prior, target, mass))
            or np.any(mass <= 0) or not np.isfinite(ridge) or ridge <= 0
            or not patches):
        raise ValueError("finite matching points, positive area weights/ridge required")
    mass = mass / mass.sum()
    candidate, coefficients = prior.copy(), []
    for patch in patches:
        w = np.asarray(patch[0], float)
        if (w.ndim != 2 or w.shape[0] != len(prior) or not w.shape[1]
                or not np.isfinite(w).all() or np.any(w < 0)
                or not np.allclose(w.sum(1), 1., atol=1e-12, rtol=0)):
            raise ValueError("patch weights must form a finite nonnegative partition")
        system = w.T @ (mass[:, None] * w) + ridge * np.eye(w.shape[1])
        rhs = w.T @ (mass[:, None] * (target - candidate))
        control = cho_solve(cho_factor(system), rhs)
        candidate += w @ control
        coefficients.append(control)
    return candidate, coefficients
