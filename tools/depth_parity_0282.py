"""Bounded video-only factorization initializer; never an accepted head."""
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import zipfile

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from headfoundry.manifest import validate_input_assets

OUT = ROOT / 'assets/private/depth-parity-0282'
REPORT = {'status': 'REJECT', 'head': 'UNVERIFIED', 'surface_mm': None}


def factorize(y, mask):
    v, n = mask.shape
    if np.any(mask.sum(0) < 3) or np.any(mask.sum(1) < 6):
        raise ValueError('insufficient training support')
    t = np.array([y[i, mask[i]].mean(0) for i in range(v)])
    w = np.where(mask[..., None], y - t[:, None], 0).transpose(0, 2, 1).reshape(2*v, n)
    u, s, vh = np.linalg.svd(w, full_matrices=False)
    a = (u[:, :3] * np.sqrt(s[:3])).reshape(v, 2, 3)
    x = (np.sqrt(s[:3, None]) * vh[:3]).T
    start = time.monotonic()
    for _ in range(50):
        for j in range(n):
            good = mask[:, j]
            x[j] = np.linalg.lstsq(a[good].reshape(-1, 3),
                                     (y[good, j]-t[good]).ravel(), rcond=None)[0]
        for i in range(v):
            design = np.c_[x[mask[i]], np.ones(mask[i].sum())]
            coeff = np.linalg.lstsq(design, y[i, mask[i]], rcond=None)[0]
            a[i], t[i] = coeff[:3].T, coeff[3]
        center = x.mean(0)
        x -= center
        t += np.einsum('vij,j->vi', a, center)
        scale = x.std(0)
        if np.any(scale < 1e-10):
            raise ValueError('rank-deficient affine shape')
        x /= scale
        a *= scale[None, None]
        if time.monotonic()-start > 120:
            raise TimeoutError('ALS120s cap')

    def quad(row):
        q, r, s = row
        return np.array([q*q, 2*q*r, 2*q*s, r*r, 2*r*s, s*s])

    constraints = []
    for aa, bb in a:
        constraints += [(quad(aa+bb)-quad(aa-bb))/4, quad(aa)-quad(bb)]
    _, singular, vh = np.linalg.svd(np.asarray(constraints), full_matrices=False)
    q = vh[-1]
    metric = np.array([[q[0], q[1], q[2]], [q[1], q[3], q[4]], [q[2], q[4], q[5]]])
    if np.trace(metric) < 0:
        metric = -metric
    eig = np.linalg.eigvalsh(metric)
    diagnostics = {'affine_train_p95_px': float(np.percentile(
        np.linalg.norm((np.einsum('vij,nj->vni', a, x)+t[:, None]-y)[mask], axis=1), 95)),
        'metric_eigenvalues': eig.tolist(), 'constraint_singular_values': singular.tolist()}
    if eig[0] <= 1e-8 or eig[-1]/eig[0] > 1e8:
        return None, diagnostics
    b = np.linalg.cholesky(metric)
    a = a @ b
    x = np.linalg.solve(b, x.T).T
    rotations, translations = [], []
    for ai, ti in zip(a, t):
        u, ss, vh = np.linalg.svd(ai, full_matrices=False)
        rows = u @ vh
        rr = np.vstack([rows, np.cross(rows[0], rows[1])])
        scale = ss.mean()
        rotations.append(rr)
        translations.append(np.r_[(ti-[360, 640])/scale, 1500/scale])
    return (x, np.asarray(rotations), np.asarray(translations)), diagnostics


def bundle(y, mask, initial):
    x0, r0, t0 = initial
    v, n = mask.shape
    vi, pi = np.where(mask)
    xy = y[vi, pi]
    # Fix one point coordinate to remove scale,not a shape prior.
    center0 = -r0[0].T @ t0[0]
    axis = int(np.argmax(np.abs(x0[0]-center0)))
    fixed = axis
    free = np.delete(np.arange(n*3), fixed)
    offset = len(free)
    camcount = (v-1)*6
    theta = np.r_[x0.ravel()[free],
                  np.c_[Rotation.from_matrix(r0[1:]).as_rotvec(), t0[1:]].ravel(), np.log(1500)]

    def unpack(z):
        xx = x0.ravel().copy()
        xx[free] = z[:offset]
        cams = z[offset:offset+camcount].reshape(-1, 6)
        rr = np.concatenate([r0[:1], Rotation.from_rotvec(cams[:, :3]).as_matrix()])
        tt = np.vstack([t0[0], cams[:, 3:]])
        return xx.reshape(n, 3), rr, tt, np.exp(z[-1])

    started = time.monotonic()

    def residual(z):
        if time.monotonic()-started > 180:
            raise TimeoutError('perspectiveBA180s cap')
        xx, rr, tt, f = unpack(z)
        cc = np.einsum('nij,nj->ni', rr[vi], xx[pi])+tt[vi]
        uv = f*cc[:, :2]/np.maximum(cc[:, 2:3], 1e-4)+[360, 640]
        return np.r_[(uv-xy).ravel(), 100*np.minimum(cc[:, 2]-.001, 0)]

    m = len(vi)
    jac = lil_matrix((m*3, len(theta)), dtype=np.int8)
    pointcols = np.full(n*3, -1)
    pointcols[free] = np.arange(offset)
    for k, (view, point) in enumerate(zip(vi, pi)):
        cols = pointcols[point*3:point*3+3]
        cols = cols[cols >= 0].tolist()
        if view:
            cols += list(range(offset+(view-1)*6, offset+view*6))
        cols += [len(theta)-1]
        for row in (k*2, k*2+1, m*2+k):
            jac[row, cols] = 1
    lower = np.full(len(theta), -np.inf)
    upper = -lower
    lower[-1], upper[-1] = np.log(400), np.log(4000)
    sol = least_squares(residual, theta, jac_sparsity=jac.tocsr(),
                        loss='soft_l1', f_scale=2, max_nfev=60,
                        x_scale='jac', bounds=(lower, upper))
    xx, rr, tt, f = unpack(sol.x)
    cc = np.einsum('nij,nj->ni', rr[vi], xx[pi])+tt[vi]
    errors = np.linalg.norm(f*cc[:, :2]/cc[:, 2:3]+[360, 640]-xy, axis=1)
    diag = {'optimizer_success': bool(sol.success), 'message': sol.message,
            'training_objective_cost': float(sol.cost), 'nfev': sol.nfev, 'focal_px': float(f), 'seconds': time.monotonic()-started,
            'train_p95_px': float(np.percentile(errors, 95)),
            'nonpositive_training_depths': int((cc[:, 2] <= 0).sum()),
            'rotation_determinant_max_error': float(np.max(np.abs(np.linalg.det(rr)-1)))}
    return (xx, rr, tt, f), diag


def held_score(y, mask, cameras):
    _, rr, tt, f = cameras
    k = np.array([[f, 0, 360], [0, f, 640], [0, 0, 1.]])
    p = k @ np.concatenate([rr, tt[..., None]], axis=2)
    centers = -np.einsum('vji,vj->vi', rr, tt)
    errors, frame_rows = [], []
    invalid = weak = 0
    for j in range(mask.shape[1]):
        visible = np.flatnonzero(mask[:, j])
        for target in visible:
            anchors = visible[visible != target]
            rows = np.concatenate([y[a, j, 0]*p[a, 2:3]-p[a, 0:1]
                                   for a in anchors] +
                                  [y[a, j, 1]*p[a, 2:3]-p[a, 1:2] for a in anchors])
            _, sv, vh = np.linalg.svd(rows, full_matrices=False)
            h = vh[-1]
            err = np.inf
            if sv[-2] > 1e-10 and abs(h[3]) > 1e-10:
                x = h[:3]/h[3]
                depth = np.einsum('vij,j->vi', rr[visible], x)+tt[visible]
                rays = x-centers[anchors]
                rays /= np.linalg.norm(rays, axis=1)[:, None]
                angle = np.rad2deg(np.arccos(np.clip(np.min(rays @ rays.T), -1, 1)))
                weak += int(angle < 1)
                if np.isfinite(depth).all() and np.all(depth[:, 2] > 0) and angle >= 1:
                    pred = p[target] @ np.r_[x, 1]
                    err = float(np.linalg.norm(pred[:2]/pred[2]-y[target, j]))
            invalid += int(not np.isfinite(err))
            errors.append(err)
            frame_rows.append(target)
    errors, frame_rows = np.asarray(errors), np.asarray(frame_rows)
    # Do not silently exclude invalid points from percentile or denominator.
    def percentile(e):
        return float(np.sort(e)[int(np.ceil(.95*len(e)))-1]) if len(e) else np.inf
    per = [{'view': i, 'count': int((frame_rows == i).sum()),
            'p95_px': percentile(errors[frame_rows == i])} for i in range(len(rr))]
    diag = {'count': len(errors), 'invalid': invalid, 'weak_anchor_angle': weak,
            'p95_px': percentile(errors), 'per_view': per,
            'threshold_passed': bool(not invalid and percentile(errors) <= 3 and
                 all(a['count'] >= 30 and a['p95_px'] <= 3 for a in per))}
    return diag, errors, frame_rows


def solve(y, mask, ids, label):
    train = ids % 5 != 0
    REPORT[label] = {'training_ids': int(train.sum()), 'held_ids': int((~train).sum())}
    init, diag = factorize(y[:, train], mask[:, train])
    REPORT[label]['factorization'] = diag
    (OUT/'progress.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
    print(json.dumps({'stage': label+' factorization', 'metric': diag['metric_eigenvalues']}), flush=True)
    if init is None:
        raise ValueError(label+':non-positive metric;no rescue')
    x, r, t = init
    s = np.diag([1., 1., -1.])
    flipped = (x @ s, s @ r @ s, t.copy())
    first = np.einsum('vij,nj->vni', r, x)+t[:, None]
    other = np.einsum('vij,nj->vni', flipped[1], flipped[0])+flipped[2][:, None]
    xy_error = float(np.max(np.abs(first[..., :2]-other[..., :2])))
    if xy_error > 1e-12 or not np.allclose(np.linalg.det(flipped[1]), 1, atol=1e-10):
        raise ValueError('parity transform violates affine/proper-rotation contract')
    if not np.array_equal(flipped[0] @ s, x) or not np.array_equal(s @ flipped[1] @ s, r):
        raise ValueError('parity involution failed')
    REPORT[label]['parity_xy_max_error'] = xy_error
    np.savez_compressed(OUT/(label+'-initial.npz'), shape=x, rotations=r, translations=t)
    candidates = []
    REPORT[label]['training_branches'] = []
    for branch, start in enumerate((init, flipped)):
        cams, ba = bundle(y[:, train], mask[:, train], start)
        finite = all(np.isfinite(value).all() for value in cams)
        eligible = bool(ba['optimizer_success'] and finite and
                        np.isfinite(ba['training_objective_cost']) and
                        ba['nonpositive_training_depths'] == 0 and
                        ba['rotation_determinant_max_error'] < 1e-6)
        ba.update(branch=branch, eligible=eligible)
        REPORT[label]['training_branches'].append(ba)
        (OUT/'progress.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
        print(json.dumps({'stage': label+' training branch', **ba}), flush=True)
        if eligible:
            candidates.append((ba['training_objective_cost'], branch, cams, ba))
    if not candidates:
        raise ValueError(label+':neither parity branch eligible')
    _, branch, cams, ba = min(candidates, key=lambda item: (item[0], item[1]))
    REPORT[label]['chosen_branch_before_held'] = branch
    REPORT[label]['perspective'] = ba
    held, errors, rows = held_score(y[:, ~train], mask[:, ~train], cams)
    REPORT[label]['held'] = held
    np.savez_compressed(OUT/(label+'-evaluation.npz'), errors=errors, views=rows,
                        rotations=cams[1], translations=cams[2], focal=cams[3])
    return cams, held


def control():
    rng = np.random.default_rng(280)
    x = rng.uniform(-1, 1, (600, 3))*[.8, 1, .6]
    r = Rotation.from_euler('yx', np.c_[[-35, -17, 0, 19, 37], [-8, 5, 0, -4, 7]], degrees=True).as_matrix()
    cc = np.einsum('vij,nj->vni', r, x)+[0, 0, 10]
    y = 1500*cc[..., :2]/cc[..., 2:3]+[360, 640]
    ids = np.arange(600)
    mask = np.arange(5)[:, None] != ((ids//5) % 5)[None]
    cams, held = solve(y, mask, ids, 'control')
    bad = y.copy()
    bad[:, :, 0] += 17*np.arange(5)[:, None]**2
    negative, _, _ = held_score(bad[:, ids % 5 == 0], mask[:, ids % 5 == 0], cams)
    REPORT['control']['negative_p95_px'] = negative['p95_px']
    if not held['threshold_passed'] or held['p95_px'] >= .1 or negative['p95_px'] <= 3:
        raise ValueError('control failed;patient solve not started')
    REPORT['control']['status'] = 'TECHNICAL_CHECK_PASSED'


def patient():
    manifest = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    doc = json.loads(manifest.read_text(encoding='utf-8'))
    case = next(c for c in doc['cases'] if c['id'] == 'real-case-001')
    selected = [a for a in doc['inputs'] if case['files']['video'] in (a.get('id'), a.get('path'), a.get('source'))]
    if len(selected) != 1:
        raise ValueError('ambiguous video manifest')
    errors = validate_input_assets({**doc, 'inputs': selected}, manifest.parent)
    if errors:
        raise ValueError(errors)
    archive = ROOT/'assets/private/closed-experiments/0267-native-dense-video/evidence.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != '54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612':
        raise ValueError('observation archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith('/observations.npz')]
        if len(names) != 1:
            raise ValueError('ambiguous observations')
        data = np.load(io.BytesIO(z.read(names[0])), allow_pickle=False)
        frame, ids, xy = data['frame'], data['ids'], data['xy']
    take = (frame >= 0) & (frame <= 876) & (frame % 12 == 0)
    frame, ids, xy = frame[take], ids[take], xy[take]
    unique, counts = np.unique(ids, return_counts=True)
    unique = unique[counts >= np.where(unique % 5 == 0, 4, 3)]
    y = np.zeros((74, len(unique), 2))
    mask = np.zeros(y.shape[:2], bool)
    index = {int(n): i for i, n in enumerate(unique)}
    for fr, ident, point in zip(frame, ids, xy):
        if int(ident) not in index:
            continue
        vi, pi = int(fr//12), index[int(ident)]
        if mask[vi, pi] or not np.isfinite(point).all():
            raise ValueError('duplicate/nonfinite observation')
        y[vi, pi], mask[vi, pi] = point, True
    REPORT['actual_data'] = {'frames': 74, 'component': [0, 876],
                             'rows': int(mask.sum()), 'video_sha256': selected[0]['sha256']}
    cams, held = solve(y, mask, unique, 'patient')
    ba = REPORT['patient']['perspective']
    valid = (ba['optimizer_success'] and ba['nonpositive_training_depths'] == 0
             and ba['train_p95_px'] <= 3 and 400 < cams[3] < 4000)
    REPORT['status'] = 'PARTIAL_SUCCESS' if valid and held['threshold_passed'] else 'REJECT'


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        control()
        patient()
    except Exception as exc:
        REPORT['failure'] = type(exc).__name__+':'+str(exc)
    finally:
        REPORT['seconds'] = time.monotonic()-start
        (OUT/'report.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
        print(json.dumps(REPORT))

