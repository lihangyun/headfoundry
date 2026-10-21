"""Known-camera point witnesses; not a camera estimator or a surface benchmark."""
import json
import cv2
import numpy as np

from headfoundry.camera import project
from headfoundry.epipolar import _triangulate


def stereo_depth(focal, baseline, disparity):
    values = np.asarray([focal, baseline, disparity], float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError('Positive finite focal/baseline/disparity required')
    return float(focal * baseline / disparity)


def witness(baseline, perturbation, scale=1.):
    intrinsic = np.array([[1000., 0, 360], [0, 1000, 640], [0, 0, 1]])
    point = np.array([[0., 0, 600.]]) * scale
    centers = np.array([[-baseline/2, 0, 0], [baseline/2, 0, 0], [100., 0, 0]]) * scale
    extrinsics = np.array([np.c_[np.eye(3), -center] for center in centers])
    projections = np.array([intrinsic @ e for e in extrinsics])
    exact = np.array([project(p, point) for p in projections])
    observed = exact[:2].copy()
    observed[0, 0, 0] += perturbation
    observed[1, 0, 0] -= perturbation
    estimate = _triangulate(observed[0], observed[1], projections[0], projections[1])
    homogeneous = cv2.triangulatePoints(projections[0], projections[1], observed[0].T, observed[1].T)
    independent = (homogeneous[:3] / homogeneous[3]).T
    analytic = np.array([[0., 0, stereo_depth(1000., baseline*scale,
                                              observed[0, 0, 0]-observed[1, 0, 0])]])
    if max(np.abs(estimate-analytic).max(), np.abs(independent-analytic).max()) > 1e-6:
        raise ValueError('Independent triangulation disagreement')
    replay = _triangulate(exact[0], exact[1], projections[0], projections[1])
    if np.abs(replay-point).max() > 1e-8:
        raise ValueError('Zero-noise metric replay')
    if not all((estimate @ e[:, :3].T + e[:, 3])[:, 2].min() > 0 for e in extrinsics):
        raise ValueError('Cheirality')
    pixels = np.concatenate([exact[:, 0], observed[:, 0]])
    if not ((pixels >= 0).all() and (pixels[:, 0] < 720).all() and (pixels[:, 1] < 1280).all()):
        raise ValueError('Native image bounds')
    held = float(np.linalg.norm(project(projections[2], estimate) - exact[2]))
    error = float(np.linalg.norm(estimate-point))
    return {'observation_error_px': abs(perturbation), 'baseline_mm': baseline*scale,
        'point_error_mm': error, 'held_projection_error_px': held,
        'conditional_point_2mm_and_held_3px': error <= 2 and held <= 3,
        'estimated_depth_mm': float(estimate[0, 2]), 'all_camera_pixels': exact.tolist()}


def check():
    narrow, wide = witness(20., .75), witness(420., 1.1)
    if narrow['conditional_point_2mm_and_held_3px'] or not wide['conditional_point_2mm_and_held_3px']:
        raise ValueError('Registered counterexamples not reproduced')
    scaled = witness(420., 1.1, 2.3)
    if (not np.allclose(scaled['all_camera_pixels'], wide['all_camera_pixels'], atol=1e-10, rtol=0)
            or abs(scaled['point_error_mm'] - 2.3*wide['point_error_mm']) > 1e-8
            or abs(scaled['held_projection_error_px'] - wide['held_projection_error_px']) > 1e-8):
        raise ValueError('Scale/pixel invariance')
    for invalid in (0., -1., float('nan')):
        try:
            stereo_depth(1000., 20., invalid)
        except ValueError:
            continue
        raise ValueError('Invalid disparity accepted')
    return {'status': 'TECHNICAL_CHECK_PASSED', 'scope': 'Conditional synthetic point witnesses only',
        'narrow': narrow, 'wide': wide, 'scaled': scaled,
        'opencv_dlt_closed_form_controls': True, 'model_or_private_input_read': False,
        'camera_head_surface_acceptance': 'UNVERIFIED'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
