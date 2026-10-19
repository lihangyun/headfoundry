"""Blender integration fixtures only; no subject or reconstructed-head input."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file
from scan_motion_truth_0230 import sample_surface
from scan_surface_metric_0237 import apply_similarity, triangle_tree, nearest_triangles, summary


def main():
    out = ROOT / 'assets/private/real-capture-pilot-v1/scan-metric-fixtures-0237'
    if out.exists():
        raise FileExistsError('Preserve exact metric fixture result')
    vertices = np.array([[-100., -100., 0.], [100., -100., 0.], [0., 100., 0.],
        [200., -100., 10.], [400., -100., 10.], [300., 100., 10.]])
    # Reversed spatial order checks original polygon IDs, not internal BVH order.
    faces = np.array([[3, 4, 5], [0, 1, 2]])
    center = np.array([150., 0., 5.])
    tree = triangle_tree(vertices, faces, center)
    distance, ids = nearest_triangles(tree, np.array([[0., 0., 2.], [300., 0., 12.]]), center)
    if not np.array_equal(ids, [1, 0]) or not np.allclose(distance, 2., atol=1e-6, rtol=0):
        raise ValueError('Exact triangle distance or original polygon identity failed')
    original = vertices[:3].copy()
    tri = np.array([[0, 1, 2]])
    transform = np.diag([2., 2., 2., 1.])
    transform[2, 3] = 2.
    candidate = apply_similarity(original / 2, transform)
    source_points, _, _ = sample_surface(original, tri, 256, 237)
    candidate_points, _, _ = sample_surface(candidate, tri, 256, 237)
    forward, _ = nearest_triangles(triangle_tree(candidate, tri, center), source_points, center)
    reverse, _ = nearest_triangles(triangle_tree(original, tri, center), candidate_points, center)
    if max(abs(forward - 2.).max(), abs(reverse - 2.).max()) > .001:
        raise ValueError('Single-similarity two-direction fixture failed')
    # The omitted distant triangle must remain a large forward error, not be
    # discarded as unsupported; the reverse direction alone cannot detect it.
    missing, _ = nearest_triangles(triangle_tree(candidate, tri, center),
        np.array([[0., 0., 0.], [300., 0., 10.]]), center)
    if missing[1] <= 100. or summary(missing)['fraction_within_2mm'] != .5:
        raise ValueError('Missing-surface coverage was hidden')
    out.mkdir()
    np.savez_compressed(out / 'fixture-arrays.npz', face_identity=ids, interior_distance_mm=distance,
        source_points=source_points, candidate_points=candidate_points, forward_mm=forward,
        reverse_mm=reverse, missing_surface_forward_mm=missing)
    report = {'status': 'TECHNICAL_CHECK_PASSED', 'role': 'METRIC_FIXTURE_NOT_RECONSTRUCTION',
        'original_polygon_identity_preserved': True, 'triangle_interior_mm': distance.tolist(),
        'source_to_candidate': summary(forward), 'candidate_to_source': summary(reverse),
        'missing_surface_forward': summary(missing),
        'producer_sha256': sha256_file(Path(__file__)),
        'metric_sha256': sha256_file(ROOT / 'tools/scan_surface_metric_0237.py'),
        'limits': 'Analytic triangles only; no real scan/geometry quality or head acceptance.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
