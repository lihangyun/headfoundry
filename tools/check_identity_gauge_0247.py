"""One scan-free numerical gauge/capacity test;no candidate export or scan metric."""
import json
import os
from pathlib import Path
import sys
import time
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from scan_motion_truth_0230 import look_at_origin
from anatomical_capacity_0239 import mesh_guard
from scan_surface_metric_0237 import apply_similarity
from video_model_0241 import project
from identity_gauge_0247 import compensate_camera, canonicalize_centroid_radius, split_similarity_fields

LOCK = ROOT/'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
BASE = ROOT/'assets/private/video-only-model-0241'
PREVIOUS = ROOT/'assets/private/bounded-profile-geometry-0246'
OUT = ROOT/'assets/private/identity-camera-gauge-0247'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first native gauge diagnostic')
    started, attempts = time.perf_counter(), []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if (path.suffix.lower() == '.stl' or path.is_relative_to((ROOT/'assets/private/real-capture-pilot-v1').resolve())
                    or 'scan-evaluation' in path.parts):
                attempts.append(str(path))
                raise PermissionError('Gauge diagnostic cannot read scans or scan-based evaluation')
    sys.addaudithook(audit)
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    baseline = np.load(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    previous = np.load(PREVIOUS/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    binding = np.load(BASE/'generic-bindings.npz', allow_pickle=False)
    skin = np.unique(model.faces[binding['skin_faces']])
    for packet in (baseline, previous):
        if not np.array_equal(packet['faces'], model.faces) or abs(model.neutral_vertices(packet['coefficients'])-packet['vertices']).max() > 1e-12:
            raise ValueError('Native video-only identity replay failed')
    OUT.mkdir()
    prereg = ROOT/'docs/experiment-0247-identity-camera-gauge.md'
    (OUT/'executed-preregistration.md').write_bytes(prereg.read_bytes())
    transform = np.eye(4)
    transform[:3, :3] = 1.006*cv2.Rodrigues(np.array([.01, -.015, .02]))[0]
    transform[:3, 3] = [.0003, -.0008, .0002]
    changed = apply_similarity(model.template, transform)
    canonical, _, normalized = canonicalize_centroid_radius(changed, model.shape_directions, model.template, skin)
    k = np.array([[937., 0, 360], [0, 937., 640], [0, 0, 1.]])
    controls = []
    for yaw in (0, -45, 45, -90, 90):
        angle = np.deg2rad(yaw)
        camera = look_at_origin(.65*np.array([np.sin(angle), 0, np.cos(angle)]))
        moved = compensate_camera(camera, transform)
        normalized_camera = compensate_camera(moved, normalized)
        controls.append({'yaw_deg': yaw,
            'similarity_projection_max_px': float(abs(project(changed, moved, k)-project(model.template, camera, k)).max()),
            'normalization_projection_max_px': float(abs(project(canonical, normalized_camera, k)-project(changed, moved, k)).max())})
    rng = np.random.default_rng(247)
    beta = rng.normal(size=300)*1e-4
    vertices = model.neutral_vertices(beta)
    _, derivative, _ = canonicalize_centroid_radius(vertices, model.shape_directions, model.template, skin)
    derivative_errors = []
    for _ in range(10):
        direction = rng.normal(size=300)
        direction /= np.linalg.norm(direction)
        delta = np.einsum('vck,k->vc', model.shape_directions, direction)
        plus = canonicalize_centroid_radius(vertices+delta*1e-5, model.shape_directions, model.template, skin)[0]
        minus = canonicalize_centroid_radius(vertices-delta*1e-5, model.shape_directions, model.template, skin)[0]
        derivative_errors.append(float(abs((plus-minus)/2e-5-np.einsum('vck,k->vc', derivative, direction)).max()))
    orthogonal, global_map, local = split_similarity_fields(baseline['vertices'][skin], model.shape_directions[skin])
    _, singular, vt = np.linalg.svd(global_map, full_matrices=True)
    rank = int((singular > singular[0]*1e-10).sum())
    null = vt[rank:].T
    delta_beta = previous['coefficients']-baseline['coefficients']
    target = local@delta_beta
    least = np.linalg.lstsq(local@null, target, rcond=1e-10)[0]
    reconstructed = null@least
    relative_error = float(np.linalg.norm(local@reconstructed-target)/np.linalg.norm(target))
    coefficients = baseline['coefficients']+reconstructed
    guard = mesh_guard(model.template+np.einsum('vck,k->vc', model.shape_directions, coefficients), model.template, model.faces)
    bound_ok = bool((abs(coefficients) <= 3).all())
    hard_ok = relative_error <= .01 and bound_ok and guard['passed']
    if max(max(r['similarity_projection_max_px'], r['normalization_projection_max_px']) for r in controls) > 1e-8 or max(derivative_errors) > 1e-7:
        raise ValueError('Exact gauge/projection/derivative fixture failed')
    result = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'hard_latent_gauge_status': 'TECHNICAL_CHECK_PASSED' if hard_ok else 'REJECT',
        'camera_equivariance': controls, 'native_directional_derivative_max_error': max(derivative_errors),
        'native_skin_vertex_count': len(skin), 'similarity_map_rank': rank, 'nullspace_dimensions': null.shape[1],
        'global_basis_energy_fraction': float(np.sum(global_map**2)/np.sum(model.shape_directions[skin]**2)),
        'hard_latent_lock_local_replay_relative_error': relative_error,
        'hypothetical_coefficients_max_absolute': float(abs(coefficients).max()),
        'hypothetical_bounds_passed': bound_ok, 'hypothetical_mesh_guard': guard,
        'asset_lock_sha256': sha256_file(LOCK), 'baseline_geometry_sha256': sha256_file(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'),
        'frozen_rejected_geometry_sha256': sha256_file(PREVIOUS/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'),
        'producer_sha256': sha256_file(Path(__file__)), 'helper_sha256': sha256_file(ROOT/'tools/identity_gauge_0247.py'),
        'preregistration_sha256': sha256_file(prereg), 'runtime_numpy': np.__version__,
        'blocked_patient_or_scan_reads': attempts, 'elapsed_seconds': time.perf_counter()-started,
        'limits': 'No export,scan alignment,camera recovery or actual head correction. Gauge mathematics adds no independent observations.'}
    if time.perf_counter()-started > 60:
        raise TimeoutError('Single native gauge diagnostic budget exhausted')
    np.savez_compressed(OUT/'numerical-replay.npz', global_map=global_map, nullspace=null,
        frozen_delta_beta=delta_beta, hypothetical_gauge_null_delta=reconstructed,
        local_target=target, local_replay=local@reconstructed, similarity_controls=transform)
    (OUT/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
