"""Bounded experimental profile-envelope step using fixed cameras."""
import numpy as np
from headfoundry.surface_diagnostic import fit_surface


def curve_residuals(points, polyline):
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
    return residual[np.arange(len(points)),nearest]


def envelope_edge(vertices, edges, projection, row, direction):
    """Outer projected edge at a pixel row, with perspective-correct 3D weights.

    All vertices must be in front. This is an outer envelope, not semantic
    face segmentation: callers must exclude unrelated foreground geometry.
    """
    v=np.asarray(vertices,float);edges=np.asarray(edges);p=np.asarray(projection,float)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or not np.isfinite(v).all()
            or edges.ndim!=2 or edges.shape[1:]!=(2,) or not np.issubdtype(edges.dtype,np.integer)
            or np.any(edges<0) or np.any(edges>=len(v)) or p.shape!=(3,4)
            or not np.isfinite(p).all() or not np.isfinite(row) or direction not in (-1,1)):
        raise ValueError('invalid envelope inputs')
    h=np.c_[v,np.ones(len(v))]@p.T
    if np.any(h[:,2]<=0):raise ValueError('surface behind camera')
    uv=h[:,:2]/h[:,2:];segments=uv[edges];dy=segments[:,1,1]-segments[:,0,1]
    crossing=(segments[:,:,1].min(1)<=row)&(segments[:,:,1].max(1)>=row)
    candidates=[]
    for index in np.flatnonzero(crossing):
        if abs(dy[index])<1e-12:
            t=float(np.argmax(direction*segments[index,:,0]))
        else:t=float((row-segments[index,0,1])/dy[index])
        x=float((1-t)*segments[index,0,0]+t*segments[index,1,0])
        candidates.append((direction*x,index,t,x))
    if not candidates:return None
    _,index,t,x=max(candidates,key=lambda a:a[0])
    weights=np.array([1-t,t])/h[edges[index],2];weights/=weights.sum()
    return edges[index],weights,np.array([x,row])


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
        h=np.c_[v,np.ones(len(v))]@camera.T
        if np.any(h[:,2]<=0):raise ValueError('surface behind camera')
        uv=h[:,:2]/h[:,2:]
        for target in curve:
            if continuous:
                support=envelope_edge(v,edges,camera,target[1],direction)
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
