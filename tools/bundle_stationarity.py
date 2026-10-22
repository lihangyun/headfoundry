"""Read-only native-camera numerical diagnostic;never applies an estimated step."""
import cv2
import numpy as np
from scipy.sparse.linalg import lsmr
from short_track_camera import intrinsics, project


def linearize(k, poses, points, train, anchor, baseline):
    """Original frozen parameterization/Jacobian;never fits or applies a step."""
    values, blocks = [float(np.log(k[0, 0]))], {}
    for camera in range(len(poses)):
        if camera == anchor:
            continue
        rotation = cv2.Rodrigues(poses[camera, :3, :3])[0].ravel().tolist()
        translation = poses[camera, :3, 3]
        if camera == baseline:
            tail = [np.arctan2(translation[1], translation[0]),
                    np.arctan2(translation[2], np.linalg.norm(translation[:2]))]
        else:
            tail = translation.tolist()
        blocks[camera] = len(values)
        values.extend(rotation+tail)
    offset = len(values)
    values = np.r_[values, points.ravel()]

    def residual(x):
        camera_poses = np.repeat(np.eye(4)[None], len(poses), axis=0)
        for camera, start in blocks.items():
            camera_poses[camera, :3, :3] = cv2.Rodrigues(x[start:start+3])[0]
            if camera == baseline:
                theta, phi = x[start+3:start+5]
                camera_poses[camera, :3, 3] = [np.cos(phi)*np.cos(theta), np.cos(phi)*np.sin(theta), np.sin(phi)]
            else:
                camera_poses[camera, :3, 3] = x[start+3:start+6]
        xy, _ = project(intrinsics(x[0]), camera_poses, x[offset:].reshape(-1, 3), train)
        return (xy-train[:, 2:]).ravel()

    r = residual(values)
    source, _ = project(k, poses, points, train)
    replay = float(np.max(np.abs(r-(source-train[:, 2:]).ravel())))
    assert replay <= 1e-8, 'frozen forward replay differs'

    def jacobian(step):
        result = np.empty((len(r), len(values)))
        for column in range(len(values)):
            h = step*max(1., abs(values[column]))
            first, second = values.copy(), values.copy()
            first[column] += h
            second[column] -= h
            result[:, column] = (residual(first)-residual(second))/(2*h)
        return result

    jac = jacobian(1e-5)
    witness = jacobian(.5e-5)
    consistency = float(np.linalg.norm(jac-witness)/max(np.linalg.norm(witness), 1e-30))
    assert consistency <= 1e-5, 'finite-difference witness differs'
    return r, jac, replay, consistency


def focal_information(jac, rcond=1e-12):
    """Local unit-noise focal sensitivity;undefined when nuisance-confounded."""
    jac = np.asarray(jac, dtype=float)
    if jac.ndim != 2 or jac.shape[1] < 1 or not np.isfinite(jac).all():
        raise ValueError('finite two-dimensional Jacobian with focal column required')
    scales = np.linalg.norm(jac, axis=0)
    normalized = jac/np.maximum(scales, 1e-30)
    nuisance = normalized[:, 1:]
    coefficient, _, nuisance_rank, nuisance_singular = np.linalg.lstsq(nuisance, jac[:, 0], rcond=rcond)
    contrast = jac[:, 0]-nuisance@coefficient
    singular = np.linalg.svd(normalized, compute_uv=False)
    rank = int(np.sum(singular > (singular[0]*rcond if len(singular) else 0)))
    identifiable = bool(rank == nuisance_rank+1 and scales[0] > 0)
    norm = float(np.linalg.norm(contrast))
    return {'focal_identifiable_locally':identifiable, 'rank':rank, 'nuisance_rank':int(nuisance_rank),
            'column_normalized_singular_values':singular.tolist(),
            'nuisance_column_normalized_singular_values':nuisance_singular.tolist(),
            'profile_focal_column_norm':norm, 'raw_focal_column_norm':float(scales[0]),
            'sigma_log_f_per_unit_pixel_noise':float(1/norm) if identifiable and norm > 0 else None}


def audit(k, poses, points, train, anchor, baseline):
    """Evaluate original frozen soft_l1 objective;no held observations accepted."""
    r, jac, replay, consistency = linearize(k, poses, points, train, anchor, baseline)
    # Exact soft_l1 score and Gauss-Newton curvature at the fixed endpoint.
    root = np.sqrt(1+(r/1.5)**2)
    psi = r/root
    weight = root**(-1.5)
    matrix = jac*weight[:, None]
    target = -psi/weight
    column_scale = np.maximum(np.linalg.norm(matrix, axis=0), 1e-30)
    matrix /= column_scale
    gradient = matrix.T@(r*root**.5)
    dense, _, rank, singular = np.linalg.lstsq(matrix, target, rcond=1e-12)
    iterative = lsmr(matrix, target, atol=1e-6, btol=1e-6)

    def linear_result(step):
        remaining = matrix@step-target
        return {'step_norm':float(np.linalg.norm(step)),
                'residual_norm':float(np.linalg.norm(remaining)),
                'normal_residual_inf':float(np.max(np.abs(matrix.T@remaining)))}

    return {'forward_replay_max_px':replay, 'jacobian_relative_witness_error':consistency,
            'rows':len(r), 'variables':jac.shape[1], 'rank_at_relative_1e_minus_12':int(rank),
            'column_normalized_singular_values':singular.tolist(),
            'soft_l1_cost':float(np.sum(2.25*(root-1))),
            'unscaled_gradient_inf':float(np.max(np.abs(jac.T@psi))),
            'column_normalized_gradient_inf':float(np.max(np.abs(gradient))),
            'dense_local_linear':linear_result(dense), 'lsmr_local_linear':linear_result(iterative[0]),
            'lsmr_stop':int(iterative[1]), 'lsmr_iterations':int(iterative[2]),
            'array_bytes':int(2*jac.nbytes+matrix.nbytes+jac.shape[1]*8+target.nbytes),
            'no_step_applied':True, 'scope':'undamped local linearization,not actual trust-region trajectory'}
