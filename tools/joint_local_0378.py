"""Bounded archived-track diagnostic; no models, scans or head fitting."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import cv2
import numpy as np
from scipy.optimize import least_squares
from bounded_process import run
from check_dense_grid_contract import bilinear
from headfoundry.manifest import validate_input_assets

OUT = ROOT / 'assets/private/joint-local-0378'
PRIVATE = ROOT / 'assets/private'
ARCHIVE = PRIVATE / 'closed-experiments/0344-aliked/evidence.zip'
PARTITION = PRIVATE / 'archived-geometry-0352/partition.npz'
OFFSETS = np.array([(x, y) for y in range(-4, 5) for x in range(-4, 5)])


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, record):
    with (OUT / name).open('x', encoding='utf8') as stream:
        json.dump(record, stream, indent=2, allow_nan=False)


def patch(image, center):
    values = bilinear(image, center + OFFSETS, [image.shape[1], image.shape[0]])
    values = values - values.mean()
    if not np.isfinite(values).all() or np.std(values) < 1 / 255:
        raise ValueError('flat or nonfinite patch')
    return values / np.linalg.norm(values)


def refine(images, xy):
    # ponytail: translation-only local patches; no untested affine warps/pyramids.
    fixed = patch(images[0], xy[0])
    def residual(delta):
        centers = xy.copy()
        centers[1:] += delta.reshape(2, 2)
        a, b = patch(images[1], centers[1]), patch(images[2], centers[2])
        return np.r_[fixed - a, fixed - b, a - b]
    initial = residual(np.zeros(4))
    result = least_squares(residual, np.zeros(4), bounds=(-4., 4.),
                           method='trf', loss='cauchy', f_scale=.25,
                           max_nfev=100, ftol=1e-8, xtol=1e-8, gtol=1e-8)
    updated = xy.copy()
    updated[1:] += result.x.reshape(2, 2)
    admitted = bool(result.success and np.isfinite(result.fun).all()
                    and np.max(abs(result.x)) < 3.99)
    return updated, dict(status='TECHNICAL_CHECK_PASSED' if admitted else 'REJECT',
        success=bool(result.success), evaluations=result.nfev,
        delta=result.x.tolist(), initial_norm=float(np.linalg.norm(initial)),
        final_norm=float(np.linalg.norm(result.fun)), message=result.message)


def controls():
    yy, xx = np.mgrid[:96, :96]
    shifts = np.array([[0., 0.], [.7, -.4], [-.7, .8]])
    images = []
    for shift, gain, bias in zip(shifts, [1., 1.1, .9], [0., .02, -.02]):
        x, y = xx - shift[0], yy - shift[1]
        images.append(gain * (.45 + .12 * np.sin(.23*x + .1*y)
                      + .15 * np.cos(.11*x - .27*y)) + bias)
    truth = np.array([44., 44.]) + shifts
    seeds = truth + [[0., 0.], [.8, -.7], [-.6, .9]]
    result, detail = refine(np.array(images), seeds)
    error = np.linalg.norm(result - truth, axis=1)
    negatives = []
    for image, center in ((np.ones((96, 96)), [44., 44.]), (images[0], [0., 0.])):
        try:
            patch(image, np.array(center))
        except ValueError:
            negatives.append(True)
        else:
            negatives.append(False)
    record = dict(max_error_px=float(error.max()), negatives=negatives, detail=detail)
    write('controls.json', record)
    if error.max() > .1 or detail['status'] != 'TECHNICAL_CHECK_PASSED' or not all(negatives):
        raise ValueError('owned refinement controls fail')


def intake():
    if sha(ARCHIVE) != '643ef663a951aa6ec6d00e6cc625fba231fb7a12a3d0b13b89b2c5c2cb181fa5':
        raise ValueError('archive identity changed')
    if sha(PARTITION) != 'd0ef30239cfed66ec573dd529ec2037976f71499ae7eed77168855b4ed33f41a':
        raise ValueError('partition identity changed')
    with zipfile.ZipFile(ARCHIVE) as archive:
        lock = json.loads(archive.read('aliked-real-0344/inputs.json'))
    manifest = PRIVATE / 'real-capture-pilot-v1/manifest.json'
    consent = manifest.parent / 'provenance-confirmation.json'
    ledger_path = PRIVATE / 'video-observability-0252/report.json'
    for path, key in ((manifest, 'manifest_sha256'), (consent, 'consent_sha256'),
                      (ledger_path, 'ledger_sha256')):
        if sha(path) != lock[key]:
            raise ValueError('intake metadata changed')
    doc = json.loads(manifest.read_text())
    records = [r for r in doc['inputs'] if r['id'] == 'real-case-001-video']
    if (len(records) != 1 or doc.get('training_allowed') is not False
            or doc.get('upload_allowed') is not False
            or doc.get('purpose') != 'local_head_reconstruction_validation'
            or validate_input_assets(dict(doc, inputs=records), manifest.parent)):
        raise ValueError('local video rights fail')
    source = Path(records[0]['path'])
    if sha(source) != lock['source_sha256']:
        raise ValueError('video changed')
    ledger = json.loads(ledger_path.read_text())
    capture = cv2.VideoCapture(str(source))
    images = []; count = 0
    try:
        while True:
            ok, bgr = capture.read()
            if not ok:
                break
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            digest = hashlib.sha256(rgb.tobytes()).hexdigest()
            if count >= len(ledger['frame_records']) or digest != ledger['frame_records'][count]['rgb_sha256']:
                raise ValueError('sequential RGB changed')
            if count in (240, 300, 630):
                if digest != lock['rgb_sha256'][str(count)]:
                    raise ValueError('selected RGB identity fails')
                images.append(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(float) / 255)
            count += 1
    finally:
        capture.release()
    if count != 1041 or len(images) != 3:
        raise ValueError('incomplete input')
    with np.load(PARTITION, allow_pickle=False) as partition:
        data = dict(partition)
    if data['xy'].shape != (3, 22, 2) or len(data['train']) != 13 or len(data['held']) != 9:
        raise ValueError('fixed partition shape differs')
    if not np.array_equal(np.sort(np.r_[data['train'], data['held']]), np.arange(22)):
        raise ValueError('partition overlap/missing identities')
    write('inputs.json', dict(lock, partition_sha256=sha(PARTITION), frames_reverified=count))
    return np.array(images), data


def worker():
    cv2.setNumThreads(1)
    controls()
    images, data = intake()
    # All authorized input is resident; no further private input/network permitted.
    def guard(event, args):
        if event.startswith(('socket.', 'subprocess.', 'os.system')):
            raise PermissionError('offline numerical worker')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if path.suffix.lower() == '.stl' or (path.is_relative_to(PRIVATE) and not path.is_relative_to(OUT)):
                raise PermissionError('unrelated private reads denied')
    sys.addaudithook(guard)
    updated = data['xy'].copy(); details = []
    for index in data['train']:
        try:
            points, detail = refine(images, data['xy'][:, index])
            updated[:, index] = points
        except ValueError as error:
            detail = dict(status='REJECT', reason=str(error))
        details.append(dict(index=int(index), source_id=int(data['source_ids'][index]), **detail))
    np.savez_compressed(OUT / 'refined.npz', **dict(data, xy=updated, original_xy=data['xy']))
    assert np.array_equal(updated[:, data['held']], data['xy'][:, data['held']])
    assert np.array_equal(updated[0], data['xy'][0])
    write('refinement.json', dict(points=details, held_unchanged=True, root_unchanged=True))
    if any(d['status'] != 'TECHNICAL_CHECK_PASSED' for d in details):
        write('result.json', dict(status='REJECT', stage='local_refinement',
              rejected_count=sum(d['status'] == 'REJECT' for d in details),
              scope='no camera/geometry/medical accuracy measured'))
        return
    k = np.array([[1280., 0, 360], [0, 1280., 640], [0, 0, 1]])
    observed = updated[:, data['train']]; seeds = []; arrays = {}
    cv2.setRNGSeed(331)
    for camera in (1, 2):
        e, mask = cv2.findEssentialMat(observed[0], observed[camera], k,
            method=cv2.RANSAC, prob=.999, threshold=1.5)
        if e is None or e.shape != (3, 3):
            seeds.append(dict(camera=camera, status='REJECT', reason='essential shape'))
            break
        positive, rotation, translation, returned = cv2.recoverPose(
            e, observed[0], observed[camera], k, mask=mask.copy())
        count = int(np.count_nonzero(mask))
        passed = count > 0 and positive >= .9 * count
        seeds.append(dict(camera=camera, status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
                          essential_support=count, combined_support=int(positive)))
        arrays.update({f'{camera}_E': e, f'{camera}_mask': mask, f'{camera}_returned': returned,
                       f'{camera}_R': rotation, f'{camera}_t': translation})
        if not passed:
            break
    np.savez_compressed(OUT / 'seeds.npz', **arrays)
    write('result.json', dict(status='TECHNICAL_CHECK_PASSED' if len(seeds) == 2
        and all(s['status'] == 'TECHNICAL_CHECK_PASSED' for s in seeds) else 'REJECT',
        stage='seed_support', seeds=seeds, scope='no optimized camera/head/medical accuracy'))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'worker':
        worker()
    else:
        OUT.mkdir(exist_ok=False)
        write('entry.json', dict(source_sha256=sha(Path(__file__)), started=time.time()))
        env = os.environ.copy()
        env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        receipt = run([sys.executable, '-B', str(Path(__file__)), 'worker'], str(ROOT), env,
                      OUT / 'worker.log', OUT / 'worker.json', 180, 2 * 1024**3)
        print(json.dumps(receipt, indent=2))
