"""Authorized video-only profiles and coarse poses;patient scans prohibited."""
import json
import os
from pathlib import Path
import sys
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from video_model_0241 import project, visible_support
from visible_profile_model_0244 import envelope
from gradient_profile_0243 import gradient_profile

BASE = ROOT/'assets/private/video-only-model-0241'
OBS = ROOT/'assets/private/gradient-profile-observations-0243'
OUT = ROOT/'assets/private/visible-profile-head-0244'
LOCK = ROOT/'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
TASK = ROOT/'assets/private/mediapipe/face_landmarker.task'
TASK_LOCK = ROOT/'examples/mediapipe-face-asset-lock.json'
PILOT = ROOT/'assets/private/real-capture-pilot-v1'
ORDINALS = (139, 416, 69, 347)


def forbid_scan(path):
    path = Path(path).resolve()
    if (path.suffix.lower() == '.stl' or path.is_relative_to(PILOT.resolve())
            or path.is_relative_to((BASE/'scan-evaluation').resolve())):
        raise PermissionError('Video profile inference cannot read patient scans/oracles/evaluation')


def install_guard():
    attempts = []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                forbid_scan(os.fsdecode(args[0]))
            except PermissionError:
                attempts.append(os.fsdecode(args[0]))
                raise
    sys.addaudithook(audit)
    return attempts


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first visible profile preparation')
    started, attempts = time.perf_counter(), install_guard()
    manifest = json.loads((OBS/'frame-manifest.json').read_text(encoding='utf-8'))
    old = json.loads((OBS/'report.json').read_text(encoding='utf-8'))
    review = json.loads((OBS/'visual-review.json').read_text(encoding='utf-8'))
    baseline = json.loads((BASE/'fit/optimization-report.json').read_text(encoding='utf-8'))
    task = json.loads(TASK_LOCK.read_text(encoding='utf-8'))
    if (old['observation_precision_status'] != 'TECHNICAL_CHECK_PASSED'
            or review['status'] != 'TECHNICAL_CHECK_PASSED' or review['report_sha256'] != sha256_file(OBS/'report.json')
            or old['frame_manifest_sha256'] != sha256_file(OBS/'frame-manifest.json')
            or baseline['mesh_feasibility_status'] != 'TECHNICAL_CHECK_PASSED'
            or baseline['source_scan_used'] is not False or baseline['case002_used'] is not False
            or task['license_id'] != 'Apache-2.0' or sha256_file(TASK) != task['face_landmarker']['sha256']):
        raise ValueError('Reviewed observation,scan-free safe baseline and exact task required')
    selected = [next(a for a in manifest['inputs'] if a['frame_ordinal'] == f) for f in ORDINALS]
    subset = dict(manifest, inputs=[dict(a, path=str(OBS/a['path'])) for a in selected])
    if validate_input_assets(subset, OUT):
        raise ValueError('Authorized exact-frame rights/hash rejected')
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    packet = np.load(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    binding = np.load(BASE/'generic-bindings.npz', allow_pickle=False)
    if not np.array_equal(packet['faces'], model.faces) or abs(model.neutral_vertices(packet['coefficients'])-packet['vertices']).max() > 1e-12:
        raise ValueError('Safe video baseline identity/topology replay failed')
    OUT.mkdir()
    os.environ['MPLCONFIGDIR'] = str(OUT/'cache')
    prereg = ROOT/'docs/experiment-0244-visible-profile-head-fit.md'
    (OUT/'executed-preregistration.md').write_bytes(prereg.read_bytes())
    path = OUT/'profile-frame-manifest.json'
    path.write_text(json.dumps(subset, indent=2), encoding='utf-8')
    from detect_face_landmarks import extract
    detected = extract(path, TASK)
    (OUT/'coarse-initialization-observations.json').write_text(json.dumps(detected, indent=2), encoding='utf-8')
    if detected['runtime_version'] != '1.0.1' or any(r['faces_detected'] != 1 for r in detected['records']):
        raise ValueError('One real-video face per declared initialization frame required')
    eligible = np.flatnonzero(binding['eligible'])
    triangles, bary = model.faces[binding['face_ids'][eligible]], binding['barycentric'][eligible]
    points = np.einsum('ni,nij->nj', bary, packet['vertices'][triangles])
    point_base = np.einsum('ni,nij->nj', bary, model.template[triangles])
    point_field = np.einsum('ni,nick->nck', bary, model.shape_directions[triangles])
    intrinsic, beta0 = packet['intrinsic'], packet['coefficients']
    skin_vertices = np.unique(model.faces[binding['skin_faces']])
    train = eligible % 5 != 0
    state = np.r_[beta0, np.zeros(12)]
    poses, curves, records, panels = [], [], [], []
    for index, (item, observation) in enumerate(zip(selected, detected['records'])):
        ordinal = item['frame_ordinal']
        right = ordinal in (139, 69)
        box = (400, 630, 590, 843) if right else (120, 630, 320, 843)
        direction = 1 if right else -1
        image = Image.open(OBS/item['path']).convert('RGB')
        if index < 2:
            # Do not regenerate or alter the two reviewed original traces.
            measured = np.load(OBS/f'profile-{ordinal:06d}-sigma1.0.npz', allow_pickle=False)
            curve = measured['curve']
            uncertainty = next(m for m in old['measurements'] if m['frame_ordinal'] == ordinal)
            precision = dict(p95_px=uncertainty['uncertainty_p95_px'], max_px=uncertainty['uncertainty_maximum_px'])
        else:
            curve, strength = gradient_profile(np.asarray(image), box)
            alternatives = [gradient_profile(np.asarray(image), box, s)[0] for s in (.75, 1.25)]
            shifts = np.max([abs(c[:, 0]-curve[:, 0]) for c in alternatives], axis=0)
            precision = dict(p95_px=float(np.percentile(shifts, 95)), max_px=float(shifts.max()))
            np.savez_compressed(OUT/f'held-observation-{ordinal:06d}.npz', curve=curve,
                alternatives=alternatives, selected_strength=strength, all_row_scale_shift=shifts)
            if precision['p95_px'] > 2 or precision['max_px'] > 4:
                raise ValueError('Held contour measurement fails fixed uncertainty guard')
        observed = np.asarray(observation['landmarks'])[eligible, :2]
        ok, r, t = cv2.solvePnP(points[train].copy(), observed[train].copy(), intrinsic, None, flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok or t[2, 0] <= 0:
            raise ValueError('Coarse positive-depth PnP failed')
        r, t = cv2.solvePnPRefineLM(points[train].copy(), observed[train].copy(), intrinsic, None, r, t)
        initial = np.r_[r.ravel(), t.ravel()]
        predicted, _, supports, extrinsic = envelope(state, model.template, model.shape_directions,
            model.faces, skin_vertices, initial, intrinsic, curve[:, 1], direction, 0)
        support_points = np.array([s[1]@packet['vertices'][s[0]] for s in supports])
        visible, gap = visible_support(packet['vertices'], model.faces, support_points, extrinsic, intrinsic, binding['skin_faces'])
        np.savez_compressed(OUT/f'initial-{ordinal:06d}.npz', pose=initial, predicted_x=predicted,
            observed_curve=curve, exact_support_visibility=visible, first_hit_gap_native=gap,
            edge_vertex_ids=np.array([s[0] for s in supports]), edge_weights=np.array([s[1] for s in supports]), extrinsic=extrinsic)
        records.append({'ordinal': ordinal, 'role': 'fit' if index < 2 else 'held_view', 'rows': len(curve),
            'uncertainty': precision, 'initial_profile_p95_px': float(np.percentile(abs(predicted-curve[:, 0]), 95)),
            'initial_visible_supports': int(visible.sum()), 'whole_mesh_min_depth_native': float((packet['vertices']@extrinsic[:, :3].T+extrinsic[:, 3])[:, 2].min())})
        poses.append(initial)
        curves.append(curve)
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        draw.line([tuple(p) for p in curve], fill=(30, 255, 80), width=1)
        draw.line([(float(x), float(y)) for x, y in zip(predicted, curve[:, 1])], fill=(255, 80, 40), width=1)
        overlay.save(OUT/f'initial-{ordinal:06d}-overlay.png')
        panels.append(overlay.crop((box[0]-50, box[1]-40, box[2]+50, box[3]+40)).resize((420, 600)))
    frontal_index = next(i for i, v in enumerate(baseline['final_views']) if v['frame_ordinal'] == 832)
    frontal_projection = intrinsic@packet['extrinsics'][frontal_index]
    frontal_target = project(points, packet['extrinsics'][frontal_index], intrinsic)
    np.savez_compressed(OUT/'prepared.npz', initial_poses=poses, curves=curves, beta0=beta0,
        intrinsic=intrinsic, skin_vertices=skin_vertices, skin_faces=binding['skin_faces'],
        frontal_projection=frontal_projection, frontal_point_base=point_base,
        frontal_point_field=point_field, frontal_target=frontal_target)
    sheet = Image.new('RGB', (1680, 640), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    for i, (panel, record) in enumerate(zip(panels, records)):
        draw.text((i*420+4, 8), f'{record["ordinal"]} {record["role"]} green=observed red=baseline', fill='white')
        sheet.paste(panel, (i*420, 30))
    sheet.save(OUT/'initial-profile-review.png')
    control = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'visual_review': 'UNVERIFIED',
        'head_acceptance': 'UNVERIFIED', 'profile_inputs': records,
        'baseline_geometry_sha256': sha256_file(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'),
        'baseline_report_sha256': sha256_file(BASE/'fit/optimization-report.json'),
        'observation_report_sha256': sha256_file(OBS/'report.json'), 'observation_review_sha256': sha256_file(OBS/'visual-review.json'),
        'frame_manifest_sha256': sha256_file(path), 'asset_lock_sha256': sha256_file(LOCK),
        'task_sha256': sha256_file(TASK), 'prepared_sha256': sha256_file(OUT/'prepared.npz'),
        'producer_sha256': sha256_file(Path(__file__)), 'preregistration_sha256': sha256_file(prereg),
        'patient_scan_or_evaluation_read_attempts': attempts, 'case002_used': False,
        'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Coarse semantic PnP initializer only; no shape fitting or accepted camera/identity.'}
    if time.perf_counter()-started > 60:
        raise TimeoutError('Single preparation/initial review budget exhausted')
    (OUT/'controls.json').write_text(json.dumps(control, indent=2), encoding='utf-8')
    print(json.dumps(control), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
