"""Single strict-state/operator/native-capacity control; no human input."""
import ctypes
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request
import os

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/private/sparse-runtime-0298'
OUT = DEST/'control'
REPORT = {'status': 'REJECT', 'physical_quality': 'UNVERIFIED'}
DONE = threading.Event()
DEADLINE = time.monotonic()+60


def digest(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def save():
    (OUT/'report.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


def phase(name, seconds):
    global DEADLINE
    DEADLINE = time.monotonic()+seconds
    REPORT['phase'] = name
    save()
    print(json.dumps({'phase': name}), flush=True)


def watchdog():
    while not DONE.wait(.25):
        if time.monotonic() > DEADLINE:
            REPORT['failure'] = 'phase deadline exceeded'
            save()
            os._exit(124)


def blocked(*args, **kwargs):
    raise RuntimeError('network/default model downloads forbidden')


def peak_working_set():
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)]+[(n, ctypes.c_size_t) for n in
                    ('peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]
    data = Counters()
    data.cb = ctypes.sizeof(data)
    kernel, psapi = ctypes.WinDLL('kernel32'), ctypes.WinDLL('psapi')
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(data), data.cb):
        raise RuntimeError('working-set counter unavailable')
    return data.peak


def state_check(model, raw):
    actual = model.state_dict()
    if set(actual) != set(raw):
        raise ValueError('full released-state keys differ')
    for name, value in actual.items():
        source = raw[name]
        if not isinstance(source, torch.Tensor) or source.shape != value.shape or source.dtype != value.dtype:
            raise ValueError('state shape/dtype mismatch:'+name)
        if source.is_floating_point() and (source.dtype != torch.float32 or not torch.isfinite(source).all()):
            raise ValueError('nonfinite/nonFP32 state:'+name)
        a = value.detach().cpu().contiguous().reshape(-1).view(torch.uint8)
        b = source.detach().cpu().contiguous().reshape(-1).view(torch.uint8)
        if not torch.equal(a, b):
            raise ValueError('copied state bytes differ:'+name)
    return {'state_tensors': len(actual), 'parameter_tensors': sum(1 for _ in model.parameters()),
            'parameters': sum(p.numel() for p in model.parameters()), 'all_copied_bytes_equal': True}


def bounded_delta(actual, expected):
    if not torch.isfinite(actual).all() or actual.shape != expected.shape:
        raise ValueError('invalid operator shape/values')
    delta = float((actual-expected).abs().max())
    bound = 32*torch.finfo(torch.float32).eps*max(1, float(expected.abs().max()))
    if delta > bound:
        raise ValueError('fixed FP32 operator roundoff bound exceeded')
    return {'values': actual.numel(), 'max_delta': delta, 'bound': bound}


def operator_controls(runtime, reference):
    generator = torch.Generator(device='cuda').manual_seed(298)
    probability = torch.rand((2, 32, 48), generator=generator, device='cuda')+.01
    options = dict(num_samples=64, device=probability.device, use_nms=False, sample_topk=True,
                   return_scoremap=True, sharpen=False, upsample=False, increase_coverage=True, remove_borders=False)
    points, confidence = runtime.sample_keypoints(probability, **options)
    expected, expected_conf = reference.sample_keypoints(probability, **options)
    if not torch.equal(points, expected):
        raise ValueError('selected coordinate/index ordering differs')
    scores = bounded_delta(confidence, expected_conf)
    y, x = torch.meshgrid(torch.arange(1280, device='cuda'), torch.arange(720, device='cuda'), indexing='ij')
    field = torch.stack((x, y)).float()[None]
    pixels = field.permute(0, 2, 3, 1)
    normalized = runtime.normalized_from_cv(pixels, 1280, 720)
    # Analytic ramp is border-extended; learned descriptor sampling remains publisher zero-padding.
    sampled = runtime.F.grid_sample(field, normalized, align_corners=False,
                                    padding_mode='border').permute(0, 2, 3, 1)
    ramp_error = float((sampled-pixels).abs().max())
    coordinate_error = float((runtime.cv_pixels(normalized, 1280, 720)-pixels).abs().max())
    if ramp_error > .001 or coordinate_error > .001:
        raise ValueError('native integer-center ramp adapter failed')
    a = torch.randn((2, 64, 16), generator=generator, device='cuda')
    b = torch.randn((2, 64, 16), generator=generator, device='cuda')
    probabilities = bounded_delta(runtime.dual_softmax_matcher(a, b, 20, True),
                                  reference.dual_softmax_matcher(a, b, 20, True))
    identity = torch.eye(4, device='cuda')
    permutation = torch.tensor([2, 0, 3, 1], device='cuda')
    pairs, ambiguous = runtime.match_indices(runtime.dual_softmax_matcher(identity, identity[permutation], 20, True))
    if len(pairs) != 4 or ambiguous or not torch.equal(permutation[pairs[:, 2]], pairs[:, 1]):
        raise ValueError('known permutation matching failed')
    ones = torch.ones((2, 4), device='cuda')
    ties, ambiguous = runtime.match_indices(runtime.dual_softmax_matcher(ones, ones, 20, True))
    if len(ties) != 4 or not ambiguous:
        raise ValueError('mutual ties silently lost or unflagged')
    for invalid in (torch.zeros_like(a), a*float('nan')):
        try:
            runtime.dual_softmax_matcher(invalid, b, 20, True)
        except ValueError:
            continue
        raise ValueError('invalid descriptor accepted')
    for invalid in (torch.zeros_like(probability), probability*float('nan')):
        try:
            runtime.sample_keypoints(invalid, **options)
        except ValueError:
            continue
        raise ValueError('invalid probability map accepted')
    return {'selected_coordinate_values': points.numel(), 'selected_indices_equal': True,
            'scores': scores, 'native_ramp_values': sampled.numel(), 'native_ramp_max_px': ramp_error,
            'native_coordinate_max_px': coordinate_error,
            'probabilities': probabilities, 'permutation_pairs': 4, 'ties_retained_and_flagged': len(ties),
            'invalid_descriptors_rejected': 2, 'invalid_probability_maps_rejected': 2}


def paired_pipeline(runtime, reference, detector_module, detector, descriptor):
    generator = torch.Generator(device='cuda').manual_seed(298)
    image = runtime.normalize_rgb(torch.rand((1, 3, 128, 192), generator=generator, device='cuda')*255)
    outputs = []
    for sampling in (reference.sample_keypoints, runtime.sample_keypoints):
        detector_module.sample_keypoints = sampling
        features = detector.detect({'image': image}, num_keypoints=64)
        described = descriptor.describe_keypoints({'image': image}, features['keypoints'])['descriptions']
        outputs.append((features, described))
    first, second = outputs
    pixel_delta = torch.linalg.vector_norm(runtime.cv_pixels(first[0]['keypoints'], 128, 192)-
                                          runtime.cv_pixels(second[0]['keypoints'], 128, 192), dim=-1)
    if float(pixel_delta.max()) > .001:
        raise ValueError('complete pipeline point equivalence failed')
    desc = bounded_delta(second[1], first[1])
    scores = bounded_delta(second[0]['confidence'], first[0]['confidence'])
    import numpy as np
    np.savez_compressed(OUT/'pipeline-deltas.npz',point_delta_px=pixel_delta.cpu().numpy(),
                        descriptor_delta=(second[1]-first[1]).cpu().numpy(),
                        score_delta=(second[0]['confidence']-first[0]['confidence']).cpu().numpy())
    return {'points': pixel_delta.numel(), 'max_point_delta_px': float(pixel_delta.max()),
            'descriptors': desc, 'scores': scores}


def main():
    global torch
    OUT.mkdir(exist_ok=False)
    started = time.monotonic()
    threading.Thread(target=watchdog, daemon=True).start()
    try:
        phase('strict-state', 60)
        import dedode_runtime_0298 as runtime
        torch = runtime.torch
        lock = runtime.LOCK
        provision = json.loads((DEST/'provision.json').read_text())
        if provision['status'] != 'TECHNICAL_CHECK_PASSED' or digest(DEST/'checkpoint-receipt.json') != sys.argv[-1]:
            raise ValueError('complete acquisition/receipt not admitted')
        versions = {w['name']: importlib.metadata.version(w['name']) for w in lock['wheels']}
        if any(versions[w['name']] != w['version'] for w in lock['wheels']):
            raise ValueError('runtime wheel version differs')
        for path, expected in lock['source_files'].items():
            if digest(DEST/'source'/path) != expected:
                raise ValueError('core/source license hash differs')
        reference_path = DEST/'source/inference-reference.py'
        if digest(reference_path) != provision['reference_extract']['sha256']:
            raise ValueError('inference-only reference differs')
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable;no fallback')
        props = torch.cuda.get_device_properties(0)
        torch.cuda.set_per_process_memory_fraction(7*2**30/props.total_memory)
        a = torch.arange(256, device='cuda', dtype=torch.float32).reshape(16, 16)
        if not torch.equal(a@torch.eye(16, device='cuda'), a):
            raise ValueError('actual CUDA identity matmul failed')
        socket.socket.connect = blocked
        urllib.request.urlopen = blocked
        torch.hub.load_state_dict_from_url = blocked
        model_module, detector_module = runtime.core_modules()
        spec = importlib.util.spec_from_file_location('inference_reference', reference_path)
        reference = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reference)
        receipts = json.loads((DEST/'checkpoint-receipt.json').read_text())
        if [r['name'] for r in receipts] != [r['name'] for r in lock['checkpoint_assets']]:
            raise ValueError('checkpoint population changed')
        models, raw_states, states = [], [], []
        for receipt, factory in zip(receipts, (model_module.dedode_detector_L, model_module.dedode_descriptor_B)):
            path = DEST/receipt['name']
            if digest(path) != receipt['sha256'] or path.stat().st_size != receipt['bytes']:
                raise ValueError('checkpoint acquired bytes changed')
            raw = torch.load(path, map_location='cpu', weights_only=True)
            if not isinstance(raw, dict) or not all(isinstance(k, str) for k in raw):
                raise ValueError('unexpected released state format')
            model = factory(device=torch.device('cuda:0'), weights=raw).eval().requires_grad_(False)
            for child in model.modules():
                if hasattr(child, 'amp'):
                    child.amp = False
            states.append(state_check(model, raw))
            models.append(model)
            raw_states.append(raw)
        REPORT['state'] = states
        REPORT['versions'] = versions
        REPORT['cuda'] = {'name': props.name, 'total_memory': props.total_memory}
        phase('software-controls', 120)
        with torch.inference_mode():
            REPORT['operators'] = operator_controls(runtime, reference)
            REPORT['pipeline'] = paired_pipeline(runtime, reference, detector_module, *models)
        phase('native-capacity', 180)
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        native_started = time.monotonic()
        with torch.inference_mode():
            generator = torch.Generator(device='cuda').manual_seed(298)
            image = runtime.normalize_rgb(torch.rand((1, 3, 1280, 720), generator=generator, device='cuda')*255)
            features = models[0].detect({'image': image}, num_keypoints=4096)
            descriptions = models[1].describe_keypoints({'image': image}, features['keypoints'])['descriptions']
            pixels = runtime.cv_pixels(features['keypoints'], 1280, 720)
        torch.cuda.synchronize()
        if descriptions.shape != (1, 4096, 256) or pixels.shape != (1, 4096, 2):
            raise ValueError('native sparse output shape differs')
        if not all(torch.isfinite(t).all() for t in (descriptions, pixels, features['confidence'])):
            raise ValueError('nonfinite native output')
        native = {'seconds': time.monotonic()-native_started, 'keypoints': 4096,
                  'descriptor_values': descriptions.numel(), 'peak_reserved': torch.cuda.max_memory_reserved(),
                  'peak_working_set': peak_working_set(), 'shape': list(descriptions.shape)}
        REPORT['native'] = native
        if native['seconds'] > 180 or native['peak_reserved'] > 7*2**30 or native['peak_working_set'] > 8*2**30:
            raise ValueError('native resource cap exceeded')
        REPORT['state_after_inference'] = [state_check(m, s) for m, s in zip(models, raw_states)]
        REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        DONE.set()
        REPORT['seconds'] = time.monotonic()-started
        save()
        print(json.dumps(REPORT), flush=True)
    return 0 if REPORT['status'] == 'TECHNICAL_CHECK_PASSED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
