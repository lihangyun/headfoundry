"""One frozen synthetic capacity recipe,not a head reconstruction pipeline."""
import hashlib
import json
import os
from datetime import datetime,timezone
from pathlib import Path
import subprocess
import sys
import time
import traceback

import cv2
import numpy as np
from PIL import Image,ImageDraw

from bounded_process import run
from check_global_geometry_contract import similarity
from headfoundry.raster import lift_pixels,render
from short_track_camera import fit,intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/direct-camera-0321'


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def mesh(context,rng):
    vertices=[];faces=[];colors=[]
    if context=='panels':
        for y in np.linspace(-.88,.88,5):
            for x in np.linspace(-.51,.51,4):
                depth=float(rng.uniform(2.6,3.4));base=len(vertices)
                xx,yy=np.meshgrid(np.linspace(x-.13,x+.13,17),np.linspace(y-.18,y+.18,17))
                vertices.extend(np.c_[xx.ravel(),yy.ravel(),np.full(xx.size,depth)])
                colors.extend(rng.uniform(.22,.7,xx.size))
                for i in range(16):
                    for j in range(16):
                        a=base+17*i+j;faces.extend([[a,a+1,a+17],[a+1,a+18,a+17]])
    else:
        for a in np.linspace(-np.pi/2+.001,np.pi/2-.001,65):
            for b in np.linspace(-np.pi,np.pi,97):
                vertices.append([.65*np.cos(a)*np.sin(b),.95*np.sin(a),3-.4*np.cos(a)*np.cos(b)])
                colors.append(rng.uniform(.22,.7))
        for i in range(64):
            for j in range(96):
                a=97*i+j;faces.extend([[a,a+1,a+97],[a+1,a+98,a+97]])
    return np.array(vertices),np.array(faces),np.repeat(np.array(colors)[:,None]*255,3,axis=1)


def prepare(context,folder):
    rng=np.random.default_rng(321)
    vertices,faces,colors=mesh(context,rng)
    poses=np.repeat(np.eye(4)[None],6,axis=0)
    for i,(yaw,pitch) in enumerate([(0,0),(12,0),(-12,0),(24,0),(-24,0),(0,16)]):
        rotation=cv2.Rodrigues(np.radians([pitch,yaw,0.]))[0]
        poses[i,:3,:3]=rotation;poses[i,:3,3]=np.array([0,0,3])-rotation@np.array([0,0,3])
    k=intrinsics(np.log(1200.));edge_k=k.copy();edge_k[:2,2]+=.5
    images=[];gains=[1,1.07,.94,1.10,.92,1.03];biases=[0,.01,-.01,.005,0,-.005]
    for i,pose in enumerate(poses):
        rgb,_,face_ids=render(vertices,faces,pose[:3],edge_k,(720,1280),vertex_colors=colors)
        gray=rgb[:,:,0]/255.;gray[face_ids<0]=.05
        gray=gains[i]*gray+biases[i]+rng.normal(0,1/255,gray.shape)
        if gray.min()<0 or gray.max()>1:raise ValueError('synthetic sensor saturation')
        images.append(gray)
    images=np.array(images)
    np.savez_compressed(folder/'inputs.npz',images=images)
    np.savez_compressed(folder/'truth.npz',vertices=vertices,faces=faces,K=k,edge_K=edge_k,poses=poses,
                        gains=gains,biases=biases)
    sheet=Image.new('RGB',(3*240,2*447),'#eeeeee');draw=ImageDraw.Draw(sheet)
    for i,gray in enumerate(images):
        tile=Image.fromarray(np.uint8(gray*255)).convert('RGB').resize((240,427))
        x,y=(i%3)*240,(i//3)*447;sheet.paste(tile,(x,y+20));draw.text((x+4,y+3),f'{context} view {i}',fill='black')
    sheet.save(folder/'inputs.png')
    write(folder/'prepared.json',{'context':context,'images':6,'shape':list(images.shape),
          'inputs_sha256':digest(folder/'inputs.npz'),'truth_sha256':digest(folder/'truth.npz'),
          'rights':'original procedural geometry/material;no external asset or human data'})


def guard(folder,stage):
    allowed={folder/'inputs.npz'}
    if stage=='direct':allowed.add(folder/'init/solution.npz')
    read_log=[]
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
        reading=not isinstance(mode,str) or not any(flag in mode for flag in ('w','a','x'))
        if not reading:return
        if path.suffix.lower()=='.stl' or (ROOT/'assets/private') in path.parents:
            if path not in allowed:raise PermissionError(f'inference read forbidden:{path.name}')
            read_log.append(str(path.relative_to(ROOT)).replace('\\','/'))
    sys.addaudithook(audit)
    return read_log


def initialize(folder):
    read_log=guard(folder,'init');images=np.load(folder/'inputs.npz')['images']
    gray=np.uint8(images*255)
    mask=np.uint8(images[0]>.12)*255;mask=cv2.erode(mask,np.ones((13,13),np.uint8))
    query=cv2.goodFeaturesToTrack(gray[0],96,.02,15,mask=mask,blockSize=5)
    if query is None:raise ValueError('no source corners')
    query=cv2.cornerSubPix(gray[0],query,(5,5),(-1,-1),(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,.001))
    matches=[query[:,0]];accepted=np.ones(len(query),bool)
    returns=[]
    for target in gray[1:]:
        points,status,_=cv2.calcOpticalFlowPyrLK(gray[0],target,query,None,winSize=(31,31),maxLevel=4,
            criteria=(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,.001))
        back,back_status,_=cv2.calcOpticalFlowPyrLK(target,gray[0],points,None,winSize=(31,31),maxLevel=4,
            criteria=(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,.001))
        error=np.linalg.norm(back[:,0]-query[:,0],axis=1);returns.append(error)
        xy=points[:,0];accepted&=(status[:,0]!=0)&(back_status[:,0]!=0)&np.isfinite(xy).all(1)&(error<=.75)
        accepted&=(xy>4).all(1)&(xy<[715,1275]).all(1)
        matches.append(xy)
    accepted&=(query[:,0]>4).all(1)&(query[:,0]<[715,1275]).all(1)
    matches=np.array(matches)[:,accepted].astype(float)
    np.savez_compressed(folder/'image-matches.npz',queries=query[:,0],accepted=accepted,
                        return_errors=np.array(returns),matches=matches)
    write(folder/'observation-screen.json',{'queries':len(query),'admitted':int(accepted.sum()),
          'screen':'image-only full-view support and FB;not certified physical identity'})
    if accepted.sum()<48:raise ValueError('fewer than48complete image tracks')
    data={'frames':list(range(6)),'xy':{(c,p):xy for c,row in enumerate(matches) for p,xy in enumerate(row)}}
    tracks=[[(c,p) for c in range(6)] for p in range(matches.shape[1])]
    eligible={(c,p) for c in range(1,6) for p in range(matches.shape[1])}
    fit(data,tracks,folder/'init',held_eligible=eligible)
    write(folder/'init-read-audit.json',{'reads':read_log,'truth_read':False,'native_sandbox':False})


def direct(folder):
    from direct_patch_solve import refine
    read_log=guard(folder,'direct')
    images=np.load(folder/'inputs.npz')['images']
    state=np.load(folder/'init/solution.npz')
    train,held=state['train'],state['held']
    queries=train[train[:,0]==0,2:]
    refine(images,queries,state['K'],state['poses'],state['points'],train,held,folder)
    write(folder/'direct-read-audit.json',{'reads':read_log,'truth_read':False,'native_sandbox':False})


def evaluate(folder):
    truth=np.load(folder/'truth.npz');v,f=truth['vertices'],truth['faces']
    k,poses,edge_k=truth['K'],truth['poses'],truth['edge_K']
    init=np.load(folder/'init/solution.npz');train,held=init['train'],init['held']
    query=train[train[:,0]==0,2:]
    ids,w=lift_pixels(v,f,poses[0,:3],edge_k,query+.5)
    if (ids<0).any():raise ValueError('an admitted source query misses scene;no pruning')
    xyz=np.einsum('ni,nij->nj',w,v[f[ids]])
    true_rows=np.array([[c,p,0.,0.] for c in range(6) for p in range(len(query))])
    truth_uv,truth_z=project(k,poses,xyz,true_rows)
    for c in range(6):
        uv=truth_uv.reshape(6,-1,2)[c]
        visible,bary=lift_pixels(v,f,poses[c,:3],edge_k,uv+.5)
        if (visible<0).any():raise ValueError('admitted point not visible in target;no pruning')
        hit=np.einsum('ni,nij->nj',bary,v[f[visible]])
        if np.linalg.norm(hit-xyz,axis=1).max()>1e-7:raise ValueError('admitted track is occluded;no pruning')
    truth_centers=-np.einsum('nji,nj->ni',poses[:,:3,:3],poses[:,:3,3])
    reports={};raw={'truth_points':xyz,'truth_uv':truth_uv,'query':query}
    for name,path in [('initial',folder/'init/solution.npz'),('direct',folder/'direct.npz')]:
        s=np.load(path);kk,pp,xx=s['K'],s['poses'],s['points']
        centers=-np.einsum('nji,nj->ni',pp[:,:3,:3],pp[:,:3,3])
        singular=np.linalg.svd(centers-centers.mean(0),compute_uv=False)
        if singular[-1]/singular[0]<1e-4:raise ValueError('noncollinear gauge rank fails')
        scale,rotation,translation=similarity(centers,truth_centers)
        transformed=(xyz-translation)@rotation/scale
        uv,z=project(kk,pp,transformed,true_rows)
        errors=np.linalg.norm(uv-truth_uv,axis=1).reshape(6,-1)
        held_uv,held_z=project(kk,pp,xx,held)
        held_errors=np.linalg.norm(held_uv-held[:,2:],axis=1)
        held_rows=[]
        for c in range(6):
            selected=held_errors[held[:,0]==c]
            held_rows.append({'view':c,'count':len(selected),'p95_px':float(np.percentile(selected,95)) if len(selected) else None})
        center_errors=np.linalg.norm(scale*centers@rotation.T+translation-truth_centers,axis=1)
        point_errors=np.linalg.norm(scale*xx@rotation.T+translation-xyz,axis=1)
        replay=0.
        for c in range(6):
            native,_=cv2.projectPoints(transformed,cv2.Rodrigues(pp[c,:3,:3])[0],pp[c,:3,3],kk,None)
            replay=max(replay,float(np.abs(native[:,0]-uv.reshape(6,-1,2)[c]).max()))
        wrong=pp.copy();wrong[0,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[0,:3,:3]
        bad,_=project(kk,wrong,transformed,true_rows[:len(xyz)])
        negative=float(np.percentile(np.linalg.norm(bad-truth_uv[:len(xyz)],axis=1),95))
        proper=bool(np.allclose(pp[:,:3,:3]@pp[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-7) and
                    (np.linalg.det(pp[:,:3,:3])>.999999).all() and np.array_equal(pp[:,3],np.tile([0,0,0,1],(6,1))))
        p95=np.percentile(errors,95,axis=1);ferr=float(abs(kk[0,0]/1200-1))
        positive=bool((z>0).all() and (held_z>0).all())
        passed=bool(proper and positive and 640.64<kk[0,0]<5114.88 and ferr<=.02 and (p95<=3).all()
             and center_errors.max()<=.01 and np.percentile(point_errors,95)<=.01 and replay<=1e-5 and negative>3
             and all(row['count']>=6 and row['p95_px']<=3 for row in held_rows[1:]))
        reports[name]={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','focal_px':float(kk[0,0]),
             'focal_relative_error':ferr,'true_projection_p95_px_per_view':p95.tolist(),'held':held_rows,
             'center_errors_scene_units':center_errors.tolist(),'point_p95_scene_units':float(np.percentile(point_errors,95)),
             'gauge_singular_values':singular.tolist(),'replay_max_px':replay,'wrong_camera_p95_px':negative,
             'proper':proper,'positive':positive,'gauge_scale':float(scale),'gauge_rotation':rotation.tolist(),
             'gauge_translation':translation.tolist()}
        raw.update({name+'_physical_errors':errors,name+'_center_errors':center_errors,name+'_point_errors':point_errors})
    numerical=json.loads((folder/'direct.json').read_text())
    passed=reports['direct']['status']=='TECHNICAL_CHECK_PASSED' and numerical['success']
    np.savez_compressed(folder/'evaluation-raw.npz',**raw)
    write(folder/'evaluation.json',{'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        'scope':'owned synthetic unit-scene only;no patient/mm/head acceptance','states':reports})
    return passed


def controller():
    # The first entry stopped before any file/worker;only that empty directory may be reused.
    if OUT.exists() and any(OUT.iterdir()):raise ValueError('nonempty experiment output refuses rerun')
    OUT.mkdir(exist_ok=True)
    plan=json.loads((ROOT/'assets/private/closed-experiments/0316-geocalib-domain/plan.json').read_text())
    protected=[]
    for row in plan['protected']:
        path=Path(row['path']);expected=plan['amendments'].get(str(path),row['expected'])
        actual=digest(path)
        if expected!=actual:raise ValueError('pre-run protected identity mismatch:'+path.name)
        protected.append({'path':str(path),'sha256':actual})
    for relative in ['tools/direct_patch_camera.py','tests/test_direct_patch_camera.py']:
        protected.append({'path':str(ROOT/relative),'sha256':digest(ROOT/relative)})
    scipy_source=ROOT/'.venv/Lib/site-packages/scipy/optimize/_lsq/trf.py'
    lines=scipy_source.read_text().splitlines()
    trials=[{'line':i+1,'context':lines[max(0,i-3):i+5]} for i,line in enumerate(lines) if 'isfinite(f_new)' in line]
    if len(trials)!=2 or not all('continue' in '\n'.join(row['context']) for row in trials):raise ValueError('TRF trial guard not verified')
    write(OUT/'entry.json',{'epoch':time.time(),'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protected':protected,'scipy_sha256':digest(scipy_source),'nonfinite_trial_source':trials,
        'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__})
    env=os.environ.copy();env.update({key:'4' for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']})
    env['PYTHONDONTWRITEBYTECODE']='1'
    script=str(Path(__file__).resolve())
    for context in ['panels','curved']:
        folder=OUT/context;folder.mkdir()
        for stage,seconds,gib in [('prepare',120,2),('init',300,3),('direct',300,3),('evaluate',60,2)]:
            remaining=datetime(2026,10,22,18,30,tzinfo=timezone.utc).timestamp()-time.time()-180
            if remaining<=0:
                write(OUT/'result.json',{'status':'REJECT','reason':'whole-recipe closeout reserve reached',
                    'context':context,'stage':stage,'head_medical':'UNVERIFIED'})
                return
            record=run([sys.executable,script,stage,context],str(ROOT),env,folder/(stage+'.log'),
                       folder/(stage+'-worker.json'),min(seconds,remaining),gib*1024**3)
            print(context,stage,record,flush=True)
            failed=record['status']!='TECHNICAL_CHECK_PASSED'
            if stage=='evaluate' and not failed:
                failed=json.loads((folder/'evaluation.json').read_text())['status']!='TECHNICAL_CHECK_PASSED'
            if failed:
                write(OUT/'result.json',{'status':'REJECT','context':context,'stage':stage,
                    'next_context':'UNVERIFIED' if context=='panels' else None,'head_medical':'UNVERIFIED'})
                return
    write(OUT/'result.json',{'status':'TECHNICAL_CHECK_PASSED','scope':'synthetic only','head_medical':'UNVERIFIED'})


if __name__=='__main__':
    cv2.setNumThreads(4)
    if len(sys.argv)==1:controller()
    else:
        stage,context=sys.argv[1:];folder=OUT/context
        try:
            if stage=='prepare':prepare(context,folder)
            elif stage=='init':initialize(folder)
            elif stage=='direct':direct(folder)
            elif stage=='evaluate':evaluate(folder)
            else:raise ValueError('unknown stage')
        except Exception:
            traceback.print_exc();sys.exit(1)
