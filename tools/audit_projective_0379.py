"""Read-only fixed observation diagnostic; no physical camera acceptance."""
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
from headfoundry.epipolar import fundamental, sampson_distance
from bounded_process import run

PRIVATE = ROOT / 'assets/private'
OUT = PRIVATE / 'closed-experiments/0379-projective-screen'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def controls():
    rng = np.random.default_rng(379)
    points = rng.uniform([-1., -1., 4.], [1., 1., 8.], (32, 3))
    angle = .2
    r = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0],
                  [-np.sin(angle), 0, np.cos(angle)]])
    second = points @ r.T + [.7, .1, .2]
    a = points[:, :2] / points[:, 2:] * 1200 + [360, 640]
    b = second[:, :2] / second[:, 2:] * 1200 + [360, 640]
    f = fundamental(a[:23], b[:23])
    lines = np.c_[a[23:], np.ones(9)] @ f.T
    normals = lines[:, :2] / np.linalg.norm(lines[:, :2], axis=1)[:, None]
    along = np.c_[-normals[:, 1], normals[:, 0]]
    values = [float(np.percentile(sampson_distance(f, a[23:], target), 95))
              for target in (b[23:], b[23:] + 40*normals, b[23:] + 40*along)]
    if values[0] >= 1e-6 or values[1] <= 3 or values[2] >= 1e-6:
        raise AssertionError('independent epipolar controls fail')
    return dict(exact_p95_px=values[0], perpendicular40_p95_px=values[1],
                along40_p95_px=values[2])


def worker():
    check = controls()
    archive = PRIVATE / 'closed-experiments/0378-joint-local/evidence.zip'
    partition = PRIVATE / 'archived-geometry-0352/partition.npz'
    if sha(archive) != 'dceeebf1d03e748eb0e96276aa7eb34a1a6a50266d897697d26aaa5ecb10f203':
        raise ValueError('archive changed')
    if sha(partition) != 'd0ef30239cfed66ec573dd529ec2037976f71499ae7eed77168855b4ed33f41a':
        raise ValueError('partition changed')
    with zipfile.ZipFile(archive) as z:
        lock = json.loads(z.read('inputs.json'))
    manifest = PRIVATE / 'real-capture-pilot-v1/manifest.json'
    consent = manifest.parent / 'provenance-confirmation.json'
    if sha(manifest) != lock['manifest_sha256'] or sha(consent) != lock['consent_sha256']:
        raise ValueError('rights changed')
    with np.load(partition, allow_pickle=False) as record:
        xy, train, held, ids = (record[k] for k in ('xy', 'train', 'held', 'source_ids'))
    assert xy.shape == (3, 22, 2) and len(train) == 13 and len(held) == 9
    assert np.array_equal(np.sort(np.r_[train, held]), np.arange(22))
    before = {str(p):sha(p) for p in (archive, partition, manifest, consent,
              ROOT/'docs/experiment-0207-coupled-lip-and-jaw.md',
              ROOT/'src/headfoundry/epipolar.py')}
    results = []
    for a, b in ((0, 1), (0, 2), (1, 2)):
        entry = dict(pair=[a, b], native_ordinals=[[240, 300, 630][i] for i in (a, b)])
        try:
            f = fundamental(xy[a, train], xy[b, train])
            errors = sampson_distance(f, xy[a], xy[b])
            p95 = float(np.percentile(errors[held], 95))
            entry.update(F=f.tolist(), singular_values=np.linalg.svd(f)[1].tolist(),
                all_residuals_px=errors.tolist(), train_p95_px=float(np.percentile(errors[train], 95)),
                held_p95_px=p95, held_max_px=float(errors[held].max()),
                status='TECHNICAL_CHECK_PASSED' if p95 <= 3 else 'REJECT')
        except (ValueError, np.linalg.LinAlgError) as error:
            entry.update(status='REJECT', reason=str(error))
        entry['train_spans_xy'] = [np.ptp(xy[i, train], axis=0).tolist() for i in (a, b)]
        entry['held_spans_xy'] = [np.ptp(xy[i, held], axis=0).tolist() for i in (a, b)]
        results.append(entry)
    assert all(sha(Path(p)) == digest for p, digest in before.items())
    result = dict(controls=check, pairs=results, source_ids=ids.tolist(),
        train=train.tolist(), held=held.tolist(), protected_sha256=before,
        source_sha256=sha(Path(__file__)),
        status='TECHNICAL_CHECK_PASSED' if all(r['status']=='TECHNICAL_CHECK_PASSED' for r in results) else 'REJECT',
        scope='uncalibrated epipolar screen only; physical identity/camera/head accuracy UNVERIFIED')
    with (OUT/'result.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(dict(status=result['status'], controls=check,
                         pairs=[{k:v for k,v in p.items() if k in ('pair','held_p95_px','train_p95_px','status')} for p in results]), indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'worker':
        worker()
    else:
        OUT.mkdir(exist_ok=False)
        env = os.environ.copy()
        env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        receipt = run([sys.executable, '-B', str(Path(__file__)), 'worker'], str(ROOT),
                      env, OUT/'worker.log', OUT/'worker.json', 60, 1024**3)
        print(json.dumps(receipt, indent=2))
