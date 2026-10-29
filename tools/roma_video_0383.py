"""Authorized fixed real-video observation and camera test, no scan reads."""
import hashlib,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import cv2
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
from bounded_process import run
from native_camera_jacobian import linearize
from short_track_camera import intrinsics,project,write
from headfoundry.manifest import validate_input_assets
OUT=ROOT/'assets/private/roma-video-0383'

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def face_cue(rgb):
    rgb=rgb.astype(np.int16);mask=np.zeros(rgb.shape[:2],np.uint8)
    mask[500:820,100:620]=((rgb[:,:,0]-rgb[:,:,2])>12)[500:820,100:620]
    count,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    if count<2:raise ValueError('fixed source foreground cue empty')
    label=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    return cv2.erode((labels==label).astype(np.uint8),np.ones((8,8),np.uint8))

def prepare():
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    document=json.loads(manifest.read_text())
    records=[row for row in document['inputs'] if row['id']=='real-case-001-video']
    if (len(records)!=1 or document.get('training_allowed') is not False or document.get('upload_allowed') is not False
            or document.get('purpose')!='local_head_reconstruction_validation'
            or validate_input_assets(dict(document,inputs=records),manifest.parent)):
        raise ValueError('exact local case001 video authorization required')
    consent=manifest.parent/'provenance-confirmation.json';provenance=json.loads(consent.read_text())
    if provenance['manifest_sha256']!=sha(manifest) or not provenance['cases']['real-case-001']['scan_video_same_stage']:
        raise ValueError('consent/provenance binding fails')
    ledger_path=ROOT/'assets/private/video-observability-0252/report.json'
    ledger=json.loads(ledger_path.read_text());record=records[0];source=Path(record['path'])
    if record['sha256']!=ledger['source_sha256']:raise ValueError('video identity binding fails')
    selected=[240,300,630];rgb_hashes={};images={}
    capture=cv2.VideoCapture(str(source));ordinal=0
    try:
        while True:
            ok,bgr=capture.read()
            if not ok:break
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            if rgb.shape!=(1280,720,3):raise ValueError('native dimensions changed')
            digest=hashlib.sha256(rgb.tobytes()).hexdigest()
            if ordinal>=len(ledger['frame_records']) or digest!=ledger['frame_records'][ordinal]['rgb_sha256']:
                raise ValueError('sequential RGB identity differs')
            if ordinal in selected:
                camera=selected.index(ordinal);name=f'view-{camera}.png'
                Image.fromarray(rgb).save(OUT/name);images[name]=sha(OUT/name);rgb_hashes[str(ordinal)]=digest
            ordinal+=1
    finally:capture.release()
    if ordinal!=1041 or ordinal!=len(ledger['frame_records']) or len(images)!=3 or sha(source)!=record['sha256']:
        raise ValueError('complete sequential decode/source identity fails')
    sheet=Image.new('RGB',(720,465),(20,20,20));draw=ImageDraw.Draw(sheet)
    for camera,frame in enumerate(selected):
        png=Image.open(OUT/f'view-{camera}.png').convert('RGB')
        if camera==0:
            cue=face_cue(np.asarray(png));edges=cv2.morphologyEx(cue,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))
            shown=np.asarray(png).copy();shown[edges>0]=[255,0,0];png=Image.fromarray(shown)
        sheet.paste(png.resize((240,427)),(camera*240,0))
        draw.text((camera*240+6,435),f'ordinal {frame}',fill='white')
    sheet.save(OUT/'inputs.png')
    write(OUT/'inputs.json',{'images':dict(sorted(images.items())),'ordinals':selected,'rgb_sha256':rgb_hashes,
        'manifest_sha256':sha(manifest),'consent_sha256':sha(consent),'ledger_sha256':sha(ledger_path),
        'source_sha256':record['sha256'],'frames_verified':ordinal,'rights':'local validation only,no upload/training',
        'scan_read':False,'case002_read':False})

def read_audit():
    private=ROOT/'assets/private'
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline worker only')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            reading=not isinstance(mode,str) or 'r' in mode or '+' in mode
            if reading and (path.name=='truth.npz' or path.suffix.lower()=='.stl' or (private in path.parents and OUT not in path.parents)):
                raise PermissionError('truth/geometry/unrelated private read denied')
    sys.addaudithook(audit)

def camera_values(k,poses):
    t=poses[1,:3,3]
    return np.r_[np.log(k[0,0]),cv2.Rodrigues(poses[1,:3,:3])[0].ravel(),
        np.arctan2(t[1],t[0]),np.arctan2(t[2],np.linalg.norm(t[:2])),
        cv2.Rodrigues(poses[2,:3,:3])[0].ravel(),poses[2,:3,3]]

def cameras(values):
    # ponytail:fixed three-view capacity gauge;not a generalized video API.
    poses=np.repeat(np.eye(4)[None],3,axis=0)
    poses[1,:3,:3]=cv2.Rodrigues(values[1:4])[0];theta,phi=values[4:6]
    poses[1,:3,3]=[np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)]
    poses[2,:3,:3]=cv2.Rodrigues(values[6:9])[0];poses[2,:3,3]=values[9:12]
    return intrinsics(values[0]),poses

def initialize():
    read_audit();cv2.setNumThreads(4);cv2.setRNGSeed(331)
    observed_file=dict(np.load(OUT/'observations.npz'));xy=observed_file['xy'];train=observed_file['train'];held=observed_file['held']
    observed=xy[:,train];k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    for camera in (1,2):
        e,inliers=cv2.findEssentialMat(observed[0],observed[camera],k,method=cv2.RANSAC,prob=.999,threshold=1.5)
        np.savez_compressed(OUT/f'seed-{camera}-essential.npz',E=np.array([]) if e is None else e,inliers=np.array([]) if inliers is None else inliers)
        if e is None or e.shape!=(3,3):raise ValueError('essential seed fails')
        positive,rotation,translation,_=cv2.recoverPose(e,observed[0],observed[camera],k,mask=inliers.copy())
        np.savez_compressed(OUT/f'seed-{camera}-pose.npz',rotation=rotation,translation=translation,positive=positive,inliers=inliers)
        if positive<.9*int(np.count_nonzero(inliers)):raise ValueError('seed combined support fails')
        poses[camera,:3,:3]=rotation;poses[camera,:3,3]=translation[:,0]
    h=cv2.triangulatePoints(k@poses[0,:3],k@poses[1,:3],observed[0].T,observed[1].T);points=(h[:3]/h[3]).T
    rows=np.array([[camera,point,*observed[camera,point]] for camera in range(3) for point in range(len(train))])
    values=np.r_[camera_values(k,poses),points.ravel()]
    def objective(x):
        kk,pp=cameras(x);xx=x[12:].reshape(-1,3)
        if (project(kk,pp,xx,rows)[1]<=1e-9).any():return np.full(2*len(rows),np.inf)
        return linearize(kk,pp,xx,rows,0,1)[0]
    def jacobian(x):
        kk,pp=cameras(x);return linearize(kk,pp,x[12:].reshape(-1,3),rows,0,1)[1]
    if not np.isfinite(objective(values)).all():raise ValueError('initial geometry invalid')
    lower=np.full(len(values),-np.inf);upper=-lower;lower[0]=np.log(640.);upper[0]=np.log(5120.)
    result=least_squares(objective,values,jac=jacobian,bounds=(lower,upper),method='trf',loss='soft_l1',f_scale=1.5,
                         x_scale='jac',max_nfev=100,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    k,poses=cameras(result.x);points=result.x[12:].reshape(-1,3)
    np.savez_compressed(OUT/'initial.npz',K=k,poses=poses,points=points,rows=rows)
    write(OUT/'initial.json',{'status':'TECHNICAL_CHECK_PASSED' if result.success else 'REJECT',
          'evaluations':result.nfev,'message':result.message,'focal_px':float(k[0,0]),'train_points':len(train),'held_points':len(held)})
    if not result.success or not 640.640<k[0,0]<5114.88 or not np.isfinite(objective(result.x)).all():
        raise ValueError('geometric initializer validity/convergence/nonbound gate fails')

def evaluate():
    observed=dict(np.load(OUT/'observations.npz'));xy=observed['xy'][:,observed['held']];n=xy.shape[1]
    scores={};arrays={}
    for name in ('initial',):
        state=dict(np.load(OUT/(name+'.npz')));k,poses=state['K'],state['poses']
        errors={0:[]};positive=True;negative=[]
        for target,stereo in ((1,2),(2,1)):
            h=cv2.triangulatePoints(k@poses[0,:3],k@poses[stereo,:3],xy[0].T,xy[stereo].T)
            if not np.isfinite(h).all() or (abs(h[3])<1e-12).any():raise ValueError('held triangulation invalid')
            points=(h[:3]/h[3]).T
            rows=np.array([[camera,point,0,0] for camera in range(3) for point in range(n)])
            uv,depth=project(k,poses,points,rows);uv=uv.reshape(3,n,2)
            positive=bool(positive and np.isfinite(uv).all() and np.isfinite(depth).all() and (depth>1e-9).all())
            errors[target]=np.linalg.norm(uv[target]-xy[target],axis=1)
            errors[0].append(np.linalg.norm(uv[0]-xy[0],axis=1))
            bad=poses.copy();bad[target,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@bad[target,:3,:3]
            wrong,_=project(k,bad,points,rows)
            negative.append(float(np.percentile(np.linalg.norm(wrong.reshape(3,n,2)[target]-uv[target],axis=1),95)))
            arrays[f'{name}_stereo_{stereo}_points']=points;arrays[f'{name}_stereo_{stereo}_depths']=depth
        errors[0]=np.concatenate(errors[0]);p95=[float(np.percentile(errors[camera],95)) for camera in range(3)]
        proper=bool(np.allclose(poses[:,3,:],[0,0,0,1],atol=1e-10,rtol=0)
            and np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-8,rtol=0)
            and (np.linalg.det(poses[:,:3,:3])>0).all())
        f=float(k[0,0]);passed=bool(n>=9 and positive and proper and 640.640<f<5114.88 and max(p95)<=3 and min(negative)>3)
        scores[name]={'status':'PARTIAL_SUCCESS' if passed else 'REJECT','held_unique_points':n,
            'held_predictive_p95_px':p95,'focal_px':f,'true_focal_accuracy':'UNVERIFIED','true_material_precision':'UNVERIFIED',
            'proper':proper,'all_held_depths_positive':positive,'wrong_camera_displacement_p95_px':negative}
        arrays.update({f'{name}_held_error_{camera}':errors[camera] for camera in range(3)})
    scores.update(status=scores['initial']['status'],scope='necessary three-view consistency only;no truecamera/medical/head acceptance')
    write(OUT/'result.json',scores);np.savez_compressed(OUT/'scores.npz',**arrays);print(json.dumps(scores,indent=2))
    if scores['status']!='PARTIAL_SUCCESS':raise ValueError('fixed necessary camera consistency fails')

def sample(field,xy):
    h,w=field.shape[:2];uv=(xy+.5)/[720,1280]*[w,h]-.5
    if not np.isfinite(uv).all() or (uv<0).any() or (uv>[w-1,h-1]).any():raise ValueError('sample domain')
    lo=np.floor(uv).astype(int);hi=np.minimum(lo+1,[w-1,h-1]);f=uv-lo
    fx,fy=f.T
    if field.ndim==3:fx=fx[:,None];fy=fy[:,None]
    return (1-fx)*(1-fy)*field[lo[:,1],lo[:,0]]+fx*(1-fy)*field[lo[:,1],hi[:,0]]+(1-fx)*fy*field[hi[:,1],lo[:,0]]+fx*fy*field[hi[:,1],hi[:,0]]

def controls():
    k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    poses[1,:3,3]=[1,0,0];poses[2,:3,3]=[0,1,0]
    rng=np.random.default_rng(383);xyz=rng.uniform([-1,-1,4],[1,1,7],(30,3))
    rows=np.array([[c,p,0,0] for c in range(3) for p in range(30)])
    uv,depth=project(k,poses,xyz,rows);uv=uv.reshape(3,30,2)
    h=cv2.triangulatePoints(k@poses[0,:3],k@poses[1,:3],uv[0].T,uv[1].T);back=(h[:3]/h[3]).T
    actual,z=project(k,poses,back,rows);error=float(abs(actual-uv.reshape(-1,2)).max())
    assert error<1e-8 and (z>0).all()
    cv=max(float(abs(cv2.projectPoints(xyz,cv2.Rodrigues(p[:3,:3])[0],p[:3,3],k,None)[0][:,0]-uv[i]).max()) for i,p in enumerate(poses))
    assert cv<1e-8
    bad=poses.copy();bad[2,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]
    wrong,_=project(k,bad,xyz,rows);negative=float(np.percentile(np.linalg.norm(wrong.reshape(3,30,2)[2]-uv[2],axis=1),95))
    assert negative>3
    write(OUT/'controls.json',dict(exact_triangulation_max_px=error,opencv_max_px=cv,wrong_camera_p95_px=negative))

def observe():
    read_audit();controls()
    meta=json.loads((OUT/'inputs.json').read_text())
    for name,h in meta['images'].items():assert sha(OUT/name)==h
    image=np.asarray(Image.open(OUT/'view-0.png').convert('RGB'));cue=face_cue(image)
    xx,yy=np.meshgrid(np.arange(112,617,24),np.arange(512,801,24));query=np.c_[xx.ravel(),yy.ravel()].astype(float)
    query=query[cue[query[:,1].astype(int),query[:,0].astype(int)]>0]
    xy=[query];valid=np.ones(len(query),bool);raw={'query':query}
    for c in (1,2):
        dense=np.load(OUT/f'dense-{c}.npz',allow_pickle=False);warp=dense['warp'];certainty=dense['certainty']
        target=(sample(warp[:,:864,2:],query)+1)*[720,1280]/2-.5
        forward_conf=sample(certainty[:,:864],query)
        supported=np.isfinite(target).all(1)&(target>=4).all(1)&(target<=[715,1275]).all(1)
        backward=np.full_like(target,np.nan);back_conf=np.zeros(len(query));fb=np.full(len(query),np.inf)
        if supported.any():
            backward[supported]=(sample(warp[:,864:,:2],target[supported])+1)*[720,1280]/2-.5
            back_conf[supported]=sample(certainty[:,864:],target[supported])
            fb[supported]=np.linalg.norm(backward[supported]-query[supported],axis=1)
        admitted=supported&(forward_conf>=.05)&(back_conf>=.05)&(fb<=.75)
        valid &= admitted;xy.append(target)
        raw.update({f'forward_{c}':target,f'backward_{c}':backward,f'confidence_{c}':forward_conf,f'back_confidence_{c}':back_conf,f'fb_{c}':fb,f'admitted_{c}':admitted})
    xy=np.stack(xy);raw['admitted_all']=valid;np.savez_compressed(OUT/'raw-observations.npz',**raw)
    n=int(valid.sum());write(OUT/'coverage.json',dict(queries=len(query),complete=n,minimum=48))
    sheet=Image.new('RGB',(2160,1280))
    for c in range(3):
        im=Image.open(OUT/f'view-{c}.png').convert('RGB');d=ImageDraw.Draw(im)
        for i,(x,y) in enumerate(xy[c]):
            if np.isfinite([x,y]).all():
                color='lime' if valid[i] else 'red';d.ellipse((x-2,y-2,x+2,y+2),fill=color)
                if i%6==0:d.text((x+3,y),str(i),fill=color)
        sheet.paste(im,(720*c,0))
    sheet.save(OUT/'tracks.png')
    if n<48:raise ValueError('complete coverage fails')
    order=sorted(range(n),key=lambda i:hashlib.sha256(f'331/hold/{i}'.encode()).digest())
    held=np.array(order[:int(.2*n)]);train=np.array(sorted(set(range(n))-set(held)))
    if len(held)<9 or len(train)<36:raise ValueError('held/train support fails')
    np.savez_compressed(OUT/'observations.npz',xy=xy[:,valid],held=held,train=train,source_ids=np.flatnonzero(valid))

def controller(stage):
    if time.time()>1793239764:raise RuntimeError('whole experiment deadline reached')
    if (OUT/(stage+'-worker.json')).exists():raise FileExistsError('no duplicate worker')
    if stage.startswith('infer') and not (OUT/'input-reviewed.json').exists():raise ValueError('source review missing')
    if stage=='initialize' and not (OUT/'tracks-reviewed.json').exists():raise ValueError('track review missing')
    seconds,gib={'prepare':(120,2),'infer':(600,8),'infer-repair':(600,8),'observe':(60,2),'initialize':(180,2),'evaluate':(60,2)}[stage]
    python=ROOT/'.venv-roma-0383/Scripts/python.exe' if stage.startswith('infer') else Path(sys.executable)
    script=ROOT/'tools/roma_infer_0383.py' if stage.startswith('infer') else Path(__file__)
    (OUT/'cache').mkdir(exist_ok=True)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1',UV_CACHE_DIR=str(OUT/'cache'),TORCH_HOME=str(OUT/'cache'),TMP=str(OUT/'cache'),TEMP=str(OUT/'cache'))
    receipt=run([str(python),'-B',str(script),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(receipt)
    if receipt['status']!='TECHNICAL_CHECK_PASSED':raise RuntimeError('worker failed; inspect receipt')

if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        try:globals()[stage[:-7]]()
        except Exception as error:
            write(OUT/(stage+'-failure.json'),dict(status='REJECT',error=str(error)));raise
    else:controller(stage)
