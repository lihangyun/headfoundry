"""Float64 pOSE conditional-point math;not camera,medical or head acceptance."""
import numpy as np


def reduce_points(cams,uv,mask):
    if np.iscomplexobj(cams) or np.iscomplexobj(uv):
        raise ValueError('real point systems required')
    cams,uv,mask = np.asarray(cams,float),np.asarray(uv,float),np.asarray(mask)
    if (mask.ndim!=2 or mask.dtype.kind!='b' or not all(mask.shape)
            or cams.shape!=(mask.shape[0],3,4) or uv.shape!=(*mask.shape,2)
            or not np.isfinite(cams).all() or not np.isfinite(uv).all()):
        raise ValueError('finite compatible cameras/observations and Boolean mask required')
    v,n = mask.shape
    valid = mask.T
    observed = uv.transpose(1,0,2)
    sw,sa = np.sqrt(.95),np.sqrt(.05)
    a_ose = sw*(cams[None,:,:2,:3]-observed[:,:,:,None]*cams[None,:,2:3,:3])
    a_aff = np.broadcast_to(sa*cams[None,:,:2,:3],a_ose.shape)
    a = (np.concatenate([a_ose,a_aff],axis=2)*valid[:,:,None,None]).reshape(n,4*v,3)
    b_ose = sw*(cams[None,:,:2,3]-observed*cams[None,:,2,3,None])
    b_aff = sa*(cams[None,:,:2,3]-observed)
    b = (np.concatenate([b_ose,b_aff],axis=2)*valid[:,:,None]).reshape(n,4*v)
    u,s,vh = np.linalg.svd(a,full_matrices=False)
    cutoff = (np.finfo(float).eps*np.maximum(4*valid.sum(1),3))[:,None]*s[:,:1]
    if np.any((s>cutoff).sum(1)!=3):
        raise ValueError('rank-deficient conditional point')
    coefficient = -np.einsum('nmk,nm->nk',u,b)/s
    points = np.einsum('nki,nk->ni',vh,coefficient)
    residual = (np.einsum('nmk,nk->nm',a,points)+b).reshape(n,v,4)
    xh = np.c_[points,np.ones(n)]
    grad = np.empty_like(cams)
    grad[:,:2] = 2*np.einsum('nvi,nj->vij',sw*residual[:,:,:2]+sa*residual[:,:,2:],xh)
    grad[:,2] = -2*sw*np.einsum('nv,nj->vj',np.sum(residual[:,:,:2]*observed,axis=2),xh)
    cost = float(np.sum(residual**2))
    if not np.isfinite(cost) or not np.isfinite(points).all() or not np.isfinite(grad).all():
        raise ValueError('nonfinite conditional solution')
    return cost,grad,points


def scalar_reference(cams,uv,mask,visible=None):
    # Exact historical per-point loop,only expose its existing point output.
    v,n = mask.shape
    visible = [np.flatnonzero(mask[:,j]) for j in range(n)] if visible is None else visible
    sw,sa = np.sqrt(.95),np.sqrt(.05)
    grad = np.zeros_like(cams)
    points = np.empty((n,3))
    cost = 0.
    for j, views in enumerate(visible):
        c, u = cams[views], uv[views,j]
        a = np.concatenate([sw*(c[:,:2,:3]-u[:,:,None]*c[:,2:3,:3]),
                            sa*c[:,:2,:3]],axis=1).reshape(-1,3)
        b = np.concatenate([sw*(c[:,:2,3]-u*c[:,2,3,None]),
                            sa*(c[:,:2,3]-u)],axis=1).ravel()
        x, _, rank, _ = np.linalg.lstsq(a,-b,rcond=None)
        if rank < 3:
            raise ValueError('rank-deficient conditional point')
        points[j] = x
        residual = (a@x+b).reshape(-1,4)
        cost += float(np.sum(residual**2))
        xh = np.r_[x,1.]
        g = np.zeros_like(c)
        g[:,:2] = 2*(sw*residual[:,:2]+sa*residual[:,2:])[:,:,None]*xh
        g[:,2] = -2*sw*np.sum(residual[:,:2]*u,axis=1)[:,None]*xh
        np.add.at(grad,views,g)
    return cost,grad,points


def check():
    rng = np.random.default_rng(285)
    cameras = rng.normal(0,.1,(4,3,4))
    cameras[:,2,3] = 1
    uv = rng.normal(0,.2,(4,12,2))
    mask = np.ones((4,12),bool)
    for j in range(0,12,2):
        mask[j%4,j] = False
    old,new = scalar_reference(cameras,uv,mask),reduce_points(cameras,uv,mask)
    for a,b in zip(old,new):
        np.testing.assert_allclose(a,b,rtol=1e-8,atol=1e-10)
    for bad in (np.zeros_like(mask),mask.astype(float)):
        try:
            reduce_points(cameras,uv,bad)
        except ValueError:
            pass
        else:
            raise ValueError('invalid/rank-deficient mask accepted')
    try:
        reduce_points(cameras.astype(complex)+1j,uv,mask)
    except ValueError:
        pass
    else:
        raise ValueError('complex system accepted')
    return {'status':'TECHNICAL_CHECK_PASSED','scope':'conditional-math-only'}

