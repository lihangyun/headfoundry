"""Perspective landmark bundle adjustment; no external model weights.

Coordinates: x image-right, y down, z away from camera in the frontal pose.
The first camera pose and the supplied focal lengths fix the camera gauge.
The shape prior fixes scale; recovered coordinates are not metric measurements.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def project(points, rotations, translations, intrinsics):
    camera = np.einsum('vij,nj->vni', rotations, points) + translations[:, None, :]
    if np.any(camera[..., 2] <= 0):
        raise ValueError('points must remain in front of every camera')
    pixels = np.einsum('vij,vnj->vni', intrinsics, camera)
    return pixels[..., :2] / pixels[..., 2:3]


def fit(document):
    prior = np.asarray(document['shape_prior'], float)
    observations = np.asarray(document['observations'], float)
    train = np.asarray(document['train_mask'], bool)
    validation = np.asarray(document['validation_mask'], bool)
    intrinsics = np.asarray(document['intrinsics'], float)
    rotations0 = np.asarray(document['rotation_vectors'], float)
    translations0 = np.asarray(document['translations'], float)
    views, count = observations.shape[:2]
    if prior.shape != (count, 3) or observations.shape != (views, count, 2):
        raise ValueError('invalid landmark shapes')
    if train.shape != (views, count) or validation.shape != train.shape:
        raise ValueError('invalid masks')
    if np.any(train & validation) or not validation.any():
        raise ValueError('independent validation observations required')
    view_names = document.get('view_names', [])
    for name in document.get('prior_source_views', []):
        if name not in view_names:
            raise ValueError('unknown shape-prior source view')
        if validation[view_names.index(name)].any():
            raise ValueError('shape-prior source view cannot supply held-out observations')
    if np.any(train.sum(axis=1) < 6) or np.any(train.sum(axis=0) < 2):
        raise ValueError('need six training points per view and two per landmark')
    for values in (prior, observations, intrinsics, rotations0, translations0):
        if not np.isfinite(values).all():
            raise ValueError('non-finite input')
    if intrinsics.shape != (views, 3, 3) or rotations0.shape != (views, 3) or translations0.shape != (views, 3):
        raise ValueError('invalid cameras')
    sigma = float(document.get('annotation_sigma_px', 4))
    strength = float(document.get('prior_strength', .2))
    if sigma <= 0 or strength <= 0:
        raise ValueError('positive uncertainty and regularization required')
    initial = np.r_[prior.ravel(), rotations0[1:].ravel(), translations0[1:].ravel()]

    def unpack(parameters):
        points = parameters[:count*3].reshape(count, 3)
        cut = count*3 + (views-1)*3
        r = np.vstack([rotations0[0], parameters[count*3:cut].reshape(-1, 3)])
        t = np.vstack([translations0[0], parameters[cut:].reshape(-1, 3)])
        return points, Rotation.from_rotvec(r).as_matrix(), t

    def residual(parameters):
        points, r, t = unpack(parameters)
        camera = np.einsum('vij,nj->vni', r, points) + t[:, None, :]
        h = np.einsum('vij,vnj->vni', intrinsics, camera)
        uv = h[..., :2] / np.maximum(h[..., 2:3], .01)
        return np.r_[((uv-observations)[train]/sigma).ravel(),
                     (strength*(points-prior)).ravel(),
                     (100*np.minimum(camera[..., 2]-.1, 0)).ravel()]

    solution = least_squares(residual, initial, loss='soft_l1', max_nfev=400)
    points, r, t = unpack(solution.x)
    predicted = project(points, r, t, intrinsics)
    errors = np.linalg.norm(predicted-observations, axis=-1)
    heldout = float(np.percentile(errors[validation], 95))
    return {
        'status': 'UNVERIFIED' if solution.success and heldout <= 3 else 'REJECT',
        'optimizer_converged': bool(solution.success),
        'train_p95_px': float(np.percentile(errors[train], 95)),
        'validation_p95_px': heldout,
        'validation_threshold_passed': bool(heldout <= 3),
        'shape': points.tolist(), 'intrinsics': intrinsics.tolist(),
        'extrinsics': np.concatenate([r, t[..., None]], axis=2).tolist(),
        'predicted_pixels': predicted.tolist(),
        'limitations': 'Focal length and shape scale are priors; no full camera or visual acceptance implied.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('observations', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = fit(json.loads(args.observations.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('status', 'optimizer_converged', 'train_p95_px', 'validation_p95_px')}))


if __name__ == '__main__':
    main()
