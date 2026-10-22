"""One procedural-only observation-noise audit;not a new camera implementation."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/camera-noise-audit-0310'

def write(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False))

def worker():
    import cv2
    import numpy as np
    from check_cycle_camera_contract import control_data
    from check_global_geometry_contract import similarity
    from cycle_consensus import select_tracks
    from short_track_camera import fit,project,split_observations
    started=time.monotonic()
    data,truth=control_data()
    vertices=sorted(data['xy'])
    clean=np.stack([data['xy'][v] for v in vertices])
    noise=np.random.default_rng(310).normal(0,.5,clean.shape)
    noisy=clean+noise
    data['xy']={v:xy for v,xy in zip(vertices,noisy)}
    tracks,graph=select_tracks(data['edges'])
    train,held=split_observations(data,tracks)
    clean_lookup={v:xy for v,xy in zip(vertices,clean)}
    labels=np.array([truth['labels'][t[0]] for t in tracks])
    purity=float(np.mean([len({truth['labels'][v] for v in t})==1 for t in tracks]))
    recall=len(set(labels.tolist()))/len(truth['points'])
    np.savez_compressed(OUT/'frozen-input.npz',vertices=vertices,clean=clean,noisy=noisy,noise=noise,
                        edges=np.asarray(sorted(data['edges'])),tracks=np.asarray(tracks),train=train,held=held,
                        labels=labels,truth_points=truth['points'],truth_centers=truth['centers'],
                        truth_poses=truth['poses'],truth_K=truth['K'])
    write('entry.json',dict(selected=len(tracks),purity=purity,recall=recall,
          noise_sigma=.5,noise_seed=310,noise_radius_p95=float(np.percentile(np.linalg.norm(noise,axis=1),95)),
          graph=graph))
    assert purity>=.99 and recall>=.4
    try:
        k,poses,points,actual_train,actual_held,metrics=fit(data,tracks,OUT/'camera')
        assert np.array_equal(train,actual_train) and np.array_equal(held,actual_held)
        centers=np.stack([-p[:3,:3].T@p[:3,3] for p in poses])
        scale,rotation,translation=similarity(centers[[0,2,4]],truth['centers'][[0,2,4]])
        center_error=np.linalg.norm(scale*centers@rotation.T+translation-truth['centers'],axis=1)
        point_error=np.linalg.norm(scale*points@rotation.T+translation-truth['points'][labels],axis=1)
        target=(truth['points'][labels]-translation)@rotation/scale
        clean_held=[]
        for row in held:
            track=tracks[int(row[1])]
            vertex=next(v for v in track if v[0]==data['frames'][int(row[0])])
            clean_held.append(clean_lookup[vertex])
        clean_held=np.asarray(clean_held)
        projected,depth=project(k,poses,target,held)
        error=np.linalg.norm(projected-clean_held,axis=1)
        wrong=poses.copy()
        wrong[0,:3]=cv2.Rodrigues(np.array([.1,0,0]))[0]@wrong[0,:3]
        mask=held[:,0]==0
        bad,_=project(k,wrong,target,held[mask])
        negative=np.linalg.norm(bad-clean_held[mask],axis=1)
        result=dict(focal_relative_error=float(abs(k[0,0]/1200-1)),center_max=float(center_error.max()),
                    point_p95=float(np.percentile(point_error,95)),noise_free_truth_held_p95=float(np.percentile(error,95)),
                    noisy_held_p95=metrics['held_p95_px'],wrong_camera_p95=float(np.percentile(negative,95)),
                    proper=metrics['proper_cameras'],positive=bool((depth>0).all()),camera_status=metrics['status'])
        passed=(metrics['status']=='TECHNICAL_CHECK_PASSED' and result['focal_relative_error']<=.02
                and result['center_max']<=.01 and result['point_p95']<=.01
                and result['noise_free_truth_held_p95']<=1 and result['wrong_camera_p95']>3 and result['positive'])
        result['status']='TECHNICAL_CHECK_PASSED' if passed else 'REJECT'
        np.savez_compressed(OUT/'physical-scores.npz',center_error=center_error,point_error=point_error,
                            noise_free_truth_error=error,clean_held=clean_held,negative_error=negative)
    except Exception as error:
        result=dict(status='REJECT',stage='camera_fit',error=type(error).__name__+':'+str(error),
                    full_solution=False)
    result.update(seconds=time.monotonic()-started,scope='one procedural noise condition;not a patient/head/mm result')
    write('result.json',result)
    print(json.dumps(result))
    return 0

if __name__=='__main__':
    if sys.argv[1:] == ['worker']:
        sys.exit(worker())
    from bounded_process import run
    OUT.mkdir(exist_ok=False)
    env=os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        env[name]='4'
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
        Path(__file__),ROOT/'tools/short_track_camera.py',ROOT/'tools/check_cycle_camera_contract.py',
        ROOT/'tools/check_global_geometry_contract.py',ROOT/'tools/cycle_consensus.py']}
    write('source-hashes.json',hashes)
    record=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',
               OUT/'worker.json',180,1024**3)
    for name,expected in hashes.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    print(json.dumps(record))
