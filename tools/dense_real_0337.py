"""Fixed detector-free real-camera experiment;no scan/prior fitting."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.append(str(ROOT/'.venv/Lib/site-packages'))
sys.path.insert(0,str(ROOT/'src'))
import cv2
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares

import dense_photo_0332 as photo
from bounded_process import run
from check_dense_grid_contract import bilinear
from headfoundry.manifest import validate_input_assets
from score_pair_0336 import oracle_controls
from short_track_camera import intrinsics,project

OUT=ROOT/'assets/private/detector-free-0337'
MODEL=ROOT/'assets/private/sea-raft-software-0335'
FIXTURE=ROOT/'assets/private/dense-photo-0332'
camera_values,cameras,linearize,read_audit=photo.camera_values,photo.cameras,photo.linearize,photo.read_audit

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(path,data):
    path=Path(path)
    if not path.is_absolute():path=OUT/path
    if path.parent.resolve()!=OUT.resolve():raise ValueError('own output files only')
    path.write_text(json.dumps(data,indent=2,allow_nan=False))

def sample_grid(mask):
    if mask.shape!=(1280,720) or not np.isfinite(mask).all():raise ValueError('finite native source mask required')
    yy,xx=np.mgrid[8:1272:16,8:712:16];points=np.column_stack((xx.ravel(),yy.ravel()))
    points=points[mask[points[:,1],points[:,0]]!=0]
    ordered=sorted(points.tolist(),key=lambda q:hashlib.sha256(f'337/grid/{q[0]}/{q[1]}'.encode()).digest())
    all_sites=np.array(ordered,dtype=float).reshape(-1,2)
    return all_sites[:96],all_sites

def verify_fixed():
    old=json.loads((MODEL/'verification.json').read_text())
    for name,identity in old['files'].items():
        if sha(MODEL/name)!=identity:raise ValueError('frozen model/software fixture changed')
    if json.loads((ROOT/'assets/private/pairwise-physical-0336/result.json').read_text())['status']!='TECHNICAL_CHECK_PASSED':
        raise ValueError('previous physical screen absent')
    return old

def control():
    verify_fixed()
    image=np.asarray(Image.open(FIXTURE/'view-0.png'),float)/255
    mask=cv2.erode((image>.12).astype(np.uint8),np.ones((17,17),np.uint8))
    query,sites=sample_grid(mask);np.savez_compressed(OUT/'control-queries.npz',query=query,candidates=sites)
    if len(query)!=96:raise ValueError('fixed control grid coverage fails')
    metadata=json.loads((FIXTURE/'inputs.json').read_text())
    if sha(FIXTURE/'truth.npz')!=metadata['truth_sha256']:raise ValueError('control truth changed')
    truth=dict(np.load(FIXTURE/'truth.npz'));k,poses=truth['K'],truth['poses']
    xyz,labels=photo.intersect(poses[0],query,truth['rectangles'],k)
    if (labels<0).any() or not np.isfinite(xyz).all():raise ValueError('source grid truth misses')
    local=xyz@poses[1,:3,:3].T+poses[1,:3,3];target=local[:,:2]/local[:,2,None]*k[0,0]+k[:2,2]
    hit,owner=photo.intersect(poses[1],target,truth['rectangles'],k)
    visible=(local[:,2]>1e-9)&(owner==labels)&np.isfinite(hit).all(1)&(np.linalg.norm(hit-xyz,axis=1)<=1e-6)&(target>=0).all(1)&(target<=[719,1279]).all(1)
    np.savez_compressed(OUT/'control-domain.npz',query=query,candidates=sites,xyz=xyz,target=target,labels=labels,visible=visible)
    domain={'candidates':len(sites),'selected':len(query),'visible':int(visible.sum()),'invisible':int((~visible).sum()),
        'domain_sha256':sha(OUT/'control-domain.npz'),'prediction_arrays_opened':False}
    write('control-domain.json',domain)
    if visible.sum()<48 or min(np.ptp(query[visible],axis=0).min(),np.ptp(target[visible],axis=0).min())<50:
        raise ValueError('known grid physical support fails')
    write('control-oracle.json',oracle_controls(target))
    if sha(MODEL/'native-output.npz')!='ee70a9304df575e5de03ec14b3f16952fa1e51328179d3bf798a64f9c57cc3b7':
        raise ValueError('fixed controlled field changed')
    field=np.load(MODEL/'native-output.npz')['flow'][0].transpose(1,2,0)
    predicted=query+bilinear(field,query,[720,1280]);errors=np.linalg.norm(predicted-target,axis=1)
    bounds=np.isfinite(predicted).all(1)&(predicted>=0).all(1)&(predicted<=[719,1279]).all(1)
    p95=float(np.percentile(errors[visible],95));passed=bool(p95<=3 and bounds[visible].all())
    np.savez_compressed(OUT/'control-scores.npz',query=query,predicted=predicted,target=target,errors=errors,visible=visible)
    report={**domain,'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','p95_px':p95,
        'max_px':float(errors[visible].max()),'median_px':float(np.median(errors[visible])),
        'above3px':int(np.sum(errors[visible]>3)),'outside':int(np.sum(~bounds[visible])),
        'scope':'fixed grid on owned pair,not clinical accuracy'}
    write('control-result.json',report);print(json.dumps(report,indent=2))
    if not passed:raise ValueError('fixed grid physical precision fails')


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
                Image.fromarray(rgb).save(OUT/('rgb-'+name))
                gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);Image.fromarray(gray).save(OUT/name)
                images[name]=sha(OUT/name);rgb_hashes[str(ordinal)]=digest
            ordinal+=1
    finally:capture.release()
    if ordinal!=1041 or ordinal!=len(ledger['frame_records']) or len(images)!=3 or sha(source)!=record['sha256']:
        raise ValueError('complete sequential decode/source identity fails')
    sheet=Image.new('RGB',(720,465),(20,20,20));draw=ImageDraw.Draw(sheet)
    for camera,frame in enumerate(selected):
        png=Image.open(OUT/f'rgb-view-{camera}.png').convert('RGB')
        if camera==0:
            cue=face_cue(np.asarray(png));query,sites=sample_grid(cue)
            np.savez_compressed(OUT/'queries.npz',query=query,candidates=sites)
            write('query-population.json',{'candidate_sites':len(sites),'selected':len(query),'rule':'337/grid/x/y native stride16'})
            if len(query)!=96:raise ValueError('fixed real grid coverage fails')
            edges=cv2.morphologyEx(cue,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))
            shown=np.asarray(png).copy();shown[edges>0]=[255,0,0];png=Image.fromarray(shown)
            marker=ImageDraw.Draw(png)
            for x,y in query:marker.ellipse((x-2,y-2,x+2,y+2),fill='lime')
        sheet.paste(png.resize((240,427)),(camera*240,0))
        draw.text((camera*240+6,435),f'ordinal {frame}',fill='white')
    sheet.save(OUT/'inputs.png')
    write(OUT/'inputs.json',{'images':dict(sorted(images.items())),'ordinals':selected,'rgb_sha256':rgb_hashes,
        'manifest_sha256':sha(manifest),'consent_sha256':sha(consent),'ledger_sha256':sha(ledger_path),
        'source_sha256':record['sha256'],'frames_verified':ordinal,'rights':'local validation only,no upload/training',
        'scan_read':False,'case002_read':False})

    write('nn-inputs.json',{'images':{f'rgb-view-{c}.png':sha(OUT/f'rgb-view-{c}.png') for c in range(3)},
        'manifest_sha256':sha(manifest),'source_sha256':record['sha256'],'purpose':'authorized case001 local validation only'})


def flow():
    verify_fixed()
    # Trusted,manifest-bound intake precedes the model audit;model receives tensors only.
    lock=json.loads((OUT/'nn-inputs.json').read_text());images=[]
    for name,identity in lock['images'].items():
        if sha(OUT/name)!=identity:raise ValueError('authorized native RGB image changed')
        images.append(np.asarray(Image.open(OUT/name).convert('RGB')).copy())
    import sea_flow_0335 as runtime
    captured={}
    def fresh_writer(name,data):
        captured[str(name)]=data;write(name,data)
    runtime.write=fresh_writer
    model,torch,np,_=runtime.model_state()
    initial_digest=captured['state.json']['postload_logical_state_sha256']
    tensors=[torch.from_numpy(image).permute(2,0,1)[None].float() for image in images]
    fields={}
    for source,target in ((0,1),(1,0),(0,2),(2,0)):
        started=time.monotonic()
        with torch.no_grad():output=model(tensors[source],tensors[target],iters=4,test_mode=True)
        stages=[]
        if len(output['flow'])!=5 or len(output['info'])!=5 or output['nf'] is not None:raise ValueError('stage count fails')
        for key,channels in (('flow',2),('info',4)):
            for index,tensor in enumerate(output[key]):
                if tuple(tensor.shape)!=(1,channels,1280,720) or tensor.dtype!=torch.float32 or not torch.isfinite(tensor).all():
                    raise ValueError('native finite FP32 stage contract fails')
                stages.append({'key':key,'index':index,'sha256':hashlib.sha256(tensor.contiguous().numpy().tobytes()).hexdigest()})
        if not torch.equal(output['final'],output['flow'][-1]):raise ValueError('final flow-stage mismatch')
        buffer=io.BytesIO()
        np.savez_compressed(buffer,flow=output['final'].numpy(),info=output['info'][-1].numpy())
        data=buffer.getvalue();name=f'field-{source}-{target}.npz'
        with (OUT/name).open('wb') as stream:stream.write(data)
        fields[f'{source}-{target}']={'source':source,'target':target,'path':name,
            'sha256':hashlib.sha256(data).hexdigest(),'seconds':time.monotonic()-started,'stages':stages}
        write('fields.json',fields)
        del output,tensor,buffer,data
    digest=hashlib.sha256()
    for name,tensor in sorted(model.state_dict().items()):
        digest.update(name.encode()+b'\0'+tensor.detach().contiguous().reshape(-1).view(torch.uint8).numpy().tobytes())
    if digest.hexdigest()!=initial_digest:raise ValueError('model state changed during inference')
    write('flow-result.json',{'status':'TECHNICAL_CHECK_PASSED','directed_fields':4,'state_unchanged':True,
        'postload_logical_state_sha256':initial_digest,'metadata_redirect_only':True,
        'scope':'raw dense predictions only,no confidence/GT or camera acceptance'})

def assemble():
    records=json.loads((OUT/'fields.json').read_text());raw=dict(np.load(OUT/'queries.npz'))
    query=raw['query'];xy=[query];valid=np.ones(len(query),bool);counts={}
    np.savez_compressed(OUT/'raw-endpoints.npz',query=query,candidates=raw['candidates'])
    for camera in (1,2):
        fields=[]
        for source,target in ((0,camera),(camera,0)):
            rec=records[f'{source}-{target}']
            if sha(OUT/rec['path'])!=rec['sha256']:raise ValueError('raw field changed')
            a=np.load(OUT/rec['path'])['flow']
            if a.shape!=(1,2,1280,720) or a.dtype!=np.float32 or not np.isfinite(a).all():raise ValueError('raw field contract')
            fields.append(a[0].transpose(1,2,0))
        uv=query+bilinear(fields[0],query,[720,1280])
        support=np.isfinite(uv).all(1)&(uv>=4).all(1)&(uv<=[715,1275]).all(1)
        backward=np.full_like(uv,np.nan);fb=np.full(len(query),np.inf)
        if support.any():
            backward[support]=uv[support]+bilinear(fields[1],uv[support],[720,1280])
            fb[support]=np.linalg.norm(backward[support]-query[support],axis=1)
        local=support&np.isfinite(backward).all(1)&(fb<=.75);valid&=local;xy.append(uv)
        raw.update({f'forward_{camera}':uv,f'backward_{camera}':backward,
            f'supported_{camera}':support,f'fb_{camera}':fb,f'admitted_{camera}':local,'admitted_all':valid.copy()})
        np.savez_compressed(OUT/'raw-endpoints.npz',query=query,**{k:v for k,v in raw.items() if k!='query'})
        counts[str(camera)]={'locally_admitted':int(local.sum()),'support':int(support.sum()),
            'finite_fb_median':float(np.median(fb[np.isfinite(fb)])) if np.isfinite(fb).any() else None,
            'finite_fb_p95':float(np.percentile(fb[np.isfinite(fb)],95)) if np.isfinite(fb).any() else None}
    all_xy=np.stack(xy);n=int(valid.sum())
    sheet=Image.new('RGB',(2160,1280))
    for camera in range(3):
        image=Image.open(OUT/f'rgb-view-{camera}.png').convert('RGB');draw=ImageDraw.Draw(image)
        for index,(x,y) in enumerate(all_xy[camera]):
            if np.isfinite([x,y]).all():
                color='lime' if valid[index] else 'red';draw.ellipse((x-2,y-2,x+2,y+2),fill=color)
                if index%6==0:draw.text((x+3,y),str(index),fill=color)
        sheet.paste(image,(camera*720,0))
    sheet.save(OUT/'tracks.png')
    write('coverage.json',{'detected':len(query),'admitted':n,'minimum':48,'cameras':counts})
    if n<48:raise ValueError('complete three-view coverage fails')
    xy=all_xy[:,valid];ordered=sorted(range(n),key=lambda index:hashlib.sha256(f'331/hold/{index}'.encode()).digest())
    held=np.array(ordered[:int(n*.2)]);train=np.array(sorted(set(range(n))-set(held)))
    if len(held)<9 or len(train)<36:raise ValueError('whole-point train/held support fails')
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
    np.savez_compressed(OUT/'seed.npz',K=k,poses=poses,points=points,rows=rows,values=values)
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
    if stage=='control':
        OUT.mkdir(exist_ok=False);write('entry.json',{'source_sha256':sha(Path(__file__)),'started_utc':time.time(),'registered':'54eaa64'})
    if stage=='prepare' and json.loads((OUT/'control-result.json').read_text())['status']!='TECHNICAL_CHECK_PASSED':
        raise ValueError('grid physical control required')
    if stage=='flow' and not (OUT/'reviewed.json').exists():raise ValueError('source/grid review required')
    if stage=='initialize' and not (OUT/'tracks-reviewed.json').exists():raise ValueError('raw track review required')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',
        PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TORCH_HOME=str(OUT/'cache'),XDG_CACHE_HOME=str(OUT/'cache'))
    seconds,gib={'control':(60,2),'prepare':(120,2),'flow':(240,4),'assemble':(60,2),'initialize':(120,2),
        'optimize':(300,2),'evaluate':(60,2)}[stage]
    executable=str(MODEL/'env/Scripts/python.exe') if stage=='flow' else sys.executable
    record=run([executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'

if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        name=stage[:-7];cv2.setNumThreads(4)
        if name in ('initialize','optimize'):photo.OUT=OUT
        {'control':control,'prepare':prepare,'flow':flow,'assemble':assemble,
         'initialize':initialize,'optimize':photo.optimize,'evaluate':evaluate}[name]()
    else:sys.exit(0 if controller(stage) else 1)

