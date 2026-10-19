"""Opt-in local affine observations; no geometry, truth or camera inputs."""
import cv2
import numpy as np


def refine_affine_patches(previous, current, points, initial):
    points,initial=np.asarray(points,np.float32),np.asarray(initial,np.float32)
    if (previous.ndim!=2 or previous.dtype!=np.uint8 or current.shape!=previous.shape or current.dtype!=np.uint8
            or points.ndim!=2 or points.shape[1:]!=(2,) or initial.shape!=points.shape
            or not np.isfinite(points).all() or not np.isfinite(initial).all()):
        raise ValueError('Matching gray images and finite source/initial endpoints required')
    source_gray,target_gray=previous.astype(np.float32)/255,current.astype(np.float32)/255
    size,radius=21,10
    y,x=np.mgrid[:size,:size]
    grid=np.stack([x,y,np.ones_like(x)],axis=-1).astype(np.float32)
    def inside(point):
        return bool((point>=[radius,radius]).all() and (point<=[previous.shape[1]-1-radius,previous.shape[0]-1-radius]).all())
    def align(source_image,target_image,source_point,target_point):
        if not inside(source_point) or not inside(target_point):
            raise ValueError('Patch outside image')
        template=cv2.getRectSubPix(source_image,(size,size),tuple(source_point))
        target=cv2.getRectSubPix(target_image,(size,size),tuple(target_point))
        correlation,warp=cv2.findTransformECC(template,target,np.eye(2,3,dtype=np.float32),cv2.MOTION_AFFINE,
            (cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,1e-5),None,1)
        if not np.isfinite(warp).all() or not np.isfinite(correlation):
            raise ValueError('Nonfinite affine estimate')
        singular=np.linalg.svd(warp[:,:2],compute_uv=False)
        if np.linalg.det(warp[:,:2])<=0 or singular.min()<.5 or singular.max()>2:
            raise ValueError('Improper or excessive local affine map')
        mapped=grid@warp.T
        valid=((mapped>=1)&(mapped<=size-2)).all(axis=-1)
        if valid.mean()<.5:
            raise ValueError('Insufficient affine patch overlap')
        aligned=cv2.warpAffine(target,warp,(size,size),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
        error=float(np.mean(abs(aligned[valid]-template[valid]))*255)
        point=target_point+warp@np.array([radius,radius,1],np.float32)-radius
        if not inside(point):
            raise ValueError('Refined patch outside image')
        return point,error,warp
    n=len(points)
    result={'pixels':initial.copy(),'eligible':np.zeros(n,bool),'fb_error':np.full(n,np.inf),
        'patch_error':np.full(n,np.inf),'back_patch_error':np.full(n,np.inf),
        'forward_warps':np.full((n,2,3),np.nan),'backward_warps':np.full((n,2,3),np.nan),
        # 0=eligible,1=ECC convergence,2=warp/support,3=photometric,4=cycle.
        'failure_codes':np.full(n,1,np.uint8)}
    for row,(point,seed) in enumerate(zip(points,initial)):
        try:
            forward,error,warp=align(source_gray,target_gray,point,seed)
            result['pixels'][row],result['patch_error'][row],result['forward_warps'][row]=forward,error,warp
            backward,back_error,reverse=align(target_gray,source_gray,forward,point)
            result['back_patch_error'][row],result['backward_warps'][row]=back_error,reverse
            fb=float(np.linalg.norm(backward-point))
            result['fb_error'][row]=fb
            if error>15:
                result['failure_codes'][row]=3
            elif fb>.75:
                result['failure_codes'][row]=4
            else:
                result['eligible'][row]=True
                result['failure_codes'][row]=0
        except cv2.error:
            result['failure_codes'][row]=1
        except ValueError:
            result['failure_codes'][row]=2
    return result
