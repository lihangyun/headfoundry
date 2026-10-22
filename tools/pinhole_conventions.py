"""Pixel-edge to integer-center calibration arithmetic,not an estimator."""
import numpy as np


def native_intrinsics(edge_params):
    params=np.asarray(edge_params,float)
    if params.shape!=(4,) or not np.isfinite(params).all() or (params[:2]<=0).any():
        raise ValueError('positive finite fx/fy and finite edge cx/cy required')
    fx,fy,cx,cy=params
    return np.array([[fx,0,cx-.5],[0,fy,cy-.5],[0,0,1.]])
