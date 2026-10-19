"""Separate case001 evaluator of a terminated,frozen video fit; never inference."""
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl
from scan_motion_truth_0230 import sample_surface
from scan_surface_metric_0237 import apply_similarity, triangle_tree, nearest_triangles, summary, backend_versions
from anatomical_capacity_0239 import fit_similarity
import fit_anatomical_capacity_0239 as visuals

INPUT = ROOT / 'assets/private/video-only-model-0241'
PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
FLAME = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
REFERENCE = PILOT / 'fixed-scan-reference-0237-interface-replay'
OUT = INPUT / 'scan-evaluation'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first frozen-video scan evaluation')
    started = time.perf_counter()
    fit = INPUT / 'fit'
    report_path = fit / 'optimization-report.json'
    fit_report = json.loads(report_path.read_text(encoding='utf-8'))
    geometry = fit / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'
    packet = np.load(geometry, allow_pickle=False)
    controls = json.loads((INPUT / 'controls.json').read_text(encoding='utf-8'))
    contract = json.loads((REFERENCE / 'contract.json').read_text(encoding='utf-8'))
    manifest = json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8'))
    # Validate only the authorized case001 video/skin subset. No bone or case002
    # source bytes are opened,even for hashing.
    subset = dict(manifest, inputs=[a for a in manifest['inputs'] if a['id'] in ('real-case-001-video', 'real-case-001-skin')])
    if (len(subset['inputs']) != 2 or validate_input_assets(subset, PILOT)
            or fit_report['mesh_feasibility_status'] != 'TECHNICAL_CHECK_PASSED'
            or fit_report['source_scan_used'] is not False or fit_report['case002_used'] is not False
            or contract['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or contract['confirmation_sha256'] != sha256_file(PILOT / 'provenance-confirmation.json')
            or contract['regions_sha256'] != sha256_file(REFERENCE / 'regions.npz')
            or contract['review_sha256'] != sha256_file(REFERENCE / 'review.json')
            or contract['review_status'] != 'TECHNICAL_CHECK_PASSED'
            or contract['backend_versions'] != backend_versions()
            or controls['source_video_sha256'] != next(a['sha256'] for a in subset['inputs'] if a['id'] == 'real-case-001-video')):
        raise ValueError('Frozen video output,source authorization or reference changed')
    model = FlameIdentityModel.from_asset_record(json.loads(FLAME.read_text(encoding='utf-8')), FLAME.parent)
    if not np.array_equal(packet['faces'], model.faces) or abs(packet['vertices'] - model.neutral_vertices(packet['coefficients'])).max() > 1e-12:
        raise ValueError('Frozen video geometry replay failed')
    source_entry = next(a for a in subset['inputs'] if a['id'] == 'real-case-001-skin')
    if source_entry['sha256'] != contract['source_sha256']:
        raise ValueError('Exact fixed source required')
    source, source_faces = read_binary_stl(source_entry['path'])
    reference = np.load(REFERENCE / 'regions.npz', allow_pickle=False)
    group = reference['sample_group']
    train = (group > 0) & (np.arange(len(group)) % 2 == 0)
    held = (group > 0) & ~train
    targets = reference['sample_points_mm'][train]
    area = np.array([r['area_mm2'] for r in contract['regions']])
    weights = area[group[train] - 1]
    weights /= weights.mean()
    native, faces = packet['vertices'], packet['faces']
    center = np.asarray(contract['numerical_center_mm'])
    transform = np.diag([1000., 1000., 1000., 1.])
    transform[:3, 3] = source[source[:, 2].argmax()] - native[native[:, 2].argmax()] * 1000
    OUT.mkdir()
    (OUT / 'executed-preregistration.md').write_bytes((ROOT / 'docs/experiment-0241-video-only-model-fit.md').read_bytes())
    history = []
    for iteration in range(10):
        current = apply_similarity(native, transform)
        closest, _ = visuals.closest_support(triangle_tree(current, faces, center), targets, center)
        transform = fit_similarity(closest, targets, weights) @ transform
        scale = float(np.linalg.norm(transform[:3, :3], axis=1).mean())
        rotation = transform[:3, :3] / scale
        angle = float(np.rad2deg(np.arccos(np.clip((np.trace(rotation) - 1) / 2, -1, 1))))
        history.append({'iteration': iteration, 'scale': scale, 'rotation_deg': angle, 'transform': transform.tolist()})
        if not 700 <= scale <= 1300 or angle > 15:
            raise ValueError('One evaluation similarity outside registered scale/pose guard')
    record = {'role': 'VIDEO_DERIVED_CANDIDATE', 'scan_geometry_used_for_inference': False,
        'video_sha256': controls['source_video_sha256'], 'geometry_path': str(geometry.relative_to(OUT.parent)).replace('\\', '/'),
        'geometry_sha256': sha256_file(geometry), 'frozen_fit_report_sha256': sha256_file(report_path),
        'reference_contract_sha256': sha256_file(REFERENCE / 'contract.json'),
        'candidate_to_scan_4x4': transform.tolist(), 'units_after_transform': 'millimeter',
        'alignment_basis': 'One post-inference similarity,ten fixed steps on even reference-face samples,area weighted; no shape fit or held odd samples',
        'alignment_history': history}
    # Absolute geometry path avoids confusing the record/output parent convention.
    record['geometry_path'] = str(geometry)
    (OUT / 'candidate-record.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    current = apply_similarity(native, transform)
    neutral = apply_similarity(model.template, transform)
    metric = {}
    for name, vertices in [('neutral-same-transform', neutral), ('video-only-candidate', current)]:
        tree = triangle_tree(vertices, faces, center)
        forward, forward_face = nearest_triangles(tree, reference['sample_points_mm'], center)
        reverse, reverse_face, reverse_bary = sample_surface(vertices, faces, 5000, 237)
        backward, nearest_source = nearest_triangles(triangle_tree(source, source_faces, center), reverse, center)
        np.savez_compressed(OUT / f'{name}-distances.npz', forward_mm=forward,
            nearest_candidate_face=forward_face, reverse_mm=backward, reverse_sample_points_mm=reverse,
            reverse_sample_face=reverse_face, reverse_sample_barycentric=reverse_bary, nearest_source_face=nearest_source)
        metric[name] = {'all_source_groups': {n: summary(forward[group == i]) for i, n in enumerate(contract['sample_groups'])},
            'alignment_held_face_regions': {n: summary(forward[held & (group == i)])
                for i, n in enumerate(contract['sample_groups']) if i > 0},
            'entire_candidate_to_full_source': summary(backward)}
    if time.perf_counter() - started > 60:
        raise TimeoutError('Single fixed-output registration/metric budget exhausted')
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'REJECT', 'physical_camera_acceptance': 'UNVERIFIED',
        'source_used_only_after_inference': True, 'case002_used': False, 'candidate_record_sha256': sha256_file(OUT / 'candidate-record.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'metric_helper_sha256': sha256_file(ROOT / 'tools/scan_surface_metric_0237.py'),
        'backend_versions': backend_versions(), 'metrics': metric, 'metric_elapsed_seconds': time.perf_counter() - started,
        'limits': 'One post-inference evaluation registration,no identity/pose/focal feedback. Diagnostic face scope only20.3%,native boundaries and unverified scan uncertainty remain.'}
    (OUT / 'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    visuals.OUT = OUT
    radius = float(np.ptp(source, axis=0).max() / 2)
    # Reuse exact public local rendering helper,but rename its historical oracle
    # label immediately in metadata and filenames: this candidate is VIDEO-derived.
    renders = visuals.render_variants(source, source_faces, neutral, current, faces, center, radius)
    for item in renders:
        if item['variant'] == 'scan-fit-oracle-NOT-VIDEO':
            old = OUT / item['image']
            item['variant'] = 'video-fit-NOT-ACCEPTED'
            item['image'] = item['image'].replace('scan-fit-oracle-NOT-VIDEO', item['variant'])
            old.rename(OUT / item['image'])
    (OUT / 'renders.json').write_text(json.dumps({'status': 'TECHNICAL_CHECK_PASSED', 'images': renders,
        'all_variants_same_similarity_camera_light': True, 'candidate_geometry_sha256': sha256_file(geometry)}, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
