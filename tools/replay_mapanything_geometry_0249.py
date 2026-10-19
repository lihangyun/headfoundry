"""Frozen-output evaluator replay; no model execution or parameter search."""
import json
from pathlib import Path
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file
from direct_geometry_capacity_0236 import evaluate_camera_only, population, projection_result
from mapanything_geometry_0249 import sample_points, convention_report


def main():
    output = ROOT/'assets/private/mapanything-apache-0248/known-geometry-0249'
    source = ROOT/'assets/private/real-capture-pilot-v1/scan-motion-truth-0230-upright'
    controls = json.loads((output/'controls.json').read_text(encoding='utf-8'))
    report = json.loads((output/'report.json').read_text(encoding='utf-8'))
    preprocessing = json.loads((output/'preprocessing.json').read_text(encoding='utf-8'))
    if (sha256_file(output/'predictions.npz') != report['predictions_sha256']
            or sha256_file(source/'known-motion.npz') != controls['known_archive_sha256']
            or sha256_file(ROOT/'tools/direct_geometry_capacity_0236.py') != controls['evaluator_sha256']
            or sha256_file(ROOT/'tools/mapanything_geometry_0249.py') != controls['helper_sha256']):
        raise ValueError('Frozen outputs/evaluator identity changed')
    known = np.load(source/'known-motion.npz', allow_pickle=False)
    arrays = dict(np.load(output/'predictions.npz', allow_pickle=False))
    transform = np.array(preprocessing['pixel_center_transform'])
    e = np.linalg.inv(arrays['camera_poses'].astype(float))[:, :3]
    k = np.linalg.inv(transform)[None]@arrays['intrinsics']
    camera, records = evaluate_camera_only(known, k, e)
    if camera != report['camera_only'] or convention_report(arrays) != report['conventions']:
        raise ValueError('Camera/convention numerical replay differs')
    max_replay = 0.
    counts = []
    for view in range(1, 6):
        selected = population(known, (0, view))
        xy = known['pixels'][0, selected]-.5
        processed = np.c_[xy, np.ones(len(xy))]@transform.T
        points = sample_points(arrays['pts3d'][0], processed[:, :2])
        score, pixels, errors = projection_result(points, k[view], e[view], known['pixels'][view, selected]-.5)
        saved = np.load(output/('joint-'+str(known['view_names'][view])+'.npz'), allow_pickle=False)
        if score != report['point_map_pose'][view-1]['prediction'] or not np.array_equal(saved['point_ids'], known['point_ids'][selected]):
            raise ValueError('Joint result/population changed')
        max_replay = max(max_replay, float(np.max(abs(saved['predicted']-pixels))), float(np.max(abs(saved['errors']-errors))))
        counts.append(int(selected.sum()))
    if max_replay > 1e-9:
        raise ValueError('Saved projection replay failed')
    value = dict(numerical_replay='TECHNICAL_CHECK_PASSED', geometry_screen=report['screen_status'],
        maximum_projection_replay_px=max_replay, unfiltered_joint_counts=counts,
        source_archive_sha256=controls['known_archive_sha256'], predictions_sha256=report['predictions_sha256'],
        producer_sha256=sha256_file(Path(__file__)), model_rerun=False,
        limits='Evaluator replay,not new precision evidence or head acceptance.')
    path = output/'numerical-replay.json'
    if path.exists():
        raise FileExistsError('Preserve first replay')
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(value))


if __name__ == '__main__':
    main()
