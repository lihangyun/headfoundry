"""Valid-domain native direct-patch residual;no optimizer,model or patient input."""
import numpy as np

from check_dense_grid_contract import bilinear
from short_track_camera import intrinsics,project


def residual(images,pixels,inverse_depth,poses,log_gains,biases,log_focal):
    """All anchor patches in all targets;invalid support raises,never prunes.

    One inverse depth per NxPx2 anchor patch,shared by its P offsets.
    Anchor world-to-camera pose and log-gain/bias must be identity/zero.
    Returns TxNxP residuals (excluding anchor) and matching native xy warps.
    """
    images,pixels,inverse_depth,poses,log_gains,biases=[np.asarray(x,float) for x in
        (images,pixels,inverse_depth,poses,log_gains,biases)]
    if (images.ndim!=3 or images.shape[1:]!=(1280,720) or len(images)<2
            or pixels.ndim!=3 or pixels.shape[-1]!=2 or min(pixels.shape[:2])<1
            or inverse_depth.shape!=(len(pixels),) or (inverse_depth<=0).any()
            or poses.shape!=(len(images),4,4) or log_gains.shape!=(len(images),)
            or biases.shape!=(len(images),) or not np.isscalar(log_focal)
            or not np.isfinite(log_focal) or not all(np.isfinite(a).all() for a in
                (images,pixels,inverse_depth,poses,log_gains,biases))
            or images.min()<0 or images.max()>1):
        raise ValueError('finite native images,patches and positive inverse depths required')
    if (not np.allclose(poses[0],np.eye(4),atol=1e-12,rtol=0)
            or log_gains[0]!=0 or biases[0]!=0
            or not np.allclose(poses[:,3,:],[0,0,0,1],atol=1e-12,rtol=0)
            or not np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-10,rtol=0)
            or not np.all(np.linalg.det(poses[:,:3,:3])>0)):
        raise ValueError('proper SE3 and fixed anchor pose/exposure gauge required')
    try:
        with np.errstate(over='raise',invalid='raise'):
            k=intrinsics(log_focal);gains=np.exp(log_gains[1:])
    except FloatingPointError as error:
        raise ValueError('focal/exposure overflow') from error
    if k[0,0]<=0 or not np.isfinite(k).all() or not np.isfinite(gains).all() or (gains<=0).any():
        raise ValueError('positive finite focal and exposure required')
    flat=pixels.reshape(-1,2)
    reference=bilinear(images[0],flat,[720,1280]).reshape(pixels.shape[:2])
    rays=np.c_[flat,np.ones(len(flat))]@np.linalg.inv(k).T
    try:
        with np.errstate(over='raise',invalid='raise'):
            points=rays/np.repeat(inverse_depth,pixels.shape[1])[:,None]
    except FloatingPointError as error:
        raise ValueError('inverse-depth backprojection overflow') from error
    rows=np.array([[camera,point,0.,0.] for camera in range(1,len(images)) for point in range(len(points))])
    uv,depth=project(k,poses,points,rows)
    if not np.isfinite(uv).all() or not np.isfinite(depth).all() or (depth<=1e-9).any():
        raise ValueError('all rays must be in the unclamped projector domain Z>1e-9')
    warps=uv.reshape(len(images)-1,*pixels.shape)
    samples=np.stack([bilinear(images[camera],warp.reshape(-1,2),[720,1280]).reshape(reference.shape)
                      for camera,warp in enumerate(warps,1)])
    predicted=gains[:,None,None]*reference+biases[1:,None,None]
    if not np.isfinite(predicted).all() or (predicted<0).any() or (predicted>1).any():
        raise ValueError('affine exposure outside normalized sensor domain')
    return samples-predicted,warps
