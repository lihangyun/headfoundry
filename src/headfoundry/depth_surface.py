"""Observed depth surfaces, deliberately not a watertight head reconstruction."""
import numpy as np


def triangulate_grid(points, mask, max_edge):
    """Return compact mesh and retained pixel indices; never bridge masked gaps."""
    p = np.asarray(points, float)
    m = np.asarray(mask)
    if (p.ndim != 3 or p.shape[2] != 3 or m.shape != p.shape[:2]
            or m.dtype != bool or not np.isfinite(p).all()
            or not np.isfinite(max_edge) or max_edge <= 0):
        raise ValueError('finite HxWx3 points, boolean mask and positive edge limit required')
    h, w = m.shape
    a = np.arange(h*w).reshape(h, w)[:-1, :-1].ravel()
    faces = np.concatenate([np.stack([a, a+w, a+1], 1),
                            np.stack([a+1, a+w, a+w+1], 1)])
    flat = p.reshape(-1, 3)
    faces = faces[m.ravel()[faces].all(axis=1)]
    edges = flat[faces] - flat[np.roll(faces, 1, axis=1)]
    faces = faces[(np.linalg.norm(edges, axis=2) <= max_edge).all(axis=1)]
    area = np.linalg.norm(np.cross(flat[faces[:, 1]]-flat[faces[:, 0]],
                                   flat[faces[:, 2]]-flat[faces[:, 0]]), axis=1)
    faces = faces[area > 1e-12]
    used, inverse = np.unique(faces, return_inverse=True)
    return flat[used], inverse.reshape(-1, 3), used


def write_observed_obj(path, vertices, faces):
    """Exclusive export: preserve prior runs and label scope in the file."""
    with open(path, 'x', encoding='utf-8') as stream:
        stream.write('# UNVERIFIED observed depth surface; not a complete head\n')
        for v in vertices:
            stream.write('v ' + ' '.join(f'{x:.9g}' for x in v) + '\n')
        for f in faces:
            stream.write('f ' + ' '.join(str(int(x)+1) for x in f) + '\n')
