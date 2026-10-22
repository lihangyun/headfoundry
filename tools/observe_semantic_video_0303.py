"""One-pass local semantic video observations;not camera/physical head acceptance."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import socket
import threading
import time
import zipfile

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw
from headfoundry.manifest import validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/semantic-video-0303'
MODEL = ROOT/'assets/private/mediapipe/face_landmarker.task'
CARDS = ROOT/'assets/private/semantic-source-0303-preflight'
ANCHORS = (0, 30, 210, 240, 300, 330, 570, 600, 840, 1020)
KEYS = sorted(set(range(0, 1041, 30))|{1040})
REPORT = {'status':'REJECT', 'physical_quality':'UNVERIFIED', 'camera_ready':False}
DONE = threading.Event()
DEADLINE = [time.monotonic()+30]
LOCK = threading.RLock()


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, value):
    with LOCK:
        (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def phase(name, seconds):
    DEADLINE[0] = time.monotonic()+seconds
    REPORT['phase'] = name
    write('report.json', REPORT)
    print(json.dumps({'phase':name}), flush=True)


def peak_memory():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)]+[(n, ctypes.c_size_t) for n in
                    ('peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel, psapi = ctypes.WinDLL('kernel32'), ctypes.WinDLL('psapi')
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise RuntimeError('memory counter unavailable')
    return counters.peak


def watch():
    while not DONE.wait(.25):
        if time.monotonic() > DEADLINE[0] or peak_memory() > 8*2**30:
            REPORT['failure'] = 'registered time/resource cap exceeded'
            write('report.json', REPORT)
            os._exit(124)


def cv_xy(normalized):
    return np.asarray(normalized, dtype=np.float64)[..., :2]*[720., 1280.]-.5


def main():
    started = time.monotonic()
    OUT.mkdir(exist_ok=False)
    (OUT/'frames').mkdir()
    records, raw, xy, present, stamps = [], None, None, None, None
    threading.Thread(target=watch, daemon=True).start()
    try:
        phase('assets-rights-coordinate-control', 30)
        if not __debug__ or mp.__version__ != '1.0.1':
            raise ValueError('registered runtime/assertions differ')
        lock = json.loads((ROOT/'examples/mediapipe-face-asset-lock.json').read_text())
        expected = lock['face_landmarker']['sha256']
        if digest(MODEL) != expected:
            raise ValueError('pinned entire task differs')
        with zipfile.ZipFile(MODEL) as bundle:
            if set(bundle.namelist()) != {r['name'] for r in lock['bundle_components']}:
                raise ValueError('component population differs')
            for row in lock['bundle_components']:
                data = bundle.read(row['name'])
                if row['license_id'] != 'Apache-2.0' or len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                    raise ValueError('component rights/bytes mismatch')
        for card in lock['model_cards']:
            if card['license_id'] != 'Apache-2.0' or digest(CARDS/(card['name']+'.pdf')) != card['sha256']:
                raise ValueError('official card provenance differs')
        manifest_path = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
        provenance = ROOT/'assets/private/real-capture-pilot-v1/provenance-confirmation.json'
        if digest(manifest_path) != 'a537ed48ee7fd0d4027be4aa5ca90472e7f5c8edd0ec9b4270735747b9081809' or digest(provenance) != '27d7513ebbcccd2fda6560b9545c9bc542ee8e77f94f8348969f61cfb9de2b2d':
            raise ValueError('authorization records differ')
        manifest = json.loads(manifest_path.read_text())
        source = next(r for r in manifest['inputs'] if r['id'] == 'real-case-001-video')
        errors = validate_input_assets({**manifest, 'inputs':[source]}, manifest_path.parent)
        if errors or manifest['training_allowed'] is not False or manifest['upload_allowed'] is not False:
            raise ValueError('local-only consent/rights invalid:'+str(errors))
        audit = json.loads((ROOT/'assets/private/video-observability-0252/report.json').read_text())
        if audit['frame_count_decoded'] != 1041 or source['sha256'] != audit['source_sha256']:
            raise ValueError('frozen source population differs')
        pixels = np.array([[0., 0.], [719., 1279.], [359.5, 639.5], [73.25, 1033.5]])
        delta = float(np.abs(cv_xy((pixels+.5)/[720., 1280.])-pixels).max())
        if delta > 1e-10:
            raise ValueError('native-center coordinate control failed')
        REPORT.update(model_sha256=expected, coordinate_control_max_px=delta, runtime=mp.__version__,
                      source_sha256=source['sha256'], domain='UNVERIFIED;presence is not visibility/identity')
        def blocked(*args, **kwargs):
            raise RuntimeError('worker network forbidden;explicit local model only')
        socket.socket.connect = blocked
        cv2.setNumThreads(4)
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL), delegate=mp.tasks.BaseOptions.Delegate.CPU),
            running_mode=mp.tasks.vision.RunningMode.VIDEO, num_faces=1,
            min_face_detection_confidence=.5, min_face_presence_confidence=.5, min_tracking_confidence=.5,
            output_face_blendshapes=False, output_facial_transformation_matrixes=False)
        raw = np.lib.format.open_memmap(OUT/'normalized-xyz.npy', mode='w+', dtype=np.float32, shape=(1041, 478, 3))
        xy = np.lib.format.open_memmap(OUT/'native-xy.npy', mode='w+', dtype=np.float64, shape=(1041, 478, 2))
        present = np.lib.format.open_memmap(OUT/'face-present.npy', mode='w+', dtype=bool, shape=(1041,))
        stamps = np.lib.format.open_memmap(OUT/'timestamps-ms.npy', mode='w+', dtype=np.int64, shape=(1041,))
        raw[:] = np.nan
        xy[:] = np.nan
        present[:] = False
        stamps[:] = -1
        sheets = [Image.new('RGB', (1080, 2088), (25, 25, 25)) for _ in range(2)]
        for sheet in sheets:
            ImageDraw.Draw(sheet).text((4, 4), 'SOURCE VIDEO OBSERVATIONS - NOT A RECONSTRUCTED HEAD', fill='white')
        capture = cv2.VideoCapture(source['path'])
        phase('sequential-native-video', 180)
        with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
            try:
                fps = capture.get(cv2.CAP_PROP_FPS)
                if not np.isfinite(fps) or fps <= 0:
                    raise ValueError('invalid nominal source FPS')
                for ordinal in range(1041):
                    ok, bgr = capture.read()
                    if not ok:
                        raise ValueError('sequential decode ended early')
                    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    rgb_sha = hashlib.sha256(rgb.tobytes()).hexdigest()
                    if rgb.shape != (1280, 720, 3) or rgb_sha != audit['frame_records'][ordinal]['rgb_sha256']:
                        raise ValueError('exact source RGB/ordinal differs')
                    stamp = round(ordinal*1000/fps)
                    if ordinal and stamp <= stamps[ordinal-1]:
                        raise ValueError('nominal SDK timestamp not increasing')
                    result = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), stamp)
                    faces = len(result.face_landmarks)
                    if faces not in (0, 1):
                        raise ValueError('unexpected face population')
                    if faces:
                        value = np.array([[p.x, p.y, p.z] for p in result.face_landmarks[0]], dtype=np.float32)
                        if value.shape != (478, 3) or not np.isfinite(value).all():
                            raise ValueError('nonfinite/incorrect full landmark shape')
                        raw[ordinal] = value
                        xy[ordinal] = cv_xy(value)
                        present[ordinal] = True
                    stamps[ordinal] = stamp
                    outside = int(((xy[ordinal] < [-.5, -.5]) | (xy[ordinal] > [719.5, 1279.5])).any(1).sum()) if faces else None
                    records.append({'ordinal':ordinal, 'rgb_sha256':rgb_sha, 'timestamp_ms':stamp,
                                    'faces':faces, 'outside_image_landmarks':outside, 'quality':'UNVERIFIED'})
                    if ordinal in KEYS:
                        image = Image.fromarray(rgb)
                        image.save(OUT/'frames'/f'frame-{ordinal:04}.png')
                        thumbnail = image.resize((180, 320))
                        slot = KEYS.index(ordinal)
                        x, y = slot%6*180, 24+slot//6*344
                        sheets[0].paste(thumbnail, (x, y))
                        overlay = thumbnail.copy()
                        draw = ImageDraw.Draw(overlay)
                        if faces:
                            for index, point in enumerate(xy[ordinal]/4):
                                px, py = point
                                draw.ellipse((px-.6, py-.6, px+.6, py+.6), fill=(0, 255, 0) if index < 468 else (255, 160, 0))
                        sheets[1].paste(overlay, (x, y))
                        for sheet in sheets:
                            ImageDraw.Draw(sheet).text((x+3, y+322), f'{ordinal} face={faces}', fill='white')
                    if ordinal%120 == 0:
                        write('progress.json', {'processed':len(records), 'faces':int(present.sum())})
                        print(json.dumps({'frame':ordinal, 'faces':int(present.sum())}), flush=True)
                if capture.read()[0]:
                    raise ValueError('unexpected extra source frame')
            finally:
                capture.release()
        if digest(MODEL) != expected:
            raise ValueError('entire task changed after inference')
        REPORT.update(processed_frames=len(records), frames_with_face=int(present.sum()),
                      missing_frames=np.flatnonzero(~present).tolist(), fixed_anchor_presence={str(i):bool(present[i]) for i in ANCHORS},
                      keyframes=len(KEYS), model_unchanged=True, nominal_fps=fps)
        for index, sheet in enumerate(sheets):
            sheet.save(OUT/('source-sheet.jpg' if index == 0 else 'observation-sheet.jpg'), quality=90)
        if not present[list(ANCHORS)].all():
            raise ValueError('fixed frontal/oblique acquisition anchor missing')
        REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        for array in (raw, xy, present, stamps):
            if array is not None:
                array.flush()
        REPORT['processed_frames'] = len(records)
        REPORT['seconds'] = time.monotonic()-started
        REPORT['peak_working_set'] = peak_memory()
        write('frames.json', records)
        DONE.set()
        write('report.json', REPORT)
        print(json.dumps(REPORT), flush=True)
    return 0 if REPORT['status'] == 'TECHNICAL_CHECK_PASSED' else 1


if __name__ == '__main__':
    raise SystemExit(main())

