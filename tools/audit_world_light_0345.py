"""Frozen owned information audit,not a pose/shape estimator or patient pipeline."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np

from bounded_process import run
from bundle_stationarity import focal_information
from native_camera_jacobian import linearize
from short_track_camera import intrinsics,project

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/world-light-information-0345'
DEADLINE=1792759579.
sys.dont_write_bytecode=True


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(name,value):
    with (OUT/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False)


def fixture(kind='curved',independent=False):
    x,y=np.meshgrid(np.linspace(-.45,.45,12),np.linspace(-.75,.75,8))
    z=3.+.12*np.sin(3*x)*np.cos(2*y)+.1*x*x
    if kind=='planar':z=np.full_like(x,3.)
    points=np.c_[x.ravel(),y.ravel(),z.ravel()];faces=[]
    for row in range(7):
        for column in range(11):
            a=row*12+column
            faces.extend([[a,a+12,a+1],[a+1,a+12,a+13]])
    faces=np.array(faces,int);r=np.array([0.,np.deg2rad(18),0.]);rotation=cv2.Rodrigues(r)[0]
    translation=np.array([0,0,3.])-rotation@np.array([0,0,3.]);baseline=np.linalg.norm(translation)
    points/=baseline;translation/=baseline
    if kind=='no_rotation':r=np.zeros(3);translation=np.array([1.,0,0])
    theta=np.arctan2(translation[1],translation[0]);phi=np.arctan2(translation[2],np.linalg.norm(translation[:2]))
    albedo=.3+.05*np.sin(2*x.ravel()+3*y.ravel());light=np.array([.18,-.12,-.30])
    if kind=='ambient':light=np.zeros(3)
    if kind=='axis_light':light=np.array([0.,-.30,0.])
    values=np.r_[np.log(1200.),359.5,639.5,r,theta,phi,points.ravel(),np.log(albedo),
                 np.tile(light,2 if independent else 1),.03,.01,-.005]
    return values,faces


def response(values,faces,independent=False,frozen_head=False,derivatives=True,algebraic=False):
    from mesh_normal_jacobian import normals
    values=np.asarray(values,float);n=int(faces.max())+1
    albedo_at=8+3*n;light_at=albedo_at+n;exposure_at=light_at+(6 if independent else 3)
    if values.shape!=(exposure_at+3,) or not np.isfinite(values).all():raise ValueError('fixed finite parameter schema required')
    points=values[8:albedo_at].reshape(n,3);normal,dnormal=normals(points,faces,derivatives=derivatives)
    poses=np.repeat(np.eye(4)[None],2,axis=0);rotation,rjac=cv2.Rodrigues(values[3:6])
    poses[1,:3,:3]=rotation;theta,phi=values[6:8]
    poses[1,:3,3]=[np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)]
    k=intrinsics(values[0]);k[:2,2]=values[1:3]
    rows=np.array([[camera,point,0,0] for camera in range(2) for point in range(n)])
    depths=np.concatenate([(points@p[:3,:3].T+p[:3,3])[:,2] for p in poses])
    if (depths<=1e-9).any() or not np.isfinite(depths).all():raise ValueError('unclamped positive domain fails')
    pixels,_=project(k,poses,points,rows)
    if not np.isfinite(pixels).all():raise ValueError('nonfinite projection')
    if not algebraic and ((pixels<0).any() or (pixels>[719,1279]).any()):raise ValueError('native projection bounds fail')
    albedo=np.exp(values[albedo_at:light_at]);irradiance=[];photon=[]
    photo_jac=np.zeros((2*n,len(values))) if derivatives else None
    for camera,pose in enumerate(poses):
        r=np.eye(3) if frozen_head else pose[:3,:3]
        offset=light_at+(3*camera if independent else 0);light=values[offset:offset+3]
        moved=normal@r.T;factor=1.+moved@light;gain=np.exp(values[exposure_at]) if camera else 1.
        image=gain*albedo*factor+values[exposure_at+1+camera]
        if (factor<=0).any() or not np.isfinite(image).all() or (image<=0).any() or (image>=1).any():
            raise ValueError('positive unclipped radiometric sensor domain fails')
        # Local front-facing samples,not a guarantee of actual skin visibility.
        local=points@pose[:3,:3].T+pose[:3,3]
        if (np.sum((normal@pose[:3,:3].T)*local,axis=1)>=0).any():raise ValueError('back-facing owned sample')
        irradiance.append(factor);photon.append(image)
        if derivatives:
            block=photo_jac[camera*n:(camera+1)*n];weight=gain*albedo
            block[:,8:albedo_at]=weight[:,None]*np.einsum('c,nck->nk',light@r,dnormal)
            block[np.arange(n),albedo_at+np.arange(n)]=weight*factor
            block[:,offset:offset+3]=weight[:,None]*moved
            if camera and not frozen_head:
                if rjac.shape!=(3,9):raise ValueError('OpenCV Rodrigues derivative axes changed')
                for axis in range(3):block[:,3+axis]=weight*((normal@rjac[axis].reshape(3,3).T)@light)
            if camera:block[:,exposure_at]=weight*factor
            block[:,exposure_at+1+camera]=1.
    intensity=np.concatenate(photon)
    output=np.r_[pixels.ravel()/.5,intensity/.01]
    if not derivatives:return output,None
    # Principal-point shifts change the forward projection,not the other columns.
    _,old,replay=linearize(intrinsics(values[0]),poses,points,rows,0,1)
    geometry=np.zeros((4*n,len(values)));geometry[:,0]=old[:,0]
    geometry[:,3:8]=old[:,1:6];geometry[:,8:albedo_at]=old[:,6:]
    geometry[0::2,1]=1.;geometry[1::2,2]=1.
    analytic=np.vstack((geometry/.5,photo_jac/.01))
    return output,analytic


def derivative_controls(values,faces):
    baseline,jac=response(values,faces);results=[]
    for step in (1e-6,5e-7):
        worst=0.;per_column=[]
        for column in range(len(values)):
            h=step*max(1.,abs(values[column]));a=values.copy();b=a.copy();a[column]+=h;b[column]-=h
            numeric=(response(a,faces,derivatives=False)[0]-response(b,faces,derivatives=False)[0])/(2*h)
            difference=float(np.linalg.norm(numeric-jac[:,column])/max(1.,np.linalg.norm(jac[:,column])))
            per_column.append(difference);worst=max(worst,difference)
        results.append({'step':step,'per_column_relative_errors':per_column,'maximum':worst})
        if worst>1e-6:raise AssertionError('analytic derivative fails independent full-column control')
    # Separate projectPoints forward replay,not the same project implementation.
    n=int(faces.max())+1;points=values[8:8+3*n].reshape(n,3);k=intrinsics(values[0]);k[:2,2]=values[1:3]
    theta,phi=values[6:8];t=np.array([np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)])
    expected=np.concatenate([cv2.projectPoints(points,r,tr,k,None)[0].reshape(-1,2)
        for r,tr in ((np.zeros(3),np.zeros(3)),(values[3:6],t))]).ravel()
    difference=float(np.max(abs(baseline[:4*n]*.5-expected)))
    if difference>1e-9:raise AssertionError('independent native projection replay fails')
    return {'status':'TECHNICAL_CHECK_PASSED','full_column_controls':results,'OpenCV_pixel_replay_max':difference}


def profile(matrix):
    report=focal_information(matrix)
    report['relative_profile_contrast']=report['profile_focal_column_norm']/max(report['raw_focal_column_norm'],1e-30)
    report['sigma_logf_under_declared_noise']=report.pop('sigma_log_f_per_unit_pixel_noise')
    return report


def guard():
    private=(ROOT/'assets/private').resolve()
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline math worker')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1];flags=args[2]
            reading=('r' in mode or '+' in mode) if isinstance(mode,str) else (flags&3)!=os.O_WRONLY
            if path.suffix.lower() in ('.stl','.mp4') or path.is_relative_to(Path('C:/Users/lihan/Downloads')) or path.is_relative_to(Path('C:/workspace/peek')):
                raise PermissionError('patient/unrelated geometry forbidden')
            if reading and path.is_relative_to(private) and not path.is_relative_to(OUT):raise PermissionError('unrelated private math read')
    sys.addaudithook(audit)


def worker():
    guard();cv2.setNumThreads(4)
    from mesh_normal_jacobian import check
    normal=check();write('normal-controls.json',normal)
    values,faces=fixture();checks=derivative_controls(values,faces);write('derivative-controls.json',checks)
    y,jac=response(values,faces);n=int(faces.max())+1
    arrays={'positive_values':values,'faces':faces,'positive_predictions':y,'positive_jacobian':jac}
    scores={'projection_only':profile(jac[:4*n]),'coupled':profile(jac)}
    for kind in ('planar','no_rotation','ambient','axis_light','frozen_head'):
        v,f=fixture(kind);out,matrix=response(v,f,frozen_head=kind=='frozen_head',algebraic=kind=='no_rotation')
        scores[kind]=profile(matrix)
        pixels=out[:4*n].reshape(-1,2)*.5
        scores[kind]['native_bounds_all_samples']=bool(((pixels>=0)&(pixels<=[719,1279])).all())
        scores[kind]['off_sensor_samples']=int(np.sum(np.any((pixels<0)|(pixels>[719,1279]),axis=1)))
        scores[kind]['own_forward_observations']=True
        scores[kind]['algebraic_not_capture']=kind in ('no_rotation','frozen_head')
        arrays.update({kind+'_values':v,kind+'_prediction':out,kind+'_jacobian':matrix})
    v,f=fixture(independent=True);out,matrix=response(v,f,independent=True)
    scores['independent_lights']=profile(matrix);arrays.update(independent_values=v,independent_predictions=out,independent_jacobian=matrix)
    np.savez_compressed(OUT/'matrices.npz',**arrays)
    controls=all(scores[name]['rank']==scores[name]['nuisance_rank'] and scores[name]['relative_profile_contrast']<=1e-10
        for name in ('projection_only','planar','no_rotation','ambient','axis_light','frozen_head'))
    candidate=scores['coupled'];information=bool(candidate['focal_identifiable_locally'] and candidate['relative_profile_contrast']>1e-6
        and candidate['sigma_logf_under_declared_noise'] is not None and candidate['sigma_logf_under_declared_noise']<=.02)
    passed=controls and information
    report={'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','negative_controls_passed':controls,
        'information_policy_passed':information,'scores':scores,'matrix_sha256':sha(OUT/'matrices.npz'),
        'pixels_noise':.5,'linear_irradiance_noise':.01,'unknown_principal_point':True,
        'geometry_normals_poses_albedo_light_exposure_all_profiled':True,'fit_or_step_applied':False,
        'patient_input':False,'scope':'local owned information only;not recovered cameras/shape/medical precision',
        'completed_utc':time.time()}
    write('result.json',report)
    print(json.dumps({key:value for key,value in report.items() if key!='scores'},indent=2))
    if not passed:raise ValueError('fixed physical information screen stops;no parameter rescue')


if __name__=='__main__':
    if ROOT!=Path('C:/workspace/headfoundry').resolve() or time.time()>DEADLINE:raise ValueError('scope/deadline fails')
    if sys.argv[1:] == ['worker']:worker()
    elif sys.argv[1:] == ['run']:
        for p in (ROOT,ROOT/'assets',ROOT/'assets/private'):
            if getattr(p.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse output')
        OUT.mkdir(exist_ok=False)
        if getattr(OUT.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse output')
        write('entry.json',{'registered':'bc9fc60','source_sha256':sha(__file__),'started_utc':time.time()})
        env=dict(os.environ);env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        record=run([sys.executable,'-B',str(Path(__file__)),'worker'],str(ROOT),env,OUT/'audit.log',OUT/'worker.json',120,1024**3)
        print(json.dumps(record,indent=2));sys.exit(0 if record['status']=='TECHNICAL_CHECK_PASSED' else 1)
    else:raise SystemExit('run only one registered audit')
