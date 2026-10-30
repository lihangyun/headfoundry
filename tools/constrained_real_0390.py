"""Fixed constrained photometric trial; archived intake, no neural/scan reads."""
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile
import cv2
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import minimize
from bounded_process import run
from direct_patch_camera import residual as photo_residual
from observation_constrained_photo import constraints,geometry
from short_track_camera import intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets
BASE=ROOT/'assets/private/constrained-photo-0390'
OUT=BASE
CLOSED=ROOT/'assets/private/closed-experiments'
DEADLINE=1793321266
OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def bootstrap():
    path=CLOSED/'0387-real-photo/evidence.zip'
    assert sha(path)=='c4f2d312cff990a7ce930dc1a034f5fb1513885079230dad54d5603054d3655c'
    with zipfile.ZipFile(path) as archive:source=archive.read('source/real_photo_0387.py')
    wanted={'functions','load','intake'}
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    assert {n.name for n in nodes}==wanted
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-intake-0387','exec'),globals())
    load()


def fit():
    global OUT
    bootstrap();read_audit()
    images=read_images();obs=dict(np.load(BASE/'observations.npz'));initial=dict(np.load(BASE/'initial.npz'))
    before=sha(BASE/'observations.npz');train=obs['train'];held=obs['held']
    assert len(train)==28 and len(held)==9 and not set(train)&set(held)
    assert set(train)|set(held)==set(range(37))
    source=obs['xy'][0,train].copy();targets=obs['xy'][1:,train].copy()
    pixels=source[:,None,:]+OFFSETS
    values=np.r_[camera_values(initial['K'],initial['poses']),np.zeros(4),np.log(1/initial['points'][:,2])]
    lower=values.copy();upper=values.copy();lower[0]=np.log(640.);upper[0]=np.log(5120.)
    lower[1:12]-=np.r_[np.full(8,.1),np.full(3,.2)];upper[1:12]+=np.r_[np.full(8,.1),np.full(3,.2)]
    lower[12:16]=[-.3,-.05,-.3,-.05];upper[12:16]=[.3,.05,.3,.05];lower[16:]-=.3;upper[16:]+=.3
    def residual(x):
        _,poses,_=geometry(x,source)
        return photo_residual(images,pixels,np.exp(x[16:]),poses,np.r_[0.,x[12],x[14]],np.r_[0.,x[13],x[15]],x[0])[0].ravel()
    def objective(x):
        r=residual(x)
        return float(np.sum(.01**2*(np.sqrt(1+(r/.01)**2)-1)))
    def slack(x):return constraints(x,source,targets)[0]
    def derivative(x):return constraints(x,source,targets)[1]
    start_slack=slack(values);start_residual=residual(values)
    write(BASE/'entry.json',dict(minimum_start_slack=float(start_slack.min()),observations_sha256=before,
                              held_count=len(held),train_count=len(train),loss_start=objective(values)))
    if (start_slack<0).any():raise ValueError('starting observation constraints infeasible')
    result=minimize(objective,values,method='SLSQP',jac='2-point',bounds=list(zip(lower,upper)),
                    constraints={'type':'ineq','fun':slack,'jac':derivative},options={'maxiter':150,'ftol':1e-9})
    k,poses,points=geometry(result.x,source);last_residual=residual(result.x);last_slack=slack(result.x)
    np.savez_compressed(BASE/'final.npz',K=k,poses=poses,points=points,values=result.x,lower=lower,upper=upper,
                        residual=last_residual,slack=last_slack,start_slack=start_slack)
    write(BASE/'optimization.json',dict(optimizer_success=bool(result.success),message=result.message,
          iterations=int(result.nit),evaluations=int(result.nfev),minimum_slack=float(last_slack.min()),
          max_train_px=float(np.sqrt(max(0,9-last_slack.min()))),violations_over_tolerance=int((last_slack<-1e-6).sum()),
          photo_rms_start=float(np.sqrt(np.mean(start_residual**2))),photo_rms_final=float(np.sqrt(np.mean(last_residual**2))),
          loss_final=float(result.fun),focal_px=float(k[0,0]),observations_unchanged=sha(BASE/'observations.npz')==before))
    assert sha(BASE/'observations.npz')==before
    if not result.success or (last_slack<-1e-6).any() or not 640.640<k[0,0]<5114.88:
        raise ValueError('optimizer,feasibility or nonbound focal gate fails')
    folder=BASE/'evaluation';folder.mkdir(exist_ok=False)
    (folder/'observations.npz').write_bytes((BASE/'observations.npz').read_bytes())
    (folder/'initial.npz').write_bytes((BASE/'final.npz').read_bytes())
    OUT=folder
    try:evaluate()
    finally:OUT=BASE


def controller(stage):
    if time.time()>DEADLINE:raise RuntimeError('whole deadline')
    if stage=='intake':BASE.mkdir(exist_ok=False)
    receipt=BASE/(stage+'-worker.json')
    if receipt.exists():raise RuntimeError('no repeat worker')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    result=run([sys.executable,'-B',str(Path(__file__).resolve()),stage+'-worker'],str(ROOT),env,
               BASE/(stage+'.log'),receipt,min(120 if stage=='intake' else 300,DEADLINE-time.time()),2*1024**3)
    print(json.dumps(result,indent=2))
    if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)


if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        try:
            if stage=='intake-worker':bootstrap();intake()
            elif stage=='fit-worker':fit()
            else:raise ValueError('unknown worker')
        except Exception as error:
            write(BASE/(stage+'-failure.json'),dict(status='REJECT',type=type(error).__name__,error=str(error)))
            raise
    else:controller(stage)
