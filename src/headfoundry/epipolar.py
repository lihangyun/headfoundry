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
