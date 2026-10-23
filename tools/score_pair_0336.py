"""Independent owned-surface evaluation;never runs a learned model."""
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

from bounded_process import run
from check_dense_grid_contract import bilinear
from dense_photo_0332 import intersect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/pairwise-physical-0336'
FIXTURE=ROOT/'assets/private/dense-photo-0332'
SOFTWARE=ROOT/'assets/private/sea-raft-software-0335'
PREDICTION_SHA='ee70a9304df575e5de03ec14b3f16952fa1e51328179d3bf798a64f9c57cc3b7'

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False))

def oracle_controls(target):
    target=np.asarray(target,np.float64)
    if target.ndim!=2 or target.shape[1]!=2 or not len(target) or not np.isfinite(target).all():
        raise ValueError('finite nonempty paired pixel coordinates required')
    scorer=lambda uv:np.linalg.norm(uv-target,axis=1)
    wrong=scorer(target+[40,0]);roundoff_bound=8*np.finfo(np.float64).eps*max(1,float(abs(target).max())+40)
    wrong_error=float(abs(wrong-40).max())
    report={'zero_max_px':float(scorer(target).max()),'wrong40_max_roundoff_px':wrong_error,
        'roundoff_bound_px':roundoff_bound,'bound_basis':'8*float64 epsilon*max(1,max_abs_true_uv+40),not a physical threshold',
        'prediction_arrays_opened':False}
    if report['zero_max_px']!=0 or wrong_error>roundoff_bound or float(np.percentile(wrong,95))<=3:
        raise ValueError('independent scoring controls fail')
    return report

def prepare():
    metadata=json.loads((FIXTURE/'inputs.json').read_text());fixed=json.loads((SOFTWARE/'fixed-owned-images.json').read_text())
    for name,identity in fixed.items():
        if metadata['images'][name]!=identity or sha(FIXTURE/name)!=identity:raise ValueError('owned source identity changed')
    if sha(FIXTURE/'truth.npz')!=metadata['truth_sha256']:raise ValueError('truth identity changed')
    if sha(FIXTURE/'raw-endpoints.npz')!='3152cc68a338169aaa85144c5dea7cb151cf64c5418c46cc6231cd74700e9370':raise ValueError('all-query identity changed')
    truth=dict(np.load(FIXTURE/'truth.npz'));query=np.load(FIXTURE/'raw-endpoints.npz')['query']
    if query.shape!=(96,2):raise ValueError('fixed original query population changed')
    k,poses,rectangles=truth['K'],truth['poses'],truth['rectangles']
    xyz,labels=intersect(poses[0],query,rectangles,k)
    if (labels<0).any() or not np.isfinite(xyz).all():raise ValueError('source first hit fails')
    local=xyz@poses[1,:3,:3].T+poses[1,:3,3]
    expected=local[:,:2]/local[:,2,None]*k[0,0]+k[:2,2]
    hit,target_labels=intersect(poses[1],expected,rectangles,k)
    visible=(local[:,2]>1e-9)&(target_labels==labels)&np.isfinite(hit).all(1)&(np.linalg.norm(hit-xyz,axis=1)<=1e-6)&(expected>=0).all(1)&(expected<=[719,1279]).all(1)
    np.savez_compressed(OUT/'frozen-domain.npz',query=query,xyz=xyz,expected=expected,labels=labels,target_labels=target_labels,visible=visible)
    report={'source_queries':len(query),'joint_visible':int(visible.sum()),'not_joint_visible':int((~visible).sum()),
        'source_span_xy':np.ptp(query[visible],axis=0).tolist() if visible.any() else [],
        'target_span_xy':np.ptp(expected[visible],axis=0).tolist() if visible.any() else [],
        'frozen_domain_sha256':sha(OUT/'frozen-domain.npz'),'prediction_arrays_opened':False,
        'truth_sha256':sha(FIXTURE/'truth.npz'),'query_sha256':sha(FIXTURE/'raw-endpoints.npz')}
    write('domain.json',report);print(json.dumps(report))
    if visible.sum()<48 or min(report['source_span_xy']+report['target_span_xy'])<50:raise ValueError('predeclared visible coverage fails')

def score():
    report=json.loads((OUT/'domain.json').read_text())
    if sha(OUT/'frozen-domain.npz')!=report['frozen_domain_sha256']:raise ValueError('frozen geometry/domain changed')
    if sha(SOFTWARE/'native-output.npz')!=PREDICTION_SHA:raise ValueError('prediction identity changed')
    domain=dict(np.load(OUT/'frozen-domain.npz'))
    q,target,visible=domain['query'],domain['expected'],domain['visible']
    scorer=lambda uv:np.linalg.norm(uv-target,axis=1)
    write('oracle-controls.json',oracle_controls(target))
    prediction=np.load(SOFTWARE/'native-output.npz')['flow']
    if prediction.shape!=(1,2,1280,720) or prediction.dtype!=np.float32 or not np.isfinite(prediction).all():raise ValueError('native field contract fails')
    uv=q+bilinear(prediction[0].transpose(1,2,0),q,[720,1280]);error=scorer(uv)
    bounds=np.isfinite(uv).all(1)&(uv>=0).all(1)&(uv<=[719,1279]).all(1)
    p95=float(np.percentile(error[visible],95));passed=bool(p95<=3 and bounds[visible].all())
    result={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','source_queries':len(q),'joint_visible':int(visible.sum()),
        'visible_endpoint_median_px':float(np.median(error[visible])),'visible_endpoint_p95_px':p95,
        'visible_endpoint_max_px':float(error[visible].max()),'visible_above3px':int(np.sum(error[visible]>3)),
        'visible_outside_native':int(np.sum(~bounds[visible])),
        'unobservable_count':int((~visible).sum()),'unobservable_p95_diagnostic_px':float(np.percentile(error[~visible],95)) if (~visible).any() else None,
        'zero_oracle_px':0,'wrong40px_oracle_px':40,'prediction_sha256':PREDICTION_SHA,
        'scope':'owned visible material-point precision only;not camera/realvideo/medical/head acceptance'}
    np.savez_compressed(OUT/'point-scores.npz',**domain,predicted=uv,errors=error,in_native=bounds)
    write('result.json',result);print(json.dumps(result,indent=2))
    if not passed:raise ValueError('fixed physical point precision fails')

def controller(stage):
    if stage=='prepare':OUT.mkdir(exist_ok=False)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    record=run([sys.executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),60 if stage=='prepare' else 30,2*1024**3)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'

if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):{'prepare':prepare,'score':score}[stage[:-7]]()
    else:sys.exit(0 if controller(stage) else 1)
