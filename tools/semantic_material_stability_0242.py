"""Known safe generic geometry,exact cameras and frozen semantic attachments."""
import json
import os
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from anatomical_capacity_0239 import mesh_guard
from scan_motion_truth_0230 import look_at_origin
from video_model_0241 import project, visible_support

PARENT = ROOT / 'assets/private/video-only-model-0241'
PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
OUT = ROOT / 'assets/private/semantic-material-stability-0242'
LOCK = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
TASK = ROOT / 'assets/private/mediapipe/face_landmarker.task'
TASK_LOCK = ROOT / 'examples/mediapipe-face-asset-lock.json'
PARENT_ALLOWED = {'controls.json', 'generic-bindings.npz', 'generic-neutral-only.png'}


def forbid_patient_data(path):
    path = Path(path).resolve()
    if (path.suffix.lower() == '.stl' or path.is_relative_to(PILOT.resolve())
            or (path.is_relative_to(PARENT.resolve()) and path.parent != PARENT.resolve())
            or (path.parent == PARENT.resolve() and path.name not in PARENT_ALLOWED)):
        raise PermissionError('Generic semantic fixture cannot read patient data or fitted outputs')


def error_summary(errors):
    errors = np.asarray(errors, float)
    if errors.ndim != 1 or not len(errors) or not np.isfinite(errors).all() or (errors < 0).any():
        raise ValueError('All finite nonnegative visible errors required,no clipping')
    return {'count': len(errors), 'median_px': float(np.median(errors)),
        'p95_px': float(np.percentile(errors, 95)), 'maximum_px': float(errors.max())}


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first semantic material-stability fixture')
    started, attempts = time.perf_counter(), []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                forbid_patient_data(os.fsdecode(args[0]))
            except PermissionError:
                attempts.append(os.fsdecode(args[0]))
                raise

    sys.addaudithook(audit)
    parent = json.loads((PARENT / 'controls.json').read_text(encoding='utf-8'))
    task = json.loads(TASK_LOCK.read_text(encoding='utf-8'))
    if (sha256_file(PARENT / 'generic-bindings.npz') != parent['bindings_sha256']
            or sha256_file(LOCK) != parent['asset_lock_sha256']
            or task['license_id'] != 'Apache-2.0'
            or sha256_file(TASK) != parent['task_sha256']
            or sha256_file(TASK) != task['face_landmarker']['sha256']):
        raise ValueError('Unchanged reviewed model,task and bindings required')
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    binding = np.load(PARENT / 'generic-bindings.npz', allow_pickle=False)
    eligible = np.flatnonzero(binding['eligible'])
    if len(eligible) != 420 or not np.array_equal(binding['semantic_ids'], np.arange(468)):
        raise ValueError('Frozen420 original semantic IDs required')
    triangles = model.faces[binding['face_ids'][eligible]]
    bary = binding['barycentric'][eligible]
    base = np.einsum('ni,nij->nj', bary, model.template[triangles])
    if abs(base - binding['points_native'][eligible]).max() > 1e-12:
        raise ValueError('Original material binding does not replay')
    source_eye_separation = float(np.linalg.norm(binding['source_pixels'][33] - binding['source_pixels'][263]))
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0242-semantic-material-stability.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    os.environ['MPLCONFIGDIR'] = str(OUT / 'cache')
    import mediapipe as mp
    if mp.__version__ != '1.0.1':
        raise ValueError('Exact prepared MediaPipe runtime required')
    options = mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(TASK)),
        output_facial_transformation_matrixes=False)
    results = []
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        for identity_name, coefficient in [('zero', 0.), ('pc0-plus1', 1.), ('pc0-minus1', -1.)]:
            beta = np.zeros(300)
            beta[0] = coefficient
            vertices = model.neutral_vertices(beta)
            guard = mesh_guard(vertices, model.template, model.faces)
            if not guard['passed']:
                raise ValueError('Predeclared known generic shape violates mesh guard; no substitute permitted')
            points = np.einsum('ni,nij->nj', bary, vertices[triangles])
            display = (vertices - binding['generic_center']) / binding['generic_radius']
            display_points = (points - binding['generic_center']) / binding['generic_radius']
            for yaw in (0, -45, 45, -75, 75):
                name = f'{identity_name}-yaw{yaw:+03d}'
                angle = np.deg2rad(yaw)
                extrinsic = look_at_origin(4 * np.array([np.sin(angle), 0, np.cos(angle)]))
                intrinsic = binding['source_intrinsic']
                truth = project(display_points, extrinsic, intrinsic)
                visible, gap = visible_support(display, model.faces, display_points, extrinsic, intrinsic, binding['skin_faces'])
                pixels, _, _ = render(display, model.faces, extrinsic, intrinsic, (512, 512), smooth_shading=True)
                image_path = OUT / (name + '.png')
                Image.fromarray(pixels).save(image_path)
                if identity_name == 'zero' and yaw == 0:
                    if not np.array_equal(pixels, np.asarray(Image.open(PARENT / 'generic-neutral-only.png'))):
                        raise ValueError('Same-image implementation control changed original pixels')
                    source_replay = float(abs(truth - binding['source_pixels'][eligible]).max())
                    if source_replay > 1e-8:
                        raise ValueError('Known material source projection does not replay')
                detected = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=pixels))
                item = {'case': name, 'coefficient0': coefficient, 'yaw_deg': yaw,
                    'mesh_guard': guard, 'visible_material_count': int(visible.sum()),
                    'visible_validation_count': int((visible & (eligible % 5 == 0)).sum()),
                    'faces_detected': len(detected.face_landmarks), 'image_sha256': sha256_file(image_path)}
                arrays = dict(eligible_semantic_ids=eligible, vertices=vertices, faces=model.faces,
                    material_triangle_vertex_ids=triangles, material_barycentric=bary,
                    material_pixels=truth, exact_visibility=visible, first_hit_gap_display=gap,
                    intrinsic=intrinsic, extrinsic_display=extrinsic)
                if len(detected.face_landmarks) != 1:
                    item.update(status='REJECT', reason='No single face detection; no replacement configuration')
                else:
                    observed = np.array([[p.x * 512, p.y * 512] for p in detected.face_landmarks[0][:468]])
                    errors = np.linalg.norm(observed[eligible] - truth, axis=1)
                    arrays.update(all468_observed_pixels=observed, all_eligible_errors_px=errors)
                    validation = visible & (eligible % 5 == 0)
                    item.update(all_visible=error_summary(errors[visible]), held_visible=error_summary(errors[validation]),
                        held_p95_fraction_source_interocular=float(np.percentile(errors[validation], 95) / source_eye_separation),
                        special_ids={str(i): {'visible': bool(visible[np.flatnonzero(eligible == i)[0]]),
                            'error_px': float(errors[np.flatnonzero(eligible == i)[0]])} for i in (4, 168, 0, 17)})
                    passed = (visible.sum() >= 100 and validation.sum() >= 20
                        and item['all_visible']['p95_px'] <= 3 and item['held_visible']['p95_px'] <= 3)
                    item['status'] = 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT'
                    if identity_name == 'zero' and yaw == 0:
                        control_error = float(abs(observed[eligible] - binding['source_pixels'][eligible]).max())
                        if control_error > 1e-3:
                            raise ValueError('Same-image detector determinism control failed')
                    marked = Image.fromarray(pixels)
                    draw = ImageDraw.Draw(marked)
                    for index in np.flatnonzero(visible):
                        x, y = truth[index]
                        ox, oy = observed[eligible[index]]
                        draw.line((x, y, ox, oy), fill=(255, 220, 40))
                        draw.ellipse((x-1, y-1, x+1, y+1), fill=(40, 255, 80))
                        draw.ellipse((ox-1, oy-1, ox+1, oy+1), fill=(255, 70, 40))
                    marked.save(OUT / (name + '-material-versus-detector.png'))
                np.savez_compressed(OUT / (name + '.npz'), **arrays)
                results.append(item)
                (OUT / 'partial-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
                print(json.dumps(item), flush=True)
                if time.perf_counter() - started > 60:
                    raise TimeoutError('Fixed semantic material-stability fixture budget exhausted')
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'fixed_material_premise_status': 'TECHNICAL_CHECK_PASSED' if all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in results) else 'REJECT',
        'head_acceptance': 'UNVERIFIED', 'role': 'KNOWN_GENERIC_GEOMETRY_NOT_RECONSTRUCTION_OR_TRAINING',
        'parent_controls_sha256': sha256_file(PARENT / 'controls.json'),
        'asset_lock_sha256': sha256_file(LOCK), 'task_sha256': sha256_file(TASK),
        'preregistration_sha256': sha256_file(prereg), 'producer_sha256': sha256_file(Path(__file__)),
        'runtime': {'numpy': np.__version__, 'mediapipe': mp.__version__},
        'source_material_projection_replay_max_px': source_replay, 'source_detector_replay_max_px': control_error,
        'source_interocular_px': source_eye_separation, 'patient_or_fitted_output_read_attempts': attempts,
        'case_results': results, 'elapsed_seconds': time.perf_counter() - started,
        'limits': 'Bounded generic shape/pose material-stability only. No real camera/shape,physical anatomy or full-head accuracy acceptance.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('execution_status', 'fixed_material_premise_status', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
