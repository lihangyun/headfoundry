"""Procedural frozen truth information only;no estimator/model/private human inputs."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/focal-information-0311'
ARCHIVE=ROOT/'assets/private/closed-experiments/0310-camera-noise-control/evidence.zip'

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def worker():
    import numpy as np
    from bundle_stationarity import audit,linearize,focal_information
    from short_track_camera import project
    start=time.monotonic()
    # Replay old/new diagnostics on the existing public8point fixture only.
    old_source=subprocess.check_output(['git','show','9e579e6:tools/bundle_stationarity.py'],cwd=ROOT,text=True)
    old={}
    exec(compile(old_source,'historical-owned-bundle-audit','exec'),old)
    control_k=np.array([[1200.,0,359.5],[0,1200.,639.5],[0,0,1.]])
    control_poses=np.repeat(np.eye(4)[None],3,axis=0)
    control_poses[1,:3,3]=[1,0,0]
    control_poses[2,:3,3]=[0,1,.2]
    control_points=np.random.default_rng(305).uniform([-1,-1,3],[1,1,6],(8,3))
    control_rows=np.array([[c,p,0,0] for c in range(3) for p in range(8)],dtype=float)
    control_rows[:,2:]=project(control_k,control_poses,control_points,control_rows)[0]
    prior=old['audit'](control_k,control_poses,control_points,control_rows,0,1)
    current=audit(control_k,control_poses,control_points,control_rows,0,1)
    assert prior==current,'refactor changed original audit outputs'
    write('backwards-replay.json',dict(equal_all_fields=True,source_ref='9e579e6',result=current))
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()=='02904964cc00551dd15ee1a44cf28e6388508afdb5c89fd08575c1389399352b'
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        data=np.load(io.BytesIO(z.read('assets/private/camera-noise-audit-0310/frozen-input.npz')))
        truth={key:data[key].copy() for key in data.files}
    original_k=truth['truth_K'].copy()
    original_k[:2,2]-=.5
    original_poses=truth['truth_poses']
    length=np.linalg.norm(truth['truth_centers'][3]-truth['truth_centers'][2])
    origin_rotation=original_poses[2,:,:3]
    origin_translation=original_poses[2,:,3]
    poses=np.repeat(np.eye(4)[None],5,axis=0)
    for camera in range(5):
        poses[camera,:3,:3]=original_poses[camera,:,:3]@origin_rotation.T
        poses[camera,:3,3]=(original_poses[camera,:,3]-poses[camera,:3,:3]@origin_translation)/length
    # Remove floating-point roundoff from the explicitly fixed gauge,not observations.
    assert np.max(np.abs(poses[2]-np.eye(4)))<1e-12
    poses[2]=np.eye(4)
    assert abs(np.linalg.norm(poses[3,:3,3])-1)<1e-12
    points=(truth['truth_points'][truth['labels']]@origin_rotation.T+origin_translation)/length
    clean_lookup={tuple(v):xy for v,xy in zip(truth['vertices'],truth['clean'])}
    train=truth['train'].copy()
    for row in train:
        track=truth['tracks'][int(row[1])]
        vertex=track[track[:,0]==int(row[0])]
        assert len(vertex)==1
        row[2:]=clean_lookup[tuple(vertex[0])]
    residual,jac,replay,witness=linearize(original_k,poses,points,train,2,3)
    assert np.max(np.abs(residual))<1e-8,'truth/native/gauge clean replay mismatch'
    information=focal_information(jac)
    unit=information['sigma_log_f_per_unit_pixel_noise']
    sigma=None if unit is None else .5*unit
    information.update(sigma_pixels_per_axis=.5,sigma_log_f=sigma,
        approximate_relative_sigma=sigma,illustrative_1_96_sigma=None if sigma is None else 1.96*sigma,
        rows=len(residual),variables=jac.shape[1],truth_replay_max_px=float(np.max(np.abs(residual))),
        forward_replay_max_px=replay,jacobian_half_step_relative_error=witness,
        next_evidence_priority='ADDITIONAL_INFORMATION_FIRST' if sigma is None or sigma>=.02 else 'OPTIMIZER_DIAGNOSIS_FIRST',
        status='TECHNICAL_CHECK_PASSED',scope='local Gaussian procedural information only;not achieved precision/patient/mm',
        no_fit_or_step=True,seconds=time.monotonic()-start)
    np.savez_compressed(OUT/'linearization.npz',J=jac,residual=residual,K=original_k,poses=poses,
                        points=points,clean_train=train)
    write('information.json',information)
    print(json.dumps({k:information[k] for k in ['focal_identifiable_locally','sigma_log_f',
          'illustrative_1_96_sigma','truth_replay_max_px','next_evidence_priority','seconds']}))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        env=os.environ.copy()
        for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            env[name]='4'
        hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            Path(__file__),ROOT/'tools/bundle_stationarity.py',ROOT/'tests/test_bundle_stationarity.py',
            ROOT/'tools/short_track_camera.py',ARCHIVE]}
        write('source-hashes.json',hashes)
        result=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',
                   OUT/'worker.json',120,1024**3)
        for name,expected in hashes.items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
        print(json.dumps(result))
