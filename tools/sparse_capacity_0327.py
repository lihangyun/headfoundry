"""One preregistered owned-scene capacity recipe;not patient reconstruction."""
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
from check_global_geometry_contract import similarity
from direct_patch_graph import residual as photometric
from short_track_camera import fit,intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/sparse-capacity-0327'
OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def intersect(pose,pixels,rectangles):
    rays=np.c_[(pixels-[359.5,639.5])/1200,np.ones(len(pixels))]@pose[:3,:3]
    center=-pose[:3,:3].T@pose[:3,3]
    best=np.full(len(pixels),np.inf);labels=np.full(len(pixels),-1,dtype=int)
    xyz=np.full((len(pixels),3),np.nan)
    for index,(x,y,z) in enumerate(rectangles):
        with np.errstate(divide='ignore',invalid='ignore'):
            distance=(z-center[2])/rays[:,2]
            points=center+distance[:,None]*rays
        visible=(distance>0)&(distance<best)&(abs(points[:,0]-x)<=.16)&(abs(points[:,1]-y)<=.19)
        best[visible],labels[visible],xyz[visible]=distance[visible],index,points[visible]
    return xyz,labels


def prepare():
    rng=np.random.default_rng(327)
    rectangles=np.array([[x,y,rng.uniform(2.6,3.5)] for y in np.linspace(-1,1,5) for x in np.linspace(-.63,.63,4)])
    poses=np.repeat(np.eye(4)[None],6,axis=0)
    vectors=np.deg2rad([[0,0,0],[0,10,0],[0,20,0],[15,0,0],[0,-10,0],[0,-20,0]])
    yy,xx=np.mgrid[:1280,:720];pixels=np.column_stack((xx.ravel(),yy.ravel()))
    gains=[1,1.07,.94,1.03,1.10,.92];biases=[0,.01,-.01,-.005,.005,0]
    sheet=Image.new('RGB',(720,1280),(20,20,20));draw=ImageDraw.Draw(sheet)
    for camera,vector in enumerate(vectors):
        rotation=cv2.Rodrigues(vector)[0]
        poses[camera,:3,:3]=rotation;poses[camera,:3,3]=np.array([0,0,3])-rotation@np.array([0,0,3])
        xyz,labels=intersect(poses[camera],pixels,rectangles)
        intensity=np.full(len(pixels),.08);valid=labels>=0
        p=xyz[valid];ids=labels[valid]
        intensity[valid]=.4+.10*np.sin(71*p[:,0]+ids)*np.cos(59*p[:,1]-ids)+.07*np.cos(113*p[:,0]+67*p[:,1])
        intensity=gains[camera]*intensity+biases[camera]+rng.normal(0,1/255,len(pixels))
        if not np.isfinite(intensity).all() or intensity.min()<0 or intensity.max()>1:
            raise ValueError('owned sensor fixture outside valid domain')
        image=Image.fromarray(np.round(intensity.reshape(1280,720)*255).astype('uint8'))
        image.save(OUT/f'view-{camera}.png')
        thumb=image.convert('RGB').resize((240,427));sheet.paste(thumb,((camera%3)*240,(camera//3)*640))
        draw.text(((camera%3)*240+8,(camera//3)*640+435),f'view {camera}',fill='white')
    sheet.save(OUT/'inputs.png')
    np.savez_compressed(OUT/'truth.npz',rectangles=rectangles,poses=poses,K=intrinsics(np.log(1200.)))
    write(OUT/'inputs.json',{'images':{f'view-{i}.png':sha(OUT/f'view-{i}.png') for i in range(6)},
                            'truth_sha256':sha(OUT/'truth.npz'),'seed':327,'rights':'original procedural validation fixture,not training'})


def load_images():
    info=json.loads((OUT/'inputs.json').read_text())
    images=[]
    for name,expected in info['images'].items():
        if sha(OUT/name)!=expected:raise ValueError('immutable image changed')
        images.append(np.asarray(Image.open(OUT/name),float)/255)
    return np.stack(images)


def audit():
    private=(ROOT/'assets/private').resolve()
    def check(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('no network/subprocess')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve()
            mode=args[1];reading=not isinstance(mode,str) or ('r' in mode or '+' in mode)
            if reading and (path.name=='truth.npz' or path.suffix.lower()=='.stl' or (private in path.parents and OUT not in path.parents)):
                raise PermissionError('truth/geometry/unrelated private read denied')
    sys.addaudithook(check)


def initialize():
    audit();cv2.setNumThreads(4);cv2.setRNGSeed(327)
    images=load_images();gray=np.round(images*255).astype('uint8')
    frames=list(range(6));xy={};tracks=[];hosts=[];queries=[];edges=[];counts=[]
    criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.001)
    for host in frames:
        mask=cv2.erode((images[host]>.12).astype('uint8'),np.ones((17,17),np.uint8))
        corners=cv2.goodFeaturesToTrack(gray[host],32,.02,15,mask=mask,blockSize=5)
        if corners is None:raise ValueError('no source corners')
        corners=cv2.cornerSubPix(gray[host],corners,(5,5),(-1,-1),criteria)
        observations={target:[] for target in frames if target!=host}
        for target in observations:
            forward,status,_=cv2.calcOpticalFlowPyrLK(gray[host],gray[target],corners,None,winSize=(31,31),maxLevel=4,criteria=criteria)
            backward,returned,_=cv2.calcOpticalFlowPyrLK(gray[target],gray[host],forward,None,winSize=(31,31),maxLevel=4,criteria=criteria)
            for index,(uv,back,ok,ret) in enumerate(zip(forward[:,0],backward[:,0],status[:,0],returned[:,0])):
                if ok and ret and np.isfinite(uv).all() and np.linalg.norm(back-corners[index,0])<=.75 and (uv>=4).all() and (uv<=[715,1275]).all():
                    observations[target].append((index,uv))
        admitted=0
        lookup={target:dict(values) for target,values in observations.items()}
        for index,query in enumerate(corners[:,0]):
            targets=[target for target,values in lookup.items() if index in values]
            if len(targets)<2 or not (query>=4).all() or not (query<=[715,1275]).all():continue
            point=len(tracks);track=[(host,point)];xy[(host,point)]=query
            hosts.append(host);queries.append(query);admitted+=1
            for target in targets:
                track.append((target,point));xy[(target,point)]=lookup[target][index];edges.append([point,target])
            tracks.append(track)
        counts.append(admitted)
    write(OUT/'observations.json',{'host_counts':counts,'points':len(tracks),'edges':len(edges),
          'complete_six_view_points':sum(len(t)==6 for t in tracks),'policy':'keep every admitted point/edge'})
    np.savez_compressed(OUT/'graph.npz',hosts=np.array(hosts),queries=np.array(queries),edges=np.array(edges))
    if min(counts)<12 or len(tracks)<72:raise ValueError('registered partial-view host coverage failed')
    eligible={v for point,track in enumerate(tracks) for v in track if v[0]!=hosts[point]}
    data={'frames':frames,'xy':xy}
    k,poses,points,train,held,metrics=fit(data,tracks,OUT/'initial',held_eligible=eligible)
    if any(sum(held[:,0]==camera)<6 for camera in frames):raise ValueError('insufficient per-camera held target rows')
    anchor=poses[0].copy();points=points@anchor[:3,:3].T+anchor[:3,3]
    poses=poses@np.linalg.inv(anchor)
    centers=-np.einsum('nji,nj->ni',poses[:,:3,:3],poses[:,:3,3])
    baseline=int(np.argmax(np.linalg.norm(centers,axis=1)));length=np.linalg.norm(centers[baseline])
    if not np.isfinite(length) or length<=1e-9:raise ValueError('bad baseline gauge')
    points/=length;poses[:,:3,3]/=length
    depths=np.array([(poses[host,:3,:3]@point+poses[host,:3,3])[2] for host,point in zip(hosts,points)])
    if not np.isfinite(depths).all() or (depths<=1e-9).any():raise ValueError('nonpositive host seed depth')
    np.savez_compressed(OUT/'initial-state.npz',K=k,poses=poses,points=points,rho=1/depths,baseline=baseline,train=train,held=held)
    write(OUT/'initialize-complete.json',{'status':'TECHNICAL_CHECK_PASSED','scope':'software initializer completed,not physical truth',
                                       'focal_px':float(k[0,0]),'baseline':baseline,'point_metric':metrics})


def optimize():
    audit();images=load_images();graph=dict(np.load(OUT/'graph.npz'));initial=dict(np.load(OUT/'initial-state.npz'))
    hosts,queries=graph['hosts'],graph['queries'];baseline=int(initial['baseline']);train=initial['train'];held=initial['held']
    edges=np.array([[int(point),int(camera)] for camera,point,_,_ in train if camera!=hosts[int(point)]])
    pixels=queries[:,None,:]+OFFSETS
    poses=initial['poses'];values=[np.log(initial['K'][0,0])];blocks={}
    for camera in range(1,6):
        rotation=cv2.Rodrigues(poses[camera,:3,:3])[0].ravel();translation=poses[camera,:3,3]
        if camera==baseline:
            translation=np.array([np.arctan2(translation[1],translation[0]),np.arctan2(translation[2],np.linalg.norm(translation[:2]))])
        blocks[camera]=slice(len(values),len(values)+len(rotation)+len(translation))
        values.extend(rotation);values.extend(translation)
    exposure=len(values);values.extend(np.zeros(10));depth_start=len(values);values.extend(np.log(initial['rho']))
    values=np.array(values);lower=values.copy();upper=values.copy()
    lower[0],upper[0]=np.log(640.),np.log(5120.)
    for camera,block in blocks.items():
        margin=np.r_[np.full(3,.1),np.full(2 if camera==baseline else 3,.1 if camera==baseline else .2)]
        lower[block]-=margin;upper[block]+=margin
    lower[exposure:depth_start]=np.tile([-.3,-.05],5);upper[exposure:depth_start]=np.tile([.3,.05],5)
    lower[depth_start:]-=.3;upper[depth_start:]+=.3

    def unpack(x):
        pp=np.repeat(np.eye(4)[None],6,axis=0)
        for camera,block in blocks.items():
            value=x[block];pp[camera,:3,:3]=cv2.Rodrigues(value[:3])[0]
            if camera==baseline:
                theta,phi=value[3:];pp[camera,:3,3]=[np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)]
            else:pp[camera,:3,3]=value[3:]
        exposure_values=np.vstack(([0.,0.],x[exposure:depth_start].reshape(5,2)))
        return pp,exposure_values[:,0],exposure_values[:,1],np.exp(x[depth_start:])

    def objective(x):
        pp,a,b,rho=unpack(x)
        try:return photometric(images,pixels,hosts,edges,rho,pp,a,b,x[0])[0].ravel()
        except ValueError as error:
            domain=('unclamped projector domain','outside complete bilinear','outside normalized sensor domain','outside image')
            if any(text in str(error) for text in domain):return np.full(len(edges)*len(OFFSETS),np.inf)
            raise

    pattern=sparse.lil_matrix((len(edges)*8,len(values)),dtype=int)
    for row,(point,target) in enumerate(edges):
        rows=slice(8*row,8*row+8);pattern[rows,0]=1;pattern[rows,depth_start+point]=1
        for camera in (hosts[point],target):
            if camera:
                pattern[rows,blocks[camera]]=1;pattern[rows,exposure+2*(camera-1):exposure+2*camera]=1
    pattern=pattern.tocsr();base=objective(values)
    if not np.isfinite(base).all():raise ValueError('nonfinite initial direct objective')
    # Check every omitted column entry,not just random selected blocks.
    worst=0.;start=time.monotonic()
    for column in range(len(values)):
        perturbed=values.copy();perturbed[column]+=1e-6
        changed=objective(perturbed)
        if not np.isfinite(changed).all():raise ValueError('nonfinite finite-difference objective')
        omitted=~pattern[:,column].toarray().ravel().astype(bool)
        if omitted.any():worst=max(worst,float(np.max(abs(changed[omitted]-base[omitted]))))
    write(OUT/'jacobian-contract.json',{'columns':len(values),'max_omitted_change':worst,'seconds':time.monotonic()-start})
    if worst>1e-12:raise ValueError('sparse Jacobian omitted dependency')
    print('jacobian checked',len(values),worst,flush=True)
    solution=least_squares(objective,values,bounds=(lower,upper),jac_sparsity=pattern,method='trf',
        loss='soft_l1',f_scale=.01,x_scale='jac',max_nfev=150,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    pp,a,b,rho=unpack(solution.x)
    rays=np.c_[(queries-[359.5,639.5])/np.exp(solution.x[0]),np.ones(len(queries))]/rho[:,None]
    points=np.einsum('nji,nj->ni',pp[hosts,:3,:3],rays-pp[hosts,:3,3])
    final=objective(solution.x)
    np.savez_compressed(OUT/'final-state.npz',K=intrinsics(solution.x[0]),poses=pp,points=points,rho=rho,
                        log_gains=a,biases=b,values=solution.x,lower=lower,upper=upper,train=train,held=held,edges=edges,residual=final)
    write(OUT/'direct-complete.json',{'status':'TECHNICAL_CHECK_PASSED' if solution.success and np.isfinite(final).all() else 'REJECT',
          'optimizer_success':solution.success,'message':solution.message,'nfev':solution.nfev,
          'focal_px':float(np.exp(solution.x[0])),'initial_rms':float(np.sqrt(np.mean(base**2))),
          'final_rms':float(np.sqrt(np.mean(final**2)))})
    if not solution.success or not np.isfinite(final).all():raise ValueError('direct solver termination gate failed')


def evaluate():
    graph=dict(np.load(OUT/'graph.npz'));truth=dict(np.load(OUT/'truth.npz'))
    identities=json.loads((OUT/'inputs.json').read_text())
    if sha(OUT/'truth.npz')!=identities['truth_sha256']:raise ValueError('truth changed')
    host_truth=[];source_labels=[]
    for host,query in zip(graph['hosts'],graph['queries']):
        point,label=intersect(truth['poses'][host],query[None],truth['rectangles'])
        if label[0]<0:raise ValueError('host query misses truth surface')
        host_truth.append(point[0]);source_labels.append(label[0])
    xyz=np.array(host_truth);k=truth['K'];truth_centers=-np.einsum('nji,nj->ni',truth['poses'][:,:3,:3],truth['poses'][:,:3,3])
    rows=np.array([[camera,point,0,0] for camera in range(6) for point in range(len(xyz))])
    true_uv,_=project(k,truth['poses'],xyz,rows)
    for point,target in graph['edges']:
        uv=true_uv.reshape(6,-1,2)[target,point]
        hit,label=intersect(truth['poses'][target],uv[None],truth['rectangles'])
        if label[0]!=source_labels[point] or np.linalg.norm(hit[0]-xyz[point])>1e-6:
            raise ValueError('included target truth visibility fails;no pruning')
    scores={};arrays={}
    for name in ('initial','final'):
        state=dict(np.load(OUT/f'{name}-state.npz'));poses=state['poses']
        centers=-np.einsum('nji,nj->ni',poses[:,:3,:3],poses[:,:3,3])
        if np.linalg.matrix_rank(centers-centers.mean(0),tol=1e-8)<3:raise ValueError('deficient center alignment')
        scale,rotation,translation=similarity(centers,truth_centers)
        estimated_xyz=(xyz-translation)@rotation/scale
        uv,depth=project(state['K'],poses,estimated_xyz,rows)
        error=np.linalg.norm(uv-true_uv,axis=1).reshape(6,-1)
        center_error=np.linalg.norm(scale*centers@rotation.T+translation-truth_centers,axis=1)
        point_error=np.linalg.norm(scale*state['points']@rotation.T+translation-xyz,axis=1)
        held=state['held'];pred,held_depth=project(state['K'],poses,state['points'],held)
        held_error=np.linalg.norm(pred-held[:,2:],axis=1)
        held_p95=[float(np.percentile(held_error[held[:,0]==camera],95)) for camera in range(6)]
        replay=[]
        for camera,pose in enumerate(poses):
            oracle=cv2.projectPoints(estimated_xyz,cv2.Rodrigues(pose[:3,:3])[0],pose[:3,3],state['K'],None)[0].reshape(-1,2)
            replay.append(float(np.max(abs(oracle-uv.reshape(6,-1,2)[camera]))))
        wrong=poses.copy();wrong[0,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[0,:3,:3]
        bad,_=project(state['K'],wrong,estimated_xyz,rows[:len(xyz)])
        negative=float(np.percentile(np.linalg.norm(bad-true_uv[:len(xyz)],axis=1),95))
        proper=bool(np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-7,rtol=0) and (np.linalg.det(poses[:,:3,:3])>.999999).all())
        p95=np.percentile(error,95,axis=1);f=float(state['K'][0,0]);relative=abs(f/1200-1)
        passed=bool(proper and min(depth.min(),held_depth.min())>0 and 640.640<f<5114.88 and relative<=.02 and
                    p95.max()<=3 and center_error.max()<=.01 and np.percentile(point_error,95)<=.01 and
                    max(held_p95)<=3 and max(replay)<1e-8 and negative>3)
        scores[name]={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','focal_px':f,'focal_rel':relative,
            'known3D_p95_px_per_camera':p95.tolist(),'center_max_scene_units':float(center_error.max()),
            'point_p95_scene_units':float(np.percentile(point_error,95)),'held_p95_px_per_camera':held_p95,
            'opencv_replay_max_px':max(replay),'wrong_camera_p95_px':negative,'proper':proper}
        arrays.update({name+'_known3D_error':error,name+'_center_error':center_error,name+'_point_error':point_error,
                       name+'_held_error':held_error,name+'_similarity':np.r_[scale,rotation.ravel(),translation]})
    np.savez_compressed(OUT/'scores.npz',**arrays)
    scores.update(status=scores['final']['status'],scope='one owned partial-visibility scene;actual patient/head/mm UNVERIFIED')
    write(OUT/'result.json',scores);print(json.dumps(scores,indent=2),flush=True)
    if scores['status']!='TECHNICAL_CHECK_PASSED':raise ValueError('registered physical precision rejected')


def controller(stage):
    limits={'prepare':(120,2),'initialize':(300,3),'optimize':(420,3),'evaluate':(60,2)}
    if stage=='prepare':
        OUT.mkdir(exist_ok=False)
        write(OUT/'entry.json',{'source_sha256':sha(Path(__file__)),'started':time.time(),'stage':stage})
    if stage!='prepare' and not (OUT/'entry.json').exists():raise ValueError('no registered own entry')
    if stage=='initialize' and not (OUT/'reviewed.json').exists():raise ValueError('input review required')
    seconds,gib=limits[stage];env=os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',NUMEXPR_NUM_THREADS='4')
    record=run([sys.executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),
               OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(json.dumps(record,indent=2))
    return record['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        {'prepare':prepare,'initialize':initialize,'optimize':optimize,'evaluate':evaluate}[stage[:-7]]()
    else:sys.exit(0 if controller(stage) else 1)
