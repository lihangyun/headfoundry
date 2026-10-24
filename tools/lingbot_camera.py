"""Fixed upstream crop coordinates and native W2C cameras; no pose estimation."""
import numpy as np
from scipy.spatial.transform import Rotation


def crop_transform(width, height):
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise ValueError('positive integer native dimensions required')
    resized_height = round(height * (518 / width) / 14) * 14
    if resized_height <= 0:
        raise ValueError('empty resized image')
    top = max(0, (resized_height-518)//2)
    sx, sy = 518/width, resized_height/height
    # PIL pixel-center mapping: dst+.5 = scale*(src+.5), followed by crop.
    affine = np.array([[sx, 0, (sx-1)/2],
                       [0, sy, (sy-1)/2-top], [0, 0, 1.]])
    return affine, (min(resized_height, 518), 518), (518, resized_height), top


def native_camera(pose, width, height):
    pose = np.asarray(pose, dtype=float)
    if pose.shape != (9,) or not np.isfinite(pose).all():
        raise ValueError('finite nine-component camera encoding required')
    if not (0 < pose[7] < np.pi and 0 < pose[8] < np.pi):
        raise ValueError('FoVs must be strictly between zero and pi')
    q = pose[3:7]
    if np.linalg.norm(q) < 1e-12:
        raise ValueError('zero quaternion')
    affine, (h, w), _, _ = crop_transform(width, height)
    rotation = Rotation.from_quat(q).as_matrix()  # upstream XYZW, C2W
    w2c = np.column_stack((rotation.T, -rotation.T @ pose[:3]))
    model_k = np.array([[w/2/np.tan(pose[8]/2), 0, w/2],
                        [0, h/2/np.tan(pose[7]/2), h/2], [0, 0, 1.]])
    native_k = np.linalg.solve(affine, model_k)
    return native_k, w2c
