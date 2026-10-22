"""Immutable sparse host/target observations;no optimizer or visibility oracle."""
import numpy as np

from direct_patch_camera import residual as pair_residual


def residual(images,pixels,hosts,observations,inverse_depth,poses,log_gains,biases,log_focal):
    """Return ExP residuals and ExPx2 warps in supplied (point,target) order.

    Each NxPx2 patch has a host camera and one positive host inverse depth.
    Missing edges are allowed;invalid included edges raise,never disappear.
    Graph connectivity/observability and physical visibility are caller gates.
    """
    images,pixels,inverse_depth,poses,log_gains,biases=[np.asarray(x,float) for x in
        (images,pixels,inverse_depth,poses,log_gains,biases)]
    hosts,observations=np.asarray(hosts),np.asarray(observations)
    if (images.ndim!=3 or images.shape[1:]!=(1280,720) or len(images)<2
            or pixels.ndim!=3 or pixels.shape[-1]!=2 or min(pixels.shape[:2])<1
            or inverse_depth.shape!=(len(pixels),) or (inverse_depth<=0).any()
            or poses.shape!=(len(images),4,4) or log_gains.shape!=(len(images),)
            or biases.shape!=(len(images),) or not np.isscalar(log_focal)
            or not np.isfinite(log_focal) or not all(np.isfinite(a).all() for a in
                (images,pixels,inverse_depth,poses,log_gains,biases))
            or images.min()<0 or images.max()>1):
        raise ValueError('finite native images,patches and positive inverse depths required')
    if (hosts.shape!=(len(pixels),) or hosts.dtype.kind not in 'iu'
            or observations.ndim!=2 or observations.shape[1:]!=(2,)
            or len(observations)<1 or observations.dtype.kind not in 'iu'
            or (hosts<0).any() or (hosts>=len(images)).any()
            or (observations<0).any() or (observations[:,0]>=len(pixels)).any()
            or (observations[:,1]>=len(images)).any()):
        raise ValueError('nonempty in-range integer host and observation IDs required')
    point_ids,targets=observations.T
    if (np.any(hosts[point_ids]==targets)
            or len(np.unique(observations,axis=0))!=len(observations)
            or len(np.unique(point_ids))!=len(pixels)):
        raise ValueError('self/duplicate edges and orphan patches are forbidden')
    if (not np.allclose(poses[:,3,:],[0,0,0,1],atol=1e-12,rtol=0)
            or not np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-10,rtol=0)
            or not np.all(np.linalg.det(poses[:,:3,:3])>0)):
        raise ValueError('all global poses must be proper SE3')
    try:
        with np.errstate(over='raise',invalid='raise'):
            gains=np.exp(log_gains);focal=np.exp(log_focal)
    except FloatingPointError as error:
        raise ValueError('global focal/exposure overflow') from error
    if (not np.isfinite(gains).all() or (gains<=0).any()
            or not np.isfinite(focal) or focal<=0):
        raise ValueError('positive finite global focal/exposure required')
    values=np.empty((len(observations),pixels.shape[1]))
    warps=np.empty((*values.shape,2))
    pairs=np.column_stack((hosts[point_ids],targets))
    # ponytail: pair calls recheck native images;optimize only if profiling needs it.
    for host,target in np.unique(pairs,axis=0):
        slots=np.flatnonzero((pairs[:,0]==host)&(pairs[:,1]==target))
        ids=point_ids[slots]
        try:
            with np.errstate(over='raise',invalid='raise'):
                a=log_gains[target]-log_gains[host]
                b=biases[target]-np.exp(a)*biases[host]
                relative=poses[target]@np.linalg.inv(poses[host])
        except FloatingPointError as error:
            raise ValueError('relative pose/exposure overflow') from error
        value,warp=pair_residual(images[[host,target]],pixels[ids],inverse_depth[ids],
            np.stack((np.eye(4),relative)),[0.,a],[0.,b],log_focal)
        values[slots],warps[slots]=value[0],warp[0]
    return values,warps
