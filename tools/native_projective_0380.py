"""Fixed rank-two objective diagnostic, not a camera reconstruction."""
import hashlib
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from headfoundry.epipolar import fundamental, sampson_distance
from bounded_process import run
OUT = ROOT/'assets/private/closed-experiments/0380-native-objective'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fit(a, b, initial):
    def transform(x):
        mean = x.mean(0); scale = np.sqrt(2)/np.linalg.norm(x-mean, axis=1).mean()
        return np.array([[scale,0,-scale*mean[0]],[0,scale,-scale*mean[1]],[0,0,1.]])
    ta,tb=transform(a),transform(b)
    normalized=np.linalg.inv(tb).T@initial@np.linalg.inv(ta)
    u,s,vt=np.linalg.svd(normalized)
    if np.linalg.det(u)<0: u[:,-1]*=-1
    if np.linalg.det(vt)<0: vt[-1]*=-1
    start=np.r_[np.zeros(6),np.arctan2(s[1],s[0])]
    def matrix(x):
        left=Rotation.from_rotvec(x[:3]).as_matrix()@u
        right=Rotation.from_rotvec(x[3:6]).as_matrix()@vt.T
        f=tb.T@left@np.diag([np.cos(x[6]),np.sin(x[6]),0.])@right.T@ta
        return f/np.linalg.norm(f)
    seed=matrix(start); initial=initial/np.linalg.norm(initial)
    assert min(np.max(abs(seed-initial)),np.max(abs(seed+initial)))<1e-10
    aa,bb=np.c_[a,np.ones(len(a))],np.c_[b,np.ones(len(b))]
    def objective(x):
        f=matrix(x);fa=aa@f.T;fb=bb@f
        denominator=np.sum(fa[:,:2]**2+fb[:,:2]**2,axis=1)
        if (denominator<1e-20).any(): raise ValueError('undefined native distance')
        return np.sum(bb*fa,axis=1)/np.sqrt(denominator)
    np.testing.assert_allclose(abs(objective(start)),sampson_distance(seed,a,b),atol=1e-10)
    lower=np.r_[np.full(6,-np.inf),1e-8];upper=np.r_[np.full(6,np.inf),np.pi/2-1e-8]
    initial_sse=float(objective(start)@objective(start))
    result=least_squares(objective,start,bounds=(lower,upper),method='trf',loss='linear',
                         x_scale='jac',max_nfev=200,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    f=matrix(result.x);sv=np.linalg.svd(f)[1]
    assert sv[-1]<1e-12 and sv[1]>0
    np.testing.assert_allclose(abs(result.fun),sampson_distance(f,a,b),atol=1e-9)
    return f,dict(converged=bool(result.success),nfev=result.nfev,message=result.message,
                  angle=float(result.x[6]),initial_sse=initial_sse,
                  final_sse=float(result.fun@result.fun),singular_values=sv.tolist())


def controls():
    rng=np.random.default_rng(379)
    points=rng.uniform([-1.,-1.,4.],[1.,1.,8.],(32,3))
    r=Rotation.from_rotvec([0,.2,0]).as_matrix();second=points@r.T+[.7,.1,.2]
    a=points[:,:2]/points[:,2:]*1200+[360,640]
    b=second[:,:2]/second[:,2:]*1200+[360,640]
    f,d=fit(a[:23],b[:23],fundamental(a[:23],b[:23]))
    exact=float(sampson_distance(f,a[23:],b[23:]).max())
    assert exact<1e-6 and d['converged']
    noisy=b+rng.normal(0,.3,b.shape)
    _,noise=fit(a[:23],noisy[:23],fundamental(a[:23],noisy[:23]))
    assert noise['converged'] and noise['final_sse']<=noise['initial_sse']+1e-12
    try: fundamental(np.ones((13,2)),np.ones((13,2)))
    except ValueError: pass
    else: raise AssertionError('degenerate input accepted')
    return dict(exact_held_max_px=exact,noisy=noise,degenerate_rejected=True)


def worker():
    check=controls()
    partition=ROOT/'assets/private/archived-geometry-0352/partition.npz'
    previous=ROOT/'assets/private/closed-experiments/0379-projective-screen/result.json'
    assert sha(partition)=='d0ef30239cfed66ec573dd529ec2037976f71499ae7eed77168855b4ed33f41a'
    assert sha(previous)=='3276acb38bd8d09e5c65a138ee0b6ddaca441ce467a90de75d3f15b8160fa9f3'
    record=json.loads(previous.read_text())
    assert all(sha(Path(p))==h for p,h in record['protected_sha256'].items())
    with np.load(partition,allow_pickle=False) as data:
        xy,train,held=(data[k] for k in ('xy','train','held'))
    results=[]
    for baseline in record['pairs']:
        a,b=baseline['pair'];initial=np.array(baseline['F'])
        f,detail=fit(xy[a,train],xy[b,train],initial)
        errors=sampson_distance(f,xy[a],xy[b]);p95=float(np.percentile(errors[held],95))
        passed=detail['converged'] and detail['final_sse']<=detail['initial_sse']+1e-12 and p95<=3
        results.append(dict(pair=[a,b],status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
            F=f.tolist(),all_residuals_px=errors.tolist(),held_p95_px=p95,
            train_p95_px=float(np.percentile(errors[train],95)),**detail))
    assert all(sha(Path(p))==h for p,h in record['protected_sha256'].items())
    result=dict(status='TECHNICAL_CHECK_PASSED' if all(r['status']=='TECHNICAL_CHECK_PASSED' for r in results) else 'REJECT',
        pairs=results,controls=check,protected_sha256=record['protected_sha256'],
        source_sha256=sha(Path(__file__)),scope='pairwise epipolar diagnostic; not physical reconstruction')
    with (OUT/'result.json').open('x') as stream: json.dump(result,stream,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in result.items() if k not in ('protected_sha256','source_sha256')},indent=2))


if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='worker':worker()
    else:
        OUT.mkdir(exist_ok=False);env=os.environ.copy()
        env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        print(run([sys.executable,'-B',str(Path(__file__)),'worker'],str(ROOT),env,
                  OUT/'worker.log',OUT/'worker.json',60,1024**3))
