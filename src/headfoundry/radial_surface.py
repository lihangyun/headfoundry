"""Experimental single radial shell; unsupported regions are prior-driven."""
import numpy as np


def fit_radial_shell(points, rows=64, columns=96):
    """Fit median radius observations with neighboring-cell regularization.

    This representation cannot reconstruct overhangs, separate ears/eyes, or
    arbitrary head topology. Caps and unobserved bins are explicitly inferred.
    """
    from scipy.sparse import coo_matrix,diags
    from scipy.sparse.linalg import spsolve
    p=np.asarray(points,float)
    if p.ndim!=2 or p.shape[1]!=3 or len(p)<20 or not np.isfinite(p).all():
        raise ValueError('finite observed points required')
    if not isinstance(rows,int) or not isinstance(columns,int) or not 8<=rows<=128 or not 8<=columns<=256:
        raise ValueError('invalid shell resolution')
    lower,upper=np.quantile(p,[.005,.995],axis=0)
    if np.any(upper-lower<1e-6):raise ValueError('three-dimensional extent required')
    center=(lower+upper)/2
    levels=np.linspace(lower[1],upper[1],rows+2)[1:-1]
    theta=np.arange(columns)*2*np.pi/columns
    y=(p[:,1]-levels[0])/(levels[-1]-levels[0])*(rows-1)
    angle=np.mod(np.arctan2(p[:,0]-center[0],-(p[:,2]-center[2])),2*np.pi)
    iy=np.rint(y).astype(int);it=np.rint(angle/(2*np.pi)*columns).astype(int)%columns
    radius=np.hypot(p[:,0]-center[0],p[:,2]-center[2])
    keep=(iy>=0)&(iy<rows)&(radius>1e-8)
    bins=iy[keep]*columns+it[keep];radius=radius[keep]
    n=rows*columns;data=np.zeros(n);weights=np.zeros(n)
    order=np.argsort(bins); sorted_bins=bins[order]
    for group in np.split(order,np.flatnonzero(np.diff(sorted_bins))+1):
        if not len(group):continue
        index=bins[group[0]];data[index]=np.median(radius[group]);weights[index]=1
    rx,rz=(upper[[0,2]]-lower[[0,2]])/2
    cross=1/np.sqrt((np.sin(theta)/rx)**2+(np.cos(theta)/rz)**2)
    height=(levels-center[1])/((upper[1]-lower[1])/2)
    prior=(np.sqrt(np.maximum(1-height**2,.01))[:,None]*cross).ravel()
    ids=np.arange(n).reshape(rows,columns)
    a=np.r_[ids.ravel(),ids[:-1].ravel()];b=np.r_[np.roll(ids,-1,axis=1).ravel(),ids[1:].ravel()]
    lap=coo_matrix((np.r_[np.ones(len(a)),np.ones(len(a)),-np.ones(len(a)),-np.ones(len(a))],
                    (np.r_[a,b,a,b],np.r_[a,b,b,a])),shape=(n,n)).tocsr()
    fitted=spsolve(diags(weights+.02)+.35*lap,weights*data+.02*prior)
    x=center[0]+fitted.reshape(rows,columns)*np.sin(theta)
    z=center[2]-fitted.reshape(rows,columns)*np.cos(theta)
    vertices=np.c_[x.ravel(),np.repeat(levels,columns),z.ravel()]
    vertices=np.vstack([vertices,[center[0],lower[1],center[2]],[center[0],upper[1],center[2]]])
    a=ids[:-1].ravel();b=np.roll(ids[:-1],-1,axis=1).ravel();c=a+columns;d=b+columns
    faces=np.vstack([np.c_[a,c,b],np.c_[b,c,d],
                     np.c_[np.full(columns,n),ids[0],np.roll(ids[0],-1)],
                     np.c_[np.full(columns,n+1),np.roll(ids[-1],-1),ids[-1]]])
    return vertices,faces,dict(status='UNVERIFIED',observed_bins=int(weights.sum()),total_bins=n,
                              prior_only_vertices=np.r_[np.flatnonzero(weights==0),n,n+1].tolist(),
                              limitation='Regularized radial shell, not validated anatomy; unsupported bins and caps inferred.')
