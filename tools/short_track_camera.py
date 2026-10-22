"""Bounded native720x1280 short-track camera math,not identity/head acceptance.

Unknown shared f;OpenCV native-center xy,world-to-camera x-right/y-down/z-forward.
No asset/model/private input path,training,medical geometry or production default.
Caller must independently validate rights/observations and bound resources.
"""
import hashlib
import itertools
import json

import cv2
import numpy as np
from scipy import sparse
from scipy.optimize import least_squares


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")


def intrinsics(log_f):
    return np.array([[np.exp(log_f), 0, 359.5], [0, np.exp(log_f), 639.5], [0, 0, 1.]])


def project(k, poses, points, observations):
    index = observations[:, :2].astype(int)
    q = np.einsum('nij,nj->ni', poses[index[:, 0], :3, :3], points[index[:, 1]])+poses[index[:, 0], :3, 3]
    z = q[:, 2].copy()
    safe = np.where(np.abs(z) < 1e-9, np.where(z < 0, -1e-9, 1e-9), z)
    uv = q[:, :2]/safe[:, None]*k[0, 0]+k[:2, 2]
    return uv, z


def fit(data, tracks, folder):
    folder.mkdir(exist_ok=False)
    if not tracks:
        raise ValueError('no cycle-certified tracks')
    frames = data['frames']
    frame_index = {f:i for i, f in enumerate(frames)}
    train, held = [], []
    for index, track in enumerate(tracks):
        withheld = min(track, key=lambda v:hashlib.sha256(f'300/hold/{v[0]}/{v[1]}'.encode()).digest())
        for vertex in track:
            (held if vertex == withheld else train).append([frame_index[vertex[0]], index, *data['xy'][vertex]])
    train, held = np.asarray(train, dtype=float), np.asarray(held, dtype=float)
    np.savez_compressed(folder/'frozen-observations.npz', train=train, held=held)
    by_frame = [{int(row[1]):row[2:] for row in train if int(row[0]) == camera} for camera in range(len(frames))]
    fundamentals = []
    for a, b in itertools.combinations(range(len(frames)), 2):
        common = sorted(set(by_frame[a]) & set(by_frame[b]))
        if len(common) < 8:
            continue
        first = np.stack([by_frame[a][p] for p in common])
        second = np.stack([by_frame[b][p] for p in common])
        cv2.setRNGSeed(300)
        matrix, mask = cv2.findFundamentalMat(first, second, cv2.USAC_MAGSAC, 1.5, .999, 10000)
        if matrix is not None and matrix.shape == (3, 3) and np.isfinite(matrix).all() and int(mask.sum()) >= 8:
            fundamentals.append((a, b, common, first, second, matrix, mask))
    if not fundamentals:
        raise ValueError('no eligible training fundamental matrix')

    def focal_residual(value):
        k = intrinsics(value[0])
        values = []
        for _, _, _, _, _, matrix, mask in fundamentals:
            singular = np.linalg.svd(k.T@matrix@k, compute_uv=False)
            weight = np.sqrt(min(int(mask.sum()), 40))
            values.extend(weight*np.array([singular[0]-singular[1], singular[2]])/max(singular[0]+singular[1], 1e-30))
        return values

    focal = least_squares(focal_residual, [np.log(1280.)], bounds=([np.log(640.)], [np.log(5120.)]),
                          max_nfev=100, diff_step=1e-4, ftol=1e-12, xtol=1e-12, gtol=1e-12)
    k = intrinsics(focal.x[0])
    initial = {'focal_seed':1280., 'focal_initializer':float(k[0, 0]), 'focal_evaluations':focal.nfev,
               'fundamental_pairs':len(fundamentals), 'pair_candidates':[], 'attached':[]}
    candidates = []
    for a, b, common, first, second, matrix, mask in fundamentals:
        essential = k.T@matrix@k
        count, rotation, translation, positive = cv2.recoverPose(essential, first, second, k, mask=mask.copy())
        inlier_count = int(mask.sum())
        selected = positive.ravel() != 0
        x = cv2.triangulatePoints(k@np.column_stack((np.eye(3), np.zeros(3))),
                                 k@np.column_stack((rotation, translation)), first.T, second.T)
        points = (x[:3]/x[3]).T
        center = -rotation.T@translation[:, 0]
        rays_a, rays_b = points, points-center
        cosine = np.sum(rays_a*rays_b, axis=1)/np.maximum(np.linalg.norm(rays_a, axis=1)*np.linalg.norm(rays_b, axis=1), 1e-30)
        parallax = float(np.median(np.degrees(np.arccos(np.clip(cosine[selected], -1, 1))))) if selected.any() else 0.
        eligible = bool(count >= 8 and count/inlier_count >= .9 and parallax >= 1 and np.isfinite(points[selected]).all())
        initial['pair_candidates'].append({'frames':[frames[a], frames[b]], 'positive':count,
                                           'train_inliers':inlier_count, 'median_parallax_deg':parallax, 'eligible':eligible})
        if eligible:
            candidates.append((count, parallax, -a, -b, a, b, rotation, translation[:, 0], inlier_count))
    write(folder/'initialization.json', initial)
    if not candidates:
        raise ValueError('no nondegenerate training initialization pair')
    chosen = max(candidates, key=lambda row:row[:4])
    _, _, _, _, anchor, baseline, rotation, translation, _ = chosen
    poses = np.repeat(np.eye(4)[None], len(frames), axis=0)
    poses[baseline, :3, :3], poses[baseline, :3, 3] = rotation, translation
    known = {anchor, baseline}
    tree = [chosen]
    while len(known) < len(frames):
        crossing = [edge for edge in candidates if (edge[4] in known) != (edge[5] in known)]
        if not crossing:
            initial['missing_rotation_frames'] = [frames[i] for i in set(range(len(frames)))-known]
            write(folder/'initialization.json', initial)
            raise ValueError('eligible relative-pose graph disconnected')
        edge = max(crossing, key=lambda row:row[:4])
        a, b, relative = edge[4:7]
        if a in known:
            poses[b, :3, :3] = relative@poses[a, :3, :3]
        else:
            poses[a, :3, :3] = relative.T@poses[b, :3, :3]
        known.update((a, b))
        tree.append(edge)
    rotation_cameras = [i for i in range(len(frames)) if i != anchor]
    rotation_seed = np.concatenate([cv2.Rodrigues(poses[i, :3, :3])[0].ravel() for i in rotation_cameras])

    def rotations(values):
        result = np.repeat(np.eye(3)[None], len(frames), axis=0)
        for slot, camera in enumerate(rotation_cameras):
            result[camera] = cv2.Rodrigues(values[3*slot:3*slot+3])[0]
        return result

    def rotation_residual(values):
        result = rotations(values)
        errors = []
        for edge in candidates:
            a, b, relative = edge[4:7]
            errors.extend(np.sqrt(edge[8])*cv2.Rodrigues(relative.T@result[b]@result[a].T)[0].ravel())
        return errors

    averaged = least_squares(rotation_residual, rotation_seed, loss='soft_l1', f_scale=np.pi/180,
                            max_nfev=100, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    poses[:, :3, :3] = rotations(averaged.x)
    center_slots = {camera:3*slot for slot, camera in enumerate(rotation_cameras)}

    def bearing_system(edges):
        offset = 3*(len(frames)-1)
        system = np.zeros((3*len(edges)+1, offset+len(edges)))
        target = np.zeros(len(system))
        directions = []
        for index, edge in enumerate(edges):
            a, b, _, translation = edge[4:8]
            direction = -poses[b, :3, :3].T@translation
            direction /= np.linalg.norm(direction)
            directions.append(direction)
            block = slice(3*index, 3*index+3)
            if a != anchor:
                system[block, center_slots[a]:center_slots[a]+3] = -np.eye(3)
            if b != anchor:
                system[block, center_slots[b]:center_slots[b]+3] = np.eye(3)
            system[block, offset+index] = -direction
            system[block] *= np.sqrt(edge[8])
            if (a, b) == (anchor, baseline):
                system[-1, offset+index], target[-1] = 1., 1.
        return system, target, np.asarray(directions)

    system, target, directions = bearing_system(candidates)
    solution, _, rank, singular = np.linalg.lstsq(system, target, rcond=1e-9)
    forest, forest_target, _ = bearing_system(tree)
    _, _, tree_rank, tree_singular = np.linalg.lstsq(forest, forest_target, rcond=1e-9)
    scales = solution[3*(len(frames)-1):]
    initial.update(rotation_evaluations=averaged.nfev, rotation_success=averaged.success,
                   bearing_rows=system.shape[0], bearing_unknowns=system.shape[1], bearing_rank=int(rank),
                   bearing_singular_values=singular.tolist(), edge_scales=scales.tolist(),
                   edges=[[frames[e[4]], frames[e[5]]] for e in candidates],
                   tree_rank=int(tree_rank), tree_unknowns=forest.shape[1],
                   tree_rank_deficient=bool(tree_rank < forest.shape[1]))
    write(folder/'initialization.json', initial)
    np.savez_compressed(folder/'bearing-system.npz', A=system, b=target, x=solution,
                        singular=singular, directions=directions, edge_scales=scales,
                        residual=system@solution-target, tree_singular=tree_singular)
    if rank != system.shape[1]:
        raise ValueError('global bearing scales not identifiable at registered rank tolerance')
    if not np.isfinite(solution).all() or not (scales > 1e-9).all():
        raise ValueError('global bearing edge scale nonpositive/nonfinite;no clamp')
    if len(frames) > 2 and not initial['tree_rank_deficient']:
        raise ValueError('tree-only negative rank witness failed')
    centers = np.zeros((len(frames), 3))
    for camera, index in center_slots.items():
        centers[camera] = solution[index:index+3]
    length = np.linalg.norm(centers[baseline]-centers[anchor])
    if not np.isfinite(length) or length <= 1e-9:
        raise ValueError('invalid baseline gauge')
    centers /= length
    for camera in range(len(frames)):
        poses[camera, :3, 3] = -poses[camera, :3, :3]@centers[camera]
    initial['normalized_centers'] = centers.tolist()
    initial['all_camera_rotations_initialized'] = len(known)
    write(folder/'initialization.json', initial)
    points = np.full((len(tracks), 3), np.nan)

    def triangulate():
        for point in range(len(tracks)):
            views = sorted(camera for camera in known if point in by_frame[camera])
            if len(views) < 2:
                continue
            rays = {}
            for camera in views:
                local = np.linalg.solve(k, np.r_[by_frame[camera][point], 1.])
                world = poses[camera, :3, :3].T@local
                rays[camera] = world/np.linalg.norm(world)
            a, b = max(itertools.combinations(views, 2), key=lambda ab:1-float(rays[ab[0]]@rays[ab[1]]))
            value = cv2.triangulatePoints(k@poses[a, :3], k@poses[b, :3],
                                         by_frame[a][point].reshape(2, 1), by_frame[b][point].reshape(2, 1))[:, 0]
            if abs(value[3]) > 1e-12 and np.isfinite(value).all():
                points[point] = value[:3]/value[3]

    triangulate()
    if not np.isfinite(points).all():
        raise ValueError('uninitialized track geometry;no point pruning')

    variables, blocks, sizes = [float(focal.x[0])], {}, {}
    for camera in range(len(frames)):
        if camera == anchor:
            continue
        rotation = cv2.Rodrigues(poses[camera, :3, :3])[0].ravel().tolist()
        translation = poses[camera, :3, 3]
        if camera == baseline:
            direction = [float(np.arctan2(translation[1], translation[0])),
                         float(np.arctan2(translation[2], np.linalg.norm(translation[:2])))]
            block = rotation+direction
        else:
            block = rotation+translation.tolist()
        blocks[camera], sizes[camera] = len(variables), len(block)
        variables.extend(block)
    point_offset = len(variables)
    variables.extend(points.ravel())
    variables = np.asarray(variables)
    pattern = sparse.lil_matrix((2*len(train), len(variables)), dtype=int)
    for row, (camera, point, _, _) in enumerate(train):
        camera, point = int(camera), int(point)
        pattern[2*row:2*row+2, 0] = 1
        if camera != anchor:
            pattern[2*row:2*row+2, blocks[camera]:blocks[camera]+sizes[camera]] = 1
        pattern[2*row:2*row+2, point_offset+3*point:point_offset+3*point+3] = 1

    def unpack(values):
        result = np.repeat(np.eye(4)[None], len(frames), axis=0)
        for camera, start in blocks.items():
            result[camera, :3, :3] = cv2.Rodrigues(values[start:start+3])[0]
            if camera == baseline:
                theta, phi = values[start+3:start+5]
                result[camera, :3, 3] = [np.cos(phi)*np.cos(theta), np.cos(phi)*np.sin(theta), np.sin(phi)]
            else:
                result[camera, :3, 3] = values[start+3:start+6]
        return intrinsics(values[0]), result, values[point_offset:].reshape(-1, 3)

    def residual(values):
        kk, pp, xx = unpack(values)
        uv, _ = project(kk, pp, xx, train)
        return (uv-train[:, 2:]).ravel()

    lower, upper = np.full(len(variables), -np.inf), np.full(len(variables), np.inf)
    lower[0], upper[0] = np.log(640.), np.log(5120.)
    optimized = least_squares(residual, variables, bounds=(lower, upper), jac_sparsity=pattern.tocsr(),
                              loss='soft_l1', f_scale=1.5, max_nfev=300, x_scale='jac',
                              ftol=1e-8, xtol=1e-8, gtol=1e-8)
    k, poses, points = unpack(optimized.x)
    predicted, held_depth = project(k, poses, points, held)
    train_predicted, train_depth = project(k, poses, points, train)
    error = np.linalg.norm(predicted-held[:, 2:], axis=1)
    train_error = np.linalg.norm(train_predicted-train[:, 2:], axis=1)
    proper = all(np.max(np.abs(p[:3, :3]@p[:3, :3].T-np.eye(3))) < 1e-7 and
                 np.linalg.det(p[:3, :3]) > .999999 and np.array_equal(p[3], [0, 0, 0, 1]) for p in poses)
    rows = []
    for camera, frame in enumerate(frames):
        values = error[held[:, 0] == camera]
        rows.append({'frame':frame, 'held_rows':len(values),
                     'p95_px':float(np.percentile(values, 95)) if len(values) else None,
                     'max_px':float(values.max()) if len(values) else None})
    positive = bool(np.isfinite(held_depth).all() and np.isfinite(train_depth).all() and
                    held_depth.min() > 0 and train_depth.min() > 0)
    reasonable = bool(640.640 < k[0, 0] < 5114.880)
    passed = bool(proper and positive and reasonable and np.isfinite(points).all() and
                  all(row['held_rows'] >= 6 and row['p95_px'] <= 3 for row in rows))
    metrics = {'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT', 'frames':rows,
               'proper_cameras':proper, 'all_positive_depths':positive, 'focal_px':float(k[0, 0]),
               'focal_nonbound':reasonable, 'training_p95_px':float(np.percentile(train_error, 95)),
               'held_p95_px':float(np.percentile(error, 95)), 'evaluations':optimized.nfev,
               'optimizer_success':optimized.success, 'optimizer_message':optimized.message,
               'anchor_frame':frames[anchor], 'baseline_frame':frames[baseline],
               'coordinate_convention':'OpenCV native-center xy;world-to-camera4x4,x-right/y-down/z-forward'}
    write(folder/'result.json', metrics)
    np.savez_compressed(folder/'solution.npz', K=k, poses=poses, points=points, train=train, held=held,
                        held_error_px=error, held_depth=held_depth, train_error_px=train_error, train_depth=train_depth)
    return k, poses, points, train, held, metrics

