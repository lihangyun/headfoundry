"""DA3 depth/camera conversion only; asset loading remains explicit and separate."""
import numpy as np


def depth_to_world(depth, extrinsics, intrinsics):
    """Unproject z-depth with pixel-space K and OpenCV camera-from-world [R|t].

    No invented depth, invalid-pixel filtering, scale calibration or acceptance.
    The result retains the depth map's view/row/column order.
    """
    depth,e,k=map(lambda value:np.asarray(value,float),(depth,extrinsics,intrinsics))
    if depth.ndim!=3 or min(depth.shape)<1:
        raise ValueError('nonempty view/height/width depth maps required')
    views,height,width=depth.shape
    if e.shape!=(views,3,4) or k.shape!=(views,3,3):raise ValueError('invalid camera formats')
    if not all(np.isfinite(x).all() for x in (depth,e,k)) or np.any(depth<=0):
        raise ValueError('finite cameras and positive z-depth required')
    r=e[:,:,:3]
    if not np.allclose(r@r.transpose(0,2,1),np.eye(3),atol=1e-4) or not np.allclose(np.linalg.det(r),1,atol=1e-4):
        raise ValueError('rigid right-handed rotations required')
    if (not np.allclose(k[:,2,:],[0,0,1]) or not np.allclose(k[:,1,0],0)
            or np.any(k[:,0,0]<=0) or np.any(k[:,1,1]<=0)):
        raise ValueError('upper-triangular pixel-space intrinsics required')
    y,x=np.mgrid[:height,:width];pixels=np.stack([x,y,np.ones_like(x)],axis=-1)
    camera=np.einsum('vij,hwj->vhwi',np.linalg.inv(k),pixels)*depth[...,None]
    return np.einsum('vji,vhwj->vhwi',r,camera-e[:,None,None,:,3])


def original_intrinsics(intrinsics, processed_size_hw, original_sizes_hw):
    """Undo pure resize only. Crop/pad transforms must not use this helper."""
    k=np.asarray(intrinsics,float);processed=np.asarray(processed_size_hw,float)
    sizes=np.asarray(original_sizes_hw,float)
    if (processed.shape!=(2,) or k.ndim!=3 or k.shape[1:]!=(3,3)
            or sizes.shape!=(len(k),2) or not len(k)
            or not all(np.isfinite(x).all() for x in (k,processed,sizes))
            or np.any(processed<=0) or np.any(sizes<=0)):
        raise ValueError('finite positive image sizes and matching camera batch required')
    result=k.copy();result[:,0,:]*=(sizes[:,1]/processed[1])[:,None]
    result[:,1,:]*=(sizes[:,0]/processed[0])[:,None]
    return result
