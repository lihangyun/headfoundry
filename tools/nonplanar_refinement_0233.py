"""Independent F context with free image residuals, never snap-to-line matching."""
import cv2
import numpy as np

from nonplanar_context_0231 import fit_context_fundamental
from context_rectification_0228 import project
from temporal_video_sfm_0220 import track_step


def refine_nonplanar(previous,current,context_source,context_target,points,initial,*,refiner=track_step):
    points,initial=np.asarray(points,np.float32),np.asarray(initial,np.float32)
    if (previous.ndim!=2 or previous.dtype!=np.uint8 or current.shape!=previous.shape or current.dtype!=np.uint8
            or points.ndim!=2 or points.shape[1:]!=(2,) or initial.shape!=points.shape
            or not np.isfinite(points).all() or not np.isfinite(initial).all()):
        raise ValueError('Matching gray images and finite source/initial endpoints required')
    result={'pixels':initial.copy(),'eligible':np.zeros(len(points),bool),
        'fb_error':np.full(len(points),np.inf),'patch_error':np.full(len(points),np.inf)}
    try:
        matrix,inliers,context=fit_context_fundamental(context_source,context_target)
        result['context']=context
        if matrix is None or context['status']!='TECHNICAL_CHECK_PASSED':
            raise ValueError('Independent nonplanar context support failed')
        a,b=np.asarray(context_source,float)[inliers],np.asarray(context_target,float)[inliers]
        ok,h1,h2=cv2.stereoRectifyUncalibrated(a,b,matrix,(current.shape[1],current.shape[0]),threshold=0)
        if not ok or h1 is None or h2 is None:
            raise ValueError('Contextual stereo rectification failed')
        transfer=np.linalg.solve(h2,h1)
        if not np.isfinite(transfer).all() or abs(transfer[2,2])<1e-12:
            raise ValueError('Invalid contextual appearance transfer')
        transfer/=transfer[2,2]
        if np.linalg.det(transfer)<=0:
            raise ValueError('Reflected contextual appearance transfer')
        seed=project(initial,np.linalg.inv(transfer))
        rectified=cv2.warpPerspective(current,transfer,(current.shape[1],current.shape[0]),
            flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
        corrected,eligible,fb,error=refiner(previous,rectified,points,initial=seed)
        # Only image-supported endpoints are mapped back. No F-line projection.
        final=initial.astype(float).copy()
        if eligible.any():
            final[eligible]=project(corrected[eligible],transfer)
        eligible &= ((final>=0)&(final<[current.shape[1],current.shape[0]])).all(axis=1)
        result.update(pixels=final,eligible=eligible,fb_error=fb,patch_error=error,
            fundamental=matrix,context_inliers=inliers,source_rectification=h1,target_rectification=h2,appearance_transfer=transfer)
    except (ValueError,np.linalg.LinAlgError,cv2.error) as error:
        result['refinement_failure']=str(error)
    return result
