"""Fixed measurement-space correction; no inference or scan data."""
import json
import os
from pathlib import Path
import sys
import cv2
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/measurement-space-0371'


def project(x,f):
    return x[:,:2]/x[:,2,None]*f


def correct(u,v,d,e,initial):
    n=len(d)
    q=np.r_[np.log(initial['f']),np.log(initial['s']),initial['shifts'],
            cv2.Rodrigues(np.array(initial['R']))[0].ravel(),initial['t'],
            (np.c_[u/initial['f'],np.ones(n)]*(d+initial['shifts'][0])[:,None]).ravel()]
    def unpack(q):
        x=q[10:].reshape(n,3)
        r=cv2.Rodrigues(q[4:7])[0]
        return x,x@r.T+q[7:10],r
    def residual(q):
        x,y,_=unpack(q)
        if np.any(y[:,2]<=0):
            return np.full(6*n,np.inf)
        return np.c_[(project(x,np.exp(q[0]))-u)/.5,
                     (project(y,np.exp(q[0]))-v)/.5,
                     (x[:,2]-q[2]-d)/.005,
                     (y[:,2]/np.exp(q[1])-q[3]-e)/.005].ravel()
    lo=np.r_[np.log(200),np.log(.1),-10,-10,np.full(6,-np.inf),np.tile([-100,-100,.01],n)]
    hi=np.r_[np.log(5000),np.log(10),10,10,np.full(6,np.inf),np.tile([100,100,100],n)]
    sol=least_squares(residual,q,bounds=(lo,hi),method='trf',loss='linear',jac='2-point',
                      x_scale='jac',max_nfev=100,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    x,y,r=unpack(sol.x)
    boundary=bool(np.any(sol.x-lo<=1e-6) or np.any(hi-sol.x<=1e-6))
    return dict(f=float(np.exp(sol.x[0])),s=float(np.exp(sol.x[1])),shifts=sol.x[2:4].tolist(),
                R=r.tolist(),t=sol.x[7:10].tolist(),nfev=sol.nfev,success=bool(sol.success),
                boundary=boundary,positive=bool(min(x[:,2].min(),y[:,2].min())>0),
                initial_rms=float(np.sqrt(np.mean(residual(q)**2))),
                final_rms=float(np.sqrt(np.mean(sol.fun**2)))),sol.x


def worker():
    report={};states={}
    for label,inp,out,f in (('0368','depth-distance-0367','constrained-distance-0368',1200),
                            ('0369','distance-heldout-0369','distance-heldout-0369',900)):
        data=dict(np.load(ROOT/f'assets/private/{inp}/inputs.npz'))
        previous=json.loads((ROOT/f'assets/private/{out}/result.json').read_text())
        for mode in ('exact','stress'):
            u,v,d,e=[data[k][:40].copy() for k in ('u','v','d','e')]
            if mode=='stress':
                u+=.5*np.sin(np.arange(80).reshape(40,2));v+=.5*np.sin(np.arange(80).reshape(40,2)+2)
                d+=.005*np.sin(np.arange(40)+4);e+=.005*np.sin(np.arange(40)+6)
            q,state=correct(u,v,d,e,previous[mode])
            selection=slice(None) if label=='0368' else slice(40,None)
            x,y=data['x'][selection],data['y'][selection]
            predicted=x@np.array(q['R']).T+q['t']
            errors=[float(np.percentile(np.linalg.norm(project(a,q['f'])-b,axis=1),95))
                    for a,b in ((x,data['u'][selection]),(predicted,data['v'][selection]))]
            focal=abs(q['f']/f-1)
            point=float(np.percentile(np.linalg.norm(predicted-y,axis=1),95))
            passed=focal<=1e-6 and point<=1e-6 if mode=='exact' else focal<=.02 and max(errors)<=3
            q.update(focal_relative_error=focal,projection_p95=errors,point_p95=point,
                     passed=bool(passed and q['success'] and not q['boundary'] and q['positive'] and np.all(predicted[:,2]>0)))
            report[label+'-'+mode]=q;states[label+'-'+mode]=state
    report['status']='TECHNICAL_CHECK_PASSED' if all(q['passed'] for q in report.values()) else 'REJECT'
    np.savez(OUT/'states.npz',**states)
    (OUT/'result.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        env=dict(os.environ,OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        print(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',120,1024**3))
