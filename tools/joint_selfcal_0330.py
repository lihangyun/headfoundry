"""Fixed opt-in owned-scene joint selfcal;no medical/human input or default."""
import hashlib,io,json,os,sys,zipfile
from pathlib import Path
import cv2
import numpy as np
from scipy.optimize import least_squares
from bounded_process import run
from native_camera_jacobian import linearize
from short_track_camera import intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/private/joint-selfcal-0330'


def prepare():
    OUT.mkdir(exist_ok=False)
    raw=(ROOT/'assets/private/closed-experiments/0329-joint-information/evidence.zip').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='acbc02d82e373025b48eb3a57a825da5d12782b1fe25552588e98f5c8a34388d':raise ValueError('source changed')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:raise ValueError('CRC fails')
        source=dict(np.load(io.BytesIO(archive.read('arrays.npz'))))
    xy=source['joint_rows'][:,2:].reshape(3,120,2)[:,:96].copy()
    xy+=np.random.default_rng(330).normal(0,.5,xy.shape)
    np.savez_compressed(OUT/'input.npz',xy=xy)
    np.savez_compressed(OUT/'truth.npz',K=source['K'],poses=source['joint_poses'],points=source['points'])
    write(OUT/'identities.json',{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('input.npz','truth.npz')})


def solve():
    private=ROOT/'assets/private'
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline only')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            if (not isinstance(mode,str) or 'r' in mode or '+' in mode) and (path.name=='truth.npz' or path.suffix=='.stl' or (private in path.parents and OUT not in path.parents)):
                raise PermissionError('truth/unrelated private read denied')
    sys.addaudithook(audit);cv2.setRNGSeed(330);cv2.setNumThreads(4)
    xy=np.load(OUT/'input.npz')['xy'];k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    for camera in (1,2):
        e,mask=cv2.findEssentialMat(xy[0],xy[camera],k,method=cv2.RANSAC,prob=.999,threshold=1.5)
        if e is None or e.shape!=(3,3):raise ValueError('essential seed failed')
        count,r,t,positive=cv2.recoverPose(e,xy[0],xy[camera],k,mask=mask.copy())
        if count<.9*int(np.count_nonzero(mask)):raise ValueError('seed cheirality support failed')
        poses[camera,:3,:3]=r;poses[camera,:3,3]=t[:,0]
    h=cv2.triangulatePoints(k@poses[0,:3],k@poses[1,:3],xy[0].T,xy[1].T);points=(h[:3]/h[3]).T
    rows=np.array([[camera,point,*xy[camera,point]] for camera in range(3) for point in range(96)])
    theta=np.arctan2(poses[1,1,3],poses[1,0,3]);phi=np.arctan2(poses[1,2,3],np.linalg.norm(poses[1,:2,3]))
    values=np.r_[np.log(1280.),cv2.Rodrigues(poses[1,:3,:3])[0].ravel(),theta,phi,
                 cv2.Rodrigues(poses[2,:3,:3])[0].ravel(),poses[2,:3,3],points.ravel()]
    def unpack(x):
        pp=np.repeat(np.eye(4)[None],3,axis=0);pp[1,:3,:3]=cv2.Rodrigues(x[1:4])[0]
        th,ph=x[4:6];pp[1,:3,3]=[np.cos(ph)*np.cos(th),np.cos(ph)*np.sin(th),np.sin(ph)]
        pp[2,:3,:3]=cv2.Rodrigues(x[6:9])[0];pp[2,:3,3]=x[9:12]
        return intrinsics(x[0]),pp,x[12:].reshape(-1,3)
    def objective(x):
        kk,pp,xx=unpack(x)
        if (project(kk,pp,xx,rows)[1]<=1e-9).any():return np.full(2*len(rows),np.inf)
        return linearize(kk,pp,xx,rows,0,1)[0]
    def jacobian(x):return linearize(*unpack(x),rows,0,1)[1]
    if not np.isfinite(objective(values)).all():raise ValueError('initial point domain failed')
    np.savez_compressed(OUT/'initial.npz',K=k,poses=poses,points=points)
    lower=np.full(len(values),-np.inf);upper=-lower;lower[0]=np.log(640.);upper[0]=np.log(5120.)
    result=least_squares(objective,values,jac=jacobian,bounds=(lower,upper),method='trf',loss='soft_l1',
                         f_scale=1.5,x_scale='jac',max_nfev=100,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    kk,pp,xx=unpack(result.x)
    np.savez_compressed(OUT/'final.npz',K=kk,poses=pp,points=xx,rows=rows)
    write(OUT/'solver.json',{'status':'TECHNICAL_CHECK_PASSED' if result.success else 'REJECT',
          'success':result.success,'message':result.message,'nfev':result.nfev,'focal_px':float(kk[0,0])})
    if not result.success:raise ValueError('solver termination failed')


def evaluate():
    truth=dict(np.load(OUT/'truth.npz'));scores={};arrays={}
    for name in ('initial','final'):
        state=dict(np.load(OUT/(name+'.npz')));k,poses,points=state['K'],state['poses'],state['points']
        held=truth['points'][96:];rows=np.array([[camera,point,0,0] for camera in range(3) for point in range(24)])
        uv,z=project(k,poses,held,rows);correct,_=project(truth['K'],truth['poses'],held,rows)
        error=np.linalg.norm(uv-correct,axis=1).reshape(3,24);p95=np.percentile(error,95,axis=1)
        point_error=np.linalg.norm(points-truth['points'][:96],axis=1)
        train=np.array([[camera,point,0,0] for camera in range(3) for point in range(96)]);_,train_z=project(k,poses,points,train)
        replay=max(float(np.max(abs(cv2.projectPoints(held,cv2.Rodrigues(p[:3,:3])[0],p[:3,3],k,None)[0].reshape(-1,2)-uv.reshape(3,24,2)[c]))) for c,p in enumerate(poses))
        wrong=poses.copy();wrong[1,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[1,:3,:3]
        bad,_=project(k,wrong,held,rows);negative=float(np.percentile(np.linalg.norm((bad-correct).reshape(3,24,2)[1],axis=1),95))
        f=float(k[0,0]);relative=abs(f/1200-1);point95=float(np.percentile(point_error,95))
        proper=bool(np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-8,rtol=0) and (np.linalg.det(poses[:,:3,:3])>0).all())
        passed=bool(proper and min(z.min(),train_z.min())>0 and 640.640<f<5114.88 and relative<=.02 and p95.max()<=3 and point95<=.01 and replay<=1e-9 and negative>3)
        scores[name]={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','focal_px':f,'focal_relative_error':relative,
                      'held_known3D_p95_px':p95.tolist(),'point_p95_scene_units':point95,'proper':proper,
                      'positive_depths':bool(min(z.min(),train_z.min())>0),'replay_max_px':replay,'wrong_camera_p95_px':negative}
        arrays[name+'_held_error']=error;arrays[name+'_point_error']=point_error
    scores.update(status=scores['final']['status'],scope='owned-scene noisy coordinate capacity only;human/head/mm UNVERIFIED')
    write(OUT/'result.json',scores);np.savez_compressed(OUT/'scores.npz',**arrays);print(json.dumps(scores,indent=2))
    return scores['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    if len(sys.argv)>1:solve()
    else:
        prepare();env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        record=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',120,2*1024**3)
        print(json.dumps(record,indent=2))
        sys.exit(0 if record['status']=='TECHNICAL_CHECK_PASSED' and evaluate() else 1)
