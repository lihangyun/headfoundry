"""Generic known-prior camera test; no patient material permitted."""
import hashlib,json,os,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import cv2
from PIL import Image
from scipy.optimize import least_squares
from headfoundry.flame import FlameIdentityModel
from headfoundry.raster import render
from bounded_process import run
OUT=ROOT/'assets/private/render-conditioned-0382'
LOCK=ROOT/'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
TASK=ROOT/'assets/private/mediapipe/face_landmarker.task'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    with (OUT/name).open('w') as f:json.dump(value,f,indent=2,allow_nan=False)
def camera(q):
    e=np.c_[cv2.Rodrigues(.1*q[:3])[0]@np.diag([1.,-1.,-1.]),[.1*q[3],.1*q[4],4*np.exp(.1*q[5])]]
    f=700*np.exp(.1*q[6]);k=np.array([[f,0,256.],[0,f,256.],[0,0,1.]])
    return e,k
def project(v,e,k):
    c=v@e[:,:3].T+e[:,3]
    if not np.isfinite(c).all() or (c[:,2]<=1e-6).any() or not np.allclose(e[:,:3]@e[:,:3].T,np.eye(3),atol=1e-8) or np.linalg.det(e[:,:3])<=0:
        raise ValueError('invalid proper positive-depth camera')
    h=c@k.T;return h[:,:2]/h[:,2:]
def draw(v,f,e,k):
    project(v,e,k)
    return render(v,f,e,k,[512,512],smooth_shading=True)[0]
def prepare():
    assert sha(LOCK)=='b3a5c27654504beb5845a578f71f51c2b89c18d21679ae55690cd8d2c05a64f2'
    assert sha(TASK)=='64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'
    model=FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text()),LOCK.parent)
    v=model.template.copy();v-=(v.max(0)+v.min(0))/2;v/=np.linalg.norm(v,axis=1).max()
    e=np.c_[cv2.Rodrigues(np.array([-.12,.32,.03]))[0]@np.diag([1.,-1.,-1.]),[.04,-.03,4.2]]
    k=np.array([[740.,0,256.],[0,740.,256.],[0,0,1.]])
    Image.fromarray(draw(v,model.faces,e,k)).save(OUT/'target.png')
    np.savez_compressed(OUT/'prior.npz',vertices=v,faces=model.faces)
    np.savez_compressed(OUT/'truth.npz',E=e,K=k)
    write('inputs.json',{p.name:sha(p) for p in (OUT/'prior.npz',OUT/'target.png',OUT/'truth.npz',LOCK,TASK)})
def fit():
    import mediapipe as mp
    assert mp.__version__=='1.0.1'
    assert sha(TASK)=='64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'
    v,f=(np.load(OUT/'prior.npz')[key] for key in ('vertices','faces'))
    target=np.asarray(Image.open(OUT/'target.png').convert('RGB'))
    def guard(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline only')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            p=Path(os.fsdecode(args[0])).resolve()
            if p.name=='truth.npz' or p.suffix.lower()=='.stl' or (p.is_relative_to(ROOT/'assets/private') and not p.is_relative_to(OUT) and p!=TASK):raise PermissionError('truth/patient read denied')
    sys.addaudithook(guard)
    options=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(TASK)),output_facial_transformation_matrixes=False)
    held=np.arange(468)%5==0;train=~held;calls=0;started=time.monotonic()
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        def detect(rgb):
            result=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)))
            if len(result.face_landmarks)!=1:raise ValueError('exactly one detected face required')
            points=np.array([[p.x*512,p.y*512] for p in result.face_landmarks[0][:468]])
            if points.shape!=(468,2) or not np.isfinite(points).all():raise ValueError('invalid semantic output')
            return points
        observed=detect(target);replay=float(abs(observed-detect(target)).max())
        write('detector-control.json',dict(replay_px=replay,runtime=mp.__version__))
        if replay>1e-3:raise ValueError('same target detector replay fails')
        np.savez_compressed(OUT/'observations.npz',observed=observed,held=held,train=train)
        def predicted(q):
            nonlocal calls
            calls+=1
            if calls>260 or time.monotonic()-started>410:raise ValueError('fixed fit budget exhausted')
            e,k=camera(q);points=detect(draw(v,f,e,k))
            write('progress.json',dict(calls=calls,seconds=time.monotonic()-started,q=q.tolist()))
            return points
        def objective(q):return (predicted(q)[train]-observed[train]).ravel()
        def jacobian(q):
            columns=[]
            for i in range(7):
                step=np.zeros(7);step[i]=.05
                columns.append((objective(q+step)-objective(q-step))/.1)
            return np.array(columns).T
        result=least_squares(objective,np.zeros(7),jac=jacobian,bounds=(-np.array([6.,6.,6.,4.,4.,4.,4.]),np.array([6.,6.,6.,4.,4.,4.,4.])),method='trf',loss='linear',x_scale='jac',max_nfev=15,ftol=1e-6,xtol=1e-6,gtol=1e-6)
        e,k=camera(result.x);points=predicted(result.x)
        np.savez_compressed(OUT/'candidate.npz',E=e,K=k,q=result.x,semantics=points)
        Image.fromarray(draw(v,f,e,k)).save(OUT/'candidate.png')
        write('fit.json',dict(converged=bool(result.success),nfev=result.nfev,message=result.message,calls=calls,held_p95_px=float(np.percentile(np.linalg.norm(points[held]-observed[held],axis=1),95))))
def evaluate():
    inputs=json.loads((OUT/'inputs.json').read_text())
    for name in ('prior.npz','target.png','truth.npz'):assert sha(OUT/name)==inputs[name]
    v=np.load(OUT/'prior.npz')['vertices'];truth=np.load(OUT/'truth.npz');candidate=np.load(OUT/'candidate.npz')
    target=project(v,truth['E'],truth['K']);actual=project(v,candidate['E'],candidate['K'])
    error=np.linalg.norm(actual-target,axis=1)
    replay=cv2.projectPoints(v,cv2.Rodrigues(candidate['E'][:,:3])[0],candidate['E'][:,3],candidate['K'],None)[0][:,0]
    assert np.max(abs(replay-actual))<1e-8
    wrong=truth['E'].copy();wrong[:,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[:,:3]
    negative=float(np.percentile(np.linalg.norm(project(v,wrong,truth['K'])-target,axis=1),95))
    for bad in (np.c_[np.diag([1.,1.,-1.]),[0.,0.,4.]],np.c_[np.eye(3),[0.,0.,-4.]]):
        try:project(v,bad,truth['K'])
        except ValueError:pass
        else:raise AssertionError('invalid camera accepted')
    detail=json.loads((OUT/'fit.json').read_text());p95=float(np.percentile(error,95));relative=abs(float(candidate['K'][0,0]/truth['K'][0,0])-1)
    passed=detail['converged'] and p95<=3 and detail['held_p95_px']<=3 and relative<=.02 and negative>3
    np.savez_compressed(OUT/'errors.npz',all_vertex_errors_px=error)
    write('result.json',dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',all_vertex_p95_px=p95,all_vertex_max_px=float(error.max()),focal_relative_error=relative,wrong_camera_p95_px=negative,scope='same-renderer known-prior only; no real video/medical accuracy',**detail))
if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        try:globals()[stage[:-7]]()
        except Exception as error:
            write(stage+'-failure.json',dict(status='REJECT',error=str(error)));raise
    else:
        if stage=='prepare':OUT.mkdir(exist_ok=False)
        if (OUT/(stage+'-worker.json')).exists():raise FileExistsError('one worker per stage')
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        print(run([sys.executable,'-B',str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),420 if stage=='fit' else 60,2*1024**3))
