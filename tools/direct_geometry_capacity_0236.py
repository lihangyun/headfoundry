"""Fixed known3D evaluation; no camera optimization or residual pruning."""
import numpy as np

from headfoundry.epipolar import _triangulate
from headfoundry.fusion import _sample_depth

SCALE = .525
RESIZE = np.array([[SCALE, 0, (SCALE - 1) / 2],
                   [0, SCALE, (SCALE - 1) / 2], [0, 0, 1.]])


def camera_structure(intrinsics, extrinsics):
    k, e = np.asarray(intrinsics, float), np.asarray(extrinsics, float)
    if (k.ndim != 3 or k.shape[1:] != (3, 3) or e.shape != (len(k), 3, 4)
            or not np.isfinite(k).all() or not np.isfinite(e).all()):
        raise ValueError('Finite matching camera batches required')
    r = e[:, :, :3]
    proper = bool(np.allclose(r @ r.transpose(0, 2, 1), np.eye(3), atol=1e-4, rtol=0)
        and np.allclose(np.linalg.det(r), 1, atol=1e-4, rtol=0))
    formatted = bool(np.allclose(k[:, 2], [0, 0, 1], atol=1e-6, rtol=0)
        and np.allclose(k[:, 1, 0], 0, atol=1e-6, rtol=0))
    focal = np.c_[k[:, 0, 0], k[:, 1, 1]]
    plausible = bool(((focal >= 400) & (focal <= 3000)).all())
    return {'proper_rotations': proper, 'intrinsic_format': formatted,
        'focal_400_to_3000_original_px': plausible, 'focal_original_px': focal.tolist(),
        'passed': proper and formatted and plausible}


def population(known, views):
    boxed = ((known['pixels'] >= [100, 500]) & (known['pixels'] < [620, 820])).all(axis=2)
    return np.all(known['visible'][list(views)] & boxed[list(views)], axis=0)


def unproject_samples(depth, intrinsic, extrinsic, pixels):
    """Sample all requested zero-centered pixels; unsupported rows remain NaN."""
    depth, k, e, pixels = map(lambda x: np.asarray(x, float), (depth, intrinsic, extrinsic, pixels))
    if (depth.ndim != 2 or k.shape != (3, 3) or e.shape != (3, 4)
            or pixels.ndim != 2 or pixels.shape[1:] != (2,)
            or not all(np.isfinite(x).all() for x in (depth, k, e, pixels)) or (depth <= 0).any()):
        raise ValueError('Finite positive z-depth, camera and Nx2 pixels required')
    indices, z = _sample_depth(depth, np.ones(depth.shape, bool), pixels, True)
    result = np.full((len(pixels), 3), np.nan)
    rays = np.c_[pixels[indices], np.ones(len(indices))] @ np.linalg.inv(k).T
    result[indices] = (rays * z[:, None] - e[:, 3]) @ e[:, :3]
    return result


def projection_result(points, k, e, expected):
    points, k, e, expected = map(lambda x: np.asarray(x, float), (points, k, e, expected))
    if (points.ndim != 2 or points.shape[1:] != (3,) or not len(points)
            or expected.shape != (len(points), 2) or not np.isfinite(expected).all()
            or k.shape != (3, 3) or e.shape != (3, 4)):
        raise ValueError('Nonempty matching point/projection observations required')
    camera = points @ e[:, :3].T + e[:, 3]
    q = camera @ k.T
    positive = np.isfinite(camera).all(axis=1) & (camera[:, 2] > 1e-8)
    supported = positive & np.isfinite(q).all(axis=1) & (abs(q[:, 2]) > 1e-10)
    pixels = np.full((len(points), 2), np.nan)
    pixels[supported] = q[supported, :2] / q[supported, 2:]
    errors = np.full(len(points), np.inf)
    errors[supported] = np.linalg.norm(pixels[supported] - expected[supported], axis=1)
    finite = bool(np.isfinite(errors).all())
    summary = {'count': len(errors), 'invalid_count': int((~np.isfinite(errors)).sum()),
        'positive_depth_fraction': float(positive.mean()),
        'p50_px': float(np.median(errors)) if finite else None,
        'p95_px': float(np.percentile(errors, 95)) if finite else None,
        'max_px': float(errors.max()) if finite else None,
        'passed': bool(finite and positive.all() and np.percentile(errors, 95) <= 3.)}
    return summary, pixels, errors


def evaluate_camera_only(known, k, e):
    structure = camera_structure(k, e)
    if len(e) != len(known['view_names']):
        raise ValueError('Exact declared view order required')
    truth = known['pixels'] - .5
    records, archives = [], {}
    for target in range(2, len(e)):
        selected = population(known, (0, 1, target))
        first, second = truth[0, selected], truth[1, selected]
        if selected.sum() < 200 or (np.ptp(first, axis=0) < 50).any():
            raise ValueError('Frozen three-view point support insufficient')
        points = _triangulate(first, second, k[0] @ e[0], k[1] @ e[1])
        projections = [projection_result(points, k[v], e[v], truth[v, selected]) for v in (0, 1, target)]
        passed = structure['passed'] and all(p[0]['passed'] for p in projections)
        name = str(known['view_names'][target])
        records.append({'view': name, 'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
            'source_front': projections[0][0], 'source_yaw_minus10': projections[1][0],
            'independent_view': projections[2][0]})
        archives[name] = {'point_ids': known['point_ids'][selected], 'triangulated': points,
            'predicted': np.stack([p[1] for p in projections]), 'errors': np.stack([p[2] for p in projections]),
            'truth': truth[[0, 1, target]][:, selected]}
    return {'structure': structure, 'results': records,
        'status': 'TECHNICAL_CHECK_PASSED' if all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT'}, archives


def relative_pose_errors(predicted, expected):
    records = []
    for view in range(1, len(expected)):
        rotations, translations = [], []
        for e in (predicted, expected):
            r = e[view, :, :3] @ e[0, :, :3].T
            rotations.append(r)
            translations.append(e[view, :, 3] - r @ e[0, :, 3])
        angle = float(np.rad2deg(np.arccos(np.clip((np.trace(rotations[0] @ rotations[1].T) - 1) / 2, -1, 1))))
        norm = np.linalg.norm(translations[0]) * np.linalg.norm(translations[1])
        direction = float(np.rad2deg(np.arccos(np.clip(np.dot(*translations) / norm, -1, 1)))) if norm > 1e-12 else None
        records.append({'view_index': view, 'relative_rotation_deg': angle, 'translation_direction_deg': direction})
    return records
