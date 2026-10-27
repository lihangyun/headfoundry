"""Frozen local response, never a camera fit."""
import json
import os
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/distance-sensitivity-0370'


def residual_jac(q,u,v,d,e):
    f,s = np.exp(q[:2])
    a,b = np.c_[u/f,np.ones(len(d))],np.c_[v/f,np.ones(len(e))]
    x,y = a*(d+q[2])[:,None],s*b*(e+q[3])[:,None]
    i,j = np.triu_indices(len(d),1)
    dx,dy = x[i]-x[j],y[i]-y[j]
    norm = max(float(np.median((d[i]-d[j])**2)),1e-6)
    zx,zy = np.zeros_like(x),np.zeros_like(y)
    xf,yf = -x.copy(),-y.copy()
    xf[:,2]=0
    yf[:,2]=0
    jac = np.column_stack([2*(np.sum(dx*(xx[i]-xx[j]),axis=1)-np.sum(dy*(yy[i]-yy[j]),axis=1))/norm
                           for xx,yy in ((xf,yf),(zx,y),(a,zy),(zx,s*b))])
    return (np.sum(dx*dx,axis=1)-np.sum(dy*dy,axis=1))/norm,jac


def worker():
    report = {}
    for label,inp,res,f in (('0368','depth-distance-0367','constrained-distance-0368',1200),
                             ('0369','distance-heldout-0369','distance-heldout-0369',900)):
        data = dict(np.load(ROOT/f'assets/private/{inp}/inputs.npz'))
        stored = json.loads((ROOT/f'assets/private/{res}/result.json').read_text())['stress']
        args = [data[k][:40].copy() for k in ('u','v','d','e')]
        q = np.array([np.log(f),np.log(1.2),.3,-.2])
        zero,jac = residual_jac(q,*args)
        errors=[]
        for k in range(4):
            h=np.zeros(4);h[k]=1e-6
            fd=(residual_jac(q+h,*args)[0]-residual_jac(q-h,*args)[0])/2e-6
            errors.append(float(np.max(abs(fd-jac[:,k]))/max(1,float(np.max(abs(fd))))))
        assert max(errors)<=1e-5
        response=lambda residual: np.linalg.lstsq(jac,-residual,rcond=1e-12)[0]
        assert np.max(abs(response(zero)))<1e-9
        assert np.max(abs(response(.001*jac[:,0])-np.array([-.001,0,0,0])))<1e-9
        nuisance=jac[:,1:]
        effective=jac[:,0]-nuisance@np.linalg.lstsq(nuisance,jac[:,0],rcond=1e-12)[0]
        shifts={}
        for mode in ('pixels','depth','combined'):
            u,v,d,e=[a.copy() for a in args]
            if mode!='depth':
                u+=.5*np.sin(np.arange(80).reshape(40,2))
                v+=.5*np.sin(np.arange(80).reshape(40,2)+2)
            if mode!='pixels':
                d+=.005*np.sin(np.arange(40)+4)
                e+=.005*np.sin(np.arange(40)+6)
            shifts[mode]=response(residual_jac(q,u,v,d,e)[0]).tolist()
        report[label]={'jacobian_relative_errors':errors,'normalized_singular_values':np.linalg.svd(jac/np.linalg.norm(jac,axis=0),compute_uv=False).tolist(),
                       'effective_focal_norm':float(np.linalg.norm(effective)),
                       'predicted_parameter_shifts':shifts,'actual_logf_shift':float(np.log(stored['f']/f)),
                       'combined_prediction_remainder':float(np.log(stored['f']/f)-shifts['combined'][0])}
    report['status']='TECHNICAL_CHECK_PASSED'
    (OUT/'result.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        env=dict(os.environ,OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        print(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',60,1024**3))
