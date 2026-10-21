"""One bounded global-SfM attempt. Patient observations stay local."""
import hashlib
import io
import json
import os
import threading
import time
import zipfile
from pathlib import Path

import numpy as np
import pycolmap as pc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/global-short-track-0275'
ARCHIVE = ROOT / 'assets/private/closed-experiments/0267-native-dense-video/evidence.zip'
EXPECTED = '54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612'


def save(name, value):
    path = OUT / name
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def arrays():
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == EXPECTED
    with zipfile.ZipFile(ARCHIVE) as z:
        n = next(n for n in z.namelist() if n.endswith('/observations.npz'))
        with np.load(io.BytesIO(z.read(n)), allow_pickle=False) as a:
            frame, ids, xy = (a[k].copy() for k in ('frame', 'ids', 'xy'))
    use = frame <= 876
    frame, ids, xy = frame[use], ids[use], xy[use].astype(np.float64)
    assert np.isfinite(xy).all() and (xy >= 0).all()
    assert (xy < [720, 1280]).all()
    unique_observations(frame, ids)
    assert np.array_equal(np.unique(frame), np.arange(0, 877, 12))
    return frame, ids, xy


def unique_observations(frame, ids):
    pairs = np.column_stack((frame, ids))
    if len(np.unique(pairs, axis=0)) != len(pairs):
        raise ValueError('duplicate frame/identity')


def deadline(stage, seconds):
    def stop():
        save('timeout.json', {'stage': stage, 'seconds': seconds})
        os._exit(124)
    timer = threading.Timer(seconds, stop)
    timer.daemon = True
    timer.start()
    return timer


def triangulate(p1, p2, xy1, xy2):
    a = np.stack((xy1[0]*p1[2]-p1[0], xy1[1]*p1[2]-p1[1],
                  xy2[0]*p2[2]-p2[0], xy2[1]*p2[2]-p2[1]))
    _, _, v = np.linalg.svd(a)
    return v[-1, :3] / v[-1, 3]


def project(p, x):
    h = p @ np.r_[x, 1.]
    return h[:2] / h[2]


def controls():
    k = np.array([[1500., 0, 360], [0, 1500, 640], [0, 0, 1]])
    a = np.column_stack((np.eye(3), [0., 0, 0]))
    b = np.column_stack((np.eye(3), [-.4, 0, 0]))
    truth = np.array([.13, -.09, 3.2])
    p1, p2 = k @ a, k @ b
    u1, u2 = project(p1, truth), project(p2, truth)
    x = triangulate(p1, p2, u1, u2)
    camera = pc.Camera(model='SIMPLE_PINHOLE', width=720, height=1280,
                       params=[1500., 360., 640.])
    lib_xy = camera.img_from_cam(truth)
    replay = float(np.max(np.abs(lib_xy-u1)))
    err = float(np.linalg.norm(x-truth))
    # Stored OpenCV coordinates are COLMAP pixel centers minus .5.
    assert np.max(np.abs((u1-.5)+.5-u1)) < 1e-7
    assert replay < 1e-7 and err < 1e-7
    try:
        unique_observations(np.array([0, 0]), np.array([5, 5]))
    except ValueError:
        pass
    else:
        raise AssertionError('duplicate guard failed')
    save('implementation-control.json', {'projection_max_px': replay,
         'triangulation_scene_units': err, 'pycolmap': pc.__version__})


def prepare():
    controls()
    frame, ids, xy = arrays()
    train = ids % 5 != 0
    keys = np.unique(frame)
    camera = pc.Camera(model='SIMPLE_PINHOLE', width=720, height=1280,
                       params=[1500., 360., 640.], has_prior_focal_length=False)
    by_frame = {}
    pair_lines, pair_info = [], []
    with pc.Database.open(OUT / 'tracks.db') as db:
        camera_id = db.write_camera(camera)
        for f in keys:
            rows = np.flatnonzero((frame == f) & train)
            order = rows[np.argsort(ids[rows])]
            name = f'frame_{f:04d}.png'
            image_id = db.write_image(pc.Image(name=name, camera_id=camera_id))
            uv = (xy[order]+.5).astype(np.float32)
            db.write_keypoints(image_id, uv)
            assert np.array_equal(db.read_keypoints(image_id), uv)
            by_frame[int(f)] = (image_id, name, ids[order])
        for i, f1 in enumerate(keys):
            id1, n1, ids1 = by_frame[int(f1)]
            for f2 in keys[i+1:]:
                id2, n2, ids2 = by_frame[int(f2)]
                common, q1, q2 = np.intersect1d(ids1, ids2, return_indices=True)
                if len(common) < 30:
                    continue
                matches = np.column_stack((q1, q2)).astype(np.uint32)
                assert np.array_equal(ids1[matches[:, 0]], ids2[matches[:, 1]])
                db.write_matches(id1, id2, matches)
                pair_lines.append(f'{n1} {n2}\n')
                pair_info.append([int(f1), int(f2), len(common)])
    with (OUT / 'pairs.txt').open('x', encoding='utf8') as f:
        f.writelines(pair_lines)
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
    m.mapper.bundle_adjustment.ceres.solver_options.trust_region_problem_dump_directory = str(OUT / 'temp')
    (OUT / 'empty-images').mkdir()
    save('controls.json', {'pycolmap': pc.__version__, 'numpy': np.__version__,
         'archive_sha256': EXPECTED, 'keys': keys.tolist(), 'training_rows': int(train.sum()),
         'pairs': pair_info, 'geometry': g.todict(), 'calibration': c.todict(),
         'mapper': m.summary()})
    # Save the exact effective API options before any data-dependent solve.
    with (OUT / 'effective-options.txt').open('x', encoding='utf8') as f:
        f.write(g.summary()+'\n'+c.summary()+'\n'+m.summary())
    return g, c, m


def run():
    started = time.monotonic()
    g, c, m = prepare()
    save('prepared.json', {'seconds': time.monotonic()-started})
    t = time.monotonic()
    timer = deadline('verification_calibration', 180)
    pc.verify_matches(OUT / 'tracks.db', OUT / 'pairs.txt', options=g)
    calibrated = pc.calibrate_view_graph(OUT / 'tracks.db', options=c)
    timer.cancel()
    with pc.Database.open(OUT / 'tracks.db') as db:
        cameras = [camera.params.tolist() for camera in db.read_all_cameras()]
    save('verification.json', {'seconds': time.monotonic()-t,
         'calibrated': bool(calibrated), 'calibrated_cameras': cameras})
    if not calibrated:
        save('result.json', {'status': 'REJECT', 'reason': 'view_graph_calibration_failed'})
        return
    t = time.monotonic()
    timer = deadline('global_mapping', 300)
    models = pc.global_mapping(OUT / 'tracks.db', OUT / 'empty-images',
                               OUT / 'sparse', options=m)
    timer.cancel()
    save('mapping.json', {'seconds': time.monotonic()-t,
         'models': {str(i): r.summary() for i, r in models.items()}})
    if len(models) != 1:
        save('result.json', {'status': 'REJECT', 'reason': 'not_exactly_one_model',
             'models': len(models)})
        return
    timer = deadline('held_evaluation', 120)
    evaluate(next(iter(models.values())))
    timer.cancel()


def evaluate(model):
    frame, ids, xy = arrays()
    poses = {int(im.name[6:10]): im.cam_from_world().matrix()
             for im in model.images.values() if im.has_pose}
    assert len(model.cameras) == 1
    camera = next(iter(model.cameras.values()))
    f, cx, cy = camera.params
    k = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.]])
    projections = {key: k@pose for key, pose in poses.items()}
    rotations = all(np.linalg.det(p[:, :3]) > .999999 and
                    np.max(np.abs(p[:, :3]@p[:, :3].T-np.eye(3))) < 1e-7
                    for p in poses.values())
    train_errors, train_depths = [], []
    for im in model.images.values():
        if not im.has_pose:
            continue
        p = im.cam_from_world().matrix()
        for point in im.points2D:
            if not point.has_point3D():
                continue
            x = model.points3D[point.point3D_id].xyz
            train_errors.append(float(np.linalg.norm(project(k@p, x)-point.xy)))
            train_depths.append(float((p@np.r_[x, 1.])[2]))
    unique, counts = np.unique(ids, return_counts=True)
    held_ids = unique[(unique % 5 == 0) & (counts >= 4)]
    results, scored_frames, errors = [], [], []
    for identity in held_ids:
        rows = np.flatnonzero(ids == identity)
        rows = rows[np.argsort(frame[rows])]
        registered = [r for r in rows if int(frame[r]) in poses]
        missing = len(rows)-len(registered)
        if len(registered) < 2:
            results.append([int(identity), missing, 0, 0., 0])
            continue
        first, last = registered[0], registered[-1]
        fa, fb = int(frame[first]), int(frame[last])
        x = triangulate(projections[fa], projections[fb], xy[first]+.5, xy[last]+.5)
        ca = -poses[fa][:, :3].T@poses[fa][:, 3]
        cb = -poses[fb][:, :3].T@poses[fb][:, 3]
        ra, rb = x-ca, x-cb
        angle = float(np.degrees(np.arccos(np.clip(np.dot(ra, rb)/
                            (np.linalg.norm(ra)*np.linalg.norm(rb)), -1, 1))))
        bad = 0
        for row in registered:
            p = poses[int(frame[row])]
            if not np.isfinite(x).all() or (p@np.r_[x, 1.])[2] <= 0:
                bad += 1
            if row in (first, last):
                continue
            e = float(np.linalg.norm(project(k@p, x)-(xy[row]+.5)))
            if not np.isfinite(e):
                bad += 1
                e = np.inf
            errors.append(e)
            scored_frames.append(int(frame[row]))
        results.append([int(identity), missing, len(registered)-2, angle, bad])
    result_array = np.asarray(results)
    errors, scored_frames = np.asarray(errors), np.asarray(scored_frames)
    per_frame = {}
    for key in sorted(poses):
        e = errors[scored_frames == key]
        per_frame[str(key)] = {'n': len(e), 'p95_px': float(np.percentile(e, 95))
                               if len(e) and np.isfinite(e).all() else None}
    p95 = float(np.percentile(errors, 95)) if len(errors) and np.isfinite(errors).all() else None
    training_p95 = float(np.percentile(train_errors, 95)) if train_errors else None
    viability = (len(poses) >= .8*74 and len(model.points3D) >= 200 and rotations
        and all(d > 0 for d in train_depths) and 400 < f < 4000
        and training_p95 is not None and training_p95 <= 3
        and any(120 <= key <= 168 for key in poses)
        and any(396 <= key <= 444 for key in poses))
    missing = int(result_array[:, 1].sum())
    weak = int((result_array[:, 3] < 1).sum())
    bad = int(result_array[:, 4].sum())
    held_pass = (missing == weak == bad == 0 and p95 is not None and p95 <= 3
                 and all(v['n'] >= 30 and v['p95_px'] is not None and v['p95_px'] <= 3
                         for v in per_frame.values()))
    np.savez_compressed(OUT / 'geometry-and-held.npz', frames=np.array(sorted(poses)),
        poses=np.stack([poses[key] for key in sorted(poses)]), K=k,
        points=np.array([point.xyz for point in model.points3D.values()]),
        held_ids=held_ids, held_summary=result_array, errors=errors,
        scored_frames=scored_frames)
    save('result.json', {'status': 'PARTIAL_SUCCESS' if viability and held_pass else 'REJECT',
        'registered': len(poses), 'points': len(model.points3D), 'focal_px': float(f),
        'registered_frames': sorted(poses), 'training_p95_px': training_p95,
        'proper_rotations': rotations, 'training_positive_depths': all(d > 0 for d in train_depths),
        'viability_pass': bool(viability), 'held_pass': bool(held_pass),
        'held_identity_count': len(held_ids), 'held_scored_rows': len(errors),
        'held_p95_px': p95, 'held_missing_camera_rows': missing,
        'held_weak_angle_ids': weak, 'held_bad_depth_or_finite_rows': bad,
        'per_frame': per_frame, 'head_mesh_produced': False,
        'medical_surface_accuracy': 'UNVERIFIED', 'physical_identity': 'UNVERIFIED'})


if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        save('failure.json', {'type': type(exc).__name__, 'message': str(exc)})
        raise
