"""Point-disjoint fundamental context; no plane warp or camera/shape fitting."""
import cv2
import numpy as np


def fit_context_fundamental(first,second):
    first,second=np.asarray(first,float),np.asarray(second,float)
    if (first.ndim!=2 or first.shape[1:]!=(2,) or second.shape!=first.shape or len(first)<12
            or not np.isfinite(first).all() or not np.isfinite(second).all()
            or (np.ptp(first,axis=0)<50).any()):
        raise ValueError('At least12 finite spatially spread context pairs required')
    cv2.setRNGSeed(231)
    matrix,inliers=cv2.findFundamentalMat(first,second,cv2.USAC_MAGSAC,3.,.999,10000)
    count=int(inliers.sum()) if inliers is not None else 0
    record={'pairs':len(first),'inliers':count,'support_fraction':count/len(first),'status':'REJECT'}
    if matrix is None or matrix.shape!=(3,3) or not np.isfinite(matrix).all():
        return None,np.zeros(len(first),bool),record
    singular=np.linalg.svd(matrix,compute_uv=False)
    valid=singular[1]>1e-12 and singular[2]/singular[1]<1e-6
    if count>=12 and count>=.5*len(first) and valid:
        record['status']='TECHNICAL_CHECK_PASSED'
    return matrix/np.linalg.norm(matrix),inliers.ravel().astype(bool),record


def symmetric_line_errors(matrix,first,second):
    a,b=np.asarray(first,float),np.asarray(second,float)
    if (a.ndim!=2 or a.shape[1:]!=(2,) or b.shape!=a.shape or np.asarray(matrix).shape!=(3,3)
            or not all(np.isfinite(x).all() for x in (a,b,matrix))):
        raise ValueError('Finite matching pixels and fundamental matrix required')
    x,y=np.c_[a,np.ones(len(a))],np.c_[b,np.ones(len(b))]
    line_y,line_x=x@matrix.T,y@matrix
    denominator=np.minimum(np.linalg.norm(line_y[:,:2],axis=1),np.linalg.norm(line_x[:,:2],axis=1))
    if (denominator<1e-12).any():
        raise ValueError('Undefined epipolar line')
    return abs(np.sum(y*line_y,axis=1))/denominator
