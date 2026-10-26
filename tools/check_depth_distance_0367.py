"""Original distance-invariant capacity check; no model or patient input."""
import json
import os
from pathlib import Path
import sys
import cv2
import numpy as np
from bounded_process import run

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/private/depth-distance-0367'


def terms(uv,d):
    i,j=np.triu_indices(len(d),1);p=d[:,None]*uv
    dp=p[i]-p[j];du=uv[i]-uv[j]
    return (np.sum(dp*dp,1),2*np.sum(dp*du,1),np.sum(du*du,1),(d[i]-d[j])**2)


def solve(u,v,d,e):
    a,b,c,h=terms(u,d);aa,bb,cc,hh=terms(v,e)
    matrix=np.column_stack((b,c,h,-aa,-bb,-cc,-hh))
    norm=np.linalg.norm(matrix,axis=0)
    if (norm==0).any():return dict(admitted=False,reason='zero column',rank=None),None
    q,_,rank,singular=np.linalg.lstsq(matrix/norm,-a,rcond=1e-12);q/=norm
    report=dict(rank=int(rank),singular_values=singular.tolist(),lifted=q.tolist(),admitted=False)
    if rank!=7 or q[2]<=0 or q[3]<=0:return report,None
    b1=q[0];b2=q[4]/q[3];scale=np.sqrt(q[3]);f=np.sqrt(q[2])
    expected=np.array([b1*b1,q[3]*b2*b2,q[3]*q[2]])
    consistency=float(np.max(abs(q[[1,5,6]]-expected)/(1+abs(expected))))
    x=(d+b1)[:,None]*np.c_[u/f,np.ones(len(d))]
    y=scale*(e+b2)[:,None]*np.c_[v/f,np.ones(len(e))]
    uu,_,vt=np.linalg.svd((x-x.mean(0)).T@(y-y.mean(0)))
    rotation=vt.T@np.diag([1,1,np.linalg.det(vt.T@uu.T)])@uu.T
    translation=y.mean(0)-rotation@x.mean(0)
    positive=bool((x[:,2]>0).all() and (y[:,2]>0).all())
    report.update(focal=float(f),scale=float(scale),b1=float(b1),b2=float(b2),
        consistency=consistency,positive=positive,admitted=positive and consistency<=1e-6)
    return report,(x,y,rotation,translation,f)


def worker():
    rng=np.random.default_rng(367)
    x=np.c_[rng.uniform(-.6,.6,(40,2)),rng.uniform(2.5,3.5,40)]
    r=cv2.Rodrigues(np.array([.12,.22,-.04]))[0];t=np.array([.18,-.08,.12]);y=x@r.T+t
    u=x[:,:2]/x[:,2,None]*1200;v=y[:,:2]/y[:,2,None]*1200
    d=x[:,2]-.3;e=y[:,2]/1.2+.2
    np.savez(OUT/'inputs.npz',x=x,y=y,R=r,t=t,u=u,v=v,d=d,e=e)
    result={}
    for label,noise in [('exact',False),('stress',True)]:
        a=u.copy();b=v.copy();dd=d.copy();ee=e.copy()
        if noise:
            a+=.5*np.sin(np.arange(80).reshape(40,2));b+=.5*np.sin(np.arange(80).reshape(40,2)+2)
            dd+=.005*np.sin(np.arange(40)+4);ee+=.005*np.sin(np.arange(40)+6)
        report,state=solve(a,b,dd,ee)
        if state is not None:
            xx,yy,rr,tt,f=state
            angle=float(np.linalg.norm(cv2.Rodrigues(rr@r.T)[0]))
            alignment=float(np.percentile(np.linalg.norm(x@rr.T+tt-y,axis=1),95))
            z=x@rr.T+tt
            px=[float(np.percentile(np.linalg.norm(x[:,:2]/x[:,2,None]*f-u,axis=1),95)),
                float(np.percentile(np.linalg.norm(z[:,:2]/z[:,2,None]*f-v,axis=1),95))]
            report.update(focal_relative_error=abs(f/1200-1),rotation_error_rad=angle,
                          alignment_p95=alignment,projection_p95_px=px)
            report['passed']=bool(report['admitted'] and (abs(f/1200-1)<=.02 and max(px)<=3 if noise else
                    abs(f/1200-1)<=1e-6 and angle<=1e-6 and alignment<=1e-6))
        else:report['passed']=False
        result[label]=report
    plane=x.copy();plane[:,2]=3;other=plane@r.T+t
    negative,_=solve(plane[:,:2]/3*1200,other[:,:2]/other[:,2,None]*1200,plane[:,2]-.3,other[:,2]/1.2+.2)
    result['plane']=negative
    result['status']='TECHNICAL_CHECK_PASSED' if result['exact']['passed'] and result['stress']['passed'] and not negative['admitted'] else 'REJECT'
    (OUT/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':
    if sys.argv[-1]=='worker':worker()
    else:
        OUT.mkdir(exist_ok=False);env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4')
        print(json.dumps(run([sys.executable,__file__,'worker'],ROOT,env,OUT/'worker.log',OUT/'worker.json',60,1024**3)))
