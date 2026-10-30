"""Fixed-state derivative/multiplier audit; never updates camera parameters."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile
import cv2
import numpy as np
from PIL import Image
from scipy.optimize import nnls
from bounded_process import run
from direct_patch_camera import residual as photo_residual
from observation_constrained_photo import constraints,geometry
from short_track_camera import write

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets
OUT=ROOT/'assets/private/stationarity-0391'
ARCHIVE=ROOT/'assets/private/closed-experiments/0390-constrained-photo/evidence.zip'
OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def worker():
    assert sha(ARCHIVE)=='53be0c19fbfe1e47ed883925858d165a2cdc3328f95941f9fda51739e9dff710'
    index=json.loads(ARCHIVE.with_name('index.json').read_text())
    assert all(sha(p)==s for p,s in index['protected'].items())
    with zipfile.ZipFile(ARCHIVE) as z:
        def load(n):return dict(np.load(io.BytesIO(z.read(n)),allow_pickle=False))
        state=load('final.npz');obs=load('observations.npz')
        meta=json.loads(z.read('rgb-inputs.json'));graymeta=json.loads(z.read('inputs.json'))
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    assert sha(manifest)==meta['manifest_sha256']
    doc=json.loads(manifest.read_text());records=[r for r in doc['inputs'] if r['id']=='real-case-001-video']
    assert len(records)==1 and doc['training_allowed'] is False and doc['upload_allowed'] is False
    assert not validate_input_assets(dict(doc,inputs=records),manifest.parent)
    consent=manifest.parent/'provenance-confirmation.json'
    assert sha(consent)==meta['consent_sha256']
    ledger_path=ROOT/'assets/private/video-observability-0252/report.json'
    assert sha(ledger_path)==meta['ledger_sha256']
    ledger=json.loads(ledger_path.read_text());video=Path(records[0]['path'])
    assert sha(video)==meta['source_sha256']
    capture=cv2.VideoCapture(str(video));images={};ordinal=0
    try:
        while True:
            ok,bgr=capture.read()
            if not ok:break
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            assert ordinal<len(ledger['frame_records']) and hashlib.sha256(rgb.tobytes()).hexdigest()==ledger['frame_records'][ordinal]['rgb_sha256']
            if ordinal in (240,300,630):
                im=Image.fromarray(rgb).convert('L');buffer=io.BytesIO();im.save(buffer,format='PNG')
                camera=(240,300,630).index(ordinal)
                assert hashlib.sha256(buffer.getvalue()).hexdigest()==graymeta['images'][f'view-{camera}.png']
                images[camera]=np.asarray(im,float)/255
            ordinal+=1
    finally:capture.release()
    assert ordinal==1041 and len(images)==3
    images=np.stack([images[i] for i in range(3)])
    source=obs['xy'][0,obs['train']];targets=obs['xy'][1:,obs['train']]
    pixels=source[:,None,:]+OFFSETS;x=state['values'];scale=(state['upper']-state['lower'])/2
    def residual(v):
        _,poses,_=geometry(v,source)
        return photo_residual(images,pixels,np.exp(v[16:]),poses,np.r_[0.,v[12],v[14]],np.r_[0.,v[13],v[15]],v[0])[0].ravel()
    def cost(v):
        r=residual(v);return float(np.sum(.01**2*(np.sqrt(1+(r/.01)**2)-1)))
    replay=float(abs(residual(x)-state['residual']).max());assert replay<1e-12
    slack,jac=constraints(x,source,targets);active=np.flatnonzero(slack<=1e-6)
    normals=[row for row in jac[active]*scale]
    lower=np.flatnonzero((x-state['lower'])/scale<=1e-8);upper=np.flatnonzero((state['upper']-x)/scale<=1e-8)
    normals.extend(np.eye(len(x))[lower]);normals.extend(-np.eye(len(x))[upper])
    matrix=np.array(normals).T if normals else np.empty((len(x),0))
    lam,exact=nnls(np.array([[1.]]),np.array([2.]))
    _,negative=nnls(np.array([[1.]]),np.array([-2.]))
    assert exact==0 and lam[0]==2 and negative==2
    reports=[];gradients=[]
    for step in (1e-6,5e-7):
        g=np.empty(len(x))
        for column in range(len(x)):
            delta=np.zeros(len(x));delta[column]=scale[column]*step
            g[column]=(cost(x+delta)-cost(x-delta))/(2*step)
        multiplier,norm=nnls(matrix,g) if matrix.shape[1] else (np.array([]),float(np.linalg.norm(g)))
        gradients.append(g)
        reports.append(dict(normalized_step=step,gradient=g.tolist(),gradient_norm=float(np.linalg.norm(g)),
                            multiplier=multiplier.tolist(),stationarity_residual_norm=float(norm),
                            residual_ratio=float(norm/max(np.linalg.norm(g),1e-30))))
    agreement=float(np.linalg.norm(gradients[0]-gradients[1])/max(np.linalg.norm(gradients[1]),1e-30))
    report=dict(status='TECHNICAL_CHECK_PASSED',scope='local numerical diagnostic only;0390REJECT unchanged',
        frames_verified=ordinal,residual_replay_max=replay,loss=cost(x),active_observation_rows=active.tolist(),
        active_lower_columns=lower.tolist(),active_upper_columns=upper.tolist(),active_matrix_shape=list(matrix.shape),
        active_rank=int(np.linalg.matrix_rank(matrix)) if matrix.size else 0,min_slack=float(slack.min()),
        relative_gradient_disagreement=agreement,steps=reports,controls=dict(exact_residual=exact,reversed_gradient_residual=negative))
    write(OUT/'result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='steps'},indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k not in ('gradient','multiplier')} for r in reports],indent=2))


def controller():
    OUT.mkdir(exist_ok=False)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    result=run([sys.executable,'-B',str(Path(__file__).resolve()),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',120,2*1024**3)
    print(json.dumps(result,indent=2))
    if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)


def archive_result():
    index=json.loads(ARCHIVE.with_name('index.json').read_text())
    assert all(sha(p)==s for p,s in index['protected'].items())
    assert sha(ARCHIVE)==index['archive_sha256']
    assert json.loads((OUT/'worker.json').read_text())['exit']==0
    destination=ROOT/'assets/private/closed-experiments/0391-stationarity'
    destination.mkdir(exist_ok=False)
    files=sorted(p for p in OUT.iterdir() if p.is_file())
    keep={p.name:p for p in files};keep['source/stationarity_0391.py']=Path(__file__)
    target=destination/'evidence.zip'
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as archive:
        for name,p in keep.items():archive.write(p,name)
    members={name:dict(bytes=p.stat().st_size,sha256=sha(p)) for name,p in keep.items()}
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==v['sha256'] for name,v in members.items())
    report=dict(archive_sha256=sha(target),archive_bytes=target.stat().st_size,members=members,
                protected=index['protected'],loose_files=len(files),loose_bytes=sum(p.stat().st_size for p in files))
    write(destination/'index.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('members','protected')},indent=2))


if __name__=='__main__':
    if sys.argv[1]=='worker':worker()
    elif sys.argv[1]=='archive':archive_result()
    else:controller()
