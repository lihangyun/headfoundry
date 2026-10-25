"""One authorized geometry-only test of the unchanged 0344 observations."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import zipfile

import numpy as np
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/archived-geometry-0352'
ARCHIVE = ROOT / 'assets/private/closed-experiments/0344-aliked/evidence.zip'


def load():
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == '643ef663a951aa6ec6d00e6cc625fba231fb7a12a3d0b13b89b2c5c2cb181fa5'
    with zipfile.ZipFile(ARCHIVE) as z:
        names = [n for n in z.namelist() if n == 'aliked-real-0344/raw-observations.npz']
        assert len(names) == 1, names
        raw = z.read(names[0])
    assert hashlib.sha256(raw).hexdigest() == '7650fc6cbf249a69b4394286309694b2e15417a6b5ff2b61e77709d8770c9e69'
    with np.load(io.BytesIO(raw), allow_pickle=False) as data:
        arrays = {k: data[k] for k in data.files}
    return arrays


def worker():
    data = load()
    ids = np.flatnonzero(data['admitted_all'])
    xy = data['all_xy'][:, ids]
    assert xy.shape == (3, 22, 2) and ids.shape == (22,)
    assert np.isfinite(xy).all() and (xy >= 4).all() and (xy <= [715, 1275]).all()
    assert len(np.unique(ids)) == 22 and np.array_equal(ids, ids.astype(int))
    assert all(len(np.unique(view, axis=0)) == 22 for view in xy)
    ordered = sorted(range(22), key=lambda i: hashlib.sha256(f'331/hold/{i}'.encode()).digest())
    held = np.array(ordered[:9]); train = np.array(sorted(set(range(22))-set(held)))
    # ponytail: reuse the exact archived solver/checker, not its deleted NN stack.
    source = subprocess.check_output(['git', 'show', '412f19c:tools/sparse_camera_0344.py'], cwd=ROOT).decode()
    ns = {'__file__': str(Path(__file__)), '__name__': 'archived_geometry'}
    exec(compile(source, 'git:412f19c:tools/sparse_camera_0344.py', 'exec'), ns)
    ns['OUT'] = OUT
    ns['_observations'] = lambda: (xy, train, held, ids)
    ns['photo'].OUT = OUT
    ns['photo'].read_audit()
    control = ns['check']()
    (OUT/'controls.json').write_text(json.dumps(control, indent=2))
    np.savez_compressed(OUT/'partition.npz', xy=xy, source_ids=ids, train=train, held=held)
    report = {'status': 'REJECT', 'train_count': 13, 'held_count': 9,
              'medical_mm': 'UNVERIFIED', 'head': 'NOT_RUN',
              'solver_source_sha256': hashlib.sha256(source.encode()).hexdigest()}
    try:
        ns['initialize']()
        with np.load(OUT/'initial.npz', allow_pickle=False) as state:
            score, arrays = ns['_score'](state['K'], state['poses'], xy[:, held], state['points'])
        report.update(status=score['status'], score=score)
        np.savez_compressed(OUT/'scores.npz', **arrays)
    except Exception as error:
        report['failure'] = str(error)
        report['traceback'] = traceback.format_exc()
    (OUT/'result.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report['status'] == 'PARTIAL_SUCCESS'


if __name__ == '__main__':
    if sys.argv[1] == 'inspect':
        print(json.dumps({k: {'shape': list(v.shape), 'dtype': str(v.dtype)} for k, v in load().items()}, indent=2))
    elif sys.argv[1] == 'worker':
        sys.exit(0 if worker() else 1)
    else:
        OUT.mkdir(exist_ok=False)
        env = os.environ.copy()
        env.update(OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1')
        print(json.dumps(run([sys.executable, str(Path(__file__)), 'worker'], str(ROOT), env,
              OUT/'worker.log', OUT/'worker.json', 180, 2*1024**3), indent=2))
