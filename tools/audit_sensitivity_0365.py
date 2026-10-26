"""Local diagnostic only: never return or save a refitted camera."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile
import numpy as np
from bounded_process import run
from dense_photo_0332 import camera_values,cameras,intersect
from native_camera_jacobian import linearize
from short_track_camera import project

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/camera-sensitivity-0365'


def derivative_check(k,poses,points,rows):
    residual,jac,_=linearize(k,poses,points,rows,0,1)
    x=np.r_[camera_values(k,poses),points.ravel()]
    def value(v):
        kk,pp=cameras(v)
        return (project(kk,pp,v[12:].reshape(-1,3),rows)[0]-rows[:,2:]).ravel()
    worst=0.
    for i in range(len(x)):
        a=x.copy();b=x.copy();a[i]+=1e-6;b[i]-=1e-6
        numeric=(value(a)-value(b))/2e-6
        worst=max(worst,float(np.max(abs(numeric-jac[:,i])/(1+abs(numeric)))))
    assert worst<=1e-5,(worst,'derivative mismatch')
    return residual,jac,worst


def worker():
    folder=ROOT/'assets/private/dense-photo-0332'
    meta=json.loads((folder/'inputs.json').read_text())
    assert hashlib.sha256((folder/'truth.npz').read_bytes()).hexdigest()==meta['truth_sha256']
    truth=dict(np.load(folder/'truth.npz'));query=np.load(folder/'raw-endpoints.npz')['query']
    poses=truth['poses'].copy();poses[:,:3,3]/=float(truth['baseline'])
    archive=ROOT/'assets/private/cleanup-0363/evidence.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6cf96bb8745147d930925fa1c163986ecde35df21b7b8e0c11dc5b88a90c4043'
    with zipfile.ZipFile(archive) as z:
        prefix='assets/private/trackon-camera-0363/'
        oldobs=dict(np.load(io.BytesIO(z.read(prefix+'observations.npz'))))
        oldstate=dict(np.load(io.BytesIO(z.read(prefix+'solution.npz'))))
    cohorts=[('0332',dict(np.load(folder/'observations.npz')),dict(np.load(folder/'initial.npz'))),
             ('0363',oldobs,oldstate)]
    report={};arrays={}
    for name,obs,state in cohorts:
        ids=obs['source_ids'][obs['train']]
        xyz,labels=intersect(truth['poses'][0],query[ids],truth['rectangles'],truth['K'])
        assert (labels>=0).all()
        xyz/=float(truth['baseline'])
        rows=np.array([[c,i,*obs['xy'][c,t]] for c in range(3) for i,t in enumerate(obs['train'])])
        r,j,err=derivative_check(truth['K'],poses,xyz,rows)
        _,_,fiterr=derivative_check(state['K'],state['poses'],state['points'],rows)
        nuisance=j[:,1:];norm=np.linalg.norm(nuisance,axis=0);assert (norm>0).all()
        nuisance=nuisance/norm
        coef,_,rank,singular=np.linalg.lstsq(nuisance,j[:,0],rcond=1e-12)
        effective=j[:,0]-nuisance@coef
        information=float(effective@effective);assert information>0 and np.isfinite(information)
        influence=effective/information
        assert abs(float(influence@(j[:,0]*.001))-.001)<1e-8
        assert float(influence@np.zeros_like(r))==0
        contribution=(-r*influence).reshape(3,-1,2).sum(2)
        predicted=float(contribution.sum());actual=float(np.log(state['K'][0,0]/truth['K'][0,0]))
        arrays[name+'_source_ids']=ids;arrays[name+'_logf_contributions']=contribution
        report[name]=dict(train_points=len(ids),truth_derivative_relative_max=err,
            fitted_derivative_relative_max=fiterr,nuisance_rank=int(rank),nuisance_columns=nuisance.shape[1],
            effective_focal_norm=float(np.sqrt(information)),raw_focal_norm=float(np.linalg.norm(j[:,0])),
            linear_predicted_logf_error=predicted,recorded_logf_error=actual,
            per_view_logf_contribution=contribution.sum(1).tolist(),
            unweighted_observation_rms_px=float(np.sqrt(np.mean(r*r))))
    report['status']='TECHNICAL_CHECK_PASSED'
    report['scope']='local unweighted diagnostic; no refit or model quality promotion'
    np.savez(OUT/'contributions.npz',**arrays)
    (OUT/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


if __name__=='__main__':
    if sys.argv[-1]=='worker':worker()
    else:
        OUT.mkdir(exist_ok=False)
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        print(json.dumps(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',60,2*1024**3)))
