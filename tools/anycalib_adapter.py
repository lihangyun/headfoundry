"""Opt-in fixed AnyCalib state/K boundary;no default path or model download."""
import numpy as np

from check_state_fingerprint import state_fingerprint


def native_intrinsics(edge_params):
    params=np.asarray(edge_params,float)
    if params.shape!=(4,) or not np.isfinite(params).all() or (params[:2]<=0).any():
        raise ValueError('positive finite fx/fy and finite edge cx/cy required')
    fx,fy,cx,cy=params
    return np.array([[fx,0,cx-.5],[0,fy,cy-.5],[0,0,1.]])


def validate_state(state,expected):
    import torch
    if not isinstance(state,dict) or set(state)!=set(expected):
        raise ValueError('exact complete state key set required')
    for name,target in expected.items():
        value=state[name]
        if (not isinstance(value,torch.Tensor) or value.device.type!='cpu'
                or value.dtype!=target.dtype or value.shape!=target.shape
                or value.layout!=torch.strided):
            raise ValueError('state tensor schema mismatch:'+name)
        array=value.detach().numpy()
        for start in range(0,array.size,262144):
            if not np.isfinite(array.flat[start:start+262144]).all():
                raise ValueError('nonfinite state tensor:'+name)


def fingerprint(state):
    return state_fingerprint({name:value.detach().numpy() for name,value in state.items()})
