"""One original analytic normal-field experiment; no external data."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/normal-integrability-0350'

def estimate(n, x, y):
    ny, nx = np.gradient(n, 2., 2., axis=(0,1))
    a,b,c = n.transpose(2,0,1)
    ax,bx,cx = nx.transpose(2,0,1)
    ay,by,cy = ny.transpose(2,0,1)
    A = c*(bx-ay)+a*cy-b*cx
    B = x*(a*bx-b*ax)+y*(a*by-b*ay)
    A,B = A[2:-2,2:-2].ravel(),B[2:-2,2:-2].ravel()
    energy = float(A@A)
    if energy < 1e-24:
        return dict(degenerate=True, energy=energy)
    f = float(-(A@B)/energy)
    return dict(degenerate=False, focal=f, energy=energy,
                equation_rms=float(np.sqrt(np.mean((A*f+B)**2))))

def main():
    OUT.mkdir(exist_ok=False)
    x,y = np.meshgrid(np.arange(-240.,241.,2.),np.arange(-320.,321.,2.))
    f = 1200.
    graphs = [
        (800+.0004*x*x+.0002*y*y+.0003*x*y,.0008*x+.0003*y,.0004*y+.0003*x),
        (800+30*np.sin(x/140)*np.cos(y/190)+.0002*x*x,
         30/140*np.cos(x/140)*np.cos(y/190)+.0004*x,
         -30/190*np.sin(x/140)*np.sin(y/190))]
    angle = np.deg2rad(1.)
    rotation = np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
    rows = []
    for z,zx,zy in graphs:
        n = np.stack([-f*zx,-f*zy,z+x*zx+y*zy],axis=-1)
        n /= np.linalg.norm(n,axis=-1,keepdims=True)
        tx = np.stack([(z+x*zx)/f,y*zx/f,zx],axis=-1)
        ty = np.stack([x*zy/f,(z+y*zy)/f,zy],axis=-1)
        tangent_error = float(max(np.abs((n*tx).sum(-1)).max(),np.abs((n*ty).sum(-1)).max()))
        assert tangent_error < 1e-12
        exact = estimate(n,x,y)
        biased = estimate(n@rotation.T,x,y)
        for item in (exact,biased):
            item['relative_focal_error'] = abs(item['focal']/f-1)
        rows.append(dict(tangent_error=tangent_error,exact=exact,bias_1degree=biased))
    plane = estimate(np.broadcast_to([0.,0.,1.],(*x.shape,3)),x,y)
    assert plane['degenerate']
    controls = all(r['exact']['relative_focal_error']<=.02 for r in rows)
    stress = all(r['bias_1degree']['relative_focal_error']<=.02 for r in rows)
    report = dict(status='TECHNICAL_CHECK_PASSED' if controls and stress else 'REJECT',
        controls_pass=controls,stress_pass=stress,plane=plane,curved_surfaces=rows,
        model_accuracy='UNVERIFIED',real_head_accuracy='UNVERIFIED')
    (OUT/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__ == '__main__':
    main()
