"""Once-only authorized 0383 observation replay; no model or medical geometry."""
import ast
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
from scipy.optimize import least_squares
from bounded_process import run
from native_camera_jacobian import linearize
from short_track_camera import intrinsics, project, write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/archive-geometry-0385'
ARCHIVE = ROOT/'assets/private/closed-experiments/0383-roma-video/evidence.zip'
DEADLINE = 1793284115  # 2026-10-29T14:28:35UTC


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load_functions():
    assert sha(ARCHIVE) == '75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266'
    with zipfile.ZipFile(ARCHIVE) as archive:
        source = archive.read('source/roma_video_0383.py')
    assert hashlib.sha256(source).hexdigest() == '837dd7de95f0f60f714275fe59acedd8993c2b0e0793137304b911acdb7bdf1a'
    wanted = {'read_audit', 'camera_values', 'cameras', 'initialize', 'evaluate', 'controls'}
    selected = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in selected} == wanted
    # Exact archived functions only: no module imports, intake, inference or controller.
    exec(compile(ast.Module(body=selected, type_ignores=[]), '0383-frozen-functions', 'exec'), globals())


def prepare():
    if time.time() > DEADLINE:
        raise RuntimeError('whole experiment deadline exceeded')
    load_functions()
    index = json.loads(ARCHIVE.with_name('index.json').read_text())
    protected = dict(index['protected'])
    protected.update({str(ROOT/'tools'/name): sha(ROOT/'tools'/name) for name in
                      ('short_track_camera.py', 'native_camera_jacobian.py', 'bounded_process.py')})
    assert all(sha(path) == digest for path, digest in protected.items())
    OUT.mkdir(exist_ok=False)
    write(OUT/'protected.json', protected)
    with zipfile.ZipFile(ARCHIVE) as archive:
        raw = archive.read('raw-observations.npz')
    assert hashlib.sha256(raw).hexdigest() == 'c9d28a59acbd23eefb68542fca71d4d6a47e18af9fdb217435e31030a130757b'
    data = dict(np.load(io.BytesIO(raw), allow_pickle=False))
    valid = data['admitted_all']
    assert valid.dtype == bool and valid.shape == (108,) and valid.sum() == 37
    assert np.array_equal(valid, data['admitted_1'] & data['admitted_2'])
    xy = np.stack([data['query'], data['forward_1'], data['forward_2']])[:, valid]
    assert xy.shape == (3, 37, 2) and np.isfinite(xy).all()
    order = sorted(range(37), key=lambda i: hashlib.sha256(f'331/hold/{i}'.encode()).digest())
    held = np.array(order[:9]); train = np.array(sorted(set(range(37))-set(held)))
    assert len(train) == 28 and not set(train) & set(held)
    assert set(train) | set(held) == set(range(37))
    source_ids = np.flatnonzero(valid)
    np.savez_compressed(OUT/'observations.npz', xy=xy, train=train, held=held, source_ids=source_ids)
    write(OUT/'split.json', dict(archive_sha256=sha(ARCHIVE), observations_sha256=sha(OUT/'observations.npz'),
          held=held.tolist(), train=train.tolist(), held_source_ids=source_ids[held].tolist(),
          train_source_ids=source_ids[train].tolist(), frozen_utc=time.time()))
    print((OUT/'split.json').read_text())


def diagnostics():
    data = dict(np.load(OUT/'observations.npz', allow_pickle=False))
    xy = data['xy'][:, data['train']]; k = intrinsics(np.log(1280.))
    seeds = {}
    for camera in (1, 2):
        path = OUT/f'seed-{camera}-pose.npz'
        if not path.exists():
            continue
        pose = dict(np.load(path, allow_pickle=False)); r, t = pose['rotation'], pose['translation']
        p0 = np.c_[np.eye(3), np.zeros(3)]; p1 = np.c_[r, t]
        h = cv2.triangulatePoints(k@p0, k@p1, xy[0].T, xy[camera].T)
        points = (h[:3]/h[3]).T; depth = np.c_[points[:, 2], (points@r.T+t[:, 0])[:, 2]]
        center = -r.T@t[:, 0]; a, b = points, points-center
        cosine = np.sum(a*b, axis=1)/(np.linalg.norm(a, axis=1)*np.linalg.norm(b, axis=1))
        parallax = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
        inliers = pose['inliers'].ravel() != 0
        np.savez_compressed(OUT/f'seed-{camera}-diagnostic.npz', points=points, depths=depth, parallax_deg=parallax, inliers=inliers)
        seeds[str(camera)] = dict(inliers=int(inliers.sum()), recover_pose_support=int(pose['positive']),
              finite_points=int(np.isfinite(points).all(1).sum()), all_train_positive_both=int((depth>0).all(1).sum()),
              inlier_positive_both=int(((depth>0).all(1)&inliers).sum()),
              inlier_positive_under50=int(((depth>0).all(1)&(depth<50).all(1)&inliers).sum()),
              median_parallax_deg=float(np.median(parallax)))
    report = {'seeds': seeds, 'rank': 'UNVERIFIED: no optimized state'}
    if (OUT/'initial.npz').exists():
        state = dict(np.load(OUT/'initial.npz', allow_pickle=False))
        residual, jac, _ = linearize(state['K'], state['poses'], state['points'], state['rows'], 0, 1)
        singular = np.linalg.svd(jac, compute_uv=False)
        np.savez_compressed(OUT/'rank-diagnostic.npz', singular=singular, residual=residual)
        report.update(rank=int(np.linalg.matrix_rank(jac)), columns=jac.shape[1], rows=jac.shape[0],
                      train_p95_px=float(np.percentile(np.linalg.norm(residual.reshape(-1, 2), axis=1), 95)))
    write(OUT/'diagnostics.json', report)


def worker():
    load_functions()
    read_audit()
    try:
        controls()
        initialize()
        diagnostics()
        evaluate()
    except Exception as error:
        write(OUT/'failure.json', dict(status='REJECT', error=str(error), error_type=type(error).__name__))
        diagnostics()
        raise


def controller():
    if time.time() > DEADLINE or (OUT/'worker.json').exists():
        raise RuntimeError('expired or already attempted; no replay')
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
    receipt = run([sys.executable, '-B', str(Path(__file__).resolve()), 'worker'], str(ROOT), env,
                  OUT/'worker.log', OUT/'worker.json', min(180, DEADLINE-time.time()), 2*1024**3)
    print(json.dumps(receipt, indent=2))
    if receipt['status'] != 'TECHNICAL_CHECK_PASSED':
        raise SystemExit(1)


def archive_result():
    protected = json.loads((OUT/'protected.json').read_text())
    assert all(sha(path) == digest for path, digest in protected.items())
    assert sha(ARCHIVE) == '75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266'
    receipt = json.loads((OUT/'worker.json').read_text())
    assert receipt['status'] == 'REJECT' and receipt['exit'] == 1
    data = dict(np.load(OUT/'observations.npz')); scores = dict(np.load(OUT/'scores.npz'))
    points = [dict(source_id=int(data['source_ids'][i]), source_xy=data['xy'][0,i].tolist(),
                   error_view1=float(scores['initial_held_error_1'][slot]),
                   error_view2=float(scores['initial_held_error_2'][slot]))
              for slot, i in enumerate(data['held'])]
    write(OUT/'held-details.json', dict(points=points, note='No point removed or rescored'))
    destination = ROOT/'assets/private/closed-experiments/0385-archive-geometry'
    destination.mkdir(exist_ok=False)
    files = sorted(path for path in OUT.rglob('*') if path.is_file())
    members = {path.relative_to(OUT).as_posix():path for path in files}
    members['source/archive_geometry_0385.py'] = Path(__file__)
    target = destination/'evidence.zip'
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, path in members.items():
            archive.write(path, name)
    inventory = {name:dict(bytes=path.stat().st_size, sha256=sha(path)) for name,path in members.items()}
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == row['sha256'] for name,row in inventory.items())
    index = dict(archive_sha256=sha(target), archive_bytes=target.stat().st_size, members=inventory,
                 protected=protected, loose_files=len(files), loose_bytes=sum(p.stat().st_size for p in files),
                 original_archive_sha256=sha(ARCHIVE), result=json.loads((OUT/'result.json').read_text()))
    write(destination/'index.json', index)
    print(json.dumps({k:v for k,v in index.items() if k not in ('members','protected')}, indent=2))


if __name__ == '__main__':
    {'prepare': prepare, 'run': controller, 'worker': worker, 'archive': archive_result}[sys.argv[1]]()
