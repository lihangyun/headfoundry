"""Detector-free authorized profile pose,then bounded shared-head correction."""
import json
import os
from pathlib import Path
import sys
import time
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.profile_fit import project_with_basis_jacobian
from video_model_0241 import project, visible_support
from visible_profile_model_0244 import envelope, pose, frontal_constraints, near_constraint_faces, ProfileDomainError
from mesh_feasibility_0240 import constraints, violated_faces
from anatomical_capacity_0239 import mesh_guard
from gradient_profile_0243 import gradient_profile
from scan_motion_truth_0230 import look_at_origin
from prepare_visible_profile_0244 import BASE, OBS, LOCK, install_guard, ORDINALS

OUT = ROOT/'assets/private/detector-free-profile-head-0245'
PREREG = ROOT/'docs/experiment-0245-detector-free-profile-fit.md'
ORIGINAL = OUT
if '--domain-safe-replay' in sys.argv:
    OUT = ROOT/'assets/private/detector-free-profile-head-0245-domain-replay'


def load():
    old = json.loads((OBS/'report.json').read_text(encoding='utf-8'))
    review = json.loads((OBS/'visual-review.json').read_text(encoding='utf-8'))
    manifest = json.loads((OBS/'frame-manifest.json').read_text(encoding='utf-8'))
    if (old['observation_precision_status'] != 'TECHNICAL_CHECK_PASSED'
            or review['status'] != 'TECHNICAL_CHECK_PASSED'
            or review['report_sha256'] != sha256_file(OBS/'report.json')
            or old['frame_manifest_sha256'] != sha256_file(OBS/'frame-manifest.json')):
        raise ValueError('Frozen reviewed authorized profile observations required')
    selected = [next(a for a in manifest['inputs'] if a['frame_ordinal'] == f) for f in ORDINALS]
    subset = dict(manifest, inputs=[dict(a, path=str(OBS/a['path'])) for a in selected])
    if validate_input_assets(subset, OUT):
        raise ValueError('Exact original-use frame rights/hash failed')
    report = json.loads((BASE/'fit/optimization-report.json').read_text(encoding='utf-8'))
    if report['source_scan_used'] is not False or report['case002_used'] is not False or report['mesh_feasibility_status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('Safe scan-free video baseline required')
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    baseline = np.load(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    binding = np.load(BASE/'generic-bindings.npz', allow_pickle=False)
    if not np.array_equal(baseline['faces'], model.faces) or abs(model.neutral_vertices(baseline['coefficients'])-baseline['vertices']).max() > 1e-12:
        raise ValueError('Native video baseline replay failed')
    return model, baseline, binding, subset, report


def stats(errors):
    errors = np.asarray(errors, float)
    return {'count': len(errors), 'median_px': float(np.median(abs(errors))),
        'p95_px': float(np.percentile(abs(errors), 95)), 'max_px': float(abs(errors).max())}


def prepare():
    if OUT.exists():
        raise FileExistsError('Preserve first detector-free preparation')
    started = time.perf_counter()
    model, baseline, binding, manifest, report = load()
    OUT.mkdir()
    (OUT/'executed-preregistration.md').write_bytes(PREREG.read_bytes())
    (OUT/'frame-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    beta0, intrinsic = baseline['coefficients'], baseline['intrinsic']
    skin = np.unique(model.faces[binding['skin_faces']])
    front_index = next(i for i, r in enumerate(report['final_views']) if r['frame_ordinal'] == 832)
    nose = baseline['vertices'][skin[np.argmax(baseline['vertices'][skin, 2])]]
    poses, curves, records, panels = [], [], [], []
    for index, ordinal in enumerate(ORDINALS):
        direction = 1 if ordinal in (139, 69) else -1
        box = (400, 630, 590, 843) if direction == 1 else (120, 630, 320, 843)
        image = Image.open(OBS/f'frame-{ordinal:06d}.png').convert('RGB')
        if index < 2:
            curve = np.load(OBS/f'profile-{ordinal:06d}-sigma1.0.npz', allow_pickle=False)['curve']
        else:
            curve, strength = gradient_profile(np.asarray(image), box)
            alternatives = [gradient_profile(np.asarray(image), box, s)[0] for s in (.75, 1.25)]
            shifts = np.max([abs(c[:, 0]-curve[:, 0]) for c in alternatives], axis=0)
            np.savez_compressed(OUT/f'held-observation-{ordinal:06d}.npz', curve=curve,
                alternatives=alternatives, selected_strength=strength, all_row_scale_shift=shifts)
            if np.percentile(shifts, 95) > 2 or shifts.max() > 4:
                raise ValueError('Held source contour uncertainty failed')
        train = np.arange(len(curve)) % 5 != 0
        angle = np.deg2rad(-90*direction)
        rotation = look_at_origin([np.sin(angle), 0, np.cos(angle)])[:, :3]
        depth = baseline['extrinsics'][front_index, 2, 3]
        tip = curve[np.argmax(direction*curve[:, 0])]
        camera_nose = rotation@nose
        translation = np.r_[(tip-[360, 640])*(camera_nose[2]+depth)/intrinsic.diagonal()[:2]-camera_nose[:2], depth]
        initial = np.r_[cv2.Rodrigues(rotation)[0].ravel(), translation]
        trace, invalid_trials = [], []

        def objective(q):
            if time.perf_counter()-started > 60:
                raise TimeoutError('Single detector-free pose preparation budget exhausted')
            try:
                x, jac, _, _ = envelope(np.r_[beta0, q, np.zeros(6)], model.template, model.shape_directions,
                    model.faces, skin, initial, intrinsic, curve[train, 1], direction, 0)
            except ProfileDomainError:
                # Extended-real objective: only invalid line-search trials have
                # +inf cost. No accepted state or required row is approximated.
                invalid_trials.append(q.tolist())
                return np.inf, np.zeros(6)
            residual = (x-curve[train, 0])/2
            return .5*(residual@residual+q@q), jac[:, 300:306].T@residual/2+q

        result = minimize(lambda q: objective(q)[0], np.zeros(6), jac=lambda q: objective(q)[1],
            bounds=[(-12, 12)]*6, method='SLSQP', options={'maxiter': 100, 'ftol': 1e-8},
            callback=lambda q: trace.append({'objective': objective(q)[0], 'q': q.tolist()}))
        r, t, _ = pose(result.x, initial)
        current = np.r_[cv2.Rodrigues(r)[0].ravel(), t]
        if OUT != ORIGINAL and index == 0:
            previous = np.load(ORIGINAL/f'pose-{ordinal:06d}.npz', allow_pickle=False)
            if abs(previous['pose']-current).max() > 1e-8 or not np.array_equal(previous['initial'], initial):
                raise ValueError('Domain repair changed original completed valid pose')
        x, _, supports, extrinsic = envelope(np.r_[beta0, np.zeros(12)], model.template, model.shape_directions,
            model.faces, skin, current, intrinsic, curve[:, 1], direction, 0)
        points = np.array([s[1]@baseline['vertices'][s[0]] for s in supports])
        visible, gap = visible_support(baseline['vertices'], model.faces, points, extrinsic, intrinsic, binding['skin_faces'])
        record = {'ordinal': ordinal, 'role': 'fit' if index < 2 else 'shape_held_pose_conditional',
            'optimizer_success': bool(result.success), 'message': str(result.message), 'iterations': int(result.nit),
            'training': stats(x[train]-curve[train, 0]), 'held_rows': stats(x[~train]-curve[~train, 0]),
            'first_hit_visible': int(visible.sum()), 'rows': len(curve), 'pose_q': result.x.tolist(),
            'invalid_trial_count': len(invalid_trials)}
        records.append(record)
        poses.append(current)
        curves.append(curve)
        np.savez_compressed(OUT/f'pose-{ordinal:06d}.npz', initial=initial, pose=current, q=result.x,
            curve=curve, predicted_x=x, exact_first_hit_visibility=visible, first_hit_gap_native=gap,
            edge_vertex_ids=np.array([s[0] for s in supports]), edge_weights=np.array([s[1] for s in supports]))
        (OUT/f'pose-{ordinal:06d}-trace.json').write_text(json.dumps(trace, indent=2), encoding='utf-8')
        (OUT/f'pose-{ordinal:06d}-invalid-trials.json').write_text(json.dumps(invalid_trials), encoding='utf-8')
        draw = ImageDraw.Draw(image)
        draw.line([tuple(p) for p in curve], fill=(30, 255, 80), width=1)
        draw.line([(float(a), float(b)) for a, b in zip(x, curve[:, 1])], fill=(255, 70, 40), width=1)
        image.save(OUT/f'pose-{ordinal:06d}-overlay.png')
        panels.append(image.crop((box[0]-50, box[1]-40, box[2]+50, box[3]+40)).resize((420, 600)))
        (OUT/'partial-pose-results.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
        print(json.dumps(record), flush=True)
        if not result.success:
            raise ValueError('Single fixed-head profile pose registration did not converge')
    eligible = np.flatnonzero(binding['eligible'])
    triangles, bary = model.faces[binding['face_ids'][eligible]], binding['barycentric'][eligible]
    point_base = np.einsum('ni,nij->nj', bary, model.template[triangles])
    point_field = np.einsum('ni,nick->nck', bary, model.shape_directions[triangles])
    target = project(np.einsum('ni,nij->nj', bary, baseline['vertices'][triangles]), baseline['extrinsics'][front_index], intrinsic)
    np.savez_compressed(OUT/'prepared.npz', beta0=beta0, initial_poses=poses, curves=curves, intrinsic=intrinsic,
        skin_vertices=skin, skin_faces=binding['skin_faces'], frontal_point_base=point_base,
        frontal_point_field=point_field, frontal_target=target, frontal_projection=intrinsic@baseline['extrinsics'][front_index])
    sheet = Image.new('RGB', (1680, 640), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    for index, (panel, record) in enumerate(zip(panels, records)):
        draw.text((index*420+4, 8), f'{record["ordinal"]} green=observed red=baseline envelope', fill='white')
        sheet.paste(panel, (index*420, 30))
    sheet.save(OUT/'pose-preparation-review.png')
    control = {'status': 'TECHNICAL_CHECK_PASSED', 'visual_review': 'UNVERIFIED', 'pose_results': records,
        'baseline_geometry_sha256': sha256_file(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'),
        'observation_report_sha256': sha256_file(OBS/'report.json'), 'prepared_sha256': sha256_file(OUT/'prepared.npz'),
        'frame_manifest_sha256': sha256_file(OUT/'frame-manifest.json'), 'producer_sha256': sha256_file(Path(__file__)),
        'asset_lock_sha256': sha256_file(LOCK), 'preregistration_sha256': sha256_file(PREREG),
        'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Conditional fixed-head contour camera initialization only;not accepted camera or new head.'}
    (OUT/'controls.json').write_text(json.dumps(control, indent=2), encoding='utf-8')


def fit():
    target = OUT/'fit'
    if target.exists():
        raise FileExistsError('Preserve first shared profile head correction')
    started = time.perf_counter()
    model, baseline, binding, manifest, _ = load()
    control = json.loads((OUT/'controls.json').read_text(encoding='utf-8'))
    review = json.loads((OUT/'visual-review.json').read_text(encoding='utf-8'))
    if (control['prepared_sha256'] != sha256_file(OUT/'prepared.npz')
            or review['status'] != 'TECHNICAL_CHECK_PASSED' or review['controls_sha256'] != sha256_file(OUT/'controls.json')):
        raise ValueError('Unchanged prepared arrays and actual contour/region review required')
    packet = np.load(OUT/'prepared.npz', allow_pickle=False)
    beta0, initial, curves = packet['beta0'], packet['initial_poses'], packet['curves']
    intrinsic, skin = packet['intrinsic'], packet['skin_vertices']
    train = np.arange(213) % 5 != 0
    start = np.r_[beta0, np.zeros(12)]
    active = near_constraint_faces(baseline['vertices'], model.template, model.faces)
    target.mkdir()
    history, success, state = [], False, start.copy()

    def check_time():
        if time.perf_counter()-started > 180:
            raise TimeoutError('Single shared-profile correction budget exhausted')

    for round_index in range(5):
        cache = {'x': None}

        def evaluate(x):
            check_time()
            if cache['x'] is None or not np.array_equal(cache['x'], x):
                residuals, jacobians = [], []
                for view, direction in enumerate((1, -1)):
                    predicted, j, _, _ = envelope(x, model.template, model.shape_directions, model.faces,
                        skin, initial[view], intrinsic, curves[view, train, 1], direction, view)
                    residuals.append((predicted-curves[view, train, 0])/2)
                    jacobians.append(j/2)
                residual, jac = np.concatenate(residuals), np.concatenate(jacobians)
                change = x-start
                c, cj = frontal_constraints(x[:300], packet['frontal_point_base'], packet['frontal_point_field'],
                    packet['frontal_projection'], packet['frontal_target'])
                m, mj = constraints(x[:300], model.template[model.faces[active]], model.shape_directions[model.faces[active]])
                full = np.zeros((len(c)+len(m), len(x)))
                full[:, :300] = np.vstack([cj, mj])
                cache.update(x=x.copy(), objective=float(.5*(residual@residual+change@change)),
                    gradient=jac.T@residual+change, constraint=np.r_[c, m], constraint_jacobian=full)
            return cache

        trace = []

        def callback(x):
            value = evaluate(x)
            trace.append({'iteration': len(trace)+1, 'objective': value['objective'], 'minimum_constraint': float(value['constraint'].min())})
            if len(trace) % 20 == 0:
                print(json.dumps({'round': round_index, **trace[-1]}), flush=True)

        result = minimize(lambda x: evaluate(x)['objective'], start, jac=lambda x: evaluate(x)['gradient'],
            bounds=[(-3+1e-8, 3-1e-8)]*312, method='SLSQP', callback=callback,
            constraints=[{'type': 'ineq', 'fun': lambda x: evaluate(x)['constraint'],
                'jac': lambda x: evaluate(x)['constraint_jacobian']}], options={'maxiter': 120, 'ftol': 1e-8})
        state = result.x
        vertices = model.neutral_vertices(state[:300])
        bad = violated_faces(vertices, model.template, model.faces)
        guard = mesh_guard(vertices, model.template, model.faces)
        minimum = float(evaluate(state)['constraint'].min())
        entry = {'round': round_index, 'optimizer_success': bool(result.success), 'message': str(result.message),
            'iterations': int(result.nit), 'active_faces': len(active), 'all_face_violations': len(bad),
            'minimum_constraint': minimum, 'mesh_guard': guard, 'trace': trace}
        history.append(entry)
        np.savez_compressed(target/f'round-{round_index:02d}.npz', state=state,
            active_faces=active, violating_faces=bad, initial_state=start)
        print(json.dumps({k: v for k, v in entry.items() if k != 'trace'}), flush=True)
        if not result.success or minimum < -1e-7:
            break
        if not len(bad) and guard['passed']:
            success = True
            break
        new_active = np.union1d(active, bad)
        if len(new_active) == len(active):
            break
        active = new_active
    views, extrinsics = [], []
    for index, ordinal in enumerate(ORDINALS):
        evaluation_state = state if index < 2 else np.r_[state[:300], np.zeros(12)]
        x, _, supports, extrinsic = envelope(evaluation_state, model.template, model.shape_directions, model.faces,
            skin, initial[index], intrinsic, curves[index, :, 1], 1 if index in (0, 2) else -1, index if index < 2 else 0)
        points = np.array([s[1]@vertices[s[0]] for s in supports])
        visible, gap = visible_support(vertices, model.faces, points, extrinsic, intrinsic, packet['skin_faces'])
        error = x-curves[index, :, 0]
        views.append({'ordinal': ordinal, 'role': 'fit' if index < 2 else 'shape_held_pose_conditional',
            'all_rows': stats(error), 'held_rows': stats(error[~train]), 'first_hit_visible': int(visible.sum()),
            'lost_supports': int((~visible).sum())})
        extrinsics.append(extrinsic)
        np.savez_compressed(target/f'final-{ordinal:06d}.npz', predicted_x=x, error_px=error,
            exact_visibility=visible, first_hit_gap_native=gap, extrinsic=extrinsic,
            edge_vertex_ids=np.array([s[0] for s in supports]), edge_weights=np.array([s[1] for s in supports]))
    c, _ = frontal_constraints(state[:300], packet['frontal_point_base'], packet['frontal_point_field'], packet['frontal_projection'], packet['frontal_target'])
    frontal_maximum = float(np.sqrt(max(0., 4.-c.min())))
    passed = success and frontal_maximum <= 2+1e-7 and all(v['held_rows']['p95_px'] <= 3 and v['lost_supports'] == 0 for v in views)
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'mesh_status': 'TECHNICAL_CHECK_PASSED' if success else 'REJECT',
        'profile_projection_status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT', 'physical_camera_acceptance': 'UNVERIFIED',
        'head_acceptance': 'UNVERIFIED', 'source_scan_used': False, 'case002_used': False,
        'history': history, 'views': views, 'frontal_self_projection_maximum_drift_px': frontal_maximum,
        'prepared_controls_sha256': sha256_file(OUT/'controls.json'), 'producer_sha256': sha256_file(Path(__file__)),
        'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Contour-conditioned pose/shape consistency,not independent physical camera or complete-head quality. No scan input;native boundaries remain.'}
    np.savez_compressed(target/'numerical-result.npz', state=state, coefficients=state[:300], intrinsic=intrinsic, extrinsics=extrinsics)
    if success and frontal_maximum <= 2+1e-7:
        np.savez_compressed(target/'experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', vertices=vertices,
            faces=model.faces, coefficients=state[:300], intrinsic=intrinsic, extrinsics=extrinsics)
        with (target/'experimental-VIDEO-ONLY-NOT-ACCEPTED.obj').open('x', encoding='ascii') as stream:
            stream.write('# Experimental video-only FLAME2023 Open CC-BY-4.0 identity correction;NOT ACCEPTED\n')
            for point in vertices:
                stream.write('v '+' '.join(f'{n:.12g}' for n in point)+'\n')
            for face in model.faces+1:
                stream.write('f '+' '.join(str(n) for n in face)+'\n')
    (target/'optimization-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('mesh_status', 'profile_projection_status', 'views', 'frontal_self_projection_maximum_drift_px', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    attempts = install_guard()
    try:
        {'prepare': prepare, 'fit': fit}[sys.argv[1]]()
    except Exception as error:
        if OUT.exists():
            path = OUT/('fit/failure.json' if len(sys.argv) > 1 and sys.argv[1] == 'fit' and (OUT/'fit').exists() else 'failure.json')
            if not path.exists():
                path.write_text(json.dumps({'status': 'REJECT', 'error': str(error), 'blocked_scan_attempts': attempts}, indent=2), encoding='utf-8')
        raise
