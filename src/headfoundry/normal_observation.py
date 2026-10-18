"""Unique signed normal-line intersections with a known target triangle mesh."""
import numpy as np
from scipy.spatial import cKDTree


def normal_line_hits(points, directions, vertices, faces, *, limit=.12, max_y=np.inf):
    """Return hit positions and distinct compatible crossing counts.

    Only count==1 yields a finite target. Range is bidirectional; duplicate
    shared-edge hits merge, while separate layers are rejected as ambiguous.
    These are geometric observations, not certified anatomical correspondence.
    """
    points, directions, vertices = (np.asarray(x, float) for x in (points, directions, vertices))
    faces = np.asarray(faces)
    if (points.ndim != 2 or points.shape[1:] != (3,) or directions.shape != points.shape
            or vertices.ndim != 2 or vertices.shape[1:] != (3,)
            or not all(np.isfinite(x).all() for x in (points, directions, vertices))
            or not np.allclose(np.linalg.norm(directions, axis=1), 1., atol=1e-8, rtol=0)
            or faces.ndim != 2 or faces.shape[1:] != (3,) or not len(faces)
            or not np.issubdtype(faces.dtype, np.integer) or np.any(faces < 0) or np.any(faces >= len(vertices))
            or not np.isfinite(limit) or limit <= 0 or np.isnan(max_y)):
        raise ValueError("finite mesh, unit directions and positive range required")
    tri = vertices[faces]
    a, e1, e2 = tri[:, 0], tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]
    normal = np.cross(e1, e2)
    length = np.linalg.norm(normal, axis=1)
    if np.any(length <= 1e-14):
        raise ValueError("degenerate target triangle")
    normal /= length[:, None]
    center = tri.mean(1)
    radius = np.linalg.norm(tri-center[:, None], axis=2).max()
    tree = cKDTree(center)
    hits, counts = np.full_like(points, np.nan), np.zeros(len(points), int)
    for index, (point, direction) in enumerate(zip(points, directions)):
        # Conservative sphere bound includes every triangle hit in the segment.
        ids = np.asarray(tree.query_ball_point(point, limit+radius+1e-12), int)
        ids = ids[(normal[ids] @ direction) > .25]
        if not len(ids):
            continue
        h = np.cross(direction, e2[ids])
        determinant = np.einsum("ij,ij->i", e1[ids], h)
        valid = np.abs(determinant) > 1e-14
        ids, h, determinant = ids[valid], h[valid], determinant[valid]
        if not len(ids):
            continue
        s = point-a[ids]
        u = np.einsum("ij,ij->i", s, h)/determinant
        q = np.cross(s, e1[ids])
        v = q @ direction/determinant
        t = np.einsum("ij,ij->i", e2[ids], q)/determinant
        inside = ((u >= -1e-10) & (v >= -1e-10) & (u+v <= 1+1e-10)
                  & (np.abs(t) <= limit) & (point[1]+t*direction[1] < max_y))
        distance = np.sort(t[inside])
        if not len(distance):
            continue
        counts[index] = 1+np.sum(np.diff(distance) > 2e-8)
        if counts[index] == 1:
            hits[index] = point+direction*distance[np.argmin(np.abs(distance))]
    return hits, counts
