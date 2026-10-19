"""Image-derived residuals with point-disjoint coarse context; no truth input."""
import cv2
import numpy as np

from temporal_video_sfm_0220 import track_step


def context_homography(first, second):
    first,second=np.asarray(first,float),np.asarray(second,float)
    if (first.ndim!=2 or first.shape[1:]!=(2,) or second.shape!=first.shape or len(first)<12
            or not np.isfinite(first).all() or not np.isfinite(second).all()
            or (np.ptp(first,axis=0)<50).any()):
        raise ValueError('At least12 finite spatially spread context pairs required')
    cv2.setRNGSeed(228)
    matrix,inliers=cv2.findHomography(first,second,cv2.USAC_MAGSAC,3.,maxIters=10000,confidence=.999)
    if matrix is None or inliers is None or inliers.sum()<12 or inliers.mean()<.5:
        raise ValueError('Insufficient coarse context warp support')
    if not np.isfinite(matrix).all() or abs(matrix[2,2])<1e-12:
        raise ValueError('Invalid context homography')
    matrix=matrix/matrix[2,2]
    if np.linalg.det(matrix)<=0 or not np.isfinite(np.linalg.inv(matrix)).all():
        raise ValueError('Improper or singular context homography')
    return matrix,{'pairs':len(first),'inliers':int(inliers.sum()),'inlier_fraction':float(inliers.mean())}


def project(points, matrix):
    points=np.asarray(points,float)
    h=np.c_[points,np.ones(len(points))]@matrix.T
    if not np.isfinite(h).all() or (h[:,2]<=1e-8).any():
        raise ValueError('Context warp crosses a measurement horizon')
    return h[:,:2]/h[:,2:]


def refine_context_rectified(previous,current,context_source,context_target,points,initial):
    points,initial=np.asarray(points,np.float32),np.asarray(initial,np.float32)
    if (previous.ndim!=2 or previous.dtype!=np.uint8 or current.shape!=previous.shape or current.dtype!=np.uint8
            or points.ndim!=2 or points.shape[1:]!=(2,) or initial.shape!=points.shape
            or not np.isfinite(points).all() or not np.isfinite(initial).all()):
        raise ValueError('Matching gray images and finite measurement endpoints required')
    result={'pixels':initial.copy(),'eligible':np.zeros(len(points),bool),
            'fb_error':np.full(len(points),np.inf),'patch_error':np.full(len(points),np.inf)}
    try:
        matrix,context=context_homography(context_source,context_target)
        seed=project(initial,np.linalg.inv(matrix))
        rectified=cv2.warpPerspective(current,matrix,(current.shape[1],current.shape[0]),
            flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
        corrected,eligible,fb,error=track_step(previous,rectified,points,initial=seed)
        # Do not replace a measured endpoint with project(points,matrix).
        final=project(corrected,matrix)
        eligible &= ((final>=0)&(final<[current.shape[1],current.shape[0]])).all(axis=1)
        result.update(pixels=final,eligible=eligible,fb_error=fb,patch_error=error,
            context_matrix=matrix,context=context)
    except (ValueError,np.linalg.LinAlgError) as error:
        result['context_failure']=str(error)
    return result
