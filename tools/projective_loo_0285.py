"""Read-only frozen projective camera diagnostic;not metric/head acceptance."""
import hashlib
import io
import json
from pathlib import Path
import time
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/batched-varpro-0285'


def evaluate(p,records):
    errors,frames,ids = [],[],[]
    invalid = 0
    for ident,observed in records.items():
        views = sorted(observed)
        for target in views:
            rows = []
            for view in views:
                if view == target:
                    continue
                u,v = observed[view]
                for row in (u*p[view,2]-p[view,0],v*p[view,2]-p[view,1]):
                    norm = np.linalg.norm(row)
                    if norm == 0 or not np.isfinite(norm):
                        raise ValueError('invalid equation row')
                    rows.append(row/norm)
            a = np.asarray(rows)
            _,sv,vh = np.linalg.svd(a,full_matrices=False)
            error = np.inf
            if len(sv)==4 and sv[-2]>np.finfo(float).eps*max(a.shape)*sv[0]:
                h = p[target]@vh[-1]
                if np.isfinite(h).all() and h[2]!=0:
                    error = float(np.linalg.norm(h[:2]/h[2]-observed[target]))
            invalid += int(not np.isfinite(error))
            errors.append(error)
            frames.append(target)
            ids.append(ident)
    errors,frames = np.asarray(errors),np.asarray(frames)
    def p95(values):
        return float(np.sort(values)[int(np.ceil(.95*len(values)))-1]) if len(values) else np.inf
    summary = {'rows':len(errors),'identities':len(records),'invalid':invalid,
               'p95_px':p95(errors),'per_view':[{'view':i,'count':int((frames==i).sum()),
               'p95_px':p95(errors[frames==i])} for i in range(len(p))],
               'scope':'PROJECTIVE_CONSISTENCY_ONLY;NO_METRIC_CAMERA_OR_HEAD_ACCEPTANCE'}
    return summary,errors,frames,np.asarray(ids)


def control():
    rng = np.random.default_rng(285)
    xyz = rng.uniform(-1,1,(40,3))
    p = np.array([[[1100.,0,360.,i*100],[0,1100.,640.,0],[0,0,1.,8.]] for i in range(5)])
    h = np.array([[1.2,.1,.05,.2],[0,.9,.03,-.1],[.02,0,1.1,.3],[.04,-.02,.01,1.]])
    cameras = p@h
    records = {}
    for j,x in enumerate(xyz):
        records[j] = {}
        for i,c in enumerate(p):
            if i == (j//5)%5:
                continue
            image = c@np.r_[x,1]
            records[j][i] = image[:2]/image[2]
    good,_,_,_ = evaluate(cameras,records)
    wrong = cameras.copy()
    wrong[2,0] += 25*wrong[2,2]
    bad,_,_,_ = evaluate(wrong,records)
    if good['invalid'] or good['p95_px']>=1e-8 or bad['p95_px']<=3:
        raise ValueError('projective evaluator control failed')
    return {'status':'TECHNICAL_CHECK_PASSED','exact_p95_px':good['p95_px'],
            'negative_p95_px':bad['p95_px']}


def main():
    start = time.monotonic()
    controls = control()
    model = OUT/'patient-projective.npz'
    before = hashlib.sha256(model.read_bytes()).hexdigest()
    with np.load(model,allow_pickle=False) as data:
        p = data['cameras']
    if p.shape!=(74,3,4) or not np.isfinite(p).all():
        raise ValueError('invalid frozen projective cameras')
    archive = ROOT/'assets/private/closed-experiments/0267-native-dense-video/evidence.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!='54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612':
        raise ValueError('frozen observations hash')
    with zipfile.ZipFile(archive) as z:
        name = next(n for n in z.namelist() if n.endswith('/observations.npz'))
        with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as obs:
            frame,ids,xy = obs['frame'],obs['ids'],obs['xy']
    records = {}
    selected = (frame>=0)&(frame<=876)&(frame%12==0)&(ids%5==0)
    for fr,ident,point in zip(frame[selected],ids[selected],xy[selected]):
        rows = records.setdefault(int(ident),{})
        view = int(fr//12)
        if view in rows or not np.isfinite(point).all():
            raise ValueError('duplicate/nonfinite held observation')
        rows[view] = point.astype(float)
    records = {i:r for i,r in records.items() if len(r)>=4}
    k = np.array([[1500.,0,360],[0,1500.,640],[0,0,1.]])
    summary,errors,frames,identities = evaluate(k@p,records)
    summary.update(control=controls,source_sha256=before,seconds=time.monotonic()-start,
                   necessary_threshold_passed=bool(not summary['invalid'] and summary['p95_px']<=3
                    and all(v['count']>=30 and v['p95_px']<=3 for v in summary['per_view'])))
    after = hashlib.sha256(model.read_bytes()).hexdigest()
    if before!=after:
        raise ValueError('frozen camera output mutated')
    summary['source_unchanged'] = True
    np.savez_compressed(OUT/'projective-held-diagnostic.npz',errors=errors,views=frames,ids=identities)
    (OUT/'projective-held-diagnostic.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
