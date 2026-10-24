"""Original two-cue algebraic capability check, not model evaluation."""
import json
import os
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/depth-normal-0351'

def estimate(x,y,p,n):
    py,px = np.gradient(p,2.,2.)
    a,b,c = n.transpose(2,0,1)
    trim = (slice(2,-2),slice(2,-2))
    M = np.concatenate([np.stack([c*px,-a],-1)[trim].reshape(-1,2),
                        np.stack([c*py,-b],-1)[trim].reshape(-1,2)])
    rhs = np.concatenate([(a*p-px*(a*x+b*y))[trim].ravel(),
                          (b*p-py*(a*x+b*y))[trim].ravel()])
    norms = np.linalg.norm(M,axis=0)
    if not np.isfinite(M).all() or not np.isfinite(rhs).all() or (norms==0).any():
        return dict(identified=False,reason='zero or invalid information')
    scaled = M/norms
    solution,_,rank,singular = np.linalg.lstsq(scaled,rhs,rcond=1e-8)
    result = dict(identified=bool(rank==2),singular_values=singular.tolist(),rank=int(rank))
    if rank != 2:
        return result
    f,k = solution/norms
    result.update(focal=float(f),shift=float(k),positive=bool(f>0 and (p+k>0).all()),
                  equation_rms=float(np.sqrt(np.mean((M@(solution/norms)-rhs)**2))))
    return result

def worker():
    x,y = np.meshgrid(np.arange(-240.,241.,2.),np.arange(-320.,321.,2.))
    f = 1200.
    graphs = [(800+.0004*x*x+.0002*y*y+.0003*x*y,.0008*x+.0003*y,.0004*y+.0003*x),
              (800+30*np.sin(x/140)*np.cos(y/190)+.0002*x*x,
               30/140*np.cos(x/140)*np.cos(y/190)+.0004*x,
               -30/190*np.sin(x/140)*np.sin(y/190))]
    angle = np.deg2rad(1.)
    rotation = np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
    rows = []
    for z,zx,zy in graphs:
        n = np.stack([-f*zx,-f*zy,z+x*zx+y*zy],-1)
        n /= np.linalg.norm(n,axis=-1,keepdims=True)
        tx = np.stack([(z+x*zx)/f,y*zx/f,zx],-1)
        ty = np.stack([x*zy/f,(z+y*zy)/f,zy],-1)
        tangent = float(max(np.abs((n*tx).sum(-1)).max(),np.abs((n*ty).sum(-1)).max()))
        p = 1000/z-.7
        row = dict(tangent_error=tangent,exact=estimate(x,y,p,n),biased=estimate(x,y,p,n@rotation.T))
        for key in ('exact','biased'):
            if row[key]['identified']:
                row[key].update(focal_relative_error=abs(row[key]['focal']/f-1),
                                shift_error=abs(row[key]['shift']-.7))
        rows.append(row)
    plane = estimate(x,y,np.full(x.shape,.55),np.broadcast_to([0.,0.,1.],(*x.shape,3)))
    passed = not plane['identified'] and all(r['tangent_error']<1e-12 and
        r['exact']['identified'] and r['exact']['positive'] and
        r['exact']['focal_relative_error']<=.02 and r['exact']['shift_error']<=.02 for r in rows)
    report = dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',rows=rows,plane=plane,
                  real_camera='UNVERIFIED',model='NOT_RUN',medical_accuracy='UNVERIFIED')
    (OUT/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        worker()
    elif not sys.argv[1:]:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        print(json.dumps(run([sys.executable,str(Path(__file__).resolve()),'--worker'],ROOT,
             dict(os.environ),OUT/'worker.log',OUT/'worker.json',60,1024**3)))
    else:
        raise SystemExit('unsupported arguments')
