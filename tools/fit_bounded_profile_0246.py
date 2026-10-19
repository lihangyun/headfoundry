"""One unaccepted head diagnostic;never hide0245's failed required347 view."""
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file
from video_model_0241 import project
import fit_visible_profile_0245 as shared

PARENT = ROOT/'assets/private/detector-free-profile-head-0245-domain-replay'
OUT = ROOT/'assets/private/bounded-profile-geometry-0246'


def prepare():
    if OUT.exists():
        raise FileExistsError('Preserve first unaccepted correction')
    shared.ORDINALS = (139, 416, 69)
    model, baseline, binding, manifest, report = shared.load()
    failure = json.loads((PARENT/'failure.json').read_text(encoding='utf-8'))
    if failure['error'] != 'Held source contour uncertainty failed':
        raise ValueError('Exact required-view failure must remain explicit')
    uncertain = np.load(PARENT/'held-observation-000347.npz', allow_pickle=False)['all_row_scale_shift']
    if np.percentile(uncertain, 95) <= 2 and uncertain.max() <= 4:
        raise ValueError('Do not fabricate a missing validation failure')
    records = json.loads((PARENT/'partial-pose-results.json').read_text(encoding='utf-8'))
    if [r['ordinal'] for r in records] != [139, 416, 69] or not all(r['optimizer_success'] and r['first_hit_visible'] == 213 for r in records):
        raise ValueError('Unchanged valid existing pose packets required')
    poses, curves, inputs = [], [], []
    for ordinal in shared.ORDINALS:
        path = PARENT/f'pose-{ordinal:06d}.npz'
        packet = np.load(path, allow_pickle=False)
        poses.append(packet['pose'])
        curves.append(packet['curve'])
        inputs.append({'ordinal': ordinal, 'pose_packet_sha256': sha256_file(path)})
    eligible = np.flatnonzero(binding['eligible'])
    triangles, bary = model.faces[binding['face_ids'][eligible]], binding['barycentric'][eligible]
    base = np.einsum('ni,nij->nj', bary, model.template[triangles])
    field = np.einsum('ni,nick->nck', bary, model.shape_directions[triangles])
    front = next(i for i, v in enumerate(report['final_views']) if v['frame_ordinal'] == 832)
    target = project(np.einsum('ni,nij->nj', bary, baseline['vertices'][triangles]), baseline['extrinsics'][front], baseline['intrinsic'])
    OUT.mkdir()
    (OUT/'executed-preregistration.md').write_bytes((ROOT/'docs/experiment-0246-bounded-profile-geometry.md').read_bytes())
    np.savez_compressed(OUT/'prepared.npz', beta0=baseline['coefficients'], initial_poses=poses, curves=curves,
        intrinsic=baseline['intrinsic'], skin_vertices=np.unique(model.faces[binding['skin_faces']]), skin_faces=binding['skin_faces'],
        frontal_point_base=base, frontal_point_field=field, frontal_target=target,
        frontal_projection=baseline['intrinsic']@baseline['extrinsics'][front])
    (OUT/'frame-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    control = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'REJECT', 'required_view347_status': 'REJECT',
        'role': 'UNACCEPTED_GEOMETRY_DIAGNOSTIC_NOT_FULL_IMAGE_VALIDATION', 'input_pose_packets': inputs,
        'prepared_sha256': sha256_file(OUT/'prepared.npz'), 'parent_failure_sha256': sha256_file(PARENT/'failure.json'),
        'failed_view347_uncertainty_p95_px': float(np.percentile(uncertain, 95)),
        'failed_view347_uncertainty_max_px': float(uncertain.max()),
        'producer_sha256': sha256_file(Path(__file__)), 'shared_fitter_sha256': sha256_file(ROOT/'tools/fit_visible_profile_0245.py')}
    (OUT/'controls.json').write_text(json.dumps(control, indent=2), encoding='utf-8')


def fit():
    shared.ORDINALS, shared.OUT = (139, 416, 69), OUT
    try:
        shared.fit()
    finally:
        path = OUT/'fit/optimization-report.json'
        if path.exists():
            report = json.loads(path.read_text(encoding='utf-8'))
            report.update(head_acceptance='REJECT', required_view347_status='REJECT', overall_image_validation_status='REJECT',
                role='UNACCEPTED_GEOMETRY_DIAGNOSTIC_NOT_FULL_IMAGE_VALIDATION',
                limits=report['limits']+' Required347 source measurement fails;three available views cannot pass the original four-view image gate.')
            path.write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    attempts = shared.install_guard()
    try:
        {'prepare': prepare, 'fit': fit}[sys.argv[1]]()
    except Exception as error:
        destination = OUT/'fit' if (OUT/'fit').exists() else OUT
        if destination.exists() and not (destination/'failure.json').exists():
            (destination/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error),
                'blocked_scan_attempts': attempts}, indent=2), encoding='utf-8')
        raise
