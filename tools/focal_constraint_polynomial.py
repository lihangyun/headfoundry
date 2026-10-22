"""Exact-fixture focal observability witness;not a noisy-camera accuracy gate."""
import numpy as np


def demazure_coefficients(centered_matrix):
    """Coefficients of 2 E(s) E(s)^T E(s)-tr(E(s) E(s)^T) E(s).

    E(s)=diag(s,s,1) F diag(s,s,1);coefficients increase in powers of s.
    A zero polynomial with rank-two F means a continuous essential family.
    Nonzero does NOT certify unique/stable calibration,especially with noise.
    Input focal units/centering belong to caller;no estimate or tolerance here.
    """
    matrix=np.asarray(centered_matrix,float)
    if matrix.shape!=(3,3) or not np.isfinite(matrix).all() or not np.any(matrix):
        raise ValueError('nonzero finite centered3x3matrix required')
    matrix=matrix/np.max(abs(matrix));matrix/=np.linalg.norm(matrix)
    e=np.zeros((3,3,3))
    for i in range(3):
        for j in range(3):e[i,j,int(i<2)+int(j<2)]=matrix[i,j]

    def multiply(a,b):
        result=np.zeros((3,3,a.shape[2]+b.shape[2]-1))
        for i in range(3):
            for j in range(3):
                for k in range(3):result[i,j]+=np.convolve(a[i,k],b[k,j])
        return result

    eet=multiply(e,e.transpose(1,0,2));result=2*multiply(eet,e)
    trace=eet[0,0]+eet[1,1]+eet[2,2]
    for i in range(3):
        for j in range(3):result[i,j]-=np.convolve(trace,e[i,j])
    return result
