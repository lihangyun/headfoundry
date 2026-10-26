"""One preregistered synthetic physical-constraint check, no model inference."""
import hashlib
import json
import os
from pathlib import Path
import sys

import cv2
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/constrained-distance-0368'
SOURCE = ROOT / 'assets/private/depth-distance-0367/inputs.npz'


def fit(u, v, d, e):
    if np.ptp(d) <= 1e-12:
        return {'admitted': False, 'reason': 'constant first-view depth'}
    i, j = np.triu_indices(len(d), 1)
    norm = max(float(np.median((d[i] - d[j]) ** 2)), 1e-6)

    def clouds(q):
        f, s = np.exp(q[:2])
        x = np.c_[u / f, np.ones(len(d))] * (d + q[2])[:, None]
        y = np.c_[v / f, np.ones(len(e))] * (s * (e + q[3]))[:, None]
        return x, y

    def residual(q):
        x, y = clouds(q)
        return (np.sum((x[i]-x[j])**2, axis=1)-np.sum((y[i]-y[j])**2, axis=1))/norm

    lo = np.array([np.log(200), np.log(.1), -min(d)+.01, -min(e)+.01])
    hi = np.array([np.log(5000), np.log(10), 10, 10])
    sol = least_squares(residual, [np.log(1000), 0, 0, 0], bounds=(lo, hi),
                        method='trf', loss='linear', max_nfev=200,
                        ftol=1e-12, xtol=1e-12, gtol=1e-12, x_scale='jac')
    x, y = clouds(sol.x)
    a, _, bt = np.linalg.svd((x-x.mean(0)).T @ (y-y.mean(0)))
    r = bt.T @ np.diag([1, 1, np.linalg.det(bt.T @ a.T)]) @ a.T
    t = y.mean(0)-r@x.mean(0)
    boundary = bool(np.any(sol.x-lo <= 1e-6) or np.any(hi-sol.x <= 1e-6))
    return {'admitted': bool(sol.success and not boundary and np.all(x[:,2]>0) and np.all(y[:,2]>0)),
            'f': float(np.exp(sol.x[0])), 's': float(np.exp(sol.x[1])),
            'shifts': sol.x[2:].tolist(), 'R': r.tolist(), 't': t.tolist(),
            'nfev': sol.nfev, 'success': bool(sol.success), 'boundary': boundary,
            'residual_rms': float(np.sqrt(np.mean(sol.fun**2)))}


def worker():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '812bbc4ed7c53c3d7d391482efb9dbb70991bba2318d9798172f36d562fd68f3'
    data = dict(np.load(SOURCE))
    results = {}
    for name in ('exact', 'stress'):
        u,v,d,e = [data[k].copy() for k in ('u','v','d','e')]
        if name == 'stress':
            u += .5*np.sin(np.arange(80).reshape(40,2))
            v += .5*np.sin(np.arange(80).reshape(40,2)+2)
            d += .005*np.sin(np.arange(40)+4)
            e += .005*np.sin(np.arange(40)+6)
        result = fit(u,v,d,e)
        r,t = np.array(result['R']),np.array(result['t'])
        predicted = data['x']@r.T+t
        def project(x,f):
            return x[:,:2]/x[:,2,None]*f
        errors = [float(np.percentile(np.linalg.norm(project(a,result['f'])-b,axis=1),95))
                  for a,b in ((data['x'],data['u']),(predicted,data['v']))]
        focal = abs(result['f']/1200-1)
        alignment = float(np.percentile(np.linalg.norm(predicted-data['y'],axis=1),95))
        rotation = float(np.linalg.norm(cv2.Rodrigues(r@data['R'].T)[0]))
        passed = focal<=1e-6 and alignment<=1e-6 and rotation<=1e-6 if name=='exact' else focal<=.02 and max(errors)<=3
        result.update(focal_relative_error=focal, alignment_p95=alignment,
                      rotation_error_rad=rotation, projection_p95=errors,
                      passed=bool(passed and result['admitted']))
        results[name] = result
    results['plane'] = fit(data['u'],data['v'],np.full(40,2.7),data['e'])
    results['status'] = 'TECHNICAL_CHECK_PASSED' if all(results[k]['passed'] for k in ('exact','stress')) and not results['plane']['admitted'] else 'REJECT'
    (OUT/'result.json').write_text(json.dumps(results,indent=2))


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:] == ['worker']:
        worker()
    else:
        from bounded_process import run
        env = dict(os.environ,OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        print(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',60,1024**3))
