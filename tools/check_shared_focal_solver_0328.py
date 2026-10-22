"""Opt-in pinned BSD solver control;no human input,training or head fitting."""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path,PurePosixPath
import sys
import time
from urllib.parse import urlparse
from urllib.request import Request,urlopen
import zipfile

import cv2
import numpy as np

from bounded_process import run
from short_track_camera import intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/shared-focal-0328'
WHEEL='poselib-2.0.5-cp312-cp312-win_amd64.whl'
WHEEL_SHA='e2db979ac77db14c89e3f07f4bd6fb5ac61dbacfc3634a8ae462964a4ac7f1f7'


def digest(data):return hashlib.sha256(data).hexdigest()


def fetch(url):
    allowed={'pypi.org','files.pythonhosted.org','api.github.com','raw.githubusercontent.com'}
    if urlparse(url).scheme!='https' or urlparse(url).hostname not in allowed:raise ValueError('unapproved source host')
    with urlopen(Request(url,headers={'User-Agent':'HeadFoundry-local-validation'}),timeout=25) as response:
        if urlparse(response.url).hostname not in allowed:raise ValueError('unapproved redirect')
        data=response.read(2*1024**2+1)
    if len(data)>2*1024**2:raise ValueError('source response too large')
    return data


def acquire():
    metadata_bytes=fetch('https://pypi.org/pypi/poselib/2.0.5/json')
    (OUT/'pypi.json').write_bytes(metadata_bytes);metadata=json.loads(metadata_bytes)
    candidates=[row for row in metadata['urls'] if row['filename']==WHEEL]
    if len(candidates)!=1 or candidates[0]['digests']['sha256']!=WHEEL_SHA:raise ValueError('publisher wheel identity mismatch')
    wheel=fetch(candidates[0]['url'])
    if digest(wheel)!=WHEEL_SHA or len(wheel)!=candidates[0]['size']:raise ValueError('wheel byte mismatch')
    (OUT/WHEEL).write_bytes(wheel)
    ref_bytes=fetch('https://api.github.com/repos/PoseLib/PoseLib/git/ref/tags/v2.0.5')
    (OUT/'tag.json').write_bytes(ref_bytes);ref=json.loads(ref_bytes)['object']
    if ref['type']=='tag':
        tag_bytes=fetch(ref['url']);(OUT/'annotated-tag.json').write_bytes(tag_bytes);ref=json.loads(tag_bytes)['object']
    if ref['type']!='commit' or len(ref['sha'])!=40:raise ValueError('unresolved source commit')
    source={}
    for path in ('LICENSE','README.md','PoseLib/robust.h','PoseLib/robust/ransac.h','pybind/pyposelib.cc'):
        data=fetch('https://raw.githubusercontent.com/PoseLib/PoseLib/'+ref['sha']+'/'+path)
        target=OUT/'source'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        source[path]=digest(data)
    finalize()


def finalize():
    wheel=(OUT/WHEEL).read_bytes()
    if digest(wheel)!=WHEEL_SHA:raise ValueError('cached wheel identity changed')
    ref=json.loads((OUT/('annotated-tag.json' if (OUT/'annotated-tag.json').exists() else 'tag.json')).read_text())['object']
    if ref['type']!='commit' or len(ref['sha'])!=40:raise ValueError('unresolved source commit')
    source={path:digest((OUT/'source'/path).read_bytes()) for path in
            ('LICENSE','README.md','PoseLib/robust.h','PoseLib/robust/ransac.h','pybind/pyposelib.cc')}
    license_bytes=(OUT/'source/LICENSE').read_bytes()
    if b'BSD 3-Clause License' not in license_bytes or b'binary forms' not in license_bytes:raise ValueError('source grant absent')
    with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
        if archive.testzip() is not None:raise ValueError('wheel CRC failure')
        names=archive.namelist()
        for name in names:
            path=PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or name.endswith('.pth'):
                raise ValueError('unsafe wheel member')
        records=[name for name in names if name.endswith('.dist-info/RECORD')]
        if len(records)!=1:raise ValueError('one RECORD required')
        for name,identity,size in csv.reader(io.StringIO(archive.read(records[0]).decode())):
            data=archive.read(name)
            if identity:
                algorithm,expected=identity.split('=',1)
                if algorithm!='sha256' or base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip('=')!=expected or len(data)!=int(size):
                    raise ValueError('wheel RECORD mismatch')
            elif name!=records[0]:raise ValueError('unsigned unexpected wheel record')
        licenses=[name for name in names if 'LICENSE' in name and '.dist-info/' in name]
        canonical=lambda data:data.replace(b'\r\r\n',b'\n').replace(b'\r\n',b'\n').replace(b'\r',b'\n').strip()
        if len(licenses)!=1 or canonical(archive.read(licenses[0]))!=canonical(license_bytes):raise ValueError('wheel/source grant mismatch')
        site=OUT/'site';site.mkdir()
        for name in names:
            info=archive.getinfo(name)
            if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('wheel symlink refused')
            target=site/PurePosixPath(name)
            if info.is_dir():target.mkdir(parents=True,exist_ok=True)
            else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(name))
    write(OUT/'asset.json',{'status':'TECHNICAL_CHECK_PASSED','wheel':WHEEL,'wheel_bytes':len(wheel),'wheel_sha256':WHEEL_SHA,
          'source_commit':ref['sha'],'source_sha256':source,'members':names,'license':'BSD-3-Clause',
          'main_environment_install':False,'binary_source_reproducibility':'UNVERIFIED'})


def prepare():
    rng=np.random.default_rng(328);xyz=rng.uniform([-.45,-.8,2.5],[.45,.8,3.5],(120,3))
    rotation=cv2.Rodrigues(np.array([0,np.deg2rad(18),0]))[0]@cv2.Rodrigues(np.array([np.deg2rad(15),0,0]))[0]
    poses=np.repeat(np.eye(4)[None],2,axis=0);poses[1,:3,:3]=rotation
    poses[1,:3,3]=np.array([0,0,3])-rotation@np.array([0,0,3]);k=intrinsics(np.log(1200.))
    rows=np.array([[camera,point,0,0] for camera in range(2) for point in range(120)])
    uv,z=project(k,poses,xyz,rows);uv=uv.reshape(2,120,2)
    if (z<=0).any() or (uv<0).any() or (uv>[719,1279]).any():raise ValueError('fixed point fixture outside sensor')
    exact=uv[:,:96].copy();noisy=exact+rng.normal(0,.5,exact.shape)
    noisy[1,-20:]=np.roll(noisy[1,-20:],1,axis=0)
    for name,points in [('exact',exact),('noisy',noisy)]:
        np.savez_compressed(OUT/(name+'-input.npz'),first=points[0],second=points[1],principal=np.array([359.5,639.5]))
    np.savez_compressed(OUT/'truth.npz',xyz=xyz,K=k,poses=poses,uv=uv)
    write(OUT/'input-identities.json',{name:digest((OUT/name).read_bytes()) for name in ('exact-input.npz','noisy-input.npz','truth.npz')})


def infer(case):
    private=ROOT/'assets/private'
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('no network/subprocess')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            reading=not isinstance(mode,str) or 'r' in mode or '+' in mode
            if reading and (path.name=='truth.npz' or path.suffix=='.stl' or (private in path.parents and OUT not in path.parents)):
                raise PermissionError('truth/geometry/unrelated private read denied')
    sys.addaudithook(audit);sys.path.insert(0,str(OUT/'site'))
    import poselib
    if poselib.__version__!='2.0.5':raise ValueError('wrong runtime version')
    if (OUT/'site') not in Path(poselib.__file__).resolve().parents:raise ValueError('runtime outside private overlay')
    data=dict(np.load(OUT/(case+'-input.npz')))
    options={'seed':328,'max_iterations':10000,'max_epipolar_error':1.5,'success_prob':.999}
    actual=poselib.RansacOptions(options)
    if any(actual[key]!=value for key,value in options.items()):raise ValueError('RANSAC options not applied')
    write(OUT/(case+'-options.json'),{'ransac':actual,'bundle':poselib.BundleOptions({'loss_scale':.75})})
    start=time.monotonic()
    pair,stats=poselib.estimate_shared_focal_relative_pose(data['first'],data['second'],data['principal'],options,{})
    f1=float(pair.camera1.focal());f2=float(pair.camera2.focal());pose=np.asarray(pair.pose.Rt)
    np.savez_compressed(OUT/(case+'-prediction.npz'),pose=pose,focals=np.array([f1,f2]),
                        camera1_params=pair.camera1.params,camera2_params=pair.camera2.params,
                        inliers=np.array(stats['inliers'],bool))
    write(OUT/(case+'-prediction.json'),{'status':'UNVERIFIED','scope':'raw solver output before truth evaluation',
         'stats':stats,'focals':[f1,f2],'pose':pose.tolist(),'seconds':time.monotonic()-start,
         'runtime_file':str(Path(poselib.__file__).relative_to(ROOT))})


def evaluate(case):
    truth=dict(np.load(OUT/'truth.npz'));prediction=dict(np.load(OUT/(case+'-prediction.npz')))
    pose=prediction['pose'];focals=prediction['focals'];inliers=prediction['inliers']
    proper=bool(pose.shape==(3,4) and np.isfinite(pose).all() and np.allclose(pose[:,:3]@pose[:,:3].T,np.eye(3),atol=1e-8,rtol=0) and np.linalg.det(pose[:,:3])>.999999)
    positive_f=bool(np.isfinite(focals).all() and (focals>0).all() and abs(focals[0]-focals[1])<1e-8)
    norm=float(np.linalg.norm(pose[:,3]));valid=bool(proper and positive_f and norm>1e-9 and inliers.shape==(96,))
    if not valid:raise ValueError('raw camera/pose schema fails')
    poses=np.repeat(np.eye(4)[None],2,axis=0);poses[1,:3]=pose
    poses[1,:3,3]*=np.linalg.norm(truth['poses'][1,:3,3])/norm
    xyz=truth['xyz'][96:];rows=np.array([[camera,point,0,0] for camera in range(2) for point in range(24)])
    k=intrinsics(np.log(focals[0]));uv,z=project(k,poses,xyz,rows)
    errors=np.linalg.norm(uv.reshape(2,24,2)-truth['uv'][:,96:],axis=2);p95=np.percentile(errors,95,axis=1)
    replay=[]
    for camera,p in enumerate(poses):
        oracle=cv2.projectPoints(xyz,cv2.Rodrigues(p[:3,:3])[0],p[:3,3],k,None)[0].reshape(-1,2)
        replay.append(float(np.max(abs(oracle-uv.reshape(2,24,2)[camera]))))
    wrong=poses.copy();wrong[1,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[1,:3,:3]
    bad,_=project(k,wrong,xyz,rows)
    negative=float(np.percentile(np.linalg.norm(bad.reshape(2,24,2)[1]-truth['uv'][1,96:],axis=1),95))
    relative=float(abs(focals[0]/1200-1));limits=(1e-5,.001) if case=='exact' else (.02,3.)
    passed=bool(relative<=limits[0] and p95.max()<=limits[1] and z.min()>0 and max(replay)<=1e-9 and negative>3)
    report={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','case':case,'focal_px':float(focals[0]),
            'focal_relative_error':relative,'held_known3D_p95_px':p95.tolist(),'held_count_each_view':24,
            'positive_depths':bool(z.min()>0),'proper_pose':proper,'translation_norm_raw':norm,
            'opencv_replay_max_px':max(replay),'wrong_camera_p95_px':negative,
            'ransac_inlier_count':int(inliers.sum()),'scope':'conditional owned-point solver only;actual-video/head/mm UNVERIFIED'}
    write(OUT/(case+'-result.json'),report);np.savez_compressed(OUT/(case+'-scores.npz'),errors=errors,poses=poses,K=k,depth=z)
    print(json.dumps(report,indent=2))
    if not passed:raise ValueError('registered physical admission failed')


def controller(stage):
    if stage=='acquire':OUT.mkdir(exist_ok=False)
    if not OUT.is_dir():raise ValueError('missing registered asset entry')
    seconds,memory=(120,256*1024**2) if stage=='acquire' else (120,2*1024**3)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    record=run([sys.executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,memory)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='acquire-worker':acquire()
    elif stage=='finalize-worker':finalize()
    elif stage=='prepare-worker':prepare()
    elif stage.startswith('infer-') and stage.endswith('-worker'):infer(stage[6:-7])
    elif stage.startswith('evaluate-') and stage.endswith('-worker'):evaluate(stage[9:-7])
    else:sys.exit(0 if controller(stage) else 1)
