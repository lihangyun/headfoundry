"""Bounded depth/camera registration of supplied training correspondences only."""
import numpy as np


def refine_depth_cameras(camera_points, extrinsics, intrinsics=None, *, depth_offset=False):
    """Keep first camera/depth fixed; fit other poses and one depth scale per view.

    Rotational increments: +/-0.1 rad per component; translations: +/-0.1 in
    input units; log depth scale: +/-0.1. No dense deformation or held-out data.
    """
    from scipy.optimize import least_squares
    from scipy.spatial.transform import Rotation
    q=np.asarray(camera_points,float); e=np.asarray(extrinsics,float)
    if not isinstance(depth_offset,bool):raise ValueError('depth_offset must be boolean')
    stride=8 if depth_offset else 7
    if (q.ndim!=3 or q.shape[2]!=3 or q.shape[0]<2 or q.shape[1]<6
            or e.shape!=(q.shape[0],3,4) or not np.isfinite(q).all()
            or not np.isfinite(e).all() or np.any(q[:,:,2]<=0)):
        raise ValueError('finite positive-depth matched camera points and extrinsics required')
    r=e[:,:,:3]
    if not np.allclose(r@r.transpose(0,2,1),np.eye(3),atol=1e-5) or not np.allclose(np.linalg.det(r),1,atol=1e-5):
        raise ValueError('right-handed rigid cameras required')
    spread=np.linalg.svd(q-q.mean(1,keepdims=True),compute_uv=False)
    if np.any(spread[:,1]<=1e-6*np.maximum(spread[:,0],1e-12)):
        raise ValueError('noncollinear training points required')
    k=None if intrinsics is None else np.asarray(intrinsics,float)
    if k is not None:
        if (k.shape!=(len(q),3,3) or not np.isfinite(k).all()
                or not np.allclose(k[:,2],[0,0,1]) or np.any(k[:,[0,1],[0,1]]<=0)):
            raise ValueError('finite pixel-space intrinsics required')
        pixels=np.einsum('vij,vnj->vni',k,q)
        pixels=pixels[:,:,:2]/pixels[:,:,2:]

    def unpack(parameters):
        delta=parameters.reshape(-1,stride); result=e.copy()
        result[1:,:,:3]=Rotation.from_rotvec(delta[:,:3]).as_matrix()@r[1:]
        result[1:,:,3]+=delta[:,3:6]
        scales=np.r_[1.,np.exp(delta[:,6])]
        offsets=np.r_[0.,delta[:,7]] if depth_offset else np.zeros(len(q))
        return result,scales,offsets

    def residual(parameters):
        cameras,scales,offsets=unpack(parameters)
        corrected=q*scales[:,None,None]+q/q[:,:,2:]*offsets[:,None,None]
        world=np.einsum('vji,vnj->vni',cameras[:,:,:3],corrected-cameras[:,None,:,3])
        residuals=((world-world.mean(0))/0.01).ravel()
        if k is not None:
            cam=np.einsum('vij,nj->vni',cameras[:,:,:3],world.mean(0))+cameras[:,None,:,3]
            h=np.einsum('vij,vnj->vni',k,cam)
            reprojection=(h[:,:,:2]/np.maximum(h[:,:,2:],1e-6)-pixels)/3.
            residuals=np.r_[residuals,reprojection.ravel()]
        return residuals

    initial=np.zeros((len(q)-1)*stride)
    lower=np.full_like(initial,-.1);upper=np.full_like(initial,.1)
    if depth_offset:lower.reshape(-1,stride)[:,7]=np.maximum(-.1,-q[1:,:,2].min(1)*np.exp(-.1)*.9999)
    fit=least_squares(residual,initial,bounds=(lower,upper),loss='soft_l1',max_nfev=200,
                      ftol=1e-9,xtol=1e-9,gtol=1e-9)
    cameras,scales,offsets=unpack(fit.x)
    def costs(parameters):
        values=np.sqrt(1+residual(parameters)**2)-1
        return np.array([values[:q.size].sum(),values[q.size:].sum()])
    active=[]
    active_indices=np.flatnonzero((fit.x-lower<1e-4)|(upper-fit.x<1e-4))
    for index in active_indices:
        step=np.zeros_like(fit.x);step[index]=1e-6
        gradient=(costs(fit.x+step)-costs(fit.x-step))/(2e-6)
        active.append(dict(view=int(index//stride+1),parameter=['rx','ry','rz','tx','ty','tz','log_depth_scale','depth_offset'][index%stride],
                           value=float(fit.x[index]),depth_cost_derivative=float(gradient[0]),
                           pixel_cost_derivative=float(gradient[1])))
    return cameras,scales,dict(status='UNVERIFIED',converged=bool(fit.success),
                              evaluations=fit.nfev,bound_active=bool(len(active_indices)),depth_offsets=offsets.tolist(),
                              initial_rms=float(np.sqrt(np.mean(residual(initial)[:q.size]**2))*.01),
                              final_rms=float(np.sqrt(np.mean(residual(fit.x)[:q.size]**2))*.01),
                              pixel_term=k is not None,active_parameters=active,
                              depth_pixel_costs=costs(fit.x).tolist())
