"""Authorized one-shot seed replay; no optimization or threshold rescue."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile
import cv2
import numpy as np
from bounded_process import run
from short_track_camera import intrinsics
import dense_photo_0332 as photo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/pose-diagnostic-0354'


def worker():
    archive = ROOT/'assets/private/closed-experiments/0344-aliked/evidence.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == '643ef663a951aa6ec6d00e6cc625fba231fb7a12a3d0b13b89b2c5c2cb181fa5'
    with zipfile.ZipFile(archive) as z:
        raw = z.read('aliked-real-0344/raw-observations.npz')
    assert hashlib.sha256(raw).hexdigest() == '7650fc6cbf249a69b4394286309694b2e15417a6b5ff2b61e77709d8770c9e69'
    with np.load(io.BytesIO(raw), allow_pickle=False) as d:
        ids = np.flatnonzero(d['admitted_all']); xy = d['all_xy'][:, ids]
    with np.load(ROOT/'assets/private/archived-geometry-0352/partition.npz', allow_pickle=False) as d:
        train, held = d['train'].copy(), d['held'].copy()
        assert np.array_equal(ids, d['source_ids']) and np.array_equal(xy, d['xy'])
    assert xy.shape == (3,22,2) and len(train) == 13 and len(held) == 9
    photo.OUT = OUT; photo.read_audit()
    cv2.setNumThreads(4); cv2.setRNGSeed(331)
    k = intrinsics(np.log(1280.)); observed = xy[:, train]
    report = {'status': 'TECHNICAL_CHECK_PASSED', 'reconstruction_status': 'REJECT',
              'opencv': cv2.__version__, 'pairs': [], 'scope': 'seed diagnostic only'}
    arrays = {'K': k, 'xy': xy, 'train': train, 'held': held, 'source_ids': ids}
    for camera in (1,2):
        e, mask = cv2.findEssentialMat(observed[0], observed[camera], k, method=cv2.RANSAC, prob=.999, threshold=1.5)
        assert e is not None and e.shape == (3,3)
        count, rotation, translation, accepted = cv2.recoverPose(e, observed[0], observed[camera], k, mask=mask.copy())
        r1, r2, t = cv2.decomposeEssentialMat(e)
        candidates = []
        for j,(r,tt) in enumerate(((r1,t),(r2,t),(r1,-t),(r2,-t))):
            p = np.c_[r,tt]; p0 = np.c_[np.eye(3),np.zeros(3)]
            h = cv2.triangulatePoints(k@p0,k@p,observed[0].T,observed[camera].T)
            with np.errstate(divide='ignore',invalid='ignore'):
                points = (h[:3]/h[3]).T
            depth = np.c_[points[:,2], (points@r.T+tt[:,0])[:,2]]
            finite = np.isfinite(points).all(1)
            positive = finite & (depth>0).all(1)
            near = positive & (depth<50).all(1)
            inlier = mask.ravel()!=0
            candidates.append({'candidate':j, 'positive_inliers':int((positive&inlier).sum()),
                'near_positive_inliers':int((near&inlier).sum()),
                'far_positive_inliers':int((positive&~near&inlier).sum())})
            arrays[f'pair{camera}_candidate{j}_depth'] = depth
            arrays[f'pair{camera}_candidate{j}_points'] = points
        selected = [j for j,(r,tt) in enumerate(((r1,t),(r2,t),(r1,-t),(r2,-t)))
                    if np.allclose(r,rotation,atol=1e-10) and np.allclose(tt,translation,atol=1e-10)]
        assert len(selected)==1
        assert candidates[selected[0]]['near_positive_inliers']==count
        arrays.update({f'pair{camera}_E':e, f'pair{camera}_inlier_mask':mask,
                       f'pair{camera}_accepted_mask':accepted, f'pair{camera}_R':rotation,
                       f'pair{camera}_t':translation})
        item = {'camera':camera,'essential_inliers':int(np.count_nonzero(mask)),
                'recoverPose_support':int(count),'selected_candidate':selected[0], 'candidates':candidates}
        report['pairs'].append(item)
        if count < .9*np.count_nonzero(mask):
            report['stop'] = 'same original seed support failure'
            break
    np.savez_compressed(OUT/'diagnostic.npz',**arrays)
    (OUT/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if sys.argv[-1]=='worker': worker()
    else:
        OUT.mkdir(exist_ok=False)
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
        print(json.dumps(run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,
              OUT/'worker.log',OUT/'worker.json',180,2*1024**3),indent=2))
