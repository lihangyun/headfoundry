"""Independent exact-surface and common-camera review of one safe scan oracle."""
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
from anatomical_capacity_0239 import mesh_guard
from mesh_feasibility_0240 import violated_faces
import fit_anatomical_capacity_0239 as renderer

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
PARENT = PILOT / 'anatomical-capacity-0239-numerical-replay'
REFERENCE = PILOT / 'fixed-scan-reference-0237-interface-replay'
LOCK = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
OUT = PILOT / 'hard-mesh-feasibility-0240'


def main():
    destination = OUT / 'evaluation-report.json'
    if destination.exists() or (OUT / 'render-report.json').exists():
        raise FileExistsError('Preserve first safe-oracle evaluation')
    started = time.perf_counter()
    controls = json.loads((OUT / 'controls.json').read_text(encoding='utf-8'))
    report = json.loads((OUT / 'optimization-report.json').read_text(encoding='utf-8'))
    contract = json.loads((REFERENCE / 'contract.json').read_text(encoding='utf-8'))
    manifest = json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8'))
    if (report['mesh_feasibility_status'] != 'TECHNICAL_CHECK_PASSED' or (OUT / 'failure.json').exists()
            or validate_input_assets(manifest, PILOT)
            or contract['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or contract['confirmation_sha256'] != sha256_file(PILOT / 'provenance-confirmation.json')
            or contract['backend_versions'] != backend_versions()
            or contract['regions_sha256'] != sha256_file(REFERENCE / 'regions.npz')
            or controls['reference_contract_sha256'] != sha256_file(REFERENCE / 'contract.json')
            or controls['asset_lock_sha256'] != sha256_file(LOCK)
            or controls['objective_sha256'] != sha256_file(PARENT / 'fit-step-04.npz')
            or controls['producer_sha256'] != sha256_file(ROOT / 'tools/solve_mesh_feasibility_0240.py')
            or controls['constraint_helper_sha256'] != sha256_file(ROOT / 'tools/mesh_feasibility_0240.py')):
        raise ValueError('Changed or unaccepted fixed-objective/source/mesh evidence')
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    packet = np.load(OUT / 'feasible-SCAN-ORACLE-NOT-VIDEO.npz', allow_pickle=False)
    prior, current, faces = packet['prior'], packet['vertices'], packet['faces']
    replay = apply_similarity(model.neutral_vertices(packet['coefficients']), packet['frozen_model_to_scan'])
    guard = mesh_guard(current, prior, faces)
    if (not guard['passed'] or len(violated_faces(current, prior, faces))
            or not np.array_equal(faces, model.faces) or abs(replay - current).max() > 1e-9):
        raise ValueError('Whole-output safety,identity replay or native topology failed')
    source_entry = next(a for a in manifest['inputs'] if a['id'] == 'real-case-001-skin')
    if source_entry['sha256'] != contract['source_sha256']:
        raise ValueError('Wrong source skin identity')
    source, source_faces = read_binary_stl(source_entry['path'])
    reference = np.load(REFERENCE / 'regions.npz', allow_pickle=False)
    center = np.asarray(contract['numerical_center_mm'])
    radius = float(np.ptp(source, axis=0).max() / 2)
    source_tree = triangle_tree(source, source_faces, center)
    targets = np.load(PARENT / 'fit-step-04.npz', allow_pickle=False)['targets_mm']
    results = {}
    for name, vertices in [('aligned_neutral', prior), ('hard_feasible_oracle', current)]:
        tree = triangle_tree(vertices, faces, center)
        distance, nearest_face = nearest_triangles(tree, reference['sample_points_mm'], center)
        reverse_points, reverse_face, reverse_bary = sample_surface(vertices, faces, 5000, 237)
        reverse, nearest_source = nearest_triangles(source_tree, reverse_points, center)
        closest, _ = renderer.closest_support(tree, targets, center)
        visible = renderer.visible_support(tree, closest, center, radius)
        stats = {label: summary(distance[reference['sample_group'] == index])
            for index, label in enumerate(contract['sample_groups'])}
        results[name] = {'source_to_surface': stats, 'whole_output_reverse': summary(reverse),
            'fit_nearest_firsthit_visible_fraction': float(visible.mean()), 'hidden_supports': int((~visible).sum()),
            'all_face_regions_p95_2mm': all(stats[label]['p95_mm'] <= 2 for label in contract['sample_groups'][1:])}
        np.savez_compressed(OUT / (name + '-evaluation.npz'), source_distances_mm=distance,
            nearest_output_face=nearest_face, reverse_mm=reverse, reverse_sample_points_mm=reverse_points,
            reverse_sample_face=reverse_face, reverse_sample_barycentric=reverse_bary,
            nearest_source_face=nearest_source, fit_support_firsthit_visible=visible)
    with (OUT / 'hard-feasible-SCAN-ORACLE-NOT-VIDEO.obj').open('x', encoding='utf-8') as stream:
        stream.write('# SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION; FLAME2023 Open CC-BY-4.0; hard mesh-constrained identity fit\n')
        for point in current:
            stream.write('v ' + ' '.join(f'{x:.12f}' for x in point) + '\n')
        for face in faces:
            stream.write('f ' + ' '.join(str(int(x) + 1) for x in face) + '\n')
    evaluation = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'diagnostic_capacity_status': 'TECHNICAL_CHECK_PASSED' if results['hard_feasible_oracle']['all_face_regions_p95_2mm'] else 'REJECT',
        'visual_review': 'UNVERIFIED', 'head_acceptance': 'UNVERIFIED',
        'role': 'SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION', 'mesh_guard': guard, 'results': results,
        'optimization_report_sha256': sha256_file(OUT / 'optimization-report.json'),
        'feasible_geometry_sha256': sha256_file(OUT / 'feasible-SCAN-ORACLE-NOT-VIDEO.npz'),
        'producer_sha256': sha256_file(Path(__file__)), 'renderer_sha256': sha256_file(ROOT / 'tools/fit_anatomical_capacity_0239.py'),
        'backend_versions': backend_versions(), 'source_uncertainty': contract['uncertainty'],
        'evaluation_seconds': time.perf_counter() - started,
        'limits': 'Safe scan-fit regional capacity only; same fixed objective/pose/regions. Open native boundaries,full-source domain mismatch,hidden supports and actual video-only/user acceptance remain unresolved.'}
    destination.write_text(json.dumps(evaluation, indent=2), encoding='utf-8')
    renderer.OUT = OUT
    renders = renderer.render_variants(source, source_faces, prior, current, faces, center, radius)
    (OUT / 'render-report.json').write_text(json.dumps({'role': evaluation['role'], 'renders': renders,
        'source_center_and_radius_common': True}, indent=2), encoding='utf-8')
    print(json.dumps(evaluation), flush=True)


if __name__ == '__main__':
    main()
