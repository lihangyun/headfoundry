"""Bounded experimental profile-envelope step using fixed cameras."""
import numpy as np
from headfoundry.surface_diagnostic import fit_surface


def _curve_terms(points, polyline):
    """Closest-point residuals to an ordered open 2D curve, including endpoints.

    The caller supplies a semantic curve: this does not segment a silhouette
    or connect disconnected components. Repeated vertices are safe.
    """
    points=np.asarray(points,float);line=np.asarray(polyline,float)
    if (points.ndim!=2 or points.shape[1:]!=(2,) or line.ndim!=2
            or line.shape[1:]!=(2,) or len(line)<2
            or not np.isfinite(points).all() or not np.isfinite(line).all()):
        raise ValueError('finite 2D points and at least two curve vertices required')
    start=line[:-1];delta=np.diff(line,axis=0);length2=(delta*delta).sum(1)
    offsets=points[:,None,:]-start
    t=np.divide((offsets*delta).sum(2),length2,out=np.zeros(offsets.shape[:2]),where=length2>0)
    residual=start+np.clip(t,0,1)[...,None]*delta-points[:,None,:]
    nearest=np.argmin((residual*residual).sum(2),axis=1)
    selected=np.arange(len(points))
    return residual[selected,nearest],delta[nearest],(t[selected,nearest]>0)&(t[selected,nearest]<1)


def curve_residuals(points, polyline):
    """Closest-point residuals to an ordered open 2D curve, including endpoints.

    The caller supplies a semantic curve: this does not segment a silhouette
    or connect disconnected components. Repeated vertices are safe.
    """
    return _curve_terms(points,polyline)[0]


def curve_residual_jacobian(points, polyline):
    """Residual and its piecewise 2x2 point derivative; ties need not be smooth."""
    residual,delta,interior=_curve_terms(points,polyline)
    jacobian=np.broadcast_to(-np.eye(2),(len(residual),2,2)).copy()
    d=delta[interior]
    jacobian[interior]+=d[:,:,None]*d[:,None,:]/(d*d).sum(1)[:,None,None]
    return residual,jacobian


def project_with_basis_jacobian(vertices, basis, projection):
    """Project current 3D points and differentiate their supplied affine basis."""
    v,b,p=(np.asarray(a,float) for a in (vertices,basis,projection))
    if (v.ndim!=2 or v.shape[1:]!=(3,) or b.ndim!=3 or b.shape[:2]!=v.shape
            or b.shape[2]==0 or p.shape!=(3,4) or not all(np.isfinite(a).all() for a in (v,b,p))):
        raise ValueError('finite matching points, affine basis and camera required')
    h=np.c_[v,np.ones(len(v))] @ p.T
    if np.any(h[:,2]<=0):raise ValueError('points behind camera')
    uv=h[:,:2]/h[:,2:]
    bh=np.einsum('ij,njk->nik',p[:,:3],b)
    return uv,(bh[:,:2]-uv[:,:,None]*bh[:,2:3])/h[:,2,None,None]


def envelope_edge(vertices, edges, projection, row, direction):
    """Outer projected edge at a pixel row, with perspective-correct 3D weights.

    All vertices must be in front. This is an outer envelope, not semantic
    face segmentation: callers must exclude unrelated foreground geometry.
    """
    return envelope_edges(vertices,edges,projection,[row],direction)[0]


def envelope_edges(vertices, edges, projection, rows, direction):
    """Batch the same row envelopes with one projection; no visibility claim."""
    v=np.asarray(vertices,float);edges=np.asarray(edges);p=np.asarray(projection,float)
    rows=np.asarray(rows,float)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or not np.isfinite(v).all()
            or edges.ndim!=2 or edges.shape[1:]!=(2,) or not np.issubdtype(edges.dtype,np.integer)
            or np.any(edges<0) or np.any(edges>=len(v)) or p.shape!=(3,4)
            or not np.isfinite(p).all() or rows.ndim!=1 or not np.isfinite(rows).all() or direction not in (-1,1)):
        raise ValueError('invalid envelope inputs')
    h=np.c_[v,np.ones(len(v))]@p.T
    if np.any(h[:,2]<=0):raise ValueError('surface behind camera')
    uv=h[:,:2]/h[:,2:];segments=uv[edges];dy=segments[:,1,1]-segments[:,0,1]
    low,high=segments[:,:,1].min(1),segments[:,:,1].max(1)
    result=[]
    for row in rows:
        ids=np.flatnonzero((low<=row)&(high>=row))
        if not len(ids):result.append(None);continue
        t=np.divide(row-segments[ids,0,1],dy[ids],out=np.zeros(len(ids)),where=np.abs(dy[ids])>=1e-12)
        horizontal=np.abs(dy[ids])<1e-12
        t[horizontal]=np.argmax(direction*segments[ids[horizontal],:,0],axis=1)
        x=(1-t)*segments[ids,0,0]+t*segments[ids,1,0]
        selected=int(np.argmax(direction*x));index=ids[selected];parameter=t[selected]
        weights=np.array([1-parameter,parameter])/h[edges[index],2];weights/=weights.sum()
        result.append((edges[index],weights,np.array([x[selected],row])))
    return result


def envelope_edges_with_jacobian(vertices, edges, projection, rows, direction, basis):
    """Covered row envelopes plus affine-coordinate x derivatives on their edges.

    Edge changes are piecewise smooth. A moving horizontal support has no unique
    derivative at the supplied row and is rejected rather than called smooth.
    """
    v,b=np.asarray(vertices,float),np.asarray(basis,float)
    if b.ndim!=3 or b.shape[:2]!=v.shape or b.shape[2]==0 or not np.isfinite(b).all():
        raise ValueError('matching finite affine vertex basis required')
    supports=envelope_edges(v,edges,projection,rows,direction)
    if any(s is None for s in supports):raise ValueError('Jacobian requires covered rows')
    if not supports:return supports,np.empty((0,b.shape[2]))
    ids=np.array([s[0] for s in supports])
    uv,jac=project_with_basis_jacobian(v[ids.ravel()],b[ids.ravel()],projection)
    uv=uv.reshape(-1,2,2);jac=jac.reshape(-1,2,2,b.shape[2])
    delta=uv[:,1]-uv[:,0];dy=delta[:,1];horizontal=np.abs(dy)<1e-12
    if np.any(np.abs(jac[horizontal,:,1])>1e-12):
        raise ValueError('moving horizontal row support has no unique derivative')
    t=np.divide(np.asarray(rows,float)-uv[:,0,1],dy,out=np.zeros(len(ids)),where=~horizontal)
    jt=np.divide(-(jac[:,0,1]+t[:,None]*(jac[:,1,1]-jac[:,0,1])),dy[:,None],
                 out=np.zeros((len(ids),b.shape[2])),where=~horizontal[:,None])
    result=jac[:,0,0]+t[:,None]*(jac[:,1,0]-jac[:,0,0])+delta[:,0,None]*jt
    if horizontal.any():
        selected=np.argmax(direction*uv[horizontal,:,0],axis=1)
        result[horizontal]=jac[horizontal][np.arange(horizontal.sum()),selected,0]
    return supports,result


def fit_profile_step(vertices, faces, projections, contours, directions, max_move=.015, *, frontal_projection=None,
                     continuous=False, protected_vertices=(), contour_face_mask=None):
    v=np.asarray(vertices,float);f=np.asarray(faces,int);p=np.asarray(projections,float)
    if not np.isfinite(max_move) or max_move<=0 or len(contours)!=len(p) or len(directions)!=len(p):
        raise ValueError('invalid profile inputs')
    fixed=np.asarray(protected_vertices)
    if (fixed.ndim!=1 or (fixed.size and not np.issubdtype(fixed.dtype,np.integer))
            or np.any(fixed<0) or np.any(fixed>=len(v))):raise ValueError('invalid protected vertices')
    fixed=fixed.astype(int)
    eligible=np.ones(len(f),bool) if contour_face_mask is None else np.asarray(contour_face_mask)
    if eligible.shape!=(len(f),) or eligible.dtype!=np.dtype(bool):raise ValueError('boolean contour face mask required')
    obs=np.zeros((len(p),len(v),2));mask=np.zeros((len(p),len(v)),bool)
    contour_faces=f[eligible]
    edges=np.unique(np.sort(np.concatenate([contour_faces[:,[0,1]],contour_faces[:,[1,2]],contour_faces[:,[2,0]]]),axis=1),axis=0)
    eligible_vertices=np.unique(contour_faces)
    constraints=[];counts=np.zeros(len(p),int)
    for view,(camera,curve,direction) in enumerate(zip(p,contours,directions)):
        curve=np.asarray(curve,float)
        if curve.ndim!=2 or curve.shape[1]!=2 or not np.isfinite(curve).all() or direction not in (-1,1):raise ValueError('invalid contour')
        if continuous:
            supports=envelope_edges(v,edges,camera,curve[:,1],direction)
        else:
            h=np.c_[v,np.ones(len(v))]@camera.T
            if np.any(h[:,2]<=0):raise ValueError('surface behind camera')
            uv=h[:,:2]/h[:,2:]
        for index,target in enumerate(curve):
            if continuous:
                support=supports[index]
                if support is not None:
                    ids,weights,_=support;constraints.append((view,ids,weights,target));counts[view]+=1
                continue
            nearby=eligible_vertices[np.abs(uv[eligible_vertices,1]-target[1])<=5]
            if not len(nearby):continue
            vertex=nearby[np.argmax(direction*uv[nearby,0])]
            if mask[view,vertex]:continue
            obs[view,vertex]=target;mask[view,vertex]=True
    selected=np.flatnonzero(mask.any(0));free=set(selected.tolist())
    for _,ids,_,_ in constraints:free.update(ids.tolist())
    # Six topology rings only: unrelated surface vertices remain exact.
    for _ in range(6):
        touch=np.isin(f,list(free)).any(1);free.update(f[touch].ravel().tolist())
    protected=np.union1d(np.setdiff1d(np.arange(len(v)),list(free)),fixed)
    rays=None
    if frontal_projection is not None:
        front=np.asarray(frontal_projection,float)
        if front.shape!=(3,4) or not np.isfinite(front).all() or np.linalg.matrix_rank(front[:,:3])<3:
            raise ValueError('finite perspective frontal projection required')
        if np.any(np.c_[v,np.ones(len(v))]@front[2]<=0):raise ValueError('surface behind frontal camera')
        center=np.linalg.solve(front[:,:3],-front[:,3])
        rays=v-center
    candidate=fit_surface(v,obs,p,f,protected,regularization=100,observation_mask=mask,
                          displacement_directions=rays,edge_observations=constraints)
    delta=candidate-v;largest=np.linalg.norm(delta,axis=1).max()
    step=min(1.,max_move/max(largest,1e-12))
    normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    while step>1e-6:
        result=v+step*delta
        updated=np.cross(result[f[:,1]]-result[f[:,0]],result[f[:,2]]-result[f[:,0]])
        front_positive=frontal_projection is None or (np.c_[result,np.ones(len(result))]@front[2]>0).all()
        if front_positive and ((updated*normal).sum(1)>0).all() and (np.linalg.norm(updated,axis=1)>=.1*np.linalg.norm(normal,axis=1)).all():break
        step*=.5
    else:raise ValueError('no non-flipping bounded profile step')
    return result,dict(status='UNVERIFIED',selected_per_view=(counts if continuous else mask.sum(1)).tolist(),
                       continuous_edge_constraints=continuous,
                       frontal_projection_preserved=frontal_projection is not None,
                       maximum_displacement=float(np.linalg.norm(result-v,axis=1).max()),step=float(step),
                       protected_vertices=protected.tolist(),limitations='Outer-envelope associations are not semantic correspondences; fitting errors are not held-out evidence.')
