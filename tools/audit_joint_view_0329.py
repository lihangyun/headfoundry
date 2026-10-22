"""One bounded read-only view-information audit;never fits cameras or geometry."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import cv2
import numpy as np

from bounded_process import run
from bundle_stationarity import focal_information,linearize as numerical
from native_camera_jacobian import linearize
from short_track_camera import project,write

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/joint-information-0329'
ARCHIVE=ROOT/'assets/private/closed-experiments/0328-shared-focal/evidence.zip'


def worker():
    start=time.monotonic();data=ARCHIVE.read_bytes()
    if hashlib.sha256(data).hexdigest()!='b36d23d6279c073793e74048fa86caaf3359587ef7f407e50d2e0a648598971a':raise ValueError('owned source capsule identity changed')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:raise ValueError('source CRC fails')
        truth=dict(np.load(io.BytesIO(archive.read('truth.npz'))))
    k,points,poses=truth['K'],truth['xyz'].copy(),truth['poses'].copy()
    third=np.eye(4)
    third[:3,:3]=cv2.Rodrigues(np.array([0,np.deg2rad(-18),0]))[0]@cv2.Rodrigues(np.array([np.deg2rad(15),0,0]))[0]
    third[:3,3]=np.array([0,0,3])-third[:3,:3]@np.array([0,0,3])
    length=np.linalg.norm(poses[1,:3,3]);points/=length;poses[:,:3,3]/=length;third[:3,3]/=length
    report={'scope':'read-only exact owned-point local information,not recovered camera/head accuracy','cases':{}}
    arrays={};base_jac=None
    for name,pp in [('two',poses),('repeat',np.concatenate((poses,poses[1:2]))),('joint',np.concatenate((poses,third[None])))]:
        rows=np.array([[camera,point,0,0] for camera in range(len(pp)) for point in range(len(points))],float)
        uv,depth=project(k,pp,points,rows);rows[:,2:]=uv
        if (depth<=0).any() or (uv<0).any() or (uv>[719,1279]).any():raise ValueError('registered native support fails;no pruning')
        residual,jac,replay=linearize(k,pp,points,rows,0,1)
        numeric_residual,finite,numeric_replay,half=numerical(k,pp,points,rows,0,1)
        relative=float(np.linalg.norm(jac-finite)/np.linalg.norm(finite))
        if relative>1e-7 or max(replay,numeric_replay)>1e-9 or np.max(abs(residual-numeric_residual))>1e-9:
            raise ValueError('analytic/numeric derivative/forward control fails')
        info=focal_information(jac);finite_info=focal_information(finite)
        contrast=info['profile_focal_column_norm']/info['raw_focal_column_norm']
        if name in ('two','repeat') and (info['focal_identifiable_locally'] or contrast>1e-10):
            raise ValueError('known critical/null control fails')
        original_error=0.
        if name=='two':base_jac=jac.copy()
        else:
            original_error=float(max(np.max(abs(jac[:len(base_jac),:6]-base_jac[:,:6])),
                                     np.max(abs(jac[:len(base_jac),12:]-base_jac[:,6:])),
                                     np.max(abs(jac[:len(base_jac),6:12]))))
            if original_error!=0:raise ValueError('original columns/observations changed')
        sigma=info['sigma_log_f_per_unit_pixel_noise']
        report['cases'][name]={'analytic_information':info,'finite_difference_information':finite_info,
            'focal_contrast_relative_norm':contrast,'jacobian_relative_difference':relative,
            'forward_replay_max_px':replay,'half_step_witness':half,'original_block_max_difference':original_error,
            'local_sigma_log_f_at_half_pixel':sigma*.5 if sigma is not None and name!='repeat' else None,
            'rows':len(residual),'columns':jac.shape[1]}
        arrays.update({name+'_jacobian':jac,name+'_finite_jacobian':finite,name+'_poses':pp,name+'_rows':rows})
    arrays.update(K=k,points=points,normalizing_baseline_length=length)
    np.savez_compressed(OUT/'arrays.npz',**arrays)
    joint=report['cases']['joint']['analytic_information']
    report.update(status='TECHNICAL_CHECK_PASSED',no_step_applied=True,seconds=time.monotonic()-start,
                  decision='JOINT_LOCAL_FOCAL_CONSTRAINT_EXISTS' if joint['focal_identifiable_locally'] else 'ADDITIONAL_INFORMATION_STILL_REQUIRED')
    write(OUT/'result.json',report)
    summary={name:{'identifiable':row['analytic_information']['focal_identifiable_locally'],
             'rank':row['analytic_information']['rank'],'nuisance_rank':row['analytic_information']['nuisance_rank'],
             'contrast_relative':row['focal_contrast_relative_norm'],'sigma_log_f_half_pixel':row['local_sigma_log_f_at_half_pixel'],
             'derivative_relative':row['jacobian_relative_difference']} for name,row in report['cases'].items()}
    print(json.dumps({'status':report['status'],'decision':report['decision'],'cases':summary,'seconds':report['seconds']},indent=2))


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker()
    else:
        OUT.mkdir(exist_ok=False)
        write(OUT/'entry.json',{'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'analytic_sha256':hashlib.sha256((ROOT/'tools/native_camera_jacobian.py').read_bytes()).hexdigest()})
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
        record=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',120,1024**3)
        print(json.dumps(record,indent=2));sys.exit(0 if record['status']=='TECHNICAL_CHECK_PASSED' else 1)
