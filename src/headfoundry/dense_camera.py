"""Alternating dense camera/surface diagnostic with fixed focal lengths.

Observations are detector estimates, not independent geometric ground truth.
No accepted camera or full-head quality is implied by optimization convergence.
"""
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from .bundle import project
from .surface_diagnostic import fit_surface


def refine(prior, observations, intrinsics, extrinsics, triangles, protected,
           train_mask, validation_mask, iterations=12):
    prior=np.asarray(prior,float); obs=np.asarray(observations,float)
    k=np.asarray(intrinsics,float); e=np.asarray(extrinsics,float).copy()
    if (prior.ndim!=2 or prior.shape[1]!=3 or obs.shape!=(len(e),len(prior),2)
            or e.shape!=(len(e),3,4) or k.shape!=(len(e),3,3)
            or not all(np.isfinite(a).all() for a in (prior,obs,k,e))):
        raise ValueError('finite, correctly shaped geometry and cameras required')
    train=np.array(train_mask,bool,copy=True); validation=np.array(validation_mask,bool,copy=True)
    if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1:
        raise ValueError('positive iteration count required')
    if train.shape!=obs.shape[:2] or validation.shape!=train.shape or np.any(train&validation):
        raise ValueError('disjoint observation masks required')
    if not validation.any() or validation[0].any():
        raise ValueError('validation required outside frontal prior source')
    train[:,protected]=False; validation[:,protected]=False
    if np.any(train.sum(axis=1)<6) or not validation.any():
        raise ValueError('insufficient unprotected observations')
    original=e.copy()
    history=[];vertices=prior.copy()
    for step in range(iterations):
        vertices=fit_surface(prior,obs,k@e,triangles,protected,observation_mask=train)
        for view in range(1,len(e)):
            init=np.r_[Rotation.from_matrix(e[view,:,:3]).as_rotvec(),e[view,:,3]]
            center=np.r_[Rotation.from_matrix(original[view,:,:3]).as_rotvec(),original[view,:,3]]
            span=np.r_[np.full(3,.3),np.full(3,.8)]
            def residual(x):
                r=Rotation.from_rotvec(x[:3]).as_matrix()
                cam=vertices@r.T+x[3:]
                h=cam@k[view].T
                uv=h[:,:2]/np.maximum(h[:,2:],.01)
                return np.r_[((uv-obs[view])[train[view]]/4).ravel(),
                             100*np.minimum(cam[:,2]-.1,0)]
            result=least_squares(residual,np.clip(init,center-span+1e-9,center+span-1e-9),
                                 bounds=(center-span,center+span),loss='soft_l1',max_nfev=100)
            if not result.success:raise ValueError('pose refinement did not converge')
            e[view,:,:3]=Rotation.from_rotvec(result.x[:3]).as_matrix()
            e[view,:,3]=result.x[3:]
        errors=np.linalg.norm(project(vertices,e[:,:,:3],e[:,:,3],k)-obs,axis=-1)
        depths=np.einsum('vij,nj->vni',e[:,:,:3],vertices)+e[:,:,3][:,None,:]
        if not np.isfinite(errors).all() or np.any(depths[:,:,2]<=.1):
            raise ValueError('invalid projection or nonpositive camera depth')
        # Validation never participates in fitting, early stopping, or model selection.
        history.append({'iteration':step+1,'train_p95_px':float(np.percentile(errors[train],95))})
    held=float(np.percentile(errors[validation],95))
    return dict(status='UNVERIFIED' if held<=3 else 'REJECT',
                validation_p95_px=held,train_p95_px=history[-1]['train_p95_px'],history=history,
                shape=vertices.tolist(),extrinsics=e.tolist(),intrinsics=k.tolist(),
                validation_count=int(validation.sum()),train_count=int(train.sum()),
                limitations='Detector consistency only; assumed intrinsics and frontal prior, no real scan or profile acceptance.')
