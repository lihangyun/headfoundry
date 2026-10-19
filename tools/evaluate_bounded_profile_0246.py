"""Separate frozen-output scan measurement;reuses0241's exact similarity,no ICP."""
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl
from scan_motion_truth_0230 import sample_surface
from scan_surface_metric_0237 import apply_similarity, triangle_tree, nearest_triangles, summary, backend_versions
import fit_anatomical_capacity_0239 as renderer

PILOT = ROOT/'assets/private/real-capture-pilot-v1'
REFERENCE = PILOT/'fixed-scan-reference-0237-interface-replay'
BASE = ROOT/'assets/private/video-only-model-0241'
INPUT = ROOT/'assets/private/bounded-profile-geometry-0246'
OUT = INPUT/'scan-evaluation'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first bounded head scan measurement')
    started = time.perf_counter()
    report_path = INPUT/'fit/optimization-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    current_path = INPUT/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'
    baseline_path = BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'
    current = np.load(current_path, allow_pickle=False)
    baseline = np.load(baseline_path, allow_pickle=False)
    alignment_path = BASE/'scan-evaluation/candidate-record.json'
    alignment = json.loads(alignment_path.read_text(encoding='utf-8'))
    contract = json.loads((REFERENCE/'contract.json').read_text(encoding='utf-8'))
    manifest = json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    subset = dict(manifest, inputs=[a for a in manifest['inputs'] if a['id'] in ('real-case-001-video', 'real-case-001-skin')])
    if (len(subset['inputs']) != 2 or validate_input_assets(subset, PILOT)
            or report['source_scan_used'] is not False or report['case002_used'] is not False
            or report['mesh_status'] != 'TECHNICAL_CHECK_PASSED'
            or report['required_view347_status'] != 'REJECT'
            or alignment['geometry_sha256'] != sha256_file(baseline_path)
            or alignment['reference_contract_sha256'] != sha256_file(REFERENCE/'contract.json')
            or contract['manifest_sha256'] != sha256_file(PILOT/'manifest.json')
            or contract['confirmation_sha256'] != sha256_file(PILOT/'provenance-confirmation.json')
            or contract['regions_sha256'] != sha256_file(REFERENCE/'regions.npz')
            or contract['review_sha256'] != sha256_file(REFERENCE/'review.json')
            or contract['backend_versions'] != backend_versions()
            or not np.array_equal(current['faces'], baseline['faces'])):
        raise ValueError('Frozen scan-free correction,baseline transform or source reference changed')
    skin = next(a for a in subset['inputs'] if a['id'] == 'real-case-001-skin')
    if skin['sha256'] != contract['source_sha256']:
        raise ValueError('Only original fixed case001 skin is authorized here')
    source, source_faces = read_binary_stl(skin['path'])
    reference = np.load(REFERENCE/'regions.npz', allow_pickle=False)
    center = np.asarray(contract['numerical_center_mm'])
    transform = np.asarray(alignment['candidate_to_scan_4x4'])
    transformed_baseline = apply_similarity(baseline['vertices'], transform)
    transformed_current = apply_similarity(current['vertices'], transform)
    OUT.mkdir()
    controls = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'REJECT',
        'source_used_only_after_inference': True, 'case002_used': False, 'no_alignment_refit': True,
        'frozen_alignment_record_sha256': sha256_file(alignment_path), 'candidate_to_scan_4x4': transform.tolist(),
        'baseline_geometry_sha256': sha256_file(baseline_path), 'candidate_geometry_sha256': sha256_file(current_path),
        'fit_report_sha256': sha256_file(report_path), 'reference_contract_sha256': sha256_file(REFERENCE/'contract.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'backend_versions': backend_versions()}
    (OUT/'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    source_tree = triangle_tree(source, source_faces, center)
    group = reference['sample_group']
    held = (group > 0) & (np.arange(len(group)) % 2 != 0)
    results = {}
    for name, vertices in [('video-baseline-0241', transformed_baseline), ('profile-candidate-0246', transformed_current)]:
        tree = triangle_tree(vertices, current['faces'], center)
        forward, forward_face = nearest_triangles(tree, reference['sample_points_mm'], center)
        reverse_points, reverse_face, reverse_bary = sample_surface(vertices, current['faces'], 5000, 237)
        reverse, nearest_source = nearest_triangles(source_tree, reverse_points, center)
        np.savez_compressed(OUT/f'{name}-distances.npz', forward_mm=forward, nearest_candidate_face=forward_face,
            reverse_mm=reverse, reverse_sample_points_mm=reverse_points, reverse_sample_face=reverse_face,
            reverse_sample_barycentric=reverse_bary, nearest_source_face=nearest_source)
        results[name] = {'source_groups': {n: summary(forward[group == i]) for i, n in enumerate(contract['sample_groups'])},
            'held_face_regions': {n: summary(forward[held & (group == i)]) for i, n in enumerate(contract['sample_groups']) if i > 0},
            'entire_output_to_full_source': summary(reverse)}
    old = json.loads((BASE/'scan-evaluation/report.json').read_text(encoding='utf-8'))['metrics']['video-only-candidate']
    replay = max(abs(results['video-baseline-0241']['source_groups'][n]['p95_mm']-old['all_source_groups'][n]['p95_mm'])
        for n in contract['sample_groups'])
    if replay > 1e-9:
        raise ValueError('Frozen transform/source/baseline metric replay drifted')
    result = dict(controls, results=results, baseline_metric_replay_max_mm=replay,
        metric_elapsed_seconds=time.perf_counter()-started, required_view347_status='REJECT',
        limits='Fixed-transform surface proximity on original engineering regions,not physical camera/scan uncertainty or full-head visual acceptance.')
    if time.perf_counter()-started > 60:
        raise TimeoutError('Single scan metric budget exhausted')
    (OUT/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    renderer.OUT = OUT
    renders = renderer.render_variants(source, source_faces, transformed_baseline, transformed_current,
        current['faces'], center, float(np.ptp(source, axis=0).max()/2))
    for entry in renders:
        replacement = {'aligned-neutral-prior': 'video-baseline-0241', 'scan-fit-oracle-NOT-VIDEO': 'profile-candidate-0246'}.get(entry['variant'])
        if replacement:
            old_path = OUT/entry['image']
            entry['image'] = entry['image'].replace(entry['variant'], replacement)
            entry['variant'] = replacement
            old_path.rename(OUT/entry['image'])
    (OUT/'renders.json').write_text(json.dumps({'status': 'TECHNICAL_CHECK_PASSED', 'images': renders,
        'same_transform_camera_light_scale': True}, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
