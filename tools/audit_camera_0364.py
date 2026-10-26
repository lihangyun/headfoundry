"""Read archived camera evidence; never refit or run a model."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np
from dense_photo_0332 import intersect
from short_track_camera import project

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/camera-audit-0364'


def main():
    OUT.mkdir(exist_ok=False)
    archive=ROOT/'assets/private/cleanup-0363/evidence.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6cf96bb8745147d930925fa1c163986ecde35df21b7b8e0c11dc5b88a90c4043'
    prefix='assets/private/trackon-camera-0363/'
    with zipfile.ZipFile(archive) as z:
        obs=dict(np.load(io.BytesIO(z.read(prefix+'observations.npz'))))
        state=dict(np.load(io.BytesIO(z.read(prefix+'solution.npz'))))
        original=json.loads(z.read(prefix+'result.json'))
        source=json.loads(z.read(prefix+'source.json'))
    prediction_path=ROOT/'assets/private/trackon-motion-0362/predictions.npz'
    assert hashlib.sha256(prediction_path.read_bytes()).hexdigest()==source['sha256']
    prediction=np.load(prediction_path)
    assert np.array_equal(obs['xy'],prediction['predictions'][[0,6,12]][:,obs['source_ids']])
    fixture=ROOT/'assets/private/dense-photo-0332'
    metadata=json.loads((fixture/'inputs.json').read_text())
    assert hashlib.sha256((fixture/'truth.npz').read_bytes()).hexdigest()==metadata['truth_sha256']
    truth=dict(np.load(fixture/'truth.npz'))
    query=np.load(fixture/'raw-endpoints.npz')['query'][obs['source_ids']]
    xyz,labels=intersect(truth['poses'][0],query,truth['rectangles'],truth['K'])
    misses=[]
    for c,p in enumerate(truth['poses']):
        local=xyz@p[:3,:3].T+p[:3,3]
        uv=local[:,:2]/local[:,2,None]*truth['K'][0,0]+truth['K'][:2,2]
        hit,target=intersect(p,uv,truth['rectangles'],truth['K'])
        bad=(target!=labels)|(~np.isfinite(hit).all(1))|(np.linalg.norm(hit-xyz,axis=1)>1e-6)
        for i in np.flatnonzero(bad):
            misses.append(dict(view=c,source_id=int(obs['source_ids'][i]),held=bool(i in obs['held']),
                               predicted_visibility=float(prediction['visibility'][[0,6,12][c],obs['source_ids'][i]])))
    baseline=float(truth['baseline']); xyz/=baseline
    poses=truth['poses'].copy();poses[:,:3,3]/=baseline
    assert np.array_equal(poses[0],np.eye(4)) and np.array_equal(state['poses'][0],np.eye(4))
    assert abs(np.linalg.norm(poses[1,:3,3])-1)<1e-12
    assert abs(np.linalg.norm(state['poses'][1,:3,3])-1)<1e-12
    held=obs['held'];train=obs['train']
    rows=np.array([[c,i,0,0] for c in range(3) for i in range(len(held))])
    correct,_=project(truth['K'],poses,xyz[held],rows)
    estimated,_=project(state['K'],state['poses'],xyz[held],rows)
    p95=np.percentile(np.linalg.norm(estimated-correct,axis=1).reshape(3,-1),95,axis=1)
    assert np.allclose(p95,original['held_known3D_p95_px'],atol=1e-10,rtol=0)
    # Identity camera: focal discrepancy alone predicts this pixel displacement.
    focal_only=np.linalg.norm(query[held]-truth['K'][:2,2],axis=1)*abs(state['K'][0,0]/truth['K'][0,0]-1)
    assert abs(np.percentile(focal_only,95)-p95[0])<1e-10
    tr=np.array([[c,i,0,0] for c in range(3) for i in range(len(train))])
    train_uv,_=project(state['K'],state['poses'],state['points'],tr)
    residual=np.linalg.norm(train_uv.reshape(3,-1,2)-obs['xy'][:,train],axis=2)
    exact,_=project(truth['K'],poses,xyz[held],rows)
    assert np.max(abs(exact-correct))==0
    result=dict(status='TECHNICAL_CHECK_PASSED',quality_decision_unchanged='REJECT',
        scope='evidence identity and arithmetic audit only; no fit or patient inference',
        admitted=len(obs['source_ids']),train=len(train),held=len(held),
        known_p95_px=p95.tolist(),first_view_focal_only_p95_px=float(np.percentile(focal_only,95)),
        training_reprojection_p95_px=np.percentile(residual,95,axis=1).tolist(),
        occluded_observations=misses,exact_camera_zero_px=float(np.max(abs(exact-correct))))
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
