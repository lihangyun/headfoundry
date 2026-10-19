"""Fixed independent-context Jacobian; only the residual endpoint sees pixels."""
import cv2
import numpy as np

from nonplanar_context_0231 import fit_context_fundamental
from temporal_video_sfm_0220 import refine_step


def local_jacobian(source, target, point):
    """Twelve-neighbor weighted affine slope; never return its intercept."""
    distance = np.linalg.norm(source - point, axis=1)
    neighbors = np.argsort(distance, kind='stable')[:12]
    scale = max(float(distance[neighbors[-1]]), 1.)
    design = np.c_[(source[neighbors] - point) / scale, np.ones(12)]
    weight = 1. / np.sqrt(1. + (distance[neighbors] / scale) ** 2)
    weighted = design * weight[:, None]
    condition = float(np.linalg.cond(weighted))
    if not np.isfinite(condition) or condition > 1000:
        return None, neighbors, condition
    # Subtract a target constant solely for numerical conditioning. Its fitted
    # intercept is discarded: this does not choose the measured endpoint.
    coefficient = np.linalg.lstsq(weighted,
        (target[neighbors] - target[neighbors].mean(axis=0)) * weight[:, None], rcond=None)[0]
    matrix = coefficient[:2].T / scale
    singular = np.linalg.svd(matrix, compute_uv=False)
    if np.linalg.det(matrix) <= 0 or singular.min() < .5 or singular.max() > 2:
        return None, neighbors, condition
    return matrix, neighbors, condition


def refine_local_geometry(previous, current, context_source, context_target, points, initial):
    points, initial = np.asarray(points, np.float64), np.asarray(initial, np.float64)
    source, target = np.asarray(context_source, np.float64), np.asarray(context_target, np.float64)
    if (previous.ndim != 2 or previous.dtype != np.uint8 or current.shape != previous.shape
            or current.dtype != np.uint8 or points.ndim != 2 or points.shape[1:] != (2,)
            or initial.shape != points.shape or not np.isfinite(points).all()
            or not np.isfinite(initial).all()):
        raise ValueError('Matching gray images and finite source/initial endpoints required')
    count = len(points)
    result = {'pixels': initial.copy(), 'eligible': np.zeros(count, bool),
        'fb_error': np.full(count, np.inf), 'patch_error': np.full(count, np.inf),
        'jacobians': np.full((count, 2, 2), np.nan),
        'neighbor_context_rows': np.full((count, 12), -1, np.int64),
        'design_condition': np.full(count, np.inf), 'failure_code': np.ones(count, np.uint8)}
    try:
        fundamental, inliers, context = fit_context_fundamental(source, target)
        result['context'] = context
        if fundamental is None or context['status'] != 'TECHNICAL_CHECK_PASSED':
            raise ValueError('Independent F context failed')
        if len(np.unique(source, axis=0)) != len(source):
            raise ValueError('Duplicate context source pixels')
        if any(np.any(np.all(source == point, axis=1)) for point in points):
            raise ValueError('Measurement pixels must not be their own context')
    except (ValueError, np.linalg.LinAlgError, cv2.error) as error:
        result['refinement_failure'] = str(error)
        return result
    result.update(fundamental=fundamental, context_inliers=inliers)
    context_rows = np.flatnonzero(inliers)
    height, width = current.shape
    y, x = np.mgrid[-19:20, -19:20]
    offsets = np.stack([x, y], axis=-1).astype(float)
    center = np.array([[19., 19.]], np.float32)
    for row, (point, seed) in enumerate(zip(points, initial)):
        matrix, neighbors, condition = local_jacobian(source[inliers], target[inliers], point)
        result['neighbor_context_rows'][row] = context_rows[neighbors]
        result['design_condition'][row] = condition
        if matrix is None:
            result['failure_code'][row] = 2
            continue
        result['jacobians'][row] = matrix
        if (point - 19 < 0).any() or (point + 19 >= [width - 1, height - 1]).any():
            result['failure_code'][row] = 3
            continue
        sampling = seed + offsets @ matrix.T
        if (sampling < 0).any() or (sampling >= [width - 1, height - 1]).any():
            result['failure_code'][row] = 4
            continue
        source_crop = cv2.getRectSubPix(previous, (39, 39), tuple(point))
        target_crop = cv2.remap(current, sampling[:, :, 0].astype(np.float32),
            sampling[:, :, 1].astype(np.float32), cv2.INTER_LINEAR)
        corrected, keep, fb, patch = refine_step(source_crop, target_crop, center, center)
        result['fb_error'][row], result['patch_error'][row] = fb[0], patch[0]
        if not keep[0]:
            result['failure_code'][row] = 5
            continue
        if (corrected[0] < 11).any() or (corrected[0] > 27).any():
            result['failure_code'][row] = 6
            continue
        result['pixels'][row] = seed + matrix @ (corrected[0] - center[0])
        result['eligible'][row] = True
        result['failure_code'][row] = 0
    return result
