"""Experimental surface triangulation under supplied, possibly rejected cameras.

This is a diagnostic, never a camera gate or accepted head reconstruction.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import lsqr


def fit_surface(prior, observations, projections, triangles, protected, regularization=30., observation_mask=None,
                displacement_directions=None):
    prior = np.asarray(prior, float)
    observations = np.asarray(observations, float)
    projections = np.asarray(projections, float)
    triangles = np.asarray(triangles, int)
    count = len(prior)
    directions = None if displacement_directions is None else np.asarray(displacement_directions, float)
    if directions is not None:
        if directions.shape != (count, 3) or not np.isfinite(directions).all() or np.any(np.linalg.norm(directions,axis=1)<1e-12):
            raise ValueError('finite nonzero displacement directions required')
        directions = directions / np.linalg.norm(directions,axis=1)[:,None]
    dimensions = 3 if directions is None else 1
    if prior.shape != (count, 3) or observations.shape != (len(projections), count, 2):
        raise ValueError('invalid observation shapes')
    mask = np.ones(observations.shape[:2],bool) if observation_mask is None else np.asarray(observation_mask,bool)
    if mask.shape != observations.shape[:2]:
        raise ValueError('invalid observation mask')
    if projections.shape[1:] != (3,4) or not all(np.isfinite(a).all() for a in (prior, observations, projections)):
        raise ValueError('invalid projections')
    if regularization <= 0 or triangles.ndim != 2 or triangles.shape[1] != 3 or np.any(triangles < 0) or np.any(triangles >= count):
        raise ValueError('invalid topology or regularization')
    protected = np.asarray(protected, int)
    if np.any(protected < 0) or np.any(protected >= count):
        raise ValueError('invalid protected indices')
    free = np.setdiff1d(np.arange(count), protected)
    if not len(free):
        return prior.copy()
    columns = {int(vertex): i*dimensions for i,vertex in enumerate(free)}
    rows, cols, values, rhs = [], [], [], []

    def equation(terms, target):
        row = len(rhs)
        for vertex, axis, coefficient in terms:
            if vertex in columns:
                rows.append(row)
                cols.append(columns[vertex]+axis if directions is None else columns[vertex])
                values.append(coefficient if directions is None else coefficient*directions[vertex,axis])
        rhs.append(target)

    # Solve displacements, retaining the supplied prior in protected regions.
    for view, (p, uv) in enumerate(zip(projections, observations)):
        homogeneous = np.c_[prior, np.ones(count)]
        depth = homogeneous @ p[2]
        if np.any(depth <= 0):
            raise ValueError('prior behind supplied camera')
        for vertex in free:
            if not mask[view,vertex]:
                continue
            for axis in range(2):
                a = (p[axis,:3] - uv[vertex,axis]*p[2,:3])/depth[vertex]
                b = (uv[vertex,axis]*p[2,3]-p[axis,3])/depth[vertex] - a@prior[vertex]
                equation([(int(vertex), k, a[k]) for k in range(3)], b)
    edges = sorted({tuple(sorted((int(a),int(b)))) for t in triangles for a,b in zip(t,np.roll(t,-1))})
    for a,b in edges:
        for axis in range(3):
            equation([(a,axis,regularization),(b,axis,-regularization)],0.)
    for vertex in free:
        for axis in range(3):
            equation([(int(vertex),axis,regularization*.1)],0.)
    system = coo_matrix((values,(rows,cols)),shape=(len(rhs),len(free)*dimensions)).tocsr()
    solved = lsqr(system,rhs,atol=1e-9,btol=1e-9,iter_lim=2000)
    if solved[1] not in (0,1,2):
        raise ValueError('surface solve failed to converge')
    delta=solved[0].reshape(-1,dimensions)
    if directions is not None:delta=delta*directions[free]
    result=prior.copy(); result[free]+=delta
    for p in projections:
        if np.any(np.c_[result,np.ones(count)]@p[2] <= 0):
            raise ValueError('fitted surface behind camera')
    return result


def write_obj(path, vertices, triangles):
    with path.open('x',encoding='utf-8') as stream:
        stream.write('# UNVERIFIED diagnostic face patch; not a full head\n')
        for x,y,z in vertices:
            stream.write(f'v {x:.8f} {y:.8f} {z:.8f}\n')
        for a,b,c in triangles:
            stream.write(f'f {a+1} {b+1} {c+1}\n')
