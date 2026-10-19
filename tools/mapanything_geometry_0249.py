"""Pixel-center transport and unfiltered point-map evaluation helpers."""
import numpy as np


def resize_transform(original_wh, target_wh):
    original, target = np.asarray(original_wh, int), np.asarray(target_wh, int)
    if original.shape != (2,) or target.shape != (2,) or (original <= 0).any() or (target <= 0).any():
        raise ValueError('Positive width,height pairs required')
    resized = np.floor(original*(np.max(target/original)+1e-8)).astype(int)
    crop = (resized-target)//2
    scale = resized/original
    matrix = np.array([[scale[0], 0, (scale[0]-1)/2-crop[0]],
        [0, scale[1], (scale[1]-1)/2-crop[1]], [0, 0, 1.]])
    return matrix, tuple(map(int, resized)), tuple(map(int, crop))


def sample_points(points, pixels):
    points, pixels = np.asarray(points, float), np.asarray(pixels, float)
    if points.ndim != 3 or points.shape[2] != 3 or pixels.ndim != 2 or pixels.shape[1] != 2:
        raise ValueError('HxWx3 map and Nx2 pixels required')
    h, w = points.shape[:2]
    valid = np.isfinite(pixels).all(axis=1) & (pixels >= 0).all(axis=1) & (pixels < [w-1, h-1]).all(axis=1)
    output = np.full((len(pixels), 3), np.nan)
    xy = pixels[valid]
    lo = np.floor(xy).astype(int)
    x, y = lo.T
    dx, dy = (xy-lo).T
    output[valid] = ((1-dx)*(1-dy))[:, None]*points[y, x] + (dx*(1-dy))[:, None]*points[y, x+1] + ((1-dx)*dy)[:, None]*points[y+1, x] + (dx*dy)[:, None]*points[y+1, x+1]
    return output


def convention_report(arrays):
    k, c2w = arrays['intrinsics'], arrays['camera_poses']
    cam, world, rays = arrays['pts3d_cam'], arrays['pts3d'], arrays['ray_directions']
    if (k.shape != (6, 3, 3) or c2w.shape != (6, 4, 4) or cam.shape != world.shape
            or rays.shape != cam.shape or cam.ndim != 4 or cam.shape[0] != 6 or cam.shape[-1] != 3):
        raise ValueError('Exact six-view camera/point/ray batches required')
    if not all(np.isfinite(value).all() for value in arrays.values()):
        raise ValueError('Nonfinite unfiltered prediction')
    if not np.allclose(c2w[:, 3], [0, 0, 0, 1], atol=1e-6, rtol=0):
        raise ValueError('Homogeneous C2W matrices required')
    expected = np.einsum('vhwj,vij->vhwi', cam, c2w[:, :3, :3])+c2w[:, None, None, :3, 3]
    difference = np.linalg.norm(expected-world, axis=-1)
    relative_max = float(difference.max()/max(np.linalg.norm(world, axis=-1).max(), 1e-8))
    q = np.einsum('vhwj,vij->vhwi', rays, k)
    with np.errstate(divide='ignore', invalid='ignore'):
        xy = q[..., :2]/q[..., 2:]
    yy, xx = np.indices(cam.shape[1:3])
    errors = np.linalg.norm(xy-np.stack([xx, yy], axis=-1), axis=-1)
    finite = bool(np.isfinite(errors).all())
    p95 = [float(np.percentile(e, 95)) for e in errors] if finite else None
    positive = bool((cam[..., 2] > 0).all() and (rays[..., 2] > 0).all())
    return {'camera_to_world_relative_max': relative_max,
        'pinhole_ray_p95_processed_px': p95, 'all_positive_camera_z_and_rays': positive,
        'passed': bool(relative_max <= 1e-5 and positive and finite and max(p95) <= .5)}
