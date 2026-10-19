"""Fixed whole-output similarity and exact triangle proximity, never a fitter."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file
from headfoundry.scan import read_binary_stl
from scan_motion_truth_0230 import sample_surface


def apply_similarity(vertices, transform):
    vertices, transform = np.asarray(vertices, float), np.asarray(transform, float)
    if (vertices.ndim != 2 or vertices.shape[1:] != (3,) or transform.shape != (4, 4)
            or not np.isfinite(vertices).all() or not np.isfinite(transform).all()
            or not np.allclose(transform[3], [0, 0, 0, 1], atol=1e-10, rtol=0)):
        raise ValueError('Finite vertices and homogeneous4x4 similarity required')
    linear = transform[:3, :3]
    scale = float(np.linalg.norm(linear, axis=1).mean())
    if scale <= 0 or not np.allclose(linear @ linear.T, np.eye(3) * scale ** 2, atol=1e-10 * scale ** 2, rtol=1e-8):
        raise ValueError('Positive uniform scale required, no anisotropic stretching')
    if not np.isclose(np.linalg.det(linear / scale), 1., atol=1e-8, rtol=0):
        raise ValueError('Proper rotation required, no reflection')
    return vertices @ linear.T + transform[:3, 3]


def summary(distances):
    distances = np.asarray(distances, float)
    if distances.ndim != 1 or not len(distances) or not np.isfinite(distances).all() or (distances < 0).any():
        raise ValueError('All finite nonnegative distances required; no sample filtering')
    return {'count': len(distances), 'p50_mm': float(np.median(distances)),
        'p95_mm': float(np.percentile(distances, 95)), 'max_mm': float(distances.max()),
        'fraction_within_2mm': float(np.mean(distances <= 2.))}


def triangle_tree(vertices, faces, center):
    from mathutils.bvhtree import BVHTree
    # Same translation for both surfaces; never scale millimeters or fit regions.
    return BVHTree.FromPolygons((vertices - center).tolist(), faces.tolist(), all_triangles=True, epsilon=0.)


def nearest_triangles(tree, points, center):
    from mathutils import Vector
    distances, ids = np.empty(len(points)), np.empty(len(points), np.int64)
    for index, point in enumerate(points - center):
        location, _, face, distance = tree.find_nearest(Vector(point))
        if location is None or face is None or distance is None:
            raise ValueError('Exact closest triangle missing; do not drop this sample')
        distances[index], ids[index] = distance, face
    return distances, ids


def backend_versions():
    import bpy
    return {'blender': bpy.app.version_string, 'numpy': np.__version__}


def main():
    # Candidate must be an explicit geometry/provenance record, not a supplied
    # reference scan smuggled through a production output path.
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 3:
        raise ValueError('Provide reference directory, candidate record and new private output')
    reference, record_path, output = map(lambda x: Path(x).resolve(), args)
    private = ROOT / 'assets/private'
    if not all(p.is_relative_to(private) for p in (reference, record_path, output)):
        raise ValueError('Local private project paths required')
    if output.exists():
        raise FileExistsError('Preserve previous measurements')
    contract_path = reference / 'contract.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8'))
    record = json.loads(record_path.read_text(encoding='utf-8'))
    if (contract['review_status'] != 'TECHNICAL_CHECK_PASSED' or contract['units'] != 'millimeter'
            or record['units_after_transform'] != 'millimeter'
            or record['reference_contract_sha256'] != sha256_file(contract_path)
            or record.get('role') != 'VIDEO_DERIVED_CANDIDATE'
            or record.get('scan_geometry_used_for_inference') is not False
            or not record.get('video_sha256') or not record.get('alignment_basis')):
        raise ValueError('Reviewed reference, video provenance and one declared millimeter alignment required')
    review_path = reference / 'review.json'
    if (sha256_file(review_path) != contract['review_sha256']
            or sha256_file(Path(__file__)) != contract['measurement_entrypoint_sha256']):
        raise ValueError('Frozen review or measurement entrypoint changed')
    review = json.loads(review_path.read_text(encoding='utf-8'))
    if review['status'] != 'TECHNICAL_CHECK_PASSED' or review['regions_sha256'] != contract['regions_sha256']:
        raise ValueError('Actual source-region review required')
    versions = backend_versions()
    if (versions != contract['backend_versions']
            or sha256_file(Path(__file__).with_name('scan_motion_truth_0230.py')) != contract['sampler_sha256']):
        raise ValueError('Frozen exact-distance or sampling runtime changed')
    manifest_path = ROOT / 'assets/private/real-capture-pilot-v1/manifest.json'
    confirmation_path = manifest_path.parent / 'provenance-confirmation.json'
    from headfoundry.manifest import validate_input_assets
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if (validate_input_assets(manifest, manifest_path.parent)
            or contract['manifest_sha256'] != sha256_file(manifest_path)
            or contract['confirmation_sha256'] != sha256_file(confirmation_path)):
        raise ValueError('Original consent/source/units changed')
    allowed_video = next(a['sha256'] for a in manifest['inputs'] if a['id'] == 'real-case-001-video')
    if record['video_sha256'] != allowed_video:
        raise ValueError('Case001 development video required; case002 is reserved')
    source_entry = next(a for a in manifest['inputs'] if a['id'] == 'real-case-001-skin')
    source = Path(contract['source_path']).resolve()
    if source != Path(source_entry['path']).resolve() or contract['source_sha256'] != source_entry['sha256']:
        raise ValueError('Only the exact consented case001 skin source is allowed')
    archive_path = reference / 'regions.npz'
    geometry_path = (record_path.parent / record['geometry_path']).resolve()
    if (not geometry_path.is_relative_to(private) or sha256_file(geometry_path) != record['geometry_sha256']
            or sha256_file(source) != contract['source_sha256'] or sha256_file(archive_path) != contract['regions_sha256']):
        raise ValueError('Source, geometry or frozen regions changed')
    vertices, faces = read_binary_stl(source)
    regions = np.load(archive_path, allow_pickle=False)
    candidate = np.load(geometry_path, allow_pickle=False)
    current = apply_similarity(candidate['vertices'], record['candidate_to_scan_4x4'])
    current_faces = candidate['faces']
    # Also validates every candidate face/index/area before BVH construction.
    reverse, reverse_face, reverse_bary = sample_surface(current, current_faces, 5000, 237)
    center = np.asarray(contract['numerical_center_mm'])
    source_tree, candidate_tree = triangle_tree(vertices, faces, center), triangle_tree(current, current_faces, center)
    forward, forward_face = nearest_triangles(candidate_tree, regions['sample_points_mm'], center)
    backward, nearest_source_face = nearest_triangles(source_tree, reverse, center)
    names = list(contract['sample_groups'])
    forward_regions = {name: summary(forward[regions['sample_group'] == index]) for index, name in enumerate(names)}
    reverse_labels = regions['face_region'][nearest_source_face]
    reverse_regions = {name: summary(backward[reverse_labels == index]) if (reverse_labels == index).any() else {'count': 0}
        for index, name in enumerate(contract['face_regions'])}
    output.mkdir()
    np.savez_compressed(output / 'all-distances.npz', forward_mm=forward, nearest_candidate_face=forward_face,
        reverse_mm=backward, reverse_sample_points_mm=reverse, reverse_sample_face=reverse_face,
        reverse_sample_barycentric=reverse_bary, nearest_source_face=nearest_source_face,
        nearest_source_region=reverse_labels)
    report = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'role': 'fixed reference-surface diagnostic, not complete product acceptance',
        'reference_contract_sha256': sha256_file(contract_path), 'candidate_record_sha256': sha256_file(record_path),
        'producer_sha256': sha256_file(Path(__file__)), 'all_distances_sha256': sha256_file(output / 'all-distances.npz'),
        'backend_versions': versions, 'sampler_sha256': contract['sampler_sha256'],
        'source_to_candidate': forward_regions, 'entire_candidate_to_full_source': summary(backward),
        'diagnostic_p95_2mm_targets': {name: value['p95_mm'] <= 2. for name, value in forward_regions.items()},
        'reverse_by_closest_source_region': reverse_regions,
        'reverse_outside_face_scope_fraction': float(np.mean(reverse_labels == 0)),
        'uncertainty': contract['uncertainty'],
        'limits': 'One fixed global similarity, no ICP/trimming. Regional membership is coarse; full-source includes documented defects. No scan acquisition accuracy or recognizable head acceptance.'}
    (output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
