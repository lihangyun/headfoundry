"""One bounded video-only native anatomical fit; deliberately cannot read scans."""
import json
import os
from pathlib import Path
import sys
import time

# Small dense nonlinear fits are faster and more reproducible without BLAS
# oversubscription; these affect execution,not the declared objective.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import cv2
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from prepare_video_only_0241 import OUT as INPUT, FLAME, forbid_patient_geometry
from video_model_0241 import camera, residual_jacobian, project, visible_support
from anatomical_capacity_0239 import mesh_guard
from mesh_feasibility_0240 import constraints, violated_faces

OUT = INPUT / 'fit'


def summary(values):
    values = np.asarray(values, float)
    return {'count': len(values), 'median_px': float(np.median(values)),
        'p95_px': float(np.percentile(values, 95)), 'maximum_px': float(values.max())}


def main():
    if OUT.exists():
        raise FileExistsError('Preserve original video fit')
    started = time.perf_counter()
    blocked = []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                forbid_patient_geometry(os.fsdecode(args[0]))
            except PermissionError:
                blocked.append(os.fsdecode(args[0]))
                raise

    sys.addaudithook(audit)
    control = json.loads((INPUT / 'controls.json').read_text(encoding='utf-8'))
    manifest = json.loads((INPUT / 'frame-manifest.json').read_text(encoding='utf-8'))
    if (control['status'] != 'TECHNICAL_CHECK_PASSED' or validate_input_assets(manifest, INPUT)
            or sha256_file(INPUT / 'frame-manifest.json') != control['frame_manifest_sha256']
            or sha256_file(INPUT / 'generic-bindings.npz') != control['bindings_sha256']
            or sha256_file(INPUT / 'video-observations.json') != control['observations_sha256']
            or sha256_file(FLAME) != control['asset_lock_sha256']):
        raise ValueError('Locked authorized video observations or prior changed')
    model = FlameIdentityModel.from_asset_record(json.loads(FLAME.read_text(encoding='utf-8')), FLAME.parent)
    binding = np.load(INPUT / 'generic-bindings.npz', allow_pickle=False)
    eligible = np.flatnonzero(binding['eligible'])
    base = binding['points_native'][eligible]
    directions = np.einsum('ni,nick->nck', binding['barycentric'][eligible],
        model.shape_directions[model.faces[binding['face_ids'][eligible]]])
    if abs(base - np.einsum('ni,nij->nj', binding['barycentric'][eligible],
            model.template[model.faces[binding['face_ids'][eligible]]])).max() > 1e-12:
        raise ValueError('Generic binding replay failed')
    records = json.loads((INPUT / 'video-observations.json').read_text(encoding='utf-8'))['records']
    observed = np.array([np.asarray(r['landmarks'])[eligible, :2] for r in records])
    training = eligible % 5 != 0
    intrinsic = np.array([[1000., 0, 360], [0, 1000., 640], [0, 0, 1.]])
    initial, support, reports = [], [], []
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0241-video-only-model-fit.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    for index, ordinal in enumerate(control['fit_frames']):
        if records[index]['id'] != f'frame-{ordinal:06d}':
            raise ValueError('Predeclared exact frame order changed')
        ok, r, t = cv2.solvePnP(base[training].copy(), observed[index, training].copy(),
            intrinsic, None, flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok or t[2, 0] <= 0:
            raise ValueError('Training-only PnP initialization failed')
        r, t = cv2.solvePnPRefineLM(base[training].copy(), observed[index, training].copy(), intrinsic, None, r, t)
        pose = np.r_[r.ravel(), t.ravel()]
        rotation = cv2.Rodrigues(r)[0]
        extrinsic = np.c_[rotation, t]
        visible, gap = visible_support(model.template, model.faces, base, extrinsic, intrinsic, binding['skin_faces'])
        initial.append(pose)
        support.append(visible)
        errors = np.linalg.norm(project(base, extrinsic, intrinsic) - observed[index], axis=1)
        reports.append({'frame_ordinal': ordinal, 'training_visible': int((visible & training).sum()),
            'validation_visible': int((visible & ~training).sum()),
            'initial_training': summary(errors[visible & training]),
            'initial_validation': summary(errors[visible & ~training]),
            'excluded_original_semantic_ids': eligible[~visible].tolist(),
            'exclusion_reason': 'Not exact nearest skin surface at initial neutral PnP; no residual filter'})
        np.savez_compressed(OUT / f'initial-{ordinal:06d}.npz', pose=pose,
            eligible_semantic_ids=eligible, initial_visibility=visible, first_hit_gap_native=gap,
            initial_errors_px=errors, intrinsic=intrinsic, extrinsic=extrinsic)
    initial, support = np.array(initial), np.array(support)
    coverage = all(r['training_visible'] >= 100 and r['validation_visible'] >= 20 for r in reports)
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'coverage_status': 'TECHNICAL_CHECK_PASSED' if coverage else 'REJECT',
        'role': 'VIDEO_ONLY_GENERIC_ANATOMICAL_FIT_NOT_ACCEPTED_HEAD',
        'binding_review': 'Anatomically plausible on generic prior; cross-person accuracy UNVERIFIED',
        'preparation_controls_sha256': sha256_file(INPUT / 'controls.json'),
        'preregistration_sha256': sha256_file(prereg), 'producer_sha256': sha256_file(Path(__file__)),
        'projection_helper_sha256': sha256_file(ROOT / 'tools/video_model_0241.py'),
        'constraint_helper_sha256': sha256_file(ROOT / 'tools/mesh_feasibility_0240.py'),
        'initial_views': reports, 'source_scan_used': False, 'case002_used': False,
        'patient_geometry_or_oracle_read_attempts': blocked, 'initial_identity': 'exact zero',
        'head_acceptance': 'UNVERIFIED', 'physical_camera_acceptance': 'UNVERIFIED'}
    (OUT / 'initialization-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if not coverage:
        print(json.dumps({'coverage_status': 'REJECT', 'initial_views': reports}), flush=True)
        return
    chosen = support & training[None, :]
    views, ids = np.where(chosen)
    data = (base[ids], directions[ids], observed[views, ids], views, initial)
    dimensions = 300 + 6 * len(initial) + 1
    bounds = [(-3 + 1e-8, 3 - 1e-8)] * (dimensions - 1)
    bounds += [(np.log(.4) / .3, np.log(3.) / .3)]
    active, history, success = np.array([], int), [], False
    coefficients, state = np.zeros(300), np.zeros(dimensions)

    def check_time():
        if time.perf_counter() - started > 180:
            raise TimeoutError('Single video fit budget exhausted')

    for round_index in range(5):
        cache = {'x': None}

        def evaluate(x):
            check_time()
            if cache['x'] is None or not np.array_equal(cache['x'], x):
                r, j = residual_jacobian(x, *data)
                cache.update(x=x.copy(), objective=float(.5 * r @ r), gradient=j.T @ r)
            return cache['objective'], cache['gradient']

        def physical(x):
            check_time()
            c, j = constraints(x[:300], model.template[model.faces[active]],
                model.shape_directions[model.faces[active]])
            full = np.zeros((len(c), dimensions))
            full[:, :300] = j
            return c, full

        iterations = []

        def callback(x):
            check_time()
            iterations.append({'iteration': len(iterations) + 1, 'objective': evaluate(x)[0]})
            if len(iterations) % 25 == 0:
                print(json.dumps({'round': round_index, **iterations[-1]}), flush=True)

        result = minimize(lambda x: evaluate(x)[0], np.zeros(dimensions), jac=lambda x: evaluate(x)[1],
            bounds=bounds, method='SLSQP', callback=callback,
            constraints=[] if not len(active) else [{'type': 'ineq', 'fun': lambda x: physical(x)[0],
                'jac': lambda x: physical(x)[1]}], options={'maxiter': 150, 'ftol': 1e-8})
        state = result.x
        coefficients = state[:300]
        vertices = model.neutral_vertices(coefficients)
        bad = violated_faces(vertices, model.template, model.faces)
        guard = mesh_guard(vertices, model.template, model.faces)
        minimum = float(physical(state)[0].min()) if len(active) else None
        entry = {'round': round_index, 'optimizer_success': bool(result.success), 'message': str(result.message),
            'iterations': int(result.nit), 'objective': evaluate(state)[0], 'active_face_count': len(active),
            'all_face_violations': len(bad), 'minimum_active_constraint': minimum,
            'mesh_guard': guard, 'iteration_trace': iterations}
        history.append(entry)
        np.savez_compressed(OUT / f'round-{round_index:02d}.npz', state=state, constrained_faces=active,
            violating_faces=bad, initial_poses=initial, frozen_support=support,
            training_semantic_ids=eligible[ids], training_view_ids=views)
        print(json.dumps({k: v for k, v in entry.items() if k != 'iteration_trace'}), flush=True)
        if not result.success or (minimum is not None and minimum < -1e-7):
            break
        if not len(bad) and guard['passed']:
            success = True
            break
        updated = np.union1d(active, bad)
        if len(updated) == len(active):
            break
        active = updated
    focal = float(1000 * np.exp(.3 * state[-1]))
    intrinsic[0, 0] = intrinsic[1, 1] = focal
    fitted = base + np.einsum('nck,k->nc', directions, coefficients)
    final_views, extrinsics = [], []
    for index, ordinal in enumerate(control['fit_frames']):
        rotation, translation, _ = camera(state[300 + 6 * index:306 + 6 * index], initial[index])
        extrinsic = np.c_[rotation, translation]
        extrinsics.append(extrinsic)
        visible, gap = visible_support(vertices, model.faces, fitted, extrinsic, intrinsic, binding['skin_faces'])
        errors = np.linalg.norm(project(fitted, extrinsic, intrinsic) - observed[index], axis=1)
        lost = support[index] & ~visible
        final_views.append({'frame_ordinal': ordinal,
            'training': summary(errors[support[index] & training]),
            'validation': summary(errors[support[index] & ~training]),
            'used_support_lost_visibility': int(lost.sum()), 'lost_semantic_ids': eligible[lost].tolist(),
            'rotation_det': float(np.linalg.det(rotation)),
            'whole_mesh_minimum_depth_native': float((vertices @ rotation.T + translation)[:, 2].min())})
        np.savez_compressed(OUT / f'final-{ordinal:06d}.npz', intrinsic=intrinsic, extrinsic=extrinsic,
            final_errors_px=errors, final_visibility=visible, first_hit_gap_native=gap)
    projection_ok = all(v['validation']['p95_px'] <= 3 and v['used_support_lost_visibility'] == 0
        and v['whole_mesh_minimum_depth_native'] > 1e-6 for v in final_views)
    report.update(mesh_feasibility_status='TECHNICAL_CHECK_PASSED' if success else 'REJECT',
        detector_projection_status='TECHNICAL_CHECK_PASSED' if projection_ok else 'REJECT',
        focal_px=focal, history=history, final_views=final_views,
        elapsed_seconds=time.perf_counter() - started,
        limits='Detector semantic consistency only,not physical correspondence/camera or head acceptance; native boundaries remain.')
    # Preserve coefficients even on failure as numerical evidence; unsafe geometry
    # is not exported for visual review.
    np.savez_compressed(OUT / 'numerical-result.npz', state=state, coefficients=coefficients,
        initial_poses=initial, frozen_support=support, intrinsic=intrinsic, extrinsics=extrinsics,
        eligible_semantic_ids=eligible)
    if success:
        np.savez_compressed(OUT / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', vertices=vertices,
            faces=model.faces, coefficients=coefficients, intrinsic=intrinsic, extrinsics=extrinsics)
        with (OUT / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.obj').open('w', encoding='ascii') as stream:
            for v in vertices:
                stream.write('v ' + ' '.join(f'{n:.12g}' for n in v) + '\n')
            for f in model.faces + 1:
                stream.write('f ' + ' '.join(str(n) for n in f) + '\n')
    (OUT / 'optimization-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('mesh_feasibility_status', 'detector_projection_status',
        'focal_px', 'final_views', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
