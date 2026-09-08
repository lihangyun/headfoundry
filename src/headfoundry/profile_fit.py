"""Bounded experimental profile-envelope step using fixed cameras."""
import numpy as np
from headfoundry.surface_diagnostic import fit_surface


def fit_profile_step(vertices, faces, projections, contours, directions, max_move=.015):
    v=np.asarray(vertices,float);f=np.asarray(faces,int);p=np.asarray(projections,float)
    if not np.isfinite(max_move) or max_move<=0 or len(contours)!=len(p) or len(directions)!=len(p):
        raise ValueError('invalid profile inputs')
    obs=np.zeros((len(p),len(v),2));mask=np.zeros((len(p),len(v)),bool)
    for view,(camera,curve,direction) in enumerate(zip(p,contours,directions)):
        curve=np.asarray(curve,float)
        if curve.ndim!=2 or curve.shape[1]!=2 or not np.isfinite(curve).all() or direction not in (-1,1):raise ValueError('invalid contour')
        h=np.c_[v,np.ones(len(v))]@camera.T
        if np.any(h[:,2]<=0):raise ValueError('surface behind camera')
        uv=h[:,:2]/h[:,2:]
        for target in curve:
            nearby=np.flatnonzero(np.abs(uv[:,1]-target[1])<=5)
            if not len(nearby):continue
            vertex=nearby[np.argmax(direction*uv[nearby,0])]
            if mask[view,vertex]:continue
            obs[view,vertex]=target;mask[view,vertex]=True
    selected=np.flatnonzero(mask.any(0));free=set(selected.tolist())
    # Six topology rings only: unrelated surface vertices remain exact.
    for _ in range(6):
        touch=np.isin(f,list(free)).any(1);free.update(f[touch].ravel().tolist())
    protected=np.setdiff1d(np.arange(len(v)),list(free))
    candidate=fit_surface(v,obs,p,f,protected,regularization=100,observation_mask=mask)
    delta=candidate-v;largest=np.linalg.norm(delta,axis=1).max()
    step=min(1.,max_move/max(largest,1e-12))
    normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    while step>1e-6:
        result=v+step*delta
        updated=np.cross(result[f[:,1]]-result[f[:,0]],result[f[:,2]]-result[f[:,0]])
        if ((updated*normal).sum(1)>0).all() and (np.linalg.norm(updated,axis=1)>=.1*np.linalg.norm(normal,axis=1)).all():break
        step*=.5
    else:raise ValueError('no non-flipping bounded profile step')
    return result,dict(status='UNVERIFIED',selected_per_view=mask.sum(1).tolist(),
                       maximum_displacement=float(np.linalg.norm(result-v,axis=1).max()),step=float(step),
                       protected_vertices=protected.tolist(),limitations='Approximate vertex-envelope associations; fitting errors are not held-out evidence.')
