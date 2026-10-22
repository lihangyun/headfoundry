"""Additional procedural observation geometry only;no fit or human data."""
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

from headfoundry.manifest import sha256_file
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/cross-axis-information-0318'
ARCHIVE=ROOT/'assets/private/closed-experiments/0311-focal-information/evidence.zip'

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def worker():
    import numpy as np
    from bundle_stationarity import focal_information,linearize
    from short_track_camera import project
    start=time.monotonic()
    assert sha256_file(ARCHIVE)=='204b58525e91a8a2c50c7b5520615633417ac3d43f369e0480a2cd7f21b5d8ac'
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        member=next(n for n in z.namelist() if n.endswith('/linearization.npz'))
        with np.load(io.BytesIO(z.read(member)),allow_pickle=False) as raw:
            saved={name:raw[name].copy() for name in raw.files}
    k,poses,points,train=saved['K'],saved['poses'],saved['points'],saved['clean_train']
    assert len(points)==141 and len(poses)==5
    baseline=focal_information(saved['J'])
    sigma=.5*baseline['sigma_log_f_per_unit_pixel_noise']
    assert abs(sigma-.07601826448441787)<1e-8
    duplicate=focal_information(np.vstack([saved['J'],saved['J']]))
    assert abs(duplicate['sigma_log_f_per_unit_pixel_noise']-baseline['sigma_log_f_per_unit_pixel_noise']/np.sqrt(2))<1e-7
    result={'baseline_sigma_log_f':sigma,'equal_information_budget_new_rows':141,'variants':{},'no_fit_or_step':True}
    centroid=points.mean(0)
    theta=np.deg2rad(20.);c,s=np.cos(theta),np.sin(theta)
    pitch=np.array([[1,0,0],[0,c,-s],[0,s,c]])
    old_offset=saved['J'].shape[1]-3*len(points)
    expected_original=np.column_stack([saved['J'][:,:old_offset],np.zeros((len(saved['J']),6)),saved['J'][:,old_offset:]])
    for name,rotation in [('repeat',np.eye(3)),('pitch20',pitch)]:
        added=np.eye(4);added[:3,:3]=rotation;added[:3,3]=centroid-rotation@centroid
        current=np.concatenate([poses,added[None]])
        rows=np.array([[5,p,0.,0.] for p in range(len(points))])
        uv,depth=project(k,current,points,rows)
        assert np.all(depth>0) and np.all((uv>=0)&(uv<np.array([720,1280])))
        assert np.max(abs(rotation@rotation.T-np.eye(3)))<1e-12 and np.linalg.det(rotation)>.999999999
        rows[:,2:]=uv;augmented=np.vstack([train,rows])
        residual,jac,replay,witness=linearize(k,current,points,augmented,2,3)
        assert np.max(abs(residual))<1e-8
        unchanged=float(np.max(abs(jac[:len(saved['J'])]-expected_original)))
        assert unchanged<1e-8,'original Jacobian changed beyond appended nuisance columns'
        info=focal_information(jac)
        unit=info['sigma_log_f_per_unit_pixel_noise']
        info.update(sigma_log_f=None if unit is None else .5*unit,forward_replay_max_px=replay,
                    truth_replay_max_px=float(np.max(abs(residual))),jacobian_half_step_relative_error=witness,
                    original_jacobian_max_difference=unchanged,rows=jac.shape[0],variables=jac.shape[1])
        result['variants'][name]=info
        np.savez_compressed(OUT/f'{name}-linearization.npz',J=jac,residual=residual,K=k,poses=current,points=points,clean_train=augmented)
    pitched=result['variants']['pitch20']['sigma_log_f'];repeated=result['variants']['repeat']['sigma_log_f']
    favorable=pitched is not None and pitched<.02 and (repeated is None or pitched<repeated)
    result.update(status='TECHNICAL_CHECK_PASSED',scope='local Gaussian procedural design only;not camera/head precision',
        next_action='SEPARATE_NOISY_CAPACITY_TEST_JUSTIFIED' if favorable else 'ADDITIONAL_INFORMATION_STILL_REQUIRED',
        seconds=time.monotonic()-start,actual_camera_or_head_accuracy='UNVERIFIED')
    write('result.json',result)
    print(json.dumps(dict(baseline=sigma,repeat=repeated,pitch20=pitched,next_action=result['next_action'],seconds=result['seconds'])))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:worker()
    else:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
        for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[name]='4'
        paths=[Path(__file__),ROOT/'tools/bundle_stationarity.py',ROOT/'tools/short_track_camera.py',ARCHIVE]
        hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in paths};write('source-hashes.json',hashes)
        record=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',120,1024**3)
        for name,digest in hashes.items():assert sha256_file(ROOT/name)==digest,name
        print(json.dumps(record))
