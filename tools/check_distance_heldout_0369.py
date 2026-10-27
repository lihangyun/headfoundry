"""Frozen independent holdout; reuse unchanged0368 estimator."""
import json
import os
from pathlib import Path
import sys
import cv2
import numpy as np
from check_constrained_distance_0368 import fit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/distance-heldout-0369'


def project(x,f):
    return x[:,:2]/x[:,2,None]*f


def worker():
    rng = np.random.default_rng(369)
    x = np.c_[rng.uniform(-.6,.6,(60,2)),rng.uniform(2.5,3.5,60)]
    r = cv2.Rodrigues(np.array([-.15,.18,.06]))[0]
    t = np.array([-.12,.09,.16])
    y = x@r.T+t
    u,v = project(x,900),project(y,900)
    d,e = x[:,2]-.3,y[:,2]/1.2+.2
    np.savez(OUT/'inputs.npz',x=x,y=y,R=r,t=t,u=u,v=v,d=d,e=e)
    results = {}
    for name in ('exact','stress'):
        uu,vv,dd,ee = [a.copy() for a in (u,v,d,e)]
        if name == 'stress':
            uu += .5*np.sin(np.arange(120).reshape(60,2))
            vv += .5*np.sin(np.arange(120).reshape(60,2)+2)
            dd += .005*np.sin(np.arange(60)+4)
            ee += .005*np.sin(np.arange(60)+6)
        q = fit(uu[:40],vv[:40],dd[:40],ee[:40])
        rr,tt = np.array(q['R']),np.array(q['t'])
        yy = x@rr.T+tt
        errors = np.c_[np.linalg.norm(project(x,q['f'])-u,axis=1),
                        np.linalg.norm(project(yy,q['f'])-v,axis=1)]
        held = np.percentile(errors[40:],95,axis=0)
        focal = abs(q['f']/900-1)
        point = float(np.percentile(np.linalg.norm(yy[40:]-y[40:],axis=1),95))
        passed = focal<=1e-6 and point<=1e-6 if name=='exact' else focal<=.02 and max(held)<=3
        q.update(focal_relative_error=focal,held_projection_p95=held.tolist(),
                 train_projection_p95=np.percentile(errors[:40],95,axis=0).tolist(),
                 held_point_p95=point,rotation_error_rad=float(np.linalg.norm(cv2.Rodrigues(rr@r.T)[0])),
                 passed=bool(passed and q['admitted'] and np.all(yy[40:,2]>0)))
        results[name] = q
    results['status'] = 'TECHNICAL_CHECK_PASSED' if all(results[k]['passed'] for k in ('exact','stress')) else 'REJECT'
    (OUT/'result.json').write_text(json.dumps(results,indent=2))


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:] == ['worker']:
        worker()
    else:
        from bounded_process import run
        env = dict(os.environ,OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        print(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',60,1024**3))
