"""Monotone vertical gap compression, given explicit per-column surface heights."""
import numpy as np


def compress_vertical_gap(vertices, upper, lower, amount, *, falloff=.08):
    """Compress [upper, lower] around its midpoint, preserving x/z exactly.

    amount is per vertex in [0,1); zero is identity. The same upper/lower/amount
    must be used for every point in a given x/z column for the continuous map
    to be monotone. This does not certify a piecewise-linear output mesh free
    of intersections or determine anatomical contact from supplied heights.
    """
    v=np.asarray(vertices,float);u=np.asarray(upper,float);l=np.asarray(lower,float)
    strength=np.asarray(amount,float)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or u.shape!=(len(v),) or l.shape!=u.shape
            or strength.shape!=u.shape or not all(np.isfinite(a).all() for a in (v,u,l,strength))
            or np.any(l<=u) or np.any(strength<0) or np.any(strength>=1)
            or not np.isscalar(falloff) or not np.isfinite(falloff) or falloff<=0):
        raise ValueError('finite vertices, ordered gap heights, amount in [0,1), positive falloff required')
    y=v[:,1];shift=(l-u)*strength/2
    displacement=np.zeros(len(v))
    above=(y>u-falloff)&(y<u);below=(y>l)&(y<l+falloff);inside=(y>=u)&(y<=l)
    displacement[above]=shift[above]*(y[above]-u[above]+falloff)/falloff
    displacement[below]=-shift[below]*(l[below]+falloff-y[below])/falloff
    displacement[inside]=strength[inside]*((u[inside]+l[inside])/2-y[inside])
    result=v.copy();result[:,1]+=displacement
    return result
