"""Fixed owned-image camera/depth experiment;not a patient reconstruction path."""
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import cv2
import numpy as np
from PIL import Image,ImageDraw
from scipy import sparse
from scipy.optimize import least_squares

from bounded_process import run
from check_dense_grid_contract import bilinear
from direct_patch_camera import residual as photo_residual
from native_camera_jacobian import linearize
from short_track_camera import intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets
OUT=ROOT/'assets/private/real-direct-0333'
OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


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


def read_images():
    metadata=json.loads((OUT/'inputs.json').read_text());images=[]
    for name,identity in metadata['images'].items():
        if sha(OUT/name)!=identity:raise ValueError('fixed image changed')
        rgb=np.asarray(Image.open(OUT/name).convert('RGB'))
        images.append(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(float)/255)
    return np.stack(images)


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


def verify_protocol():
    source=ROOT/'tools/dense_photo_0332.py';reference=source.read_text();candidate=Path(__file__).read_text()
    def bodies(text):
        return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(text).body if isinstance(node,ast.FunctionDef)}
    before,after=bodies(reference),bodies(candidate)
    names=['sha','read_audit','camera_values','cameras','dense_associations','optimize']
    if any(before[name]!=after[name] for name in names):raise ValueError('successful method body changed')
    fixture=ROOT/'assets/private/dense-photo-0332'
    protected=[{'path':str(p),'sha256':sha(p)} for p in sorted(fixture.iterdir()) if p.is_file()]
    write(OUT/'protocol.json',{'successful_source_sha256':sha(source),'unchanged_functions':names,
        'successful_fixture_protected':protected,'registered_ordinals':[240,300,630],
        'scope':'real partial-camera consistency only,no medical/truef/head acceptance'})


def dense_associations(gray,query):
    raw={'query':query.copy()};xy=[query.copy()]
    valid=np.isfinite(query).all(1)&(query>=4).all(1)&(query<=[715,1275]).all(1)
    records={}
    np.savez_compressed(OUT/'raw-endpoints.npz',**raw)
    getters=['getCoarsestScale','getFinestScale','getPatchSize','getPatchStride',
        'getGradientDescentIterations','getVariationalRefinementIterations','getVariationalRefinementAlpha',
        'getVariationalRefinementDelta','getVariationalRefinementGamma','getVariationalRefinementEpsilon',
        'getUseMeanNormalization','getUseSpatialPropagation']
    for camera in (1,2):
        fields=[]
        for source,target in ((0,camera),(camera,0)):
            algorithm=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            parameters={name:getattr(algorithm,name)() for name in getters if hasattr(algorithm,name)}
            field=algorithm.calc(gray[source],gray[target],None)
            if field.shape!=(1280,720,2) or field.dtype!=np.float32 or not np.isfinite(field).all():
                raise ValueError('native finite float32 dense field required')
            records[f'{source}-{target}']={'parameters':parameters,'shape':list(field.shape),
                'dtype':str(field.dtype),'sha256':hashlib.sha256(field.tobytes()).hexdigest()}
            write(OUT/'dense-fields.json',records);fields.append(field)
        uv=query+bilinear(fields[0],query,[720,1280])
        supported=np.isfinite(uv).all(1)&(uv>=4).all(1)&(uv<=[715,1275]).all(1)
        backward=np.full_like(uv,np.nan,dtype=float);fb=np.full(len(query),np.inf)
        if supported.any():
            backward[supported]=uv[supported]+bilinear(fields[1],uv[supported],[720,1280])
            fb[supported]=np.linalg.norm(backward[supported]-query[supported],axis=1)
        local=supported&np.isfinite(backward).all(1)&(fb<=.75)
        raw.update({f'forward_{camera}':uv,f'backward_{camera}':backward,
            f'fb_{camera}':fb,f'supported_{camera}':supported,f'admitted_{camera}':local})
        valid&=local;xy.append(uv);raw['admitted_all']=valid.copy()
        np.savez_compressed(OUT/'raw-endpoints.npz',**raw)
    return np.stack(xy),valid



def observe():
    read_audit();cv2.setNumThreads(4);cv2.setRNGSeed(331)
    images=read_images();gray=np.round(images*255).astype('uint8')
    mask=face_cue(np.asarray(Image.open(OUT/'view-0.png').convert('RGB')))
    criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.001)
    query=cv2.goodFeaturesToTrack(gray[0],96,.02,15,mask=mask,blockSize=5)
    if query is None:raise ValueError('no source queries')
    query=cv2.cornerSubPix(gray[0],query,(5,5),(-1,-1),criteria);count=len(query)
    all_xy,valid=dense_associations(gray,query[:,0]);xy=all_xy[:,valid];n=xy.shape[1]
    write(OUT/'coverage.json',{'detected':count,'admitted':n,'minimum':48})
    sheet=Image.new('RGB',(2160,1280))
    for camera in range(3):
        image=Image.open(OUT/f'view-{camera}.png').convert('RGB');draw=ImageDraw.Draw(image)
        for index,uv in enumerate(all_xy[camera]):
            if np.isfinite(uv).all():
                x,y=map(float,uv);color='lime' if valid[index] else 'red'
                draw.ellipse((x-2,y-2,x+2,y+2),fill=color)
                if index%6==0:draw.text((x+3,y),str(index),fill=color)
        sheet.paste(image,(camera*720,0))
    sheet.save(OUT/'tracks.png')
    if n<48:raise ValueError('complete three-view coverage fails')
    ordered=sorted(range(n),key=lambda index:hashlib.sha256(f'331/hold/{index}'.encode()).digest())
    held=np.array(ordered[:int(n*.2)]);train=np.array(sorted(set(range(n))-set(held)))
    if len(held)<9 or len(train)<36:raise ValueError('whole-point training/held coverage fails')
    np.savez_compressed(OUT/'observations.npz',xy=xy,held=held,train=train,source_ids=np.flatnonzero(valid))


def initialize():
    read_audit();cv2.setNumThreads(4);cv2.setRNGSeed(331)
    observed_file=dict(np.load(OUT/'observations.npz'));xy=observed_file['xy'];train=observed_file['train'];held=observed_file['held']
    observed=xy[:,train];k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    for camera in (1,2):
        e,inliers=cv2.findEssentialMat(observed[0],observed[camera],k,method=cv2.RANSAC,prob=.999,threshold=1.5)
        if e is None or e.shape!=(3,3):raise ValueError('essential seed fails')
        positive,rotation,translation,_=cv2.recoverPose(e,observed[0],observed[camera],k,mask=inliers.copy())
        if positive<.9*int(np.count_nonzero(inliers)):raise ValueError('seed positive support fails')
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


def optimize():
    read_audit();images=read_images();observed=dict(np.load(OUT/'observations.npz'));initial=dict(np.load(OUT/'initial.npz'))
    query=observed['xy'][0,observed['train']];pixels=query[:,None,:]+OFFSETS;n=len(query)
    values=np.r_[camera_values(initial['K'],initial['poses']),np.zeros(4),np.log(1/initial['points'][:,2])]
    lower=values.copy();upper=values.copy();lower[0]=np.log(640.);upper[0]=np.log(5120.)
    lower[1:12]-=np.r_[np.full(8,.1),np.full(3,.2)];upper[1:12]+=np.r_[np.full(8,.1),np.full(3,.2)]
    lower[12:16]=[-.3,-.05,-.3,-.05];upper[12:16]=[.3,.05,.3,.05];lower[16:]-=.3;upper[16:]+=.3
    def objective(x):
        _,poses=cameras(x);a=np.r_[0.,x[12],x[14]];b=np.r_[0.,x[13],x[15]]
        try:return photo_residual(images,pixels,np.exp(x[16:]),poses,a,b,x[0])[0].ravel()
        except ValueError as error:
            if any(text in str(error) for text in ('unclamped projector domain','query outside complete bilinear interpolation domain','affine exposure outside normalized sensor domain')):
                return np.full(16*n,np.inf)
            raise
    pattern=sparse.lil_matrix((16*n,len(values)),dtype=int)
    for camera in (1,2):
        for point in range(n):
            rows=slice(((camera-1)*n+point)*8,((camera-1)*n+point+1)*8)
            pattern[rows,0]=1;pattern[rows,16+point]=1
            if camera==1:pattern[rows,1:6]=1
            else:pattern[rows,6:12]=1
            pattern[rows,12+2*(camera-1):14+2*(camera-1)]=1
    pattern=pattern.tocsr();base=objective(values)
    if not np.isfinite(base).all():raise ValueError('initial photometric domain fails')
    worst=0.
    for column in range(len(values)):
        changed=values.copy();changed[column]+=1e-6;residual=objective(changed)
        if not np.isfinite(residual).all():raise ValueError('nonfinite direct finite-difference control')
        omitted=~pattern[:,column].toarray().ravel().astype(bool)
        if omitted.any():worst=max(worst,float(np.max(abs(residual[omitted]-base[omitted]))))
    write(OUT/'sparsity.json',{'columns':len(values),'max_omitted_change':worst})
    if worst>1e-12:raise ValueError('omitted direct derivative dependency')
    result=least_squares(objective,values,bounds=(lower,upper),jac_sparsity=pattern,method='trf',loss='soft_l1',f_scale=.01,
                         x_scale='jac',max_nfev=150,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    k,poses=cameras(result.x);rho=np.exp(result.x[16:])
    points=np.c_[(query-k[:2,2])/k[0,0],np.ones(n)]/rho[:,None]
    final=objective(result.x)
    np.savez_compressed(OUT/'final.npz',K=k,poses=poses,points=points,values=result.x,residual=final,lower=lower,upper=upper)
    write(OUT/'direct.json',{'status':'TECHNICAL_CHECK_PASSED' if result.success else 'REJECT',
          'evaluations':result.nfev,'message':result.message,'focal_px':float(k[0,0]),
          'initial_rms':float(np.sqrt(np.mean(base**2))),'final_rms':float(np.sqrt(np.mean(final**2)))})
    if not result.success or not np.isfinite(final).all():raise ValueError('direct convergence/domain gate fails')


def evaluate():
    observed=dict(np.load(OUT/'observations.npz'));xy=observed['xy'][:,observed['held']];n=xy.shape[1]
    scores={};arrays={}
    for name in ('initial','final'):
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
    scores.update(status=scores['final']['status'],scope='necessary three-view consistency only;no truecamera/medical/head acceptance')
    write(OUT/'result.json',scores);np.savez_compressed(OUT/'scores.npz',**arrays);print(json.dumps(scores,indent=2))
    if scores['status']!='PARTIAL_SUCCESS':raise ValueError('fixed necessary camera consistency fails')



def controller(stage):
    if stage=='prepare':
        OUT.mkdir(exist_ok=False);verify_protocol()
        write(OUT/'entry.json',{'source_sha256':sha(Path(__file__)),'registered_entry':time.time()})
    if stage=='observe' and not (OUT/'reviewed.json').exists():raise ValueError('source review required')
    if stage=='initialize' and not (OUT/'tracks-reviewed.json').exists():raise ValueError('raw track review required')
    limits={'prepare':(120,2),'observe':(120,2),'initialize':(120,2),'optimize':(300,2),'evaluate':(60,2)}
    seconds,gib=limits[stage];env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    record=run([sys.executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):{'prepare':prepare,'observe':observe,'initialize':initialize,'optimize':optimize,'evaluate':evaluate}[stage[:-7]]()
    else:sys.exit(0 if controller(stage) else 1)

