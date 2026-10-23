"""Replay a successful complete sparse-point fixture without models or Torch."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'assets/private/aliked-physical-0343'


def check():
    report=json.loads((FIXTURE/'result.json').read_text())
    for name,digest in (('scores.npz',report['scores_sha256']),('domain.npz',report['domain_sha256'])):
        with (FIXTURE/name).open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()!=digest:raise ValueError('frozen point fixture changed')
    with np.load(FIXTURE/'scores.npz',allow_pickle=False) as data:raw=dict(data)
    q,target,m0,m1,pairs=[raw[key] for key in ('q','target','matches0','matches1','pairs')]
    if m0.shape!=(len(q),) or m1.shape!=(len(target),) or ((m0< -1)|(m0>=len(target))).any() or ((m1< -1)|(m1>=len(q))).any():
        raise ValueError('complete native source/target population required')
    assigned=np.flatnonzero(m0>=0);other=np.flatnonzero(m1>=0)
    if (not np.array_equal(m1[m0[assigned]],assigned) or not np.array_equal(m0[m1[other]],other)
            or not np.array_equal(pairs,np.column_stack((assigned,m0[assigned])))):
        raise ValueError('full bidirectional point index mismatch')
    replay=np.full(len(q),np.nan)
    for source in assigned:
        predicted=target[m0[source]];truth=raw['true_uv'][source]
        valid=bool(raw['visible'][source] and np.isfinite(predicted).all()
            and (predicted>=0).all() and (predicted<=[719,1279]).all())
        replay[source]=math.hypot(*(predicted-truth)) if valid else np.inf
    expected=raw['errors']
    if not np.array_equal(np.isnan(replay),np.isnan(expected)) or not np.array_equal(np.isposinf(replay),np.isposinf(expected)):
        raise AssertionError('unsupported or unmatched population changed')
    finite=np.isfinite(expected);delta=float(np.max(abs(replay[finite]-expected[finite])))
    coordinate=max(1.,float(np.max(abs(target))),float(np.max(abs(raw['true_uv'][raw['visible']]))))
    bound=8*np.finfo(np.float64).eps*coordinate
    if delta>bound:raise AssertionError('scalar endpoint replay exceeds roundoff bound')
    primary=raw['primary']&(m0>=0);errors=np.sort(replay[primary]);index=(len(errors)-1)*.95
    low,high=math.floor(index),math.ceil(index)
    p95=float(errors[low]+(index-low)*(errors[high]-errors[low])) if np.isfinite(errors[high]) else math.inf
    if not math.isfinite(p95) or abs(p95-report['primary_assigned']['p95_px'])>bound or p95>3:
        raise AssertionError('complete assigned precision no longer passes')
    return {'status':'TECHNICAL_CHECK_PASSED','source_population':len(q),'primary_assigned':int(primary.sum()),
        'primary_unsupported_retained':int(np.isposinf(replay[primary]).sum()),'p95_px':p95,
        'scalar_replay_max_roundoff_px':delta,'derived_roundoff_bound_px':bound,
        'models_loaded':False,'scope':'saved owned-pair endpoint fixture only;not clinical camera/head/medical accuracy'}


if __name__=='__main__':print(json.dumps(check(),indent=2))
