"""Shape-independent two-view diagnostic; not calibrated camera acceptance."""
import numpy as np


def fundamental(first, second):
    """Normalized eight-point fit. Inputs must already exclude validation points."""
    a,b=np.asarray(first,float),np.asarray(second,float)
    if a.ndim!=2 or a.shape[1]!=2 or b.shape!=a.shape or len(a)<8:
        raise ValueError('at least eight paired 2D points required')
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('finite points required')
    def normalize(points):
        center=points.mean(axis=0)
        distance=np.linalg.norm(points-center,axis=1).mean()
        if distance<1e-10:raise ValueError('degenerate points')
        scale=np.sqrt(2)/distance
        t=np.array([[scale,0,-scale*center[0]],[0,scale,-scale*center[1]],[0,0,1]])
        return (np.c_[points,np.ones(len(points))]@t.T),t
    x,ta=normalize(a);y,tb=normalize(b)
    design=np.einsum('ni,nj->nij',y,x).reshape(-1,9)
    if np.linalg.matrix_rank(design)<8:raise ValueError('degenerate correspondence geometry')
    _,_,vt=np.linalg.svd(design,full_matrices=True)
    u,s,v=np.linalg.svd(vt[-1].reshape(3,3));s[-1]=0
    f=tb.T@(u@np.diag(s)@v)@ta
    return f/np.linalg.norm(f)


def sampson_distance(matrix, first, second):
    """First-order symmetric epipolar distance in pixels, not reprojection error."""
    a,b=np.asarray(first,float),np.asarray(second,float)
    f=np.asarray(matrix,float)
    if a.ndim!=2 or a.shape[1]!=2 or b.shape!=a.shape or f.shape!=(3,3):
        raise ValueError('invalid epipolar inputs')
    if not all(np.isfinite(x).all() for x in (a,b,f)):
        raise ValueError('finite epipolar inputs required')
    x=np.c_[a,np.ones(len(a))];y=np.c_[b,np.ones(len(b))]
    fx=x@f.T;fty=y@f
    denominator=np.sum(fx[:,:2]**2+fty[:,:2]**2,axis=1)
    if np.any(denominator<1e-20):raise ValueError('undefined epipolar distance')
    return np.abs(np.sum(y*fx,axis=1))/np.sqrt(denominator)


def calibrated_pose(first, second, intrinsic_first, intrinsic_second):
    """Recover a training-only relative pose, with arbitrary unit baseline.

    This does not recover metric scale or certify supplied focal lengths.
    Validation observations must not be passed to this function.
    """
    normalized=[]
    for points,intrinsic in [(first,intrinsic_first),(second,intrinsic_second)]:
        points=np.asarray(points,float);k=np.asarray(intrinsic,float)
        if (k.shape!=(3,3) or not np.isfinite(k).all()
                or not np.allclose(k[2],[0,0,1]) or min(k[0,0],k[1,1])<=0):
            raise ValueError('invalid intrinsics')
        if points.ndim!=2 or points.shape[1]!=2 or not np.isfinite(points).all():
            raise ValueError('invalid observations')
        h=np.c_[points,np.ones(len(points))]@np.linalg.inv(k).T
        normalized.append(h[:,:2]/h[:,2:])
    a,b=normalized
    estimate=fundamental(a,b)
    u,s,vt=np.linalg.svd(estimate)
    if np.linalg.det(u)<0:u[:,-1]*=-1
    if np.linalg.det(vt)<0:vt[-1]*=-1
    w=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    candidates=[]
    p=np.c_[np.eye(3),np.zeros(3)]
    for r in [u@w@vt,u@w.T@vt]:
        for t in [u[:,2],-u[:,2]]:
            q=np.c_[r,t]
            system=np.stack([a[:,0,None]*p[2]-p[0],a[:,1,None]*p[2]-p[1],
                             b[:,0,None]*q[2]-q[0],b[:,1,None]*q[2]-q[1]],axis=1)
            _,_,vectors=np.linalg.svd(system)
            homogeneous=vectors[:,-1]
            finite=np.abs(homogeneous[:,3])>1e-10
            points=np.full((len(a),3),np.nan)
            points[finite]=homogeneous[finite,:3]/homogeneous[finite,3:]
            camera=points@r.T+t
            positive=finite&(points[:,2]>1e-8)&(camera[:,2]>1e-8)
            candidates.append((int(positive.sum()),r,t,points,positive))
    candidates.sort(key=lambda item:item[0],reverse=True)
    count,r,t,points,positive=candidates[0]
    # A unique solution and broad positive-depth support are necessary, not sufficient.
    if count==candidates[1][0] or count/len(a)<.95:
        raise ValueError('ambiguous or insufficient positive-depth support')
    return dict(status='UNVERIFIED',extrinsic=np.c_[r,t].tolist(),
                positive_depth_fraction=count/len(a),
                essential_singular_ratio=float(s[1]/s[0]),
                limitations='Assumed calibration; unit baseline; training-only pose, not camera acceptance.')
