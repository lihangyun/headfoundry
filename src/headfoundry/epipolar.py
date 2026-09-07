"""Shape-independent two-view diagnostic; not calibrated camera acceptance."""
import numpy as np


def _triangulate(a, b, p, q):
    system=np.stack([a[:,0,None]*p[2]-p[0],a[:,1,None]*p[2]-p[1],
                     b[:,0,None]*q[2]-q[0],b[:,1,None]*q[2]-q[1]],axis=1)
    _,_,vectors=np.linalg.svd(system)
    homogeneous=vectors[:,-1]
    finite=np.abs(homogeneous[:,3])>1e-10
    points=np.full((len(a),3),np.nan)
    points[finite]=homogeneous[finite,:3]/homogeneous[finite,3:]
    return points


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
            points=_triangulate(a,b,p,q)
            camera=points@r.T+t
            positive=np.isfinite(points).all(axis=1)&(points[:,2]>1e-8)&(camera[:,2]>1e-8)
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


def refine_pose(first, second, intrinsic_first, intrinsic_second):
    """Training-only nonlinear pose refinement, retaining supplied calibration.

    Requires the optional geometry dependency. Uses signed Sampson residuals,
    not a face prior. Pairwise consistency cannot replace multiview validation.
    """
    from scipy.optimize import least_squares
    from scipy.spatial.transform import Rotation
    initial=calibrated_pose(first,second,intrinsic_first,intrinsic_second)
    a,b=np.asarray(first,float),np.asarray(second,float)
    ka,kb=np.asarray(intrinsic_first,float),np.asarray(intrinsic_second,float)
    e=np.array(initial['extrinsic']);t=e[:,3]
    start=np.r_[Rotation.from_matrix(e[:,:3]).as_rotvec(),np.arctan2(t[1],t[0]),np.arcsin(np.clip(t[2],-1,1))]
    span=np.array([.6,.6,.6,1.,.8])
    one=np.c_[a,np.ones(len(a))];two=np.c_[b,np.ones(len(b))]
    ia,ib=np.linalg.inv(ka),np.linalg.inv(kb)
    def unpack(x):
        r=Rotation.from_rotvec(x[:3]).as_matrix()
        az,el=x[3:];t=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
        skew=np.array([[0,-t[2],t[1]],[t[2],0,-t[0]],[-t[1],t[0],0]])
        f=ib.T@skew@r@ia
        return r,t,f/np.linalg.norm(f)
    def residual(x):
        f=unpack(x)[2];fx=one@f.T;fty=two@f
        denominator=np.maximum(np.sum(fx[:,:2]**2+fty[:,:2]**2,axis=1),1e-20)
        return np.sum(two*fx,axis=1)/np.sqrt(denominator)
    fit=least_squares(residual,start,bounds=(start-span,start+span),loss='soft_l1',f_scale=2.,
                      max_nfev=500,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    r,t,f=unpack(fit.x)
    points=_triangulate(a,b,ka@np.c_[np.eye(3),np.zeros(3)],kb@np.c_[r,t])
    positive=np.isfinite(points).all(axis=1)&(points[:,2]>1e-8)&((points@r.T+t)[:,2]>1e-8)
    if not fit.success or positive.mean()<.95:
        raise ValueError('refinement failed convergence or positive-depth check')
    return dict(status='UNVERIFIED',extrinsic=np.c_[r,t].tolist(),fundamental=f.tolist(),
                positive_depth_fraction=float(positive.mean()),nfev=int(fit.nfev),
                train_sampson_p95_px=float(np.percentile(np.abs(residual(fit.x)),95)),
                limitations='Fixed assumed calibration and unit baseline; no multiview or visual acceptance.')


def robust_refine_pose(first, second, intrinsic_first, intrinsic_second, *,
                       threshold_px=2., min_support_fraction=.6, min_parallax_deg=1.,
                       iterations=512, seed=0):
    """Training-only deterministic consensus followed by inlier pose refinement.

    Callers must split off validation before calling. Neither the consensus
    count nor the selected-point error is a camera acceptance measurement.
    The fixed sampling budget is a bounded diagnostic, not guaranteed recovery.
    """
    a,b=np.asarray(first,float),np.asarray(second,float)
    ka,kb=np.asarray(intrinsic_first,float),np.asarray(intrinsic_second,float)
    if (a.ndim!=2 or a.shape[1]!=2 or b.shape!=a.shape or len(a)<12
            or not all(np.isfinite(x).all() for x in (a,b))):
        raise ValueError('at least twelve finite paired training points required')
    if (not np.isfinite(threshold_px) or threshold_px<=0
            or not np.isfinite(min_support_fraction) or not 0<min_support_fraction<=1
            or not np.isfinite(min_parallax_deg) or not 0<min_parallax_deg<180
            or not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1
            or not isinstance(seed,int) or isinstance(seed,bool) or seed<0):
        raise ValueError('invalid consensus settings')
    for k in (ka,kb):
        if (k.shape!=(3,3) or not np.isfinite(k).all() or not np.allclose(k[2],[0,0,1])
                or not np.allclose(k[np.tril_indices(3,-1)],0)
                or min(k[0,0],k[1,1])<=0 or abs(np.linalg.det(k))<1e-12):
            raise ValueError('invalid intrinsics')
    if any(len(np.unique(x,axis=0))!=len(x) for x in (a,b)):
        raise ValueError('duplicate training endpoints do not provide independent support')
    if any(np.linalg.matrix_rank(x-x.mean(axis=0))<2 for x in (a,b)):
        raise ValueError('degenerate correspondence geometry')
    ia,ib=np.linalg.inv(ka),np.linalg.inv(kb)
    required=max(12,int(np.ceil(min_support_fraction*len(a))))
    rng=np.random.default_rng(seed); best=None; best_score=(-1,-np.inf)
    for _ in range(iterations):
        selected=rng.choice(len(a),8,replace=False)
        try:
            e=np.asarray(calibrated_pose(a[selected],b[selected],ka,kb)['extrinsic'])
            tx,ty,tz=e[:,3]
            skew=np.array([[0,-tz,ty],[tz,0,-tx],[-ty,tx,0]])
            f=ib.T@skew@e[:,:3]@ia
            distance=sampson_distance(f,a,b)
        except (ValueError,np.linalg.LinAlgError):
            continue
        mask=distance<=threshold_px
        score=(int(mask.sum()),-float(np.minimum(distance,threshold_px).sum()))
        if score>best_score:
            best_score=score; best=mask
    if best is None or best.sum()<required:
        raise ValueError(f'insufficient training consensus support: {max(best_score[0],0)}/{len(a)}; require {required}')
    result=refine_pose(a[best],b[best],ka,kb)
    distance=sampson_distance(result['fundamental'],a,b)
    support=int(np.count_nonzero(distance<=threshold_px))
    if support<required:
        raise ValueError(f'refined pose lost training consensus support: {support}/{len(a)}; require {required}')
    e=np.asarray(result['extrinsic'])
    points=_triangulate(a[best],b[best],ka@np.c_[np.eye(3),np.zeros(3)],kb@e)
    positive=np.isfinite(points).all(axis=1)&(points[:,2]>1e-8)&((points@e[:,:3].T+e[:,3])[:,2]>1e-8)
    first_rays=points[positive];second_rays=first_rays+e[:,:3].T@e[:,3]
    first_rays=first_rays/np.linalg.norm(first_rays,axis=1,keepdims=True)
    second_rays=second_rays/np.linalg.norm(second_rays,axis=1,keepdims=True)
    angles=np.degrees(np.arccos(np.clip(np.sum(first_rays*second_rays,axis=1),-1,1)))
    parallax=np.percentile(angles,[5,50,95])
    # Depth uncertainty amplifies roughly as 1/sin(parallax); one degree already
    # permits about 57x angular-noise amplification. This is a guard, not accuracy proof.
    if parallax[1]<min_parallax_deg:
        raise ValueError(f'insufficient triangulation parallax: median {parallax[1]:.6f} deg; require {min_parallax_deg}')
    result.update(candidate_count=len(a),fit_inlier_count=int(best.sum()),
                  fit_inlier_indices=np.flatnonzero(best).tolist(),
                  support_count=support,support_fraction=support/len(a),
                  candidate_sampson_p95_px=float(np.percentile(distance,95)),
                  threshold_px=float(threshold_px),min_support_fraction=float(min_support_fraction),
                  parallax_p05_deg=float(parallax[0]),parallax_median_deg=float(parallax[1]),
                  parallax_p95_deg=float(parallax[2]),parallax_positive_count=int(positive.sum()),
                  min_parallax_deg=float(min_parallax_deg),
                  iterations=iterations,seed=seed,
                  limitations='Training-selected consensus only; assumed calibration, unit baseline, no held-out or visual acceptance.')
    return result
