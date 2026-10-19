"""Native shared-prior projection math; no scan or file access."""
import cv2
import numpy as np


def camera(state, initial):
    state, initial = np.asarray(state, float), np.asarray(initial, float)
    if state.shape != (6,) or initial.shape != (6,) or initial[5] <= 0:
        raise ValueError('Six pose coordinates and positive initial depth required')
    rotation = initial[:3] + .1 * state[:3]
    translation = initial[3:].copy()
    translation[:2] += .1 * state[3:5]
    translation[2] *= np.exp(.5 * state[5])
    matrix, derivative = cv2.Rodrigues(rotation)
    return matrix, translation, derivative.reshape(3, 3, 3)


def residual_jacobian(state, base, directions, observations, views, initial):
    """Residuals/4 plus unit identity prior; rows match finite-difference tests."""
    dimensions = directions.shape[-1]
    if (base.shape != observations.shape[:1] + (3,) or directions.shape != (*base.shape, dimensions)
            or observations.shape != (len(base), 2) or views.shape != (len(base),)
            or initial.ndim != 2 or initial.shape[1] != 6
            or state.shape != (dimensions + 6 * len(initial) + 1,)
            or not all(np.isfinite(a).all() for a in (state, base, directions, observations, initial))
            or (views < 0).any() or (views >= len(initial)).any()):
        raise ValueError('Finite shared prior, observations and matching state required')
    beta = state[:dimensions]
    points = base + np.einsum('nck,k->nc', directions, beta)
    focal = 1000 * np.exp(.3 * state[-1])
    residual = np.empty((len(base), 2))
    jacobian = np.zeros((len(base), 2, len(state)))
    for view in range(len(initial)):
        chosen = np.flatnonzero(views == view)
        start = dimensions + 6 * view
        rotation, translation, derivative = camera(state[start:start + 6], initial[view])
        cam = points[chosen] @ rotation.T + translation
        if (cam[:, 2] <= 1e-6).any():
            raise ValueError('Positive camera depth required')
        xy = cam[:, :2] / cam[:, 2:]
        residual[chosen] = (focal * xy + [360, 640] - observations[chosen]) / 4
        dp = np.zeros((len(chosen), 2, 3))
        dp[:, 0, 0] = focal / cam[:, 2]
        dp[:, 1, 1] = focal / cam[:, 2]
        dp[:, :, 2] = -focal * xy / cam[:, 2, None]
        jacobian[chosen, :, :dimensions] = np.einsum('nij,jc,nck->nik', dp, rotation, directions[chosen]) / 4
        dr = .1 * np.einsum('kij,nj->nik', derivative, points[chosen])
        jacobian[chosen, :, start:start + 3] = np.einsum('nij,njk->nik', dp, dr) / 4
        jacobian[chosen, :, start + 3:start + 5] = dp[:, :, :2] * .1 / 4
        jacobian[chosen, :, start + 5] = dp[:, :, 2] * (.5 * translation[2]) / 4
        jacobian[chosen, :, -1] = .3 * focal * xy / 4
    regularization = np.zeros((dimensions, len(state)))
    regularization[:, :dimensions] = np.eye(dimensions)
    return np.r_[residual.ravel(), beta], np.vstack([jacobian.reshape(-1, len(state)), regularization])


def project(points, extrinsic, intrinsic):
    cam = points @ extrinsic[:, :3].T + extrinsic[:, 3]
    if (cam[:, 2] <= 1e-6).any():
        raise ValueError('Positive camera depth required')
    h = cam @ intrinsic.T
    return h[:, :2] / h[:, 2:]


def visible_support(vertices, faces, points, extrinsic, intrinsic, skin):
    from headfoundry.raster import lift_pixels
    ids, bary = lift_pixels(vertices, faces, extrinsic, intrinsic,
        project(points, extrinsic, intrinsic), allowed_faces=skin)
    hit = ids >= 0
    gap = np.full(len(points), np.inf)
    lifted = np.einsum('ni,nij->nj', bary[hit], vertices[faces[ids[hit]]])
    gap[hit] = np.linalg.norm(lifted - points[hit], axis=1)
    return gap <= 1e-5, gap
