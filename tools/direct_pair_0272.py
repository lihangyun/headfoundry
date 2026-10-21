"""Bounded local correspondence prerequisite; no camera/head reconstruction."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/direct-pair-0272'
MODEL = OUT / 'model'
sys.path.insert(0, str(ROOT / 'src'))
from headfoundry.manifest import sha256_file, validate_input_assets

WEIGHT_SHA = '00a5edc343fa222eba763643553548ad37a05aa3d00d266553c9f6cf67bb0e64'
FRAME_IDS = (612, 876, 888, 1040)


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')


def deadline():
    record = json.loads((OUT / 'phase.json').read_text())
    if time.time() > record['deadline_epoch']:
        raise TimeoutError('Registered whole-phase deadline')


def private_guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0]).lower().replace('\\', '/')
        if name.endswith('.stl') or 'case002' in name or '/oracle' in name:
            raise PermissionError('Scan/bone/held-case/oracle excluded')
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise PermissionError('Worker is offline')


def to_native(normalized):
    value = np.asarray(normalized)
    if value.ndim != 3 or value.shape[0] != 2 or value.shape[-1] != 2:
        raise ValueError('Expected 2 x N x xy floating coordinates')
    if not np.issubdtype(value.dtype, np.floating) or not np.isfinite(value).all():
        raise ValueError('Finite floating coordinates required')
    return value.astype(np.float64) * [720., 1280.]


def selfcheck():
    value = np.array([[[.12345, .67891]], [[.31415, .27182]]])
    recovered = to_native(value)
    if not np.allclose(recovered / [720, 1280], value, atol=1e-15, rtol=0):
        raise ValueError('Normalized/native inversion')
    if np.array_equal(recovered, recovered.astype(int)):
        raise ValueError('Subpixel witness lost')
    for bad in (value.astype(int), value.reshape(2, 2), value * np.nan):
        try:
            to_native(bad)
        except ValueError:
            continue
        raise ValueError('Invalid coordinate accepted')
    return {'float_inverse': True, 'subpixel_retained': True, 'invalid_rejected': True}


def cue(image):
    import cv2
    rgb = image.astype(np.int16)
    mask = np.zeros(rgb.shape[:2], np.uint8)
    mask[500:820, 100:620] = (rgb[500:820, 100:620, 0] - rgb[500:820, 100:620, 2] > 12)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count < 2:
        return mask.astype(bool)
    mask = (labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    return cv2.erode(mask, np.ones((8, 8), np.uint8)).astype(bool)


def on_cue(points, mask):
    xy = np.floor(points + .5).astype(int)
    valid = ((xy[:, 0] >= 0) & (xy[:, 0] < 720) & (xy[:, 1] >= 0) & (xy[:, 1] < 1280))
    result = np.zeros(len(points), bool)
    result[valid] = mask[xy[valid, 1], xy[valid, 0]]
    return result


def prepare():
    import cv2
    deadline()
    pilot = ROOT / 'assets/private/real-capture-pilot-v1'
    manifest = json.loads((pilot / 'manifest.json').read_text(encoding='utf-8'))
    # Validate ONLY the explicitly selected authorized video, not other cases/STLs.
    selected = [asset for asset in manifest['inputs'] if asset['id'] == 'real-case-001-video']
    if len(selected) != 1:
        raise ValueError('Unique selected video required')
    subset = dict(manifest, inputs=selected)
    if manifest.get('training_allowed') is not False or manifest.get('upload_allowed') is not False:
        raise ValueError('Local validation only')
    errors = validate_input_assets(subset, pilot)
    if errors:
        raise ValueError(str(errors))
    source = Path(selected[0]['path'])
    prior = json.loads((ROOT / 'assets/private/video-observability-0252/report.json').read_text())
    if sha256_file(source) != prior['source_sha256']:
        raise ValueError('Original video identity changed')
    capture = cv2.VideoCapture(str(source))
    frames = {}
    for index in range(max(FRAME_IDS) + 1):
        deadline()
        ok, bgr = capture.read()
        if not ok:
            raise ValueError('Sequential decode truncated')
        if index in FRAME_IDS:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            if rgb.shape != (1280, 720, 3):
                raise ValueError('Native frame size changed')
            if hashlib.sha256(rgb.tobytes()).hexdigest() != prior['frame_records'][index]['rgb_sha256']:
                raise ValueError('Source ordinal RGB hash mismatch')
            frames[str(index)] = rgb
    capture.release()
    matrix = cv2.getRotationMatrix2D((360, 640), 3, .97)
    matrix[:, 2] += [4, -3]
    frames['warped'] = cv2.warpAffine(frames['612'], matrix, (720, 1280), flags=cv2.INTER_LINEAR)
    np.savez_compressed(OUT / 'input.npz', **frames, homography=np.vstack([matrix, [0, 0, 1]]),
                        cue612=cue(frames['612']))
    if sha256_file(source) != prior['source_sha256']:
        raise ValueError('Source changed during preparation')
    save('preparation.json', {'source_unchanged': True, 'verified_ordinals': list(FRAME_IDS),
        'source_sha256': prior['source_sha256'], 'input_sha256': sha256_file(OUT / 'input.npz'),
        'shared_selfcheck': selfcheck(), 'scan_read': False, 'case002_read': False,
        'training': False, 'upload': False})


def planar_report(points, valid, data):
    selected = valid & on_cue(points[0], data['cue612'])
    first, second = points[:, selected]
    truth = np.c_[first, np.ones(len(first))] @ data['homography'].T
    truth = truth[:, :2] / truth[:, 2:]
    errors = np.linalg.norm(second - truth, axis=1)
    unique = len(np.unique(first, axis=0))
    span = np.ptp(first, axis=0) if len(first) else np.zeros(2)
    p95, maximum = (float(np.percentile(errors, 95)), float(errors.max())) if len(errors) else (None, None)
    passed = unique == len(first) and unique >= 50 and bool((span >= 100).all())
    passed = passed and p95 <= 1 and maximum <= 3
    np.savez_compressed(OUT / 'planar-errors.npz', selected=selected, errors=errors, expected=truth)
    return {'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        'scope': 'Selected-output planar localization, NOT physical3D/camera/head',
        'all_outputs': len(valid), 'eligible_count': len(first), 'unique_sources': unique,
        'source_span_px': span.tolist(), 'p95_px': p95, 'max_px': maximum,
        'all_eligible_outputs_scored': True, 'all_point_recall': 'UNVERIFIED'}


def memory_bytes():
    class Memory(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ('peak', 'working', 'poolpeak', 'pool',
                'nonpagepeak', 'nonpage', 'page', 'pagepeak')]
    counters = Memory()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Memory), ctypes.c_ulong]
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    if not ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise OSError('Memory measurement failed')
    return int(counters.peak)


def infer():
    phase = json.loads((OUT / 'phase.json').read_text())
    started = time.perf_counter() - max(0, time.time() - phase['inference_started_epoch'])
    sys.addaudithook(private_guard)
    import torch
    from safetensors.torch import load_file
    from transformers import EfficientLoFTRConfig, EfficientLoFTRImageProcessor
    from aligned_index_0272 import AlignedIndexMatcher, check_actual_contracts
    from PIL import Image
    deadline()
    torch.set_num_threads(8)
    if sha256_file(MODEL / 'model.safetensors') != WEIGHT_SHA:
        raise ValueError('Wrong checkpoint')
    for name, digest in [('config.json', 'eaa141ed38f64ec65efe7b663338e2b44d260ff2b26f5829624e5241ff29f1d8'),
                         ('preprocessor_config.json', '22151d20a71d5d25bee2b5f5c3a5999befa3285597218a9d1ea63998f84dc606')]:
        if sha256_file(MODEL / name) != digest:
            raise ValueError('Configuration identity changed')
    model = AlignedIndexMatcher(EfficientLoFTRConfig.from_json_file(MODEL / 'config.json'))
    state = load_file(MODEL / 'model.safetensors', device='cpu')
    expected = model.state_dict()
    if state.keys() != expected.keys():
        raise ValueError('Full key mismatch')
    for key, value in state.items():
        if value.shape != expected[key].shape or value.dtype != expected[key].dtype or not torch.isfinite(value).all():
            raise ValueError('State shape/dtype/finite mismatch: ' + key)
    model.load_state_dict(state, strict=True)
    model.eval()
    save('actual-index-controls.json', check_actual_contracts(model))
    del expected, state
    processor = EfficientLoFTRImageProcessor.from_pretrained(MODEL, local_files_only=True)
    data = np.load(OUT / 'input.npz', allow_pickle=False)
    steps = []
    for name, first, second in [('planar', '612', 'warped'), ('boundary', '876', '888'), ('return', '612', '1040')]:
        deadline()
        if time.perf_counter() - started > 180 or memory_bytes() > 4_000_000_000:
            raise TimeoutError('Inference resource budget')
        inputs = processor([Image.fromarray(data[first]), Image.fromarray(data[second])],
                           size={'height': 672, 'width': 384}, return_tensors='pt')
        if inputs['pixel_values'].shape[:2] != (1, 2):
            raise ValueError('Only a single image-pair batch is permitted')
        with torch.inference_mode():
            outputs = model(**inputs)
        points = to_native(outputs.keypoints[0].cpu().numpy())
        scores = outputs.matching_scores[0].cpu().numpy()
        indices = outputs.matches[0].cpu().numpy()
        if scores.shape != indices.shape or scores.shape != points.shape[:2] or not np.isfinite(scores).all():
            raise ValueError('Output shape/finite mismatch')
        valid = (indices >= 0).all(axis=0) & (scores > .2).all(axis=0)
        np.savez_compressed(OUT / (name + '.npz'), points=points, scores=scores, indices=indices, valid=valid)
        row = {'pair': name, 'seconds_since_worker_start': time.perf_counter() - started,
               'all_outputs': int(points.shape[1]), 'peak_bytes': memory_bytes()}
        steps.append(row)
        save('worker-progress.json', {'steps': steps, 'strict_full_state': True})
        if name == 'planar':
            report = planar_report(points, valid, data)
            save('planar-report.json', report)
            if report['status'] != 'TECHNICAL_CHECK_PASSED':
                break
    deadline()
    elapsed, peak = time.perf_counter() - started, memory_bytes()
    save('worker.json', {'execution_status': 'TECHNICAL_CHECK_PASSED' if elapsed <= 180 and peak <= 4_000_000_000 else 'REJECT',
        'steps': steps, 'elapsed_seconds': elapsed, 'peak_bytes': peak, 'strict_full_state': True,
        'torch': torch.__version__, 'offline_guard': True, 'physical_camera': 'UNVERIFIED', 'head': 'UNVERIFIED'})


def evaluate():
    import cv2
    deadline()
    report = json.loads((OUT / 'planar-report.json').read_text())
    if report['status'] != 'TECHNICAL_CHECK_PASSED':
        save('result.json', {'status': 'REJECT', 'stop': 'Planar precision prerequisite', 'planar': report,
                             'real_pairs_executed': False, 'camera': 'UNVERIFIED', 'head': 'UNVERIFIED'})
        return
    data = np.load(OUT / 'input.npz', allow_pickle=False)
    rows = []
    for name, a, b in [('boundary', '876', '888'), ('return', '612', '1040')]:
        record = np.load(OUT / (name + '.npz'), allow_pickle=False)
        points = record['points']
        selected = record['valid'] & on_cue(points[0], cue(data[a])) & on_cue(points[1], cue(data[b]))
        p, q = points[:, selected]
        even = np.arange(len(p)) % 2 == 0
        spans = np.ptp(points[:, selected], axis=1) if len(p) else np.zeros((2, 2))
        unique = all(len(np.unique(x, axis=0)) == len(p) for x in (p, q))
        eligible = len(p) >= 50 and unique and (spans >= 100).all() and min(even.sum(), (~even).sum()) >= 20
        errors = np.empty(0)
        matrix = None
        if eligible:
            cv2.setRNGSeed(270)
            matrix, _ = cv2.findFundamentalMat(p[even], q[even], cv2.USAC_MAGSAC, 1., .999, 10000)
            if matrix is not None and matrix.shape == (3, 3) and np.isfinite(matrix).all() and np.linalg.matrix_rank(matrix) == 2:
                x, y = np.c_[p[~even], np.ones((~even).sum())], np.c_[q[~even], np.ones((~even).sum())]
                line_b, line_a = x @ matrix.T, y @ matrix
                numerator = np.abs(np.sum(y * line_b, axis=1))
                den_a, den_b = np.linalg.norm(line_a[:, :2], axis=1), np.linalg.norm(line_b[:, :2], axis=1)
                if min(den_a.min(), den_b.min()) > 0:
                    errors = np.maximum(numerator / den_a, numerator / den_b)
        p95 = float(np.percentile(errors, 95)) if len(errors) and np.isfinite(errors).all() else None
        passed = bool(eligible) and p95 is not None and p95 <= 3
        np.savez_compressed(OUT / (name + '-evaluation.npz'), selected=selected, even=even,
                            held_errors=errors, fundamental=matrix if matrix is not None else np.empty((0, 0)))
        rows.append({'pair': name, 'eligible_count': len(p), 'spans_px': spans.tolist(),
            'unique': unique, 'held_count': len(errors), 'held_epipolar_p95_px': p95,
            'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT'})
    save('result.json', {'status': 'TECHNICAL_CHECK_PASSED' if all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in rows) else 'REJECT',
        'scope': 'Limited pixel/F-readiness only, NOT physical identity, camera or head', 'planar': report,
        'real_pairs_executed': True, 'pairs': rows, 'camera': 'UNVERIFIED', 'head': 'UNVERIFIED'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'infer', 'evaluate', 'selfcheck'])
    args = parser.parse_args()
    if args.stage == 'selfcheck':
        print(json.dumps(selfcheck()))
    else:
        sys.addaudithook(private_guard)
        try:
            globals()[args.stage]()
        except Exception as error:
            if OUT.exists():
                save('failure.json', {'status': 'REJECT', 'stage': args.stage, 'error': repr(error)})
            raise

