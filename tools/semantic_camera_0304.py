"""One bounded conditional camera trial;no scan/model-depth/head construction."""
from pathlib import Path
import hashlib
import ctypes
import io
import json
import os
import socket
import sys
import threading
import time
import zipfile

import cv2
import numpy as np

from short_track_camera import fit, write
from check_cycle_camera_contract import check

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/semantic-camera-0304'
ARCHIVE = ROOT / 'assets/private/closed-experiments/0303-semantic-video/evidence.zip'
EXPECTED = '0c1d4e82a60f6be70bf5d49edb0b0ed056eb085549a4a953e9b65be8df24ec26'
FRAMES = [0, 240, 300, 630]


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def deny_network(*args, **kwargs):
    raise RuntimeError('local validation only;network disabled')


socket.socket = deny_network
socket.create_connection = deny_network


def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, os.PathLike)):
        path = str(args[0]).lower().replace('\\', '/')
        if path.endswith(('.stl', 'normalized-xyz.npy')) or '/xuling/' in path:
            raise RuntimeError('medical/case002/predicted-depth input forbidden')


sys.addaudithook(guard)


def prepare():
    import mediapipe as mp
    assert mp.__version__ == '1.0.1'
    assert digest(ARCHIVE) == EXPECTED
    record = json.loads((ROOT / 'assets/private/closed-experiments/0303-semantic-video/precheck.json').read_text())
    for row in record['protected']:
        if 'manifest.json' in row['path'] or 'provenance-confirmation.json' in row['path']:
            assert digest(row['path']) == row['expected']
    manifest = json.loads((ROOT / 'assets/private/real-capture-pilot-v1/manifest.json').read_text())
    assert manifest['training_allowed'] is False and manifest['upload_allowed'] is False
    source = next(row for row in manifest['inputs'] if row['id'] == 'real-case-001-video')
    assert source['consent']['biometric_processing'] is True
    assert source['license_id'] == 'private-user-authorized-local-validation-only'
    assert 'local_head_reconstruction_validation' in source['allowed_uses']
    assert digest(source['path']) == source['sha256']
    edges = mp.tasks.vision.FaceLandmarksConnections.FACE_LANDMARKS_NOSE
    ids = sorted({v for edge in edges for v in (edge.start, edge.end)} | {33, 133, 263, 362})
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        xy = np.load(io.BytesIO(archive.read('native-xy.npy')), allow_pickle=False)
        presence = np.load(io.BytesIO(archive.read('face-present.npy')), allow_pickle=False)
        ledger = json.loads(archive.read('frames.json'))
    assert presence[FRAMES].all()
    chosen = xy[np.ix_(FRAMES, ids)]
    assert chosen.shape == (4, len(ids), 2) and np.isfinite(chosen).all()
    assert (chosen >= 0).all() and (chosen < [720, 1280]).all()
    OUT.mkdir(exist_ok=False)
    np.savez_compressed(OUT / 'frozen-xy.npz', xy=chosen, frames=FRAMES, ids=ids)
    capture = cv2.VideoCapture(source['path'])
    panels, rows = [], []
    try:
        for ordinal in range(max(FRAMES) + 1):
            ok, bgr = capture.read()
            if not ok:
                raise ValueError('sequential decode incomplete')
            if ordinal not in FRAMES:
                continue
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            assert rgb.shape == (1280, 720, 3)
            actual = hashlib.sha256(rgb.tobytes()).hexdigest()
            assert ledger[ordinal]['ordinal'] == ordinal and actual == ledger[ordinal]['rgb_sha256']
            points = chosen[FRAMES.index(ordinal)]
            image = bgr.copy()
            for point, label in zip(points, ids):
                center = tuple(np.rint(point).astype(int))
                cv2.circle(image, center, 2, (0, 255, 255), -1)
                cv2.putText(image, str(label), (center[0]+2, center[1]-2), cv2.FONT_HERSHEY_SIMPLEX, .28, (0, 0, 0), 1)
            full = cv2.resize(bgr, (288, 512))
            low = np.maximum(np.floor(points.min(axis=0)-25).astype(int), 0)
            high = np.minimum(np.ceil(points.max(axis=0)+25).astype(int), [720, 1280])
            crop = image[low[1]:high[1], low[0]:high[0]]
            zoom = cv2.resize(crop, (288, 288), interpolation=cv2.INTER_NEAREST)
            panel = np.vstack([full, zoom])
            cv2.putText(panel, str(ordinal)+' raw semantic XY', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, .45, (0, 0, 255), 1)
            panels.append(panel)
            rows.append({'ordinal':ordinal, 'rgb_sha256':actual, 'nominal_domain':'source-reviewed,physical attachment unverified'})
    finally:
        capture.release()
    sheet = np.vstack([np.zeros((28, 1152, 3), np.uint8), np.hstack(panels)])
    cv2.putText(sheet, 'SOURCE ANATOMICAL OBSERVATIONS - NOT A RECONSTRUCTED HEAD', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
    assert cv2.imwrite(str(OUT / 'source-review.jpg'), sheet)
    meta = {'prepared_utc':time.time(), 'archive_sha256':EXPECTED, 'source_sha256':source['sha256'],
            'frames':FRAMES, 'ids':ids, 'source_rows':rows, 'xy_sha256':digest(OUT/'frozen-xy.npz'),
            'status':'PREPARED_UNVERIFIED', 'predicted_depth_read':False, 'scan_read':False}
    write(OUT / 'prepared.json', meta)
    print(json.dumps(meta), flush=True)


def run():
    meta = json.loads((OUT / 'prepared.json').read_text())
    assert digest(ARCHIVE) == EXPECTED and digest(OUT/'frozen-xy.npz') == meta['xy_sha256']
    assert time.time()-meta['prepared_utc'] <= 900
    review = json.loads((OUT / 'visual-review.json').read_text())
    assert review['xy_sha256'] == meta['xy_sha256'] and review['gross_occlusion_reject'] is False
    values = np.load(OUT/'frozen-xy.npz', allow_pickle=False)
    xy, frames, ids = values['xy'], values['frames'].tolist(), values['ids'].tolist()
    assert frames == FRAMES and len(ids) == len(meta['ids'])
    data = {'frames':frames, 'xy':{(frame, label):xy[camera, slot]
                                for camera, frame in enumerate(frames) for slot, label in enumerate(ids)}}
    tracks = [[(frame, label) for frame in frames] for label in ids]
    state = {'status':'RUNNING', 'pid':os.getpid(), 'phase':'control', 'started':time.time(),
             'scope':'conditional anatomical-video cameras,not head acceptance'}
    stopped = threading.Event()

    class Memory(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in
            ('peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]

    memory = Memory()
    memory.cb = ctypes.sizeof(memory)
    ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
    get_memory.argtypes = [ctypes.c_void_p, ctypes.POINTER(Memory), ctypes.c_ulong]
    handle = ctypes.windll.kernel32.GetCurrentProcess()

    def memory_guard():
        while not stopped.wait(.1):
            if not get_memory(handle, ctypes.byref(memory), memory.cb):
                state.update(status='REJECT', failure='memory measurement unavailable')
                write(OUT/'report.json', state)
                os._exit(125)
            state['peak_working_set'] = int(memory.peak)
            if memory.peak > 4*1024**3:
                state.update(status='REJECT', failure='registered working-set limit exceeded')
                write(OUT/'report.json', state)
                os._exit(126)

    watcher = threading.Thread(target=memory_guard, daemon=True)
    watcher.start()

    def timeout():
        state.update(status='REJECT', failure='registered stage time limit exceeded')
        write(OUT/'report.json', state)
        os._exit(124)

    timer = threading.Timer(120, timeout)
    timer.daemon = True
    timer.start()
    exit_code = 1
    try:
        write(OUT/'report.json', state)
        result = check(OUT/'control')
        write(OUT/'control-result.json', result)
        timer.cancel()
        state['phase'] = 'four-view-camera'
        write(OUT/'report.json', state)
        timer = threading.Timer(180, timeout)
        timer.daemon = True
        timer.start()
        _, _, _, _, _, metrics = fit(data, tracks, OUT/'camera')
        state.update(camera=metrics, status='PARTIAL_SUCCESS' if metrics['status']=='TECHNICAL_CHECK_PASSED' else 'REJECT')
        exit_code = 0 if state['status'] == 'PARTIAL_SUCCESS' else 1
    except Exception as error:
        state.update(status='REJECT', failure=type(error).__name__+':'+str(error))
    finally:
        timer.cancel()
        stopped.set()
        watcher.join(timeout=1)
        state.update(seconds=time.time()-state['started'], head=False, medical_mm='UNVERIFIED', physical_identity='UNVERIFIED')
        write(OUT/'report.json', state)
        print(json.dumps(state), flush=True)
    raise SystemExit(exit_code)


if __name__ == '__main__':
    assert Path.cwd().resolve() == ROOT
    {'prepare':prepare, 'run':run}[sys.argv[1]]()
