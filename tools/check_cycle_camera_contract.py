"""Procedural corrupted short-track unknown-camera control;no human inputs."""
import itertools
import numpy as np
from check_global_geometry_contract import scene, similarity
from cycle_consensus import select_tracks
from short_track_camera import fit, project


def control_data():
    xyz, centers, poses, truth_k, observations = scene()
    rng = np.random.default_rng(300)
    xy, labels, lookup = {}, {}, {}
    for camera, (ids, points) in observations.items():
        lookup[camera] = {}
        for key, slot in enumerate(rng.permutation(len(ids))):
            vertex = (camera, key)
            xy[vertex] = points[slot].copy()
            labels[vertex] = int(ids[slot])
            lookup[camera][int(ids[slot])] = vertex
    edges, corrupted = set(), 0
    for a, b in itertools.combinations(observations, 2):
        ids = sorted(set(lookup[a]) & set(lookup[b]))
        if not ids:
            continue
        mapped = ids.copy()
        chosen = rng.choice(len(ids), max(2, int(round(.2*len(ids)))), replace=False)
        for i, j in zip(chosen, np.roll(chosen, 1)):
            mapped[i] = ids[j]
        for source, target in zip(ids, mapped):
            edges.add((lookup[a][source], lookup[b][target]))
            corrupted += source != target
    data = {'frames':list(observations), 'xy':xy, 'edges':edges}
    # Truth is returned separately and is never an estimator argument.
    truth = {'points':xyz, 'centers':centers, 'poses':poses, 'K':truth_k,
             'labels':labels, 'corrupted_edges':corrupted}
    return data, truth



def check(folder):
    folder.mkdir(exist_ok=False)
    data, truth = control_data()
    tracks, graph = select_tracks(data['edges'])
    purity = [len({truth['labels'][v] for v in track}) == 1 for track in tracks]
    recall = len({truth['labels'][t[0]] for t, good in zip(tracks, purity) if good})/len(truth['points'])
    k, poses, points, train, held, metrics = fit(data, tracks, folder/'camera')
    centers = np.stack([-p[:3, :3].T@p[:3, 3] for p in poses])
    scale, rotation, translation = similarity(centers[[0, 2, 4]], truth['centers'][[0, 2, 4]])
    center_error = np.linalg.norm(scale*centers@rotation.T+translation-truth['centers'], axis=1)
    labels = np.array([truth['labels'][track[0]] for track in tracks])
    target = (truth['points'][labels]-translation)@rotation/scale
    projected, depth = project(k, poses, target, held)
    error = np.linalg.norm(projected-held[:, 2:], axis=1)
    point_error = np.linalg.norm(scale*points@rotation.T+translation-truth['points'][labels], axis=1)
    import cv2
    wrong = poses.copy()
    wrong[0, :3] = cv2.Rodrigues(np.array([.1, 0, 0]))[0]@wrong[0, :3]
    bad, _ = project(k, wrong, target, held[held[:, 0] == 0])
    negative = np.linalg.norm(bad-held[held[:, 0] == 0, 2:], axis=1)
    result = {'selected_tracks':len(tracks), 'purity':float(np.mean(purity)),
              'recall':recall, 'focal_relative_error':float(abs(k[0, 0]/1200.-1)),
              'center_max':float(center_error.max()), 'point_p95':float(np.percentile(point_error, 95)),
              'held_GT_p95_px':float(np.percentile(error, 95)), 'wrong_camera_p95_px':float(np.percentile(negative, 95)),
              'proper_cameras':metrics['proper_cameras'], 'positive_depths':bool((depth > 0).all()),
              'scope':'procedural software only,not patient/head accuracy'}
    if not (metrics['status'] == 'TECHNICAL_CHECK_PASSED' and result['purity'] >= .99 and recall >= .4
            and result['focal_relative_error'] <= .02 and result['center_max'] <= .01
            and result['point_p95'] <= .01 and result['held_GT_p95_px'] <= 1
            and result['wrong_camera_p95_px'] > 3 and result['positive_depths']):
        raise AssertionError('procedural short-track unknown-camera control failed')
    result['status'] = 'TECHNICAL_CHECK_PASSED'
    return result

