"""Three-view image-observation constraints; no solver, assets or acceptance claim."""
import numpy as np

from dense_photo_0332 import cameras
from native_camera_jacobian import linearize


def geometry(values, source):
    """0332 layout:12camera,4exposure,Nlog inverse depths; source rays fixed."""
    values, source = np.asarray(values, float), np.asarray(source, float)
    if (source.ndim != 2 or source.shape[1:] != (2,) or not len(source)
            or values.shape != (16+len(source),) or not np.isfinite(values).all()
            or not np.isfinite(source).all() or (source < 0).any()
            or (source > [719,1279]).any()):
        raise ValueError('finite native source pixels and fixed parameter layout required')
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            k, poses = cameras(values[:12])
            points = np.c_[(source-k[:2,2])/k[0,0], np.ones(len(source))] / np.exp(values[16:])[:,None]
    except FloatingPointError as error:
        raise ValueError('finite positive inverse-depth domain required') from error
    if not all(np.isfinite(x).all() for x in (k,poses,points)) or k[0,0] <= 0:
        raise ValueError('finite positive focal/depth domain required')
    return k, poses, points


def constraints(values, source, targets):
    """Return9-||projection-observation||^2 and its analytic parameter Jacobian.

    Nonnegative slack means within3nativepx, NOT physical truth. Caller must
    supply only training coordinates; this API cannot certify their provenance.
    """
    k, poses, points = geometry(values, source)
    targets = np.asarray(targets, float)
    n = len(points)
    if targets.shape != (2,n,2) or not np.isfinite(targets).all():
        raise ValueError('two finite target observation arrays required')
    rows = np.array([[c,i,*targets[c-1,i]] for c in (1,2) for i in range(n)])
    residual, free_jac, _ = linearize(k,poses,points,rows,0,1)
    # Chain freeXYZ derivatives through source-ray/logf and log inverse depth.
    point_jac = free_jac[:,12:].reshape(4*n,n,3)
    jac = np.zeros((4*n,16+n))
    jac[:,:12] = free_jac[:,:12]
    focal_chain = -points.copy(); focal_chain[:,2] = 0
    jac[:,0] += np.einsum('rij,ij->r',point_jac,focal_chain)
    jac[:,16:] = np.einsum('rij,ij->ri',point_jac,-points)
    error = residual.reshape(2*n,2)
    slack = 9-np.sum(error**2,axis=1)
    derivative = -2*np.einsum('ri,rij->rj',error,jac.reshape(2*n,2,16+n))
    return slack, derivative
