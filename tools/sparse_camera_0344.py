"""Fixed three-view conditional camera check;no model,scan or head fitting."""
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import least_squares

import dense_photo_0332 as photo
from short_track_camera import intrinsics,project,write

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/aliked-real-0344'


def _observations():
    with np.load(OUT/'observations.npz',allow_pickle=False) as record:
        xy=record['xy'];train=record['train'];held=record['held'];source_ids=record['source_ids']
    if (xy.ndim!=3 or xy.shape[0]!=3 or xy.shape[2]!=2 or xy.shape[1]<48
            or not np.isfinite(xy).all() or (xy<4).any() or (xy>[715,1275]).any()):
        raise ValueError('complete finite native three-view observation domain required')
    n=xy.shape[1]
    if any(len(np.unique(view,axis=0))!=n for view in xy):
        raise ValueError('duplicate native endpoints cannot count as distinct support')
    for ids in (train,held,source_ids):
        if ids.ndim!=1 or not np.isfinite(ids).all() or not np.array_equal(ids,ids.astype(int)):
            raise ValueError('integer point identities required')
    train,held,source_ids=[ids.astype(int) for ids in (train,held,source_ids)]
    if (len(train)<36 or len(held)<9 or len(source_ids)!=n or (source_ids<0).any()
            or len(np.unique(source_ids))!=n
            or not np.array_equal(np.sort(np.r_[train,held]),np.arange(n))):
        raise ValueError('whole-point training/held partition and stable source IDs required')
    return xy,train,held,source_ids


def initialize():
    photo.OUT=OUT;photo.read_audit();cv2.setNumThreads(4);cv2.setRNGSeed(331)
    xy,train,held,_=_observations();observed=xy[:,train]
    k=intrinsics(np.log(1280.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    # Same geometric tail/numerical choices as0332/0337;only observations differ.
    for camera in (1,2):
        e,inliers=cv2.findEssentialMat(observed[0],observed[camera],k,method=cv2.RANSAC,prob=.999,threshold=1.5)
        if e is None or e.shape!=(3,3):raise ValueError('essential seed fails')
        positive,rotation,translation,_=cv2.recoverPose(e,observed[0],observed[camera],k,mask=inliers.copy())
        if positive<.9*int(np.count_nonzero(inliers)):raise ValueError('seed positive support fails')
        poses[camera,:3,:3]=rotation;poses[camera,:3,3]=translation[:,0]
    h=cv2.triangulatePoints(k@poses[0,:3],k@poses[1,:3],observed[0].T,observed[1].T)
    points=(h[:3]/h[3]).T
    rows=np.array([[camera,point,*observed[camera,point]] for camera in range(3) for point in range(len(train))])
    values=np.r_[photo.camera_values(k,poses),points.ravel()]
    def objective(x):
        kk,pp=photo.cameras(x);xx=x[12:].reshape(-1,3)
        if (project(kk,pp,xx,rows)[1]<=1e-9).any():return np.full(2*len(rows),np.inf)
        return photo.linearize(kk,pp,xx,rows,0,1)[0]
    def jacobian(x):
        kk,pp=photo.cameras(x);return photo.linearize(kk,pp,x[12:].reshape(-1,3),rows,0,1)[1]
    np.savez_compressed(OUT/'seed.npz',K=k,poses=poses,points=points,rows=rows,values=values)
    if not np.isfinite(objective(values)).all():raise ValueError('initial geometry invalid')
    lower=np.full(len(values),-np.inf);upper=-lower
    lower[0]=np.log(640.);upper[0]=np.log(5120.)
    result=least_squares(objective,values,jac=jacobian,bounds=(lower,upper),method='trf',loss='soft_l1',f_scale=1.5,
                         x_scale='jac',max_nfev=100,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    k,poses=photo.cameras(result.x);points=result.x[12:].reshape(-1,3)
    np.savez_compressed(OUT/'initial.npz',K=k,poses=poses,points=points,rows=rows)
    write(OUT/'initial.json',{'status':'TECHNICAL_CHECK_PASSED' if result.success else 'REJECT',
        'optimizer_success':bool(result.success),'evaluations':result.nfev,'message':result.message,
        'focal_px':float(k[0,0]),'train_points':len(train),'held_points':len(held)})
    if not result.success or not 640.640<k[0,0]<5114.88 or not np.isfinite(objective(result.x)).all():
        raise ValueError('geometric initializer validity/convergence/nonbound gate fails')


def optimize():
    photo.OUT=OUT
    photo.optimize()


def _score(k,poses,xy,training_points):
    """Each held point is triangulated WITHOUT its scored camera's pixels."""
    k,poses,xy=[np.asarray(value,float) for value in (k,poses,xy)]
    if (k.shape!=(3,3) or poses.shape!=(3,4,4) or xy.ndim!=3 or xy.shape[0]!=3
            or xy.shape[2]!=2 or xy.shape[1]==0 or k[0,0]<=0
            or not all(np.isfinite(value).all() for value in (k,poses,xy))
            or not np.allclose(k,intrinsics(np.log(k[0,0])),atol=1e-10,rtol=0)):
        raise ValueError('finite native square-focal K,three poses and held observations required')
    n=xy.shape[1];arrays={};p95=[];maximum=[];negative=[];positive=True
    proper=bool(np.allclose(poses[:,3,:],[0,0,0,1],atol=1e-10,rtol=0)
        and np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-8,rtol=0)
        and (np.linalg.det(poses[:,:3,:3])>0).all())
    gauge=bool(np.allclose(poses[0],np.eye(4),atol=1e-8,rtol=0)
        and np.isclose(np.linalg.norm(poses[1,:3,3]),1.,atol=1e-8,rtol=0))
    for target,(a,b) in enumerate(((1,2),(0,2),(0,1))):
        h=cv2.triangulatePoints(k@poses[a,:3],k@poses[b,:3],xy[a].T,xy[b].T)
        valid=np.isfinite(h).all(0)&(abs(h[3])>=1e-12)
        points=np.full((n,3),np.nan)
        points[valid]=(h[:3,valid]/h[3,valid]).T
        rows=np.array([[camera,point,0.,0.] for camera in range(3) for point in range(n)])
        uv,depth=project(k,poses,points,rows);uv=uv.reshape(3,n,2)
        positive=bool(positive and valid.all() and np.isfinite(uv).all()
            and np.isfinite(depth).all() and (depth>1e-9).all())
        error=np.linalg.norm(uv[target]-xy[target],axis=1)
        error[~np.isfinite(error)]=np.inf
        p95.append(float(np.percentile(error,95)) if np.isfinite(error).all() else None)
        maximum.append(float(error.max()) if np.isfinite(error).all() else None)
        bad=poses.copy();bad[target,:3,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@bad[target,:3,:3]
        wrong,_=project(k,bad,points,rows)
        displacement=np.linalg.norm(wrong.reshape(3,n,2)[target]-uv[target],axis=1)
        negative.append(float(np.percentile(displacement,95)) if np.isfinite(displacement).all() else None)
        arrays.update({f'target_{target}_stereo':np.array([a,b]),f'target_{target}_points':points,
            f'target_{target}_depths':depth,f'target_{target}_predicted':uv,
            f'target_{target}_errors':error,f'target_{target}_wrong_displacement':displacement})
    points=np.asarray(training_points,float)
    if points.ndim!=2 or points.shape[1]!=3 or len(points)==0 or not np.isfinite(points).all():
        raise ValueError('finite nonempty training points required')
    rows=np.array([[camera,point,0.,0.] for camera in range(3) for point in range(len(points))])
    uv,depth=project(k,poses,points,rows)
    training_positive=bool(np.isfinite(uv).all() and np.isfinite(depth).all() and (depth>1e-9).all())
    arrays.update(training_points=points,training_depths=depth,training_predicted=uv)
    f=float(k[0,0]);nonbound=bool(640.640<f<5114.88)
    passed=bool(n>=9 and proper and gauge and positive and training_positive and nonbound
        and all(value is not None and value<=3 for value in p95)
        and all(value is not None and value>3 for value in negative))
    return {'status':'PARTIAL_SUCCESS' if passed else 'REJECT','held_unique_points':n,
        'held_predictive_p95_px':p95,'held_predictive_max_px':maximum,'focal_px':f,
        'proper':proper,'valid_anchor_baseline_gauges':gauge,'focal_nonbound':nonbound,
        'all_held_depths_positive':positive,'all_training_depths_positive':training_positive,
        'wrong_camera_displacement_p95_px':negative,'true_focal_accuracy':'UNVERIFIED',
        'true_material_precision':'UNVERIFIED','scope':'three whole-point LOO consistency only;not physical camera/head/medical acceptance'},arrays


def evaluate():
    photo.OUT=OUT;photo.read_audit()
    xy,train,held,source_ids=_observations()
    for stage,metadata in (('initialize','initial'),('optimize','direct')):
        worker=json.loads((OUT/(stage+'-worker.json')).read_text())
        detail=json.loads((OUT/(metadata+'.json')).read_text())
        if (worker.get('status')!='TECHNICAL_CHECK_PASSED' or worker.get('exit')!=0
                or detail.get('status')!='TECHNICAL_CHECK_PASSED'
                or detail.get('optimizer_success',True) is not True):
            raise ValueError('both initializer/direct workers must terminate successfully and converge')
    scores={};arrays={'held_observations':xy[:,held],'held_source_ids':source_ids[held],
        'train_source_ids':source_ids[train]}
    for name in ('initial','final'):
        with np.load(OUT/(name+'.npz'),allow_pickle=False) as state:
            k,poses,points=state['K'],state['poses'],state['points']
        if points.shape!=(len(train),3):raise ValueError('full unchanged training population required')
        scores[name],raw=_score(k,poses,xy[:,held],points)
        arrays.update({name+'_'+key:value for key,value in raw.items()})
    scores.update(status=scores['final']['status'],scope='conditional three-view LOO only;no true camera/mm/head acceptance')
    write(OUT/'result.json',scores);np.savez_compressed(OUT/'scores.npz',**arrays)
    if scores['status']!='PARTIAL_SUCCESS':raise ValueError('fixed conditional camera consistency fails')


def check():
    """Owned fixed nonplanar controls;no files,models or private input."""
    k=intrinsics(np.log(1200.));poses=np.repeat(np.eye(4)[None],3,axis=0)
    poses[1,:3,:3]=cv2.Rodrigues(np.array([.04,.07,.01]))[0]
    poses[1,:3,3]=np.array([1.,.02,.01])/np.linalg.norm([1.,.02,.01])
    poses[2,:3,:3]=cv2.Rodrigues(np.array([-.03,-.09,.02]))[0]
    poses[2,:3,3]=[-.6,.2,.1]
    xx,yy=np.meshgrid(np.linspace(-.5,.5,8),np.linspace(-.7,.7,4))
    points=np.c_[xx.ravel(),yy.ravel(),6.+.35*np.sin(np.arange(xx.size))]
    rows=np.array([[camera,point,0.,0.] for camera in range(3) for point in range(len(points))])
    xy,_=project(k,poses,points,rows);xy=xy.reshape(3,len(points),2)
    exact,_=_score(k,poses,xy,points)
    if exact['status']!='PARTIAL_SUCCESS' or max(exact['held_predictive_max_px'])>1e-8:
        raise AssertionError('owned exact LOO control fails')
    if np.linalg.norm(xy-xy,axis=2).max()!=0:raise AssertionError('zero scoring control fails')
    wrong=xy.copy();wrong[0,:,0]+=40
    rejected,_=_score(k,poses,wrong,points)
    if rejected['status']!='REJECT' or rejected['held_predictive_p95_px'][0]<=3:
        raise AssertionError('wrong held camera0 observations evade LOO')
    behind=points.copy();behind[:,2]*=-1
    bad,_=project(k,poses,behind,rows)
    negative,_=_score(k,poses,bad.reshape(3,len(points),2),behind)
    if negative['status']!='REJECT' or negative['all_held_depths_positive']:
        raise AssertionError('negative raw depth evades gate')
    return {'status':'TECHNICAL_CHECK_PASSED','exact_LOO_max_px':max(exact['held_predictive_max_px']),
        'wrong_camera0_p95_px':rejected['held_predictive_p95_px'][0],
        'negative_depth_rejected':True,'scope':'owned camera/checker math only'}
