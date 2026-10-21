"""Local frozen-track diagnosis only;no calibrated camera or head output."""
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import zipfile

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.epipolar import sampson_distance
from headfoundry.manifest import validate_input_assets
OUT = ROOT/'assets/private/uncalibrated-tracks-0286'
FIELDS = ['confidence','isParallel','loIterations','loMethod','loSampleSize',
          'maxIterations','neighborsSearch','randomGeneratorState','sampler','score','threshold']
REPORT = {'status':'REJECT','camera_status':'UNVERIFIED','head_status':'UNVERIFIED','pairs':[]}


def options():
    p = cv2.UsacParams()
    p.confidence,p.maxIterations,p.threshold = .999,10000,2.
    p.randomGeneratorState,p.isParallel = 286,False
    p.sampler,p.score = cv2.SAMPLING_UNIFORM,cv2.SCORE_METHOD_MAGSAC
    return p


def estimate(a,b):
    f,inliers = cv2.findFundamentalMat(a,b,options())
    if f is None or f.shape!=(3,3) or not np.isfinite(f).all():
        raise ValueError('no finite fundamental model')
    f = f/np.linalg.norm(f)
    s = np.linalg.svd(f,compute_uv=False)
    if s[1]<=1e-12*s[0] or s[2]>1e-7*s[1]:
        raise ValueError('not a numerical rank-two fundamental matrix')
    return f,inliers


def p95(values):
    return float(np.sort(values)[int(np.ceil(.95*len(values)))-1])


def controls():
    rng = np.random.default_rng(286)
    x = rng.uniform(-1,1,(300,3))+[0,0,5]
    r = Rotation.from_euler('yx',[16,4],degrees=True).as_matrix()
    other = x@r.T+[.7,.03,.12]
    a = 1100*x[:,:2]/x[:,2:]+[360,640]
    b = 1100*other[:,:2]/other[:,2:]+[360,640]
    train = np.arange(len(x))%5!=0
    f,_ = estimate(a[train],b[train])
    original = sampson_distance(f,a[~train],b[~train])
    lines = np.c_[a[~train],np.ones((~train).sum())]@f.T
    normal = lines[:,:2]/np.linalg.norm(lines[:,:2],axis=1)[:,None]
    across = sampson_distance(f,a[~train],b[~train]+40*normal)
    along = sampson_distance(f,a[~train],b[~train]+40*normal[:,::-1]*[-1,1])
    result = {'exact_held_p95_px':p95(original),'across_line_p95_px':p95(across),
              'along_line_40px_blindspot_p95_px':p95(along),'status':'TECHNICAL_CHECK_PASSED'}
    if p95(original)>=.01 or p95(across)<=3 or p95(along)>=.01:
        raise ValueError('two-view diagnostic controls failed')
    return result


def read_observations():
    manifest = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    doc = json.loads(manifest.read_text(encoding='utf-8'))
    case = next(c for c in doc['cases'] if c['id']=='real-case-001')
    selected = [a for a in doc['inputs'] if case['files']['video'] in (a.get('id'),a.get('path'),a.get('source'))]
    if len(selected)!=1:
        raise ValueError('video identity ambiguous')
    errors = validate_input_assets({**doc,'inputs':selected},manifest.parent)
    if errors:
        raise ValueError(errors)
    archive = ROOT/'assets/private/closed-experiments/0267-native-dense-video/evidence.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!='54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612':
        raise ValueError('observation archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith('/observations.npz')]
        if len(names)!=1:
            raise ValueError('observation member ambiguous')
        with np.load(io.BytesIO(z.read(names[0])),allow_pickle=False) as data:
            frame,ids,xy = data['frame'],data['ids'],data['xy']
    take = (frame>=0)&(frame<=876)&(frame%12==0)
    frame,ids,xy = frame[take],ids[take],xy[take]
    unique,counts = np.unique(ids,return_counts=True)
    eligible = set(unique[counts>=np.where(unique%5==0,4,3)].tolist())
    views = [{} for _ in range(74)]
    for fr,ident,point in zip(frame,ids,xy):
        if int(ident) not in eligible:
            continue
        row = views[int(fr//12)]
        if int(ident) in row or not np.isfinite(point).all():
            raise ValueError('duplicate/nonfinite source observation')
        row[int(ident)] = point.astype(float)
    REPORT['input'] = {'frames':74,'rows':sum(map(len,views)),
                       'video_sha256':selected[0]['sha256']}
    return views


def run():
    cv2.setNumThreads(4)
    p = options()
    REPORT['options'] = {name:getattr(p,name) for name in FIELDS}
    REPORT['runtime'] = {'opencv':cv2.__version__,'numpy':np.__version__}
    REPORT['controls'] = controls()
    views = read_observations()
    cohorts = []
    for i in range(74):
        for j in range(i+1,74):
            common = sorted(views[i].keys()&views[j].keys())
            train,held = [k for k in common if k%5!=0],[k for k in common if k%5==0]
            row = {'first':i*12,'second':j*12,'training':len(train),'held':len(held),'eligible':False}
            REPORT['pairs'].append(row)
            if min(len(train),len(held))<30:
                row['ineligible'] = 'fewer than30training/held common IDs'
                continue
            arrays = [np.array([views[v][k] for k in group]) for group in (train,held) for v in (i,j)]
            if any(np.any(np.ptp(a,axis=0)<50) for a in arrays):
                row['ineligible'] = 'less than50px partition span'
                continue
            row['eligible'] = True
            cohorts.append((row,arrays))
    REPORT['cohort'] = {'all_pairs':len(REPORT['pairs']),'eligible_pairs':len(cohorts)}
    started = time.monotonic()
    for index,(row,arrays) in enumerate(cohorts):
        if time.monotonic()-started>180:
            raise TimeoutError('audit180s cap')
        a,b,held_a,held_b = arrays
        try:
            f,inliers = estimate(a,b)
            errors = sampson_distance(f,held_a,held_b)
            row.update(fundamental=f.tolist(),training_inlier_fraction=float(np.count_nonzero(inliers)/len(a)),
                       training_p95_px=p95(sampson_distance(f,a,b)),held_p95_px=p95(errors),
                       held_screen_passed=bool(p95(errors)<=3))
        except (ValueError,cv2.error) as error:
            row.update(held_screen_passed=False,model_error=str(error))
        try:
            h,hmask = cv2.findHomography(a,b,options())
            if h is None or not np.isfinite(h).all():
                raise ValueError('no homography model')
            fraction = float(np.count_nonzero(hmask)/len(a))
            row.update(homography=h.tolist(),homography_fraction=fraction,
                       non_homography_dominated=bool(fraction<.8))
        except (ValueError,cv2.error) as error:
            row.update(non_homography_dominated=False,homography_error=str(error))
        if (index+1)%100==0:
            (OUT/'progress.json').write_text(json.dumps(REPORT),encoding='utf-8')
            print(json.dumps({'completed_pairs':index+1,'total':len(cohorts)}),flush=True)
    groups = {'all':cohorts,'gap12':[p for p in cohorts if p[0]['second']-p[0]['first']==12],
              'gap24..120':[p for p in cohorts if 24<=p[0]['second']-p[0]['first']<=120],
              'gap>120':[p for p in cohorts if p[0]['second']-p[0]['first']>120],
              'non_homography_dominated':[p for p in cohorts if p[0]['non_homography_dominated']]}
    REPORT['summary'] = {name:{'pairs':len(group),'passed':sum(r['held_screen_passed'] for r,_ in group),
        'failed':sum(not r['held_screen_passed'] for r,_ in group),
        'median_pair_p95_px':float(np.median([r['held_p95_px'] for r,_ in group if 'held_p95_px' in r]))
            if any('held_p95_px' in r for r,_ in group) else None} for name,group in groups.items()}
    REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
    REPORT['data_screen_status'] = 'REJECT' if not cohorts or any(not r['held_screen_passed'] for r,_ in cohorts) else 'UNVERIFIED'
    REPORT['audit_seconds'] = time.monotonic()-started


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=False)
    start = time.monotonic()
    try:
        run()
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        REPORT['seconds'] = time.monotonic()-start
        (OUT/'report.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in REPORT.items() if k!='pairs'}))
