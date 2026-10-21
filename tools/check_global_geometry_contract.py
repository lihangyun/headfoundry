"""Optional full-SfM software control, not a head reconstruction benchmark."""
import json
import os
from pathlib import Path
import sys
import threading
import time

import numpy as np


def project(k, pose, xyz):
    camera = xyz @ pose[:, :3].T + pose[:, 3]
    homogeneous = camera @ k.T
    return homogeneous[:, :2] / homogeneous[:, 2:], camera[:, 2]


def scene():
    rng = np.random.default_rng(276)
    xyz = rng.uniform([-.35, -.4, -.3], [.35, .4, .3], (270, 3))
    centers = np.array([[-.7, -.15, -3], [-.35, .2, -2.8], [0, -.1, -2.9],
                        [.4, .25, -2.85], [.75, -.2, -3.05]])
    poses = []
    for center in centers:
        forward = -center / np.linalg.norm(center)
        right = np.cross([0, 1, 0], forward)
        right /= np.linalg.norm(right)
        down = np.cross(forward, right)
        rotation = np.stack((right, down, forward))
        poses.append(np.column_stack((rotation, -rotation @ center)))
    k = np.array([[1200., 0, 360], [0, 1200, 640], [0, 0, 1]])
    ids = np.arange(270)
    observations = {}
    for i, pose in enumerate(poses):
        visible = (ids // 90 <= i) & (i <= ids // 90 + 2)
        uv, depth = project(k, pose, xyz[visible])
        assert (depth > 0).all() and (uv > 0).all() and (uv < [720, 1280]).all()
        # Store in the same OpenCV convention as the native-video observations.
        observations[i] = (ids[visible], uv - .5)
    return xyz, centers, np.stack(poses), k, observations


def similarity(source, target):
    x, y = source-source.mean(0), target-target.mean(0)
    u, d, vt = np.linalg.svd(y.T @ x / len(x))
    sign = np.ones(3)
    sign[-1] = np.linalg.det(u @ vt)
    rotation = u @ np.diag(sign) @ vt
    scale = np.sum(d * sign) / np.mean(np.sum(x*x, axis=1))
    translation = target.mean(0)-scale*rotation@source.mean(0)
    assert scale > 0 and np.linalg.det(rotation) > .999999
    return scale, rotation, translation


def run(out):
    import pycolmap as pc

    assert pc.__version__ == '4.2.0'
    out.mkdir(exist_ok=True)

    def save(name, data):
        with (out / name).open('x', encoding='utf8') as f:
            json.dump(data, f, indent=2, allow_nan=False)

    def timeout():
        save('timeout.json', {'stage': 'complete_worker', 'limit_seconds': 180})
        os._exit(124)

    timer = threading.Timer(180, timeout)
    timer.daemon = True
    timer.start()
    start = time.monotonic()
    xyz, truth_centers, truth_poses, truth_k, observations = scene()
    np.savez_compressed(out / 'synthetic-truth.npz', xyz=xyz, centers=truth_centers,
                        poses=truth_poses, K=truth_k)
    camera = pc.Camera(model='SIMPLE_PINHOLE', width=720, height=1280,
                       params=[1500., 360., 640.], has_prior_focal_length=False)
    images, pairs = {}, []
    with pc.Database.open(out / 'synthetic.db') as db:
        cam_id = db.write_camera(camera)
        for i, (ids, xy) in observations.items():
            train = ids % 5 != 0
            image_id = db.write_image(pc.Image(name=f'frame_{i:04d}.png', camera_id=cam_id))
            uv = (xy[train]+.5).astype(np.float32)
            db.write_keypoints(image_id, uv)
            assert np.array_equal(db.read_keypoints(image_id), uv)
            images[i] = (image_id, ids[train])
        for i in range(5):
            for j in range(i+1, 5):
                common, a, b = np.intersect1d(images[i][1], images[j][1], return_indices=True)
                if len(common) >= 30:
                    matches = np.column_stack((a, b)).astype(np.uint32)
                    assert np.array_equal(images[i][1][a], images[j][1][b])
                    db.write_matches(images[i][0], images[j][0], matches)
                    pairs.append((images[i][0], images[j][0]))
    g = pc.TwoViewGeometryOptions()
    g.ransac.max_error = 2.
    g.ransac.random_seed = 275
    g.ransac.num_threads = 4
    c = pc.ViewGraphCalibrationOptions()
    c.random_seed = 275
    m = pc.GlobalPipelineOptions()
    m.num_threads = m.mapper.num_threads = 4
    m.random_seed = m.mapper.random_seed = 275
    m.mapper.rotation_averaging.random_seed = 275
    m.mapper.global_positioning.random_seed = 275
    m.mapper.retriangulation.random_seed = 275
    m.mapper.global_positioning.use_gpu = False
    m.mapper.bundle_adjustment.ceres.use_gpu = False
    m.mapper.bundle_adjustment.ceres.solver_options.num_threads = 4
    m.mapper.bundle_adjustment.ceres.solver_options.trust_region_problem_dump_directory = str(out)
    save('controls.json', {'numpy': np.__version__, 'pycolmap': pc.__version__,
         'training_id_count': 216, 'held_id_count': 54, 'pairs': pairs,
         'geometry': g.summary(), 'calibration': c.summary(), 'mapping': m.summary()})
    with pc.Database.open(out / 'synthetic.db') as db:
        for a, b in pairs:
            geo = pc.estimate_two_view_geometry(camera, db.read_keypoints(a), camera,
                   db.read_keypoints(b), db.read_matches(a, b), options=g)
            db.write_two_view_geometry(a, b, geo)
    if not pc.calibrate_view_graph(out / 'synthetic.db', options=c):
        save('result.json', {'status': 'REJECT', 'reason': 'calibration_failed'})
        timer.cancel()
        return False
    (out / 'empty-images').mkdir()
    models = pc.global_mapping(out / 'synthetic.db', out / 'empty-images', out / 'sparse', options=m)
    save('mapping.json', {'models': {str(i): model.summary() for i, model in models.items()}})
    if len(models) != 1 or next(iter(models.values())).num_reg_images() != 5:
        save('result.json', {'status': 'REJECT', 'reason': 'missing_model_or_cameras', 'models': len(models)})
        timer.cancel()
        return False
    model = next(iter(models.values()))
    poses = {int(im.name[6:10]): im.cam_from_world().matrix()
             for im in model.images.values() if im.has_pose}
    centers = np.stack([-poses[i][:, :3].T @ poses[i][:, 3] for i in range(5)])
    anchors = [0, 2, 4]
    scale, gauge_r, gauge_t = similarity(centers[anchors], truth_centers[anchors])
    center_errors = np.linalg.norm(scale*centers@gauge_r.T+gauge_t-truth_centers, axis=1)
    assert len(model.cameras) == 1
    f, cx, cy = next(iter(model.cameras.values())).params
    k = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.]])
    errors, depths, rotations, negative = [], [], [], []
    for i, (ids, xy) in observations.items():
        held = ids % 5 == 0
        x = (xyz[ids[held]]-gauge_t)@gauge_r/scale
        uv, depth = project(k, poses[i], x)
        errors.extend(np.linalg.norm(uv-(xy[held]+.5), axis=1).tolist())
        depths.extend(depth.tolist())
        relative = poses[i][:, :3]@gauge_r.T@truth_poses[i][:, :3].T
        rotations.append(float(np.degrees(np.arccos(np.clip((np.trace(relative)-1)/2, -1, 1)))))
        if i == 0:
            cosine, sine = np.cos(.1), np.sin(.1)
            wrong = np.array([[1., 0, 0], [0, cosine, -sine], [0, sine, cosine]])@poses[i]
            bad_uv, _ = project(k, wrong, x)
            negative = np.linalg.norm(bad_uv-(xy[held]+.5), axis=1).tolist()
    # Check all fitted observations, separately from truly withheld projections.
    fitted_depths = []
    for im in model.images.values():
        p = im.cam_from_world().matrix()
        for point in im.points2D:
            if point.has_point3D():
                fitted_depths.append(float((p @ np.r_[model.points3D[point.point3D_id].xyz, 1.])[2]))
    proper = all(np.max(np.abs(p[:, :3]@p[:, :3].T-np.eye(3))) < 1e-7
                 and np.linalg.det(p[:, :3]) > .999999 for p in poses.values())
    p95 = float(np.percentile(errors, 95))
    negative_p95 = float(np.percentile(negative, 95))
    positive = bool(np.isfinite(depths).all() and min(depths+fitted_depths) > 0)
    passed = (len(model.points3D) >= 200 and proper and positive and abs(f/1200-1) <= .001
              and p95 <= .1 and max(rotations) <= .05 and max(center_errors) <= .001
              and negative_p95 > 3)
    save('result.json', {'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
         'scope': 'synthetic software chain only', 'registered': len(poses),
         'training_points': len(model.points3D), 'held_ids': 54, 'held_projections': len(errors),
         'focal_px': float(f), 'focal_relative_error': float(abs(f/1200-1)),
         'held_p95_px': p95, 'held_max_px': max(errors), 'rotation_errors_deg': rotations,
         'center_errors_scene_units': center_errors.tolist(), 'proper_rotations': proper,
         'positive_depths': positive, 'negative_control_p95_px': negative_p95,
         'worker_seconds': time.monotonic()-start, 'patient_accuracy': 'UNVERIFIED'})
    timer.cancel()
    return passed


if __name__ == '__main__':
    sys.exit(0 if run(Path(sys.argv[1]).resolve()) else 1)
