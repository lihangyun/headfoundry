"""One fixed-state interpolation attribution; no camera optimization."""
import ast
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/'assets/private/closed-experiments/0391-stationarity/evidence.zip'


def audit(images,pixels,x,scale,state,source,geometry,photo_residual,**unused):
    def evaluate(v):
        _,poses,_=geometry(v,source)
        return photo_residual(images,pixels,np.exp(v[16:]),poses,
            np.r_[0.,v[12],v[14]],np.r_[0.,v[13],v[15]],v[0])
    residual,uv=evaluate(x)
    assert np.max(abs(residual.ravel()-state['residual']))<1e-12
    low=np.floor(uv).astype(int)
    def corners(image,ij):
        a=image[ij[...,1],ij[...,0]];b=image[ij[...,1],ij[...,0]+1]
        c=image[ij[...,1]+1,ij[...,0]];d=image[ij[...,1]+1,ij[...,0]+1]
        return a,b-a,c-a,d-b-c+a
    co=np.array([corners(im,ij) for im,ij in zip(images[1:],low)])
    def polynomial(w):
        dx,dy=np.moveaxis(w-low,-1,0)
        return co[:,0]+co[:,1]*dx+co[:,2]*dy+co[:,3]*dx*dy
    frac=uv-low
    spatial=np.stack((co[:,1]+co[:,3]*frac[...,1],co[:,2]+co[:,3]*frac[...,0]),-1)
    reference=(polynomial(uv)-residual-x[[13,15],None,None])/np.exp(x[[12,14],None,None])
    def loss(r):return np.sum(.0001*(np.sqrt(1+(r/.01)**2)-1))
    influence=residual/np.sqrt(1+(residual/.01)**2)
    # Known affine polynomial and kink-crossing controls.
    plane=np.arange(25).reshape(5,5)*3.+np.arange(5)[None,:]*2.
    a,b,c,d=corners(plane,np.array([[1,1]]))
    assert b[0]==5 and c[0]==15 and d[0]==0
    assert abs(abs(-.1)-(-.1))==.2
    results=[]
    for h in (1e-6,5e-7):
        actual=[];frozen=[];chain=[];crossings=[]
        for j in range(len(x)):
            delta=np.zeros(len(x));delta[j]=scale[j]*h
            rp,wp=evaluate(x+delta);rm,wm=evaluate(x-delta)
            def fixed(v,w):
                return polynomial(w)-np.exp(v[[12,14],None,None])*reference-v[[13,15],None,None]
            actual.append(float((loss(rp)-loss(rm))/(2*h)))
            frozen.append(float((loss(fixed(x+delta,wp))-loss(fixed(x-delta,wm)))/(2*h)))
            dr=np.sum(spatial*(wp-wm)/(2*h),axis=-1)
            if j in (12,14):dr[(j-12)//2]-=np.exp(x[j])*reference[(j-12)//2]*scale[j]
            if j in (13,15):dr[(j-13)//2]-=scale[j]
            chain.append(float(np.sum(influence*dr)))
            crossed=np.any((np.floor(wp)!=low)|(np.floor(wm)!=low),axis=-1)
            if crossed.any():crossings.append(dict(column=j,samples=np.argwhere(crossed).tolist()))
        results.append(dict(step=h,actual=actual,frozen=frozen,hybrid_chain=chain,crossings=crossings))
    norm=lambda v:float(np.linalg.norm(v))
    report=dict(status='TECHNICAL_CHECK_PASSED',scope='fixed-state interpolation only',steps=results,
        actual_difference=norm(np.subtract(results[0]['actual'],results[1]['actual'])),
        frozen_difference=norm(np.subtract(results[0]['frozen'],results[1]['frozen'])),
        chain_difference=norm(np.subtract(results[0]['hybrid_chain'],results[1]['hybrid_chain'])),
        frozen_chain_errors=[norm(np.subtract(r['frozen'],r['hybrid_chain'])) for r in results])
    out=ROOT/'assets/private/closed-experiments/0392-cells'
    out.mkdir(exist_ok=False)
    payload=json.dumps(report,indent=2).encode()
    with zipfile.ZipFile(out/'evidence.zip','x',zipfile.ZIP_DEFLATED) as z:
        z.writestr('result.json',payload);z.write(__file__,'source/cell_audit_0392.py')
    with zipfile.ZipFile(out/'evidence.zip') as z:assert z.testzip() is None
    print(json.dumps({k:v for k,v in report.items() if k!='steps'},indent=2))
    print('crossed samples', [sum(len(c['samples']) for c in r['crossings']) for r in results])
    print('archive_sha256',hashlib.sha256((out/'evidence.zip').read_bytes()).hexdigest())


assert hashlib.sha256(ARCH.read_bytes()).hexdigest()=='bbea7583e92a2faf7f23cfd93459cbcd6e07f24ed794bdb52e8d64579f999a70'
with zipfile.ZipFile(ARCH) as z:tree=ast.parse(z.read('source/stationarity_0391.py'))
worker=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='worker')
cut=next(i for i,n in enumerate(worker.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Tuple) and any(isinstance(q,ast.Name) and q.id=='slack' for q in t.elts) for t in n.targets))
worker.body=worker.body[:cut]+ast.parse('audit(**locals(), geometry=geometry, photo_residual=photo_residual)').body
tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
env={'__file__':str(Path(__file__).resolve()),'audit':audit}
exec(compile(ast.fix_missing_locations(tree),'<archived-intake-only>','exec'),env)
env['worker']()
