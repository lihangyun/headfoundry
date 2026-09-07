"""Conservative coordinate-based cycle joining, independent of fitted cameras."""
import numpy as np


def join_three_views(first_second, first_third, second_third, tolerance_px=2.):
    """Join pair rows [x_a,y_a,x_b,y_b] only when all endpoints agree uniquely.

    Keeps original observations, without averaging inconsistent endpoints.
    A closed cycle is only a candidate correspondence, not physical evidence.
    """
    pairs=[np.asarray(p,float) for p in (first_second,first_third,second_third)]
    if not np.isfinite(tolerance_px) or tolerance_px<=0:
        raise ValueError('positive finite endpoint tolerance required')
    for pair in pairs:
        if pair.ndim!=2 or pair.shape[1]!=4 or not np.isfinite(pair).all() or len(pair)>4096:
            raise ValueError('finite N x 4 pairs required, at most 4096 per pair')
    def unique_links(a,b):
        if not len(a) or not len(b):return {}
        close=np.sum((a[:,None]-b[None])**2,axis=-1)<=tolerance_px**2
        row_counts=close.sum(axis=1);column_counts=close.sum(axis=0)
        rows,cols=np.nonzero(close)
        return {int(i):int(j) for i,j in zip(rows,cols) if row_counts[i]==1 and column_counts[j]==1}
    ab,ac,bc=pairs
    front=unique_links(ab[:,:2],ac[:,:2])
    second=unique_links(ab[:,2:],bc[:,:2])
    third=unique_links(ac[:,2:],bc[:,2:])
    indices=[(i,j,second[i]) for i,j in front.items() if i in second and third.get(j)==second[i]]
    observations=np.array([[ab[i,:2],ab[i,2:],ac[j,2:]] for i,j,k in indices],float).reshape(-1,3,2)
    return observations,np.array(indices,int).reshape(-1,3)
