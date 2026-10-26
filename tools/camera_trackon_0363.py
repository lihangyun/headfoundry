"""Fixed prediction-only camera fit and separate truth-only evaluation."""
import hashlib
import json
import os
from pathlib import Path
import sys
import cv2
import numpy as np
from scipy.optimize import least_squares
from bounded_process import run
from dense_photo_0332 import camera_values, cameras, intersect
from native_camera_jacobian import linearize
from short_track_camera import intrinsics, project

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets/private/trackon-camera-0363"


def fit():
    def audit(event,args):
        if event.startswith(("socket.","subprocess.","os.system")):raise PermissionError("offline fit")
        if event=="open" and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0]))
            if path.name=="truth.npz" or path.suffix.lower()==".stl":raise PermissionError("truth forbidden in fit")
    sys.addaudithook(audit)
    cv2.setNumThreads(4);cv2.setRNGSeed(331)
    source=ROOT/"assets/private/trackon-motion-0362/predictions.npz"
    data=np.load(source);xy=data["predictions"][[0,6,12]].astype(float)
    admitted=np.isfinite(xy).all((0,2))&(xy>=4).all((0,2))&(xy<=[715,1275]).all((0,2))
    admitted&=(data["visibility"][[0,6,12]]>=.8).all(0)
    ids=np.flatnonzero(admitted);xy=xy[:,ids];n=len(ids)
    assert n>=48
    ordered=sorted(range(n),key=lambda i:hashlib.sha256(f"331/hold/{i}".encode()).digest())
    held=np.array(ordered[:int(n*.2)]);train=np.array(sorted(set(range(n))-set(held)))
    assert len(held)>=9 and len(train)>=36
    np.savez(OUT/"observations.npz",xy=xy,source_ids=ids,held=held,train=train)
    (OUT/"source.json").write_text(json.dumps(dict(sha256=hashlib.sha256(source.read_bytes()).hexdigest(),admitted=n,train=len(train),held=len(held))))
    observed=xy[:,train];k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    seeds={}
    for camera in (1,2):
        e,inliers=cv2.findEssentialMat(observed[0],observed[camera],k,method=cv2.RANSAC,prob=.999,threshold=1.5)
        assert e is not None and e.shape==(3,3)
        count,rotation,translation,mask=cv2.recoverPose(e,observed[0],observed[camera],k,mask=inliers.copy())
        seeds[str(camera)]=dict(E=e.tolist(),inliers=inliers.ravel().tolist(),returned_count=count,
            rotation=rotation.tolist(),translation=translation.tolist(),returned_mask=mask.ravel().tolist())
        (OUT/"seeds.json").write_text(json.dumps(seeds,indent=2))
        assert count>=.9*np.count_nonzero(inliers)
        poses[camera,:3,:3]=rotation;poses[camera,:3,3]=translation[:,0]
    h=cv2.triangulatePoints(k@poses[0,:3],k@poses[1,:3],observed[0].T,observed[1].T)
    points=(h[:3]/h[3]).T
    rows=np.array([[c,p,*observed[c,p]] for c in range(3) for p in range(len(train))])
    values=np.r_[camera_values(k,poses),points.ravel()]
    def objective(x):
        kk,pp=cameras(x);xx=x[12:].reshape(-1,3)
        if (project(kk,pp,xx,rows)[1]<=1e-9).any():return np.full(2*len(rows),np.inf)
        return linearize(kk,pp,xx,rows,0,1)[0]
    def jacobian(x):
        kk,pp=cameras(x);return linearize(kk,pp,x[12:].reshape(-1,3),rows,0,1)[1]
    assert np.isfinite(objective(values)).all()
    lower=np.full(len(values),-np.inf);upper=-lower;lower[0]=np.log(640.);upper[0]=np.log(5120.)
    result=least_squares(objective,values,jac=jacobian,bounds=(lower,upper),method="trf",loss="soft_l1",f_scale=1.5,
                         x_scale="jac",max_nfev=100,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    k,poses=cameras(result.x)
    np.savez(OUT/"solution.npz",K=k,poses=poses,points=result.x[12:].reshape(-1,3))
    report=dict(success=bool(result.success),evaluations=result.nfev,message=result.message,focal_px=float(k[0,0]))
    (OUT/"fit.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))


def evaluate():
    obs=np.load(OUT/"observations.npz");state=np.load(OUT/"solution.npz")
    fixture=ROOT/"assets/private/dense-photo-0332"
    metadata=json.loads((fixture/"inputs.json").read_text())
    assert hashlib.sha256((fixture/"truth.npz").read_bytes()).hexdigest()==metadata["truth_sha256"]
    truth=np.load(fixture/"truth.npz")
    queries=np.load(fixture/"raw-endpoints.npz")["query"][obs["source_ids"]]
    xyz,labels=intersect(truth["poses"][0],queries,truth["rectangles"],truth["K"])
    visibility_misses=0
    for p in truth["poses"]:
        local=xyz@p[:3,:3].T+p[:3,3];uv=local[:,:2]/local[:,2,None]*truth["K"][0,0]+truth["K"][:2,2]
        hit,target=intersect(p,uv,truth["rectangles"],truth["K"])
        visibility_misses+=int(np.sum((target!=labels)|(~np.isfinite(hit).all(1))|(np.linalg.norm(hit-xyz,axis=1)>1e-6)))
    baseline=float(truth["baseline"]);xyz/=baseline
    correct_poses=truth["poses"].copy();correct_poses[:,:3,3]/=baseline
    held=obs["held"];train=obs["train"];held_xyz=xyz[held]
    rows=np.array([[c,p,0,0] for c in range(3) for p in range(len(held))])
    correct,_=project(truth["K"],correct_poses,held_xyz,rows)
    k,poses,points=state["K"],state["poses"],state["points"]
    uv,depth=project(k,poses,held_xyz,rows)
    known=np.percentile(np.linalg.norm(uv-correct,axis=1).reshape(3,-1),95,axis=1)
    observed=np.percentile(np.linalg.norm(uv.reshape(3,-1,2)-obs["xy"][:,held],axis=2),95,axis=1)
    point95=float(np.percentile(np.linalg.norm(points-xyz[train],axis=1),95))
    tr=np.array([[c,p,0,0] for c in range(3) for p in range(len(points))]);_,td=project(k,poses,points,tr)
    proper=bool(np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),rtol=0,atol=1e-8) and (np.linalg.det(poses[:,:3,:3])>0).all())
    replay=max(float(np.max(abs(cv2.projectPoints(held_xyz,cv2.Rodrigues(p[:3,:3])[0],p[:3,3],k,None)[0].reshape(-1,2)-uv.reshape(3,-1,2)[c]))) for c,p in enumerate(poses))
    bad=poses.copy();bad[1,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@bad[1,:3,:3]
    wrong,_=project(k,bad,held_xyz,rows);negative=float(np.percentile(np.linalg.norm((wrong-correct).reshape(3,-1,2)[1],axis=1),95))
    f=float(k[0,0]);relative=abs(f/1200-1);positive=bool(min(depth.min(),td.min())>0)
    gates=dict(converged=json.loads((OUT/"fit.json").read_text())["success"],proper=proper,positive=positive,
        focal_nonbound=640.640<f<5114.88,focal_2percent=relative<=.02,known_3px=bool(known.max()<=3),
        observed_3px=bool(observed.max()<=3),points_001=point95<=.01,projection_replay=replay<=1e-9,
        negative_control=negative>3,visible=visibility_misses==0 and bool((labels>=0).all()))
    report=dict(status="TECHNICAL_CHECK_PASSED" if all(gates.values()) else "REJECT",gates=gates,focal_px=f,
        focal_relative_error=relative,held_known3D_p95_px=known.tolist(),held_observed_p95_px=observed.tolist(),
        point_p95_scene_units=point95,visibility_misses=visibility_misses,opencv_replay_max_px=replay,
        negative_p95_px=negative,scope="owned known-scene camera, not patient/medicalmm")
    (OUT/"result.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))


def main():
    OUT.mkdir(parents=True,exist_ok=True);stage=sys.argv[1]
    if stage.endswith("-worker"):{"fit":fit,"evaluate":evaluate}[stage[:-7]]();return
    receipt=OUT/(stage+"-worker.json")
    if receipt.exists():raise RuntimeError("one-shot stage already attempted")
    env=os.environ.copy();env.update(OMP_NUM_THREADS="4",OPENBLAS_NUM_THREADS="4",MKL_NUM_THREADS="4")
    result=run([sys.executable,__file__,stage+"-worker"],ROOT,env,OUT/(stage+".log"),receipt,
               180 if stage=="fit" else 30,(2 if stage=="fit" else 1)*1024**3)
    print(json.dumps(result))


if __name__=="__main__":main()
