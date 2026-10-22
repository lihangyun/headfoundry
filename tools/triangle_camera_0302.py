"""One triangle-component association trial;no model/head/scan construction."""
import ctypes
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import socket
import threading
import time
import zipfile

import cv2
import numpy as np
import scipy
from check_cycle_camera_contract import control_data
from check_global_geometry_contract import similarity
from cycle_consensus import select_tracks as legacy_select
from short_track_camera import fit, project

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/triangle-camera-0302'
REPORT = {'status':'REJECT', 'head':'UNVERIFIED', 'medical_mm':'UNVERIFIED'}
DONE = threading.Event()
LOCK = threading.RLock()
DEADLINE = [time.monotonic()+180]
FRAMES = (0, 60, 120, 240, 300, 360, 420, 600, 690)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    with LOCK:
        path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def phase(name, seconds):
    REPORT['phase'] = name
    DEADLINE[0] = time.monotonic()+seconds
    write(OUT/'report.json', REPORT)
    print(json.dumps({'phase':name}), flush=True)


def peak_memory():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)]+[(n, ctypes.c_size_t) for n in
                    ('peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]
    data = Counters()
    data.cb = ctypes.sizeof(data)
    kernel, psapi = ctypes.WinDLL('kernel32'), ctypes.WinDLL('psapi')
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(data), data.cb):
        raise RuntimeError('memory counter unavailable')
    return data.peak


def watch():
    while not DONE.wait(.25):
        if time.monotonic() > DEADLINE[0] or peak_memory() > 8*2**30:
            REPORT['failure'] = 'registered phase/resource cap exceeded'
            write(OUT/'report.json', REPORT)
            os._exit(124)


def select_tracks(raw):
    """Partial cycle closure;coordinates/labels/scores never enter this function."""
    started = time.monotonic()
    edges, adjacency = set(), {}
    for a, b in raw:
        if a[0] == b[0] or a == b:
            raise ValueError('same-frame observation edge')
        a, b = sorted((a, b))
        edges.add((a, b))
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    supported = set()
    for a, b in edges:
        if time.monotonic()-started > 60:
            raise RuntimeError('triangle construction time cap')
        if adjacency[a] & adjacency[b]:
            supported.add((a, b))
    graph = {}
    for a, b in supported:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    seen, tracks, rows = set(), [], []
    for vertex in sorted(graph):
        if vertex in seen:
            continue
        queue, component = [vertex], set()
        seen.add(vertex)
        while queue:
            if time.monotonic()-started > 60:
                raise RuntimeError('triangle closure time cap')
            current = queue.pop()
            component.add(current)
            for neighbor in graph[current]-seen:
                queue.append(neighbor)
                seen.add(neighbor)
        vertices = tuple(sorted(component))
        unique_images = len({v[0] for v in vertices}) == len(vertices)
        accepted = unique_images and len(vertices) >= 3
        rows.append({'vertices':vertices, 'selected':accepted,
                     'reason':'partial-cycle-consistent' if accepted else 'duplicate-frame-identity'})
        if accepted:
            tracks.append(vertices)
    tracks.sort(key=lambda track:(-len(track), track))
    return tracks, {'raw_vertices':len(adjacency), 'raw_edges':len(edges), 'supported_edges':len(supported),
                    'unsupported_edges':len(edges-supported), 'triangle_vertices':len(graph),
                    'components':rows, 'selected_tracks':len(tracks),
                    'selected_observations':sum(map(len, tracks)),
                    'conflicting_components':sum(not row['selected'] for row in rows),
                    'seconds':time.monotonic()-started}


def literal_controls():
    partial = [((0, 0), (1, 0), (2, 0)), ((0, 0), (1, 0), (3, 0))]
    edges = {pair for track in partial for pair in itertools.combinations(track, 2)}
    assert legacy_select(edges)[0] == []
    assert select_tracks(edges)[0] == [tuple((i, 0) for i in range(4))]
    tracks = [tuple((f, p) for f in range(4)) for p in range(2)]
    edges = {pair for track in tracks for pair in itertools.combinations(track, 2)}
    edges.add(((0, 0), (1, 1)))
    assert set(select_tracks(edges)[0]) == set(tracks)
    contradictory = [((0, 0), (1, 0), (2, 0)), ((0, 1), (1, 0), (3, 0))]
    edges = {pair for track in contradictory for pair in itertools.combinations(track, 2)}
    assert select_tracks(edges)[0] == []
    wrong = ((0, 0), (1, 0), (2, 1))
    assert select_tracks(set(itertools.combinations(wrong, 2)))[0] == [wrong]
    return {'partial_cycles_merge':True, 'false_bridge_removed':True, 'conflicting_component_rejected':True,
            'coherent_false_cycle_not_physical_truth':True}


def snapshot(data, path, truth=None, compare=False):
    vertices = sorted(data['xy'])
    raw = {'vertices':np.asarray(vertices, dtype=np.int64), 'xy':np.stack([data['xy'][v] for v in vertices]),
           'edges':np.asarray(sorted(data['edges']), dtype=np.int64)}
    np.savez_compressed(path/'raw-input.npz', **raw)
    if truth is not None:
        np.savez_compressed(path/'truth.npz', vertices=raw['vertices'],
             labels=np.asarray([truth['labels'][v] for v in vertices]), points=truth['points'],
             centers=truth['centers'], poses=truth['poses'], K=truth['K'])
    if compare:
        previous = ROOT/'assets/private/closed-experiments/0301-bearing-camera/evidence.zip'
        if digest(previous) != 'f8c997811bb4a465392d7872a2ba42a063b3e84eac908a0c1a8f31f533ae3472':
            raise ValueError('previous fixed raw control evidence differs')
        with zipfile.ZipFile(previous) as archive:
            original = np.load(io.BytesIO(archive.read('control/raw-input.npz')))
            for name, current in raw.items():
                if current.dtype != original[name].dtype or current.shape != original[name].shape or current.tobytes() != original[name].tobytes():
                    raise ValueError('entire raw control changed:'+name)
        write(path/'raw-equality.json', {'all_raw_array_bytes_equal':True,
              'scalar_values':sum(value.size for value in raw.values())})


def control():
    folder = OUT/'control'
    folder.mkdir()
    data, truth = control_data()
    snapshot(data, folder, truth, compare=True)
    tracks, graph = select_tracks(data['edges'])
    write(folder/'graph.json', graph)
    purity = [len({truth['labels'][v] for v in track}) == 1 for track in tracks]
    recall = len({truth['labels'][t[0]] for t, good in zip(tracks, purity) if good})/len(truth['points'])
    identity = {'purity':float(np.mean(purity)) if purity else 0., 'recall':recall, 'selected_tracks':len(tracks)}
    write(folder/'identity.json', identity)
    if identity['purity'] < .99 or recall < .4:
        raise ValueError('corrupted control identity condition failed')
    k, poses, points, train, held, metrics = fit(data, tracks, folder/'camera')
    centers = np.stack([-p[:3, :3].T@p[:3, 3] for p in poses])
    scale, rotation, translation = similarity(centers[[0, 2, 4]], truth['centers'][[0, 2, 4]])
    center_error = np.linalg.norm(scale*centers@rotation.T+translation-truth['centers'], axis=1)
    labels = np.array([truth['labels'][track[0]] for track in tracks])
    target = (truth['points'][labels]-translation)@rotation/scale
    projected, depth = project(k, poses, target, held)
    error = np.linalg.norm(projected-held[:, 2:], axis=1)
    point_error = np.linalg.norm(scale*points@rotation.T+translation-truth['points'][labels], axis=1)
    wrong = poses.copy()
    wrong[0, :3] = cv2.Rodrigues(np.array([.1, 0, 0]))[0]@wrong[0, :3]
    bad, _ = project(k, wrong, target, held[held[:, 0] == 0])
    negative = np.linalg.norm(bad-held[held[:, 0] == 0, 2:], axis=1)
    result = {**identity, 'focal_relative_error':float(abs(k[0, 0]/1200.-1)),
              'center_max':float(center_error.max()), 'point_p95':float(np.percentile(point_error, 95)),
              'held_GT_p95_px':float(np.percentile(error, 95)), 'wrong_camera_p95_px':float(np.percentile(negative, 95)),
              'proper_cameras':metrics['proper_cameras'], 'positive_depths':bool((depth > 0).all()),
              'scope':'procedural software only,not patient/head accuracy'}
    write(folder/'result.json', result)
    np.savez_compressed(folder/'truth-evaluation.npz', center_error=center_error, point_error=point_error,
                        held_GT_error_px=error, negative_error_px=negative)
    if not (metrics['status'] == 'TECHNICAL_CHECK_PASSED' and result['purity'] >= .99 and recall >= .4
            and result['focal_relative_error'] <= .02 and result['center_max'] <= .01
            and result['point_p95'] <= .01 and result['held_GT_p95_px'] <= 1
            and result['wrong_camera_p95_px'] > 3 and result['positive_depths']):
        raise AssertionError('procedural short-track unknown-camera control failed')
    result['status'] = 'TECHNICAL_CHECK_PASSED'
    return result


def patient_data():
    from headfoundry.manifest import validate_input_assets
    manifest_path = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    provenance = ROOT/'assets/private/real-capture-pilot-v1/provenance-confirmation.json'
    if digest(manifest_path) != 'a537ed48ee7fd0d4027be4aa5ca90472e7f5c8edd0ec9b4270735747b9081809' or digest(provenance) != '27d7513ebbcccd2fda6560b9545c9bc542ee8e77f94f8348969f61cfb9de2b2d':
        raise ValueError('authorized input/consent record differs')
    manifest = json.loads(manifest_path.read_text())
    source = next(row for row in manifest['inputs'] if row['id'] == 'real-case-001-video')
    errors = validate_input_assets({**manifest, 'inputs':[source]}, manifest_path.parent)
    if errors or manifest['training_allowed'] is not False or manifest['upload_allowed'] is not False:
        raise ValueError('local-only rights not established:'+str(errors))
    archive_path = ROOT/'assets/private/closed-experiments/0299-real-sparse-observations/evidence.zip'
    if digest(archive_path) != '479842be79bb6f272b4792dac05d1303b9dca6ba55a8e8a36860dd5f432d6f3d':
        raise ValueError('original raw observations differ')
    xy, features, edges = {}, {}, set()
    with zipfile.ZipFile(archive_path) as archive:
        for frame in FRAMES:
            features[frame] = dict(np.load(io.BytesIO(archive.read(f'frame-{frame:04}-features.npz'))))
            for key, point in zip(features[frame]['global_ids'], features[frame]['points']):
                xy[(frame, int(key))] = point.astype(float)
        for a, b in itertools.combinations(FRAMES, 2):
            match = np.load(io.BytesIO(archive.read(f'pair-{a:04}-{b:04}.npz')))
            for ia, ib in match['pairs'][match['unique']]:
                edges.add(((a, int(features[a]['global_ids'][ia])), (b, int(features[b]['global_ids'][ib]))))
    return {'frames':list(FRAMES), 'xy':xy, 'edges':edges}


def main():
    started = time.monotonic()
    OUT.mkdir(exist_ok=False)
    def blocked(*args, **kwargs):
        raise RuntimeError('network forbidden')
    socket.socket.connect = blocked
    cv2.setNumThreads(4)
    threading.Thread(target=watch, daemon=True).start()
    try:
        if not __debug__:
            raise ValueError('registered literal controls require assertions')
        prior = json.loads((ROOT/'assets/private/closed-experiments/0301-bearing-camera/precheck.json').read_text())
        retained = {'short_track_camera.py', 'check_cycle_camera_contract.py', 'cycle_consensus.py', 'check_global_geometry_contract.py'}
        rows = [row for row in prior['protected'] if Path(row['path']).name in retained]
        if len(rows) != 4 or any(digest(row['path']) != row['expected'] for row in rows):
            raise ValueError('shared backend/fixture/default source changed')
        if (np.__version__, scipy.__version__, cv2.__version__) != ('2.5.2', '1.18.1', '5.0.0'):
            raise ValueError('registered runtime versions differ')
        REPORT['shared_sources_unchanged'] = 4
        phase('literal-constructor-controls', 60)
        REPORT['literal'] = literal_controls()
        phase('independent-unknown-camera-control', 180)
        REPORT['control'] = control()
        phase('actual-fixed-triangle-components', 180)
        data = patient_data()
        snapshot(data, OUT)
        tracks, graph = select_tracks(data['edges'])
        write(OUT/'patient-graph.json', graph)
        REPORT['patient_graph'] = {key:value for key, value in graph.items() if key != 'components'}
        REPORT['full_source_face_vertices'] = len(data['xy'])
        _, _, _, _, _, metrics = fit(data, tracks, OUT/'patient-camera')
        REPORT['patient_camera'] = metrics
        if metrics['status'] != 'TECHNICAL_CHECK_PASSED':
            raise ValueError('actual fixed held-camera gate failed')
        REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
        REPORT['scope'] = 'provisional correspondence/camera consistency,not head/medical acceptance'
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        REPORT['seconds'] = time.monotonic()-started
        REPORT['peak_working_set'] = peak_memory()
        DONE.set()
        write(OUT/'report.json', REPORT)
        print(json.dumps(REPORT), flush=True)
    return 0 if REPORT['status'] == 'TECHNICAL_CHECK_PASSED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
