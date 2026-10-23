"""Fixed owned-image camera/depth experiment;not a patient reconstruction path."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

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
OUT=ROOT/'assets/private/joint-photometric-0331'
OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def intersect(pose,pixels,rectangles,k):
    rays=np.c_[(pixels-k[:2,2])/k[0,0],np.ones(len(pixels))]@pose[:3,:3]
    center=-pose[:3,:3].T@pose[:3,3]
    best=np.full(len(pixels),np.inf);labels=np.full(len(pixels),-1,int);xyz=np.full((len(pixels),3),np.nan)
    for index,(x,y,z) in enumerate(rectangles):
        with np.errstate(divide='ignore',invalid='ignore'):
            distance=(z-center[2])/rays[:,2];points=center+distance[:,None]*rays
        valid=(distance>0)&(distance<best)&(abs(points[:,0]-x)<=.16)&(abs(points[:,1]-y)<=.19)
        best[valid],labels[valid],xyz[valid]=distance[valid],index,points[valid]
    return xyz,labels


def prepare():
    rng=np.random.default_rng(331)
    rectangles=np.array([[x,y,rng.uniform(2.6,3.5)] for y in np.linspace(-1,1,5) for x in np.linspace(-.63,.63,4)])
    textures=[]
    for _ in rectangles:
        texture=cv2.GaussianBlur(rng.normal(size=(64,64)),(0,0),.8)
        texture=.25+.4*(texture-texture.min())/(texture.max()-texture.min());textures.append(texture)
    k=intrinsics(np.log(1200.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    for camera,yaw in ((1,18),(2,-18)):
        rotation=cv2.Rodrigues(np.array([0,np.deg2rad(yaw),0]))[0]@cv2.Rodrigues(np.array([np.deg2rad(15),0,0]))[0]
        poses[camera,:3,:3]=rotation;poses[camera,:3,3]=np.array([0,0,3])-rotation@np.array([0,0,3])
    yy,xx=np.mgrid[:1280,:720];pixels=np.column_stack((xx.ravel(),yy.ravel()))
    sheet=Image.new('RGB',(720,465),(20,20,20));draw=ImageDraw.Draw(sheet)
    for camera,(gain,bias) in enumerate(zip([1.,1.07,.94],[0.,.01,-.01])):
        xyz,labels=intersect(poses[camera],pixels,rectangles,k);image=np.full(len(pixels),.08)
        for index,(x,y,_) in enumerate(rectangles):
            selected=labels==index
            # Renderer-only roundoff at rectangle boundaries,not fitted warps.
            uv=np.clip((xyz[selected,:2]-[x-.16,y-.19])/[.32,.38]*63,0,63)
            image[selected]=bilinear(textures[index],uv,[64,64])
        image=gain*image+bias+rng.normal(0,1/255,len(image))
        if not np.isfinite(image).all() or image.min()<0 or image.max()>1:raise ValueError('sensor domain fails')
        png=Image.fromarray(np.round(image.reshape(1280,720)*255).astype('uint8'));png.save(OUT/f'view-{camera}.png')
        sheet.paste(png.convert('RGB').resize((240,427)),(camera*240,0));draw.text((camera*240+8,435),f'view {camera}',fill='white')
    sheet.save(OUT/'inputs.png')
    np.savez_compressed(OUT/'truth.npz',K=k,poses=poses,rectangles=rectangles,baseline=np.linalg.norm(poses[1,:3,3]))
    write(OUT/'inputs.json',{'images':{f'view-{camera}.png':sha(OUT/f'view-{camera}.png') for camera in range(3)},
          'truth_sha256':sha(OUT/'truth.npz'),'rights':'owned original procedural validation,no training','seed':331})


def read_images():
    metadata=json.loads((OUT/'inputs.json').read_text());images=[]
    for name,identity in metadata['images'].items():
        if sha(OUT/name)!=identity:raise ValueError('fixed image changed')
        images.append(np.asarray(Image.open(OUT/name),float)/255)
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


def initialize():
    read_audit();cv2.setNumThreads(4);cv2.setRNGSeed(331)
    images=read_images();gray=np.round(images*255).astype('uint8')
    mask=cv2.erode((images[0]>.12).astype('uint8'),np.ones((17,17),np.uint8))
    criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.001)
    query=cv2.goodFeaturesToTrack(gray[0],96,.02,15,mask=mask,blockSize=5)
    if query is None:raise ValueError('no source queries')
    query=cv2.cornerSubPix(gray[0],query,(5,5),(-1,-1),criteria);count=len(query)
    xy=[query[:,0]];valid=np.isfinite(query[:,0]).all(1)&(query[:,0]>=4).all(1)&(query[:,0]<=[715,1275]).all(1)
    for camera in (1,2):
        forward,status,_=cv2.calcOpticalFlowPyrLK(gray[0],gray[camera],query,None,winSize=(31,31),maxLevel=4,criteria=criteria)
        backward,returned,_=cv2.calcOpticalFlowPyrLK(gray[camera],gray[0],forward,None,winSize=(31,31),maxLevel=4,criteria=criteria)
        uv=forward[:,0]
        valid&=(status[:,0]!=0)&(returned[:,0]!=0)&np.isfinite(uv).all(1)&(np.linalg.norm(backward[:,0]-query[:,0],axis=1)<=.75)&(uv>=4).all(1)&(uv<=[715,1275]).all(1)
        xy.append(uv)
    xy=np.stack(xy)[:,valid];n=xy.shape[1]
    write(OUT/'coverage.json',{'detected':count,'admitted':n,'minimum':48})
    if n<48:raise ValueError('complete three-view coverage fails')
    ordered=sorted(range(n),key=lambda index:hashlib.sha256(f'331/hold/{index}'.encode()).digest())
    held=np.array(ordered[:int(n*.2)]);train=np.array(sorted(set(range(n))-set(held)))
    if len(held)<9 or len(train)<36:raise ValueError('whole-point training/held coverage fails')
    np.savez_compressed(OUT/'observations.npz',xy=xy,held=held,train=train)
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
            pattern[rows,1:6 if camera==1 else 1]=1 if camera==1 else 0
            if camera==2:pattern[rows,6:12]=1
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
    metadata=json.loads((OUT/'inputs.json').read_text())
    if sha(OUT/'truth.npz')!=metadata['truth_sha256']:raise ValueError('truth changed')
    truth=dict(np.load(OUT/'truth.npz'));observed=dict(np.load(OUT/'observations.npz'))
    k,poses,rectangles=truth['K'],truth['poses'],truth['rectangles'];baseline=float(truth['baseline'])
    query=observed['xy'][0];xyz,labels=intersect(poses[0],query,rectangles,k)
    visibility_misses=0;patch_misses=0
    for camera in (1,2):
        projected=(xyz@poses[camera,:3,:3].T+poses[camera,:3,3]);uv=projected[:,:2]/projected[:,2,None]*k[0,0]+k[:2,2]
        hit,target_labels=intersect(poses[camera],uv,rectangles,k)
        visibility_misses+=int(np.sum((target_labels!=labels)|(~np.isfinite(hit).all(1))|(np.linalg.norm(hit-xyz,axis=1)>1e-6)))
        q=(query[observed['train'],None,:]+OFFSETS).reshape(-1,2);patch_xyz,patch_labels=intersect(poses[0],q,rectangles,k)
        local=patch_xyz@poses[camera,:3,:3].T+poses[camera,:3,3];p=local[:,:2]/local[:,2,None]*k[0,0]+k[:2,2]
        hit,target=intersect(poses[camera],p,rectangles,k)
        patch_misses+=int(np.sum((target!=patch_labels)|(~np.isfinite(hit).all(1))|(np.linalg.norm(hit-patch_xyz,axis=1)>1e-6)))
    if (labels<0).any():raise ValueError('admitted query misses source surface')
    true_poses=poses.copy();true_poses[:,:3,3]/=baseline;xyz/=baseline
    held=observed['held'];train=observed['train'];held_xyz=xyz[held];n=len(held)
    held_rows=np.array([[camera,point,0,0] for camera in range(3) for point in range(n)])
    correct,_=project(k,true_poses,held_xyz,held_rows);scores={};arrays={'truth_queries':xyz,'labels':labels}
    for name in ('initial','final'):
        state=dict(np.load(OUT/(name+'.npz')));kk,pp,points=state['K'],state['poses'],state['points']
        uv,depth=project(kk,pp,held_xyz,held_rows);error=np.linalg.norm(uv-correct,axis=1).reshape(3,n)
        p95=np.percentile(error,95,axis=1);point_error=np.linalg.norm(points-xyz[train],axis=1)
        held_obs=np.percentile(np.linalg.norm(uv.reshape(3,n,2)-observed['xy'][:,held],axis=2),95,axis=1)
        replay=max(float(np.max(abs(cv2.projectPoints(held_xyz,cv2.Rodrigues(p[:3,:3])[0],p[:3,3],kk,None)[0].reshape(-1,2)-uv.reshape(3,n,2)[camera]))) for camera,p in enumerate(pp))
        bad=pp.copy();bad[1,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@bad[1,:3,:3]
        wrong,_=project(kk,bad,held_xyz,held_rows);negative=float(np.percentile(np.linalg.norm((wrong-correct).reshape(3,n,2)[1],axis=1),95))
        training_rows=np.array([[camera,point,0,0] for camera in range(3) for point in range(len(points))])
        _,training_depth=project(kk,pp,points,training_rows)
        proper=bool(np.allclose(pp[:,:3,:3]@pp[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-8,rtol=0) and (np.linalg.det(pp[:,:3,:3])>0).all())
        f=float(kk[0,0]);relative=abs(f/1200-1);point95=float(np.percentile(point_error,95));positive=bool(min(depth.min(),training_depth.min())>0)
        passed=bool(proper and positive and 640.640<f<5114.88 and relative<=.02 and p95.max()<=3 and point95<=.01 and held_obs.max()<=3 and replay<=1e-9 and negative>3 and visibility_misses==0 and patch_misses==0)
        scores[name]={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','focal_px':f,'focal_relative_error':relative,
           'held_known3D_p95_px':p95.tolist(),'held_observed_p95_px':held_obs.tolist(),'point_p95_scene_units':point95,
           'proper':proper,'positive_depths':positive,'opencv_replay_max_px':replay,'wrong_camera_p95_px':negative}
        arrays[name+'_held_error']=error;arrays[name+'_point_error']=point_error
    scores.update(status=scores['final']['status'],visibility_misses=visibility_misses,patch_visibility_misses=patch_misses,
                  scope='one owned image-based camera/depth capacity,not actualvideo/head/medicalmm')
    write(OUT/'result.json',scores);np.savez_compressed(OUT/'scores.npz',**arrays);print(json.dumps(scores,indent=2))
    if scores['status']!='TECHNICAL_CHECK_PASSED':raise ValueError('fixed physical admission fails')


def controller(stage):
    if stage=='prepare':
        OUT.mkdir(exist_ok=False);write(OUT/'entry.json',{'source_sha256':sha(Path(__file__)),'registered_entry':time.time()})
    if stage=='initialize' and not (OUT/'reviewed.json').exists():raise ValueError('input review required')
    limits={'prepare':(120,2),'initialize':(120,2),'optimize':(300,2),'evaluate':(60,2)}
    seconds,gib=limits[stage];env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    record=run([sys.executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):{'prepare':prepare,'initialize':initialize,'optimize':optimize,'evaluate':evaluate}[stage[:-7]]()
    else:sys.exit(0 if controller(stage) else 1)
