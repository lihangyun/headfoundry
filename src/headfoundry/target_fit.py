"""Bounded graphical-target point fitting; callers verify rights and visibility."""
import numpy as np
from scipy.optimize import least_squares


def fit_target_points(prior, deltas, projections, observations, mask, sigma_px,
                      *, maximum_weight=0.5, regularization=1.0):
    """Fit nonnegative target weights to fixed-camera point observations.

    Points may be verified barycentric surface samples. Deltas must use the
    same sample identities. A mask is explicit observation eligibility, not
    inferred from detector availability. Sigmas are supplied pixel scales,
    not estimated confidence. No silhouette, collision or acceptance claim.
    """
    x,b,p,y=[np.asarray(a,float) for a in (prior,deltas,projections,observations)]
    m=np.asarray(mask);sigma=np.asarray(sigma_px,float)
    if (x.ndim!=2 or x.shape[1:]!=(3,) or len(x)==0 or b.ndim!=3
            or b.shape[1:]!=x.shape or len(b)==0 or p.ndim!=3
            or p.shape[1:]!=(3,4) or len(p)==0
            or y.shape!=(len(p),len(x),2) or m.shape!=y.shape[:2]
            or m.dtype!=np.bool_ or sigma.shape!=m.shape or not m.any()):
        raise ValueError('matching points, target deltas, cameras, observations, mask and sigmas required')
    if (not all(np.isfinite(a).all() for a in (x,b,p))
            or not np.isfinite(y[m]).all() or not np.isfinite(sigma[m]).all()
            or np.any(sigma[m]<=0) or not np.isfinite(maximum_weight)
            or maximum_weight<=0 or not np.isfinite(regularization) or regularization<0):
        raise ValueError('finite geometry and eligible observations with positive uncertainty required')
    if any(np.linalg.matrix_rank(camera[:,:3])<3 for camera in p):
        raise ValueError('nondegenerate perspective cameras required')
    supported=np.any(np.any(b!=0,axis=2)&m.any(axis=0)[None,:],axis=1)
    if not supported.any():raise ValueError('no target displacement on eligible observations')
    active_basis=b[supported]
    def homogeneous(weights):
        points=x+np.einsum('k,knj->nj',weights,active_basis)
        return np.einsum('vij,nj->vni',p,np.c_[points,np.ones(len(x))])
    initial=np.zeros(len(active_basis));h0=homogeneous(initial)
    if np.any(h0[:,:,2]<=0):raise ValueError('initial points behind camera')
    def residual(weights):
        h=homogeneous(weights);uv=h[:,:,:2]/np.maximum(h[:,:,2:],1e-8)
        return np.r_[((uv[m]-y[m])/sigma[m,None]).ravel(),
                     np.sqrt(regularization)*weights,
                     100*np.minimum(h[:,:,2]-1e-6,0).ravel()]
    # Start inside bounds: the solver can otherwise stop at its nudged zero bound.
    solved=least_squares(residual,np.full(len(active_basis),maximum_weight*.1),
                         bounds=(0,maximum_weight),loss='soft_l1',max_nfev=300)
    h=homogeneous(solved.x)
    if not solved.success or np.any(h[:,:,2]<=0):raise ValueError('target solve failed or points behind camera')
    report={'status':'UNVERIFIED','eligible_observations':int(m.sum()),
            'active_bounds':solved.active_mask.tolist(),
            'fitted_control_indices':np.flatnonzero(supported).tolist(),
            'unsupported_control_indices':np.flatnonzero(~supported).tolist(),
            'cost':float(solved.cost),
            'limitation':'Training fit only. Explicit supplied visibility and uncertainty; no camera, mesh or identity acceptance.'}
    for label,values in [('before',h0),('after',h)]:
        errors=np.linalg.norm(values[:,:,:2]/values[:,:,2:]-y,axis=2)[m]
        report[label]={'mean_error_px':float(errors.mean()),'errors_px':errors.tolist()}
    weights=np.zeros(len(b));weights[supported]=solved.x
    return weights,report
