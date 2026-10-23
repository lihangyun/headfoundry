"""Independent complete-population score of frozen owned sparse observations."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

from bounded_process import run
from dense_photo_0332 import intersect
from endpoint_oracle import oracle_controls

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/aliked-physical-0343'
FIXTURE=ROOT/'assets/private/dense-photo-0332'
PREDICTIONS=ROOT/'assets/private/aliked-runtime-0342'
IDENTITIES={'truth.npz':'3dbb05fca621f3e2c7bf48ba91a6cd19b2ccd6fbada0da87846da67780308398',
    'view-0.png':'24a41defda99bdeab85917c8edd55ad5420b2f35a8c11a965338a2db46a07177',
    'view-1.png':'4ea0b7fc2c4ffb6878b9fab0c4b420112fb4ed91126330e72cffc78c83ef6297',
    'native-source-q.npy':'f7c7f7ed5b484630e99699473086b4deb8b88b888e86db162b0c7c2563141892',
    'native-target-features.npz':'dd8abb069626335982e7edf9a1819f0c1c429341c274960ca2111f750aad73b7',
    'native-matches.npz':'d6e3f09ca8ffbebfa855a4d6eca5bdc55efca8940e0ea8928cf423c835f2fbe1'}

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(name,value):
    path=OUT/name
    if path.exists():raise FileExistsError('immutable evidence exists')
    path.write_text(json.dumps(value,indent=2,allow_nan=False))

def guard(stage):
    permitted={FIXTURE/'truth.npz',FIXTURE/'view-0.png',PREDICTIONS/'native-source-q.npy'}
    if stage=='score':permitted|={PREDICTIONS/'native-target-features.npz',PREDICTIONS/'native-matches.npz'}
    permitted={p.resolve() for p in permitted}
    private=(ROOT/'assets/private').resolve()
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline evaluator')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            reading=not isinstance(mode,str) or 'r' in mode or '+' in mode
            if path.suffix.lower() in ('.stl','.mp4') or path.is_relative_to(Path('C:/workspace/peek')) or path.is_relative_to(Path('C:/Users/lihan/Downloads')):
                raise PermissionError('patient/unrelated geometry denied')
            if reading and path.is_relative_to(private) and path not in permitted and not path.is_relative_to(OUT):
                raise PermissionError('prediction-before-domain/unrelated private read denied')
    sys.addaudithook(audit)

def linear_quantile(values,p):
    values=np.sort(np.asarray(values,float))
    if not len(values):return None
    if np.isnan(values).any() or np.isneginf(values).any():raise ValueError('undefined error bookkeeping')
    index=(len(values)-1)*p;low=int(np.floor(index));high=int(np.ceil(index))
    if np.isposinf(values[high]):return np.inf
    return float(values[low]+(index-low)*(values[high]-values[low]))

def describe(errors):
    def encode(value):return 'INF_UNSUPPORTED' if value is not None and not np.isfinite(value) else value
    return {'count':len(errors),'undefined_assigned':int(np.isposinf(errors).sum()),
        'median_px':encode(linear_quantile(errors,.5)),'p95_px':encode(linear_quantile(errors,.95)),
        'max_px':encode(float(np.max(errors)) if len(errors) else None),'over3_count':int((errors>3).sum())}

def errors_for(target,m0,visible,truth):
    error=np.full(len(m0),np.nan);assigned=m0>=0;error[assigned]=np.inf
    source=np.flatnonzero(assigned)
    predicted=target[m0[source]]
    supported=np.isfinite(predicted).all(1)&(predicted>=0).all(1)&(predicted<=[719,1279]).all(1)&visible[source]
    selected=source[supported]
    error[selected]=np.linalg.norm(predicted[supported]-truth[selected],axis=1)
    return error

def controls():
    finite=np.arange(100)/3
    if linear_quantile(finite,.95)!=np.percentile(finite,95):raise AssertionError('linear finite quantile mismatch')
    if not np.isposinf(linear_quantile([0,np.inf],.95)) or linear_quantile([np.inf],.95)!=np.inf:
        raise AssertionError('infinite physical failure lost in quantile')
    target=np.array([[10.,20.],[30.,40.]])
    result=errors_for(target,np.array([0,1,-1]),np.array([True,False,True]),np.array([[10.,20.],[30.,40.],[30.,40.]]))
    if result[0]!=0 or not np.isposinf(result[1]) or not np.isnan(result[2]):raise AssertionError('invalid/missing point hidden')
    return {'finite_linear_quantile':True,'undefined_assigned_is_inf':True,'unmatched_not_gathered_as_minus_one':True}

def domain():
    guard('domain');cv2.setNumThreads(4)
    checks=controls();denied=[]
    for name in ('native-target-features.npz','native-matches.npz'):
        try:
            with (PREDICTIONS/name).open('rb'):pass
        except PermissionError:denied.append(name)
        else:raise AssertionError('prediction accessible before domain freeze')
    for folder,name in ((FIXTURE,'truth.npz'),(FIXTURE,'view-0.png'),(PREDICTIONS,'native-source-q.npy')):
        if sha(folder/name)!=IDENTITIES[name]:raise ValueError('immutable input changed:'+name)
    q=np.load(PREDICTIONS/'native-source-q.npy',allow_pickle=False).astype(float)
    if q.shape!=(1024,2) or not np.isfinite(q).all() or (q<0).any() or (q>[719,1279]).any():raise ValueError('source native point contract')
    with Image.open(FIXTURE/'view-0.png') as source:image=np.asarray(source,dtype=float)/255
    if image.shape!=(1280,720):raise ValueError('source image axes')
    cue=cv2.erode((image>.12).astype('uint8'),np.ones((17,17),np.uint8))
    pixel=np.floor(q+.5).astype(int);primary=cue[pixel[:,1],pixel[:,0]]!=0
    with np.load(FIXTURE/'truth.npz',allow_pickle=False) as data:k,poses,rectangles=data['K'],data['poses'],data['rectangles']
    xyz,labels=intersect(poses[0],q,rectangles,k);source_valid=labels>=0
    local=xyz@poses[1,:3,:3].T+poses[1,:3,3]
    with np.errstate(invalid='ignore',divide='ignore'):uv=local[:,:2]/local[:,2,None]*k[0,0]+k[:2,2]
    positive=source_valid&(local[:,2]>0)&np.isfinite(uv).all(1)
    inside=positive&(uv>=0).all(1)&(uv<=[719,1279]).all(1)
    hit,target=intersect(poses[1],uv,rectangles,k)
    visible=inside&(target==labels)&np.isfinite(hit).all(1)&(np.linalg.norm(hit-xyz,axis=1)<=1e-6)
    category=np.full(len(q),0,int);category[source_valid&~inside]=1;category[inside&~visible]=2;category[visible]=3
    if any(not np.isfinite(uv[visible]).all() for _ in [0]):raise ValueError('invalid visible truth')
    replay=cv2.projectPoints(xyz[source_valid],cv2.Rodrigues(poses[1,:3,:3])[0],poses[1,:3,3],k,None)[0].reshape(-1,2)
    difference=float(np.max(abs(replay-uv[source_valid])))
    if difference>1e-9:raise ValueError('independent projection replay mismatch')
    np.savez_compressed(OUT/'domain.npz',q=q,primary=primary,xyz=xyz,labels=labels,true_uv=uv,
        visible=visible,category=category,target_labels=target)
    counts={str(i):int((category==i).sum()) for i in range(4)}
    report={'status':'TECHNICAL_CHECK_PASSED','population':len(q),'primary':int(primary.sum()),
        'primary_GTvisible':int((primary&visible).sum()),'categories':counts,
        'category_meanings':{'0':'source_no_hit','1':'target_behind_nonfinite_or_offscreen','2':'target_occluded_or_hit_mismatch','3':'joint_visible'},
        'projection_replay_max_px':difference,'domain_sha256':sha(OUT/'domain.npz'),
        'prediction_arrays_opened_during_domain_freeze':False,'denied_prediction_read_controls':denied,
        'controls':checks,'completed_utc':time.time()}
    if (primary&visible).sum()<48:report['status']='REJECT'
    write('domain.json',report)
    if report['status']!='TECHNICAL_CHECK_PASSED':raise ValueError('fixed physical-domain support policy fails')
    oracle=oracle_controls(uv[primary&visible]);write('oracle.json',oracle)
    print(json.dumps(report))

def score():
    guard('score')
    frozen=json.loads((OUT/'domain.json').read_text())
    if frozen['status']!='TECHNICAL_CHECK_PASSED' or sha(OUT/'domain.npz')!=frozen['domain_sha256']:
        raise ValueError('domain must be frozen first')
    oracle=json.loads((OUT/'oracle.json').read_text())
    if oracle['zero_max_px']!=0:raise ValueError('scoring oracle not passed')
    for name in ('native-target-features.npz','native-matches.npz'):
        if sha(PREDICTIONS/name)!=IDENTITIES[name]:raise ValueError('frozen prediction changed')
    with np.load(OUT/'domain.npz',allow_pickle=False) as data:q,primary,visible,uv=data['q'],data['primary'],data['visible'],data['true_uv']
    with np.load(PREDICTIONS/'native-target-features.npz',allow_pickle=False) as data:target=data['keypoints'][0].astype(float)
    with np.load(PREDICTIONS/'native-matches.npz',allow_pickle=False) as data:
        m0,m1,pairs,scores0=data['matches0'],data['matches1'],data['matches'],data['matching_scores0']
    if target.ndim!=2 or target.shape[1]!=2 or m0.shape!=(len(q),) or m1.shape!=(len(target),):raise ValueError('index/population shape')
    if not all(np.issubdtype(x.dtype,np.integer) for x in (m0,m1,pairs)):raise ValueError('integral match indices required')
    if ((m0< -1)|(m0>=len(target))).any() or ((m1< -1)|(m1>=len(q))).any():raise ValueError('match index outside native population')
    ids=np.flatnonzero(m0>=0);targets=m0[ids];other=np.flatnonzero(m1>=0)
    if not np.array_equal(m1[targets],ids) or not np.array_equal(m0[m1[other]],other) or not np.array_equal(pairs,np.column_stack((ids,targets))):
        raise ValueError('bidirectional/compact indices disagree')
    errors=errors_for(target,m0,visible,uv);assigned=m0>=0;selected=primary&assigned
    predicted=target[m0[selected]];source_span=np.ptp(q[selected],axis=0) if selected.any() else np.zeros(2)
    target_span=np.ptp(predicted,axis=0) if len(predicted) else np.zeros(2)
    statistics=describe(errors[selected]);p95=linear_quantile(errors[selected],.95)
    supported=bool(selected.sum()>=48 and min(source_span.min(),target_span.min())>=50)
    passed=bool(supported and p95 is not None and p95<=3)
    correct=selected&np.isfinite(errors)&(errors<=3);primary_visible=primary&visible
    report={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','primary_assigned':statistics,
        'primary_visible_assigned':describe(errors[selected&visible]),'outside_cue_assigned_diagnostic':describe(errors[assigned&~primary]),
        'raw_source':len(q),'raw_target':len(target),'all_assigned':int(assigned.sum()),'primary_source':int(primary.sum()),
        'primary_GTvisible':int(primary_visible.sum()),'primary_unmatched':int((primary&~assigned).sum()),
        'primary_visible_unmatched':int((primary_visible&~assigned).sum()),'correct_le3':int(correct.sum()),
        'correct_per_primary_assignment':float(correct.sum()/selected.sum()) if selected.any() else None,
        'correct_per_primary_GTvisible':float(correct.sum()/primary_visible.sum()) if primary_visible.any() else None,
        'source_span_px':source_span.tolist(),'predicted_target_span_px':target_span.tolist(),
        'prototype_support_policy_passed':supported,'domain_sha256':frozen['domain_sha256'],
        'prediction_arrays_opened_for_score':True,'completed_utc':time.time(),
        'scope':'all assigned source-cue points,invalid/invisible=Inf;owned pair only,not actual camera/medical/head'}
    np.savez_compressed(OUT/'scores.npz',q=q,target=target,matches0=m0,matches1=m1,pairs=pairs,
        primary=primary,visible=visible,true_uv=uv,errors=errors,model_scores0=scores0)
    report['scores_sha256']=sha(OUT/'scores.npz');write('result.json',report);print(json.dumps(report))
    if not passed:raise ValueError('fixed complete-assigned physical point screen rejected')

if __name__=='__main__':
    if ROOT!=Path('C:/workspace/headfoundry').resolve():raise ValueError('unexpected repository')
    OUT.mkdir(exist_ok=True)
    for path in (ROOT,ROOT/'assets',ROOT/'assets/private',OUT):
        if getattr(path.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse path')
    if len(sys.argv)==3 and sys.argv[1]=='worker':{'domain':domain,'score':score}[sys.argv[2]]()
    else:
        stage=sys.argv[1]
        if stage not in ('domain','score') or (OUT/(stage+'-worker.json')).exists():raise ValueError('unknown/repeated physical stage')
        env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
        result=run([sys.executable,str(Path(__file__).resolve()),'worker',stage],str(ROOT),env,
            OUT/(stage+'.log'),OUT/(stage+'-worker.json'),60,2*1024**3)
        print(json.dumps(result))
        if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)
