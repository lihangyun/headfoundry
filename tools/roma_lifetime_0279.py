"""One pinned RoMa pair; truth is read only by the separate evaluator stage."""
import ctypes
import gc
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import weakref

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/roma-lifetime-0279'
IMAGE_HASHES = {'pos': 'd511845b67f90afc9b5b3fc8018000d04e413057e6946d04c398e0982c137516',
                'neg': '8fc3538eb50923ae53855615caf4f8871b1bf4914a3ee38d3f4aa0456f355258'}


def save(name, value):
    with (OUT / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


class Memory(ctypes.Structure):
    _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
        (k, ctypes.c_size_t) for k in ['peak', 'working', 'pp', 'p', 'pnp', 'np', 'pf', 'ppf']]


def memory_usage():
    info = Memory()
    info.cb = ctypes.sizeof(info)
    get = ctypes.windll.psapi.GetProcessMemoryInfo
    get.argtypes = [ctypes.c_void_p, ctypes.POINTER(Memory), ctypes.c_ulong]
    if not get(ctypes.c_void_p(-1), ctypes.byref(info), info.cb):
        raise OSError('cannot read process memory')
    return {'peak_bytes': int(info.peak), 'working_bytes': int(info.working)}


def peak():
    return memory_usage()['peak_bytes']


def arm(stage, seconds):
    def stop():
        save('timeout.json', {'stage': stage, 'seconds': seconds})
        os._exit(124)
    timer = threading.Timer(seconds, stop)
    timer.daemon = True
    timer.start()
    return timer


def pixel_controls(torch, model):
    w, h = 23, 17
    xy = np.array([[3.2, 5.4], [10., 8.], [17.8, 11.2]])
    normal = 2*(xy+.5)/[w, h]-1
    roundtrip = np.max(np.abs((normal+1)*[w, h]/2-.5-xy))
    yy, xx = torch.meshgrid(torch.linspace(-1+1/h, 1-1/h, h),
                            torch.linspace(-1+1/w, 1-1/w, w), indexing='ij')
    field = torch.stack((xx, yy), -1)
    query = torch.tensor(normal, dtype=torch.float32)[None, None]
    sampled = torch.nn.functional.grid_sample(field.permute(2, 0, 1)[None], query,
                                              align_corners=False)[0, :, 0].T
    edge = model.to_pixel_coordinates(sampled, h, w).numpy()
    error = float(np.max(np.abs(edge-.5-xy)))
    wrong = float(np.max(np.abs(edge-xy)))
    assert roundtrip <= 1e-10 and error <= .001 and wrong > .1
    return {'numpy_roundtrip_max_px': float(roundtrip), 'torch_bilinear_max_px': error,
            'wrong_half_pixel_max_px': wrong}


def full_state(torch, model, supplied):
    state = model.state_dict()
    assert set(state) == set(supplied)
    values = 0
    for name, actual in state.items():
        expected = supplied[name]
        assert torch.is_tensor(expected) and actual.shape == expected.shape
        assert actual.dtype == expected.dtype
        if actual.numel():
            assert actual.data_ptr() != expected.data_ptr()
        if expected.is_floating_point():
            assert expected.dtype == torch.float32
        assert bool(torch.isfinite(expected).all())
        assert torch.equal(actual.cpu(), expected)
        values += expected.numel()
    return {'state_items': len(state), 'state_values': values,
            'registered_parameters': sum(p.numel() for p in model.parameters())}


def component_fingerprint(model):
    from check_state_fingerprint import state_fingerprint
    return state_fingerprint({name: value.detach().cpu().numpy()
                              for name, value in model.state_dict().items()})


def lifetime_control(torch):
    from check_state_fingerprint import check
    check()
    torch.manual_seed(279)
    source = torch.nn.Linear(5, 3).eval()
    path = OUT / 'tiny-lifetime-control.pt'
    torch.save(source.state_dict(), path)
    copied = torch.nn.Linear(5, 3).eval()
    checkpoint = torch.load(path, map_location='cpu', mmap=True, weights_only=True)
    copied.load_state_dict(checkpoint, strict=True)
    full_state(torch, copied, checkpoint)
    expected = component_fingerprint(source)
    assert component_fingerprint(copied) == expected
    references = [weakref.ref(value) for value in checkpoint.values()]
    del checkpoint
    gc.collect()
    assert all(ref() is None for ref in references)
    with torch.inference_mode():
        copied(torch.ones((2, 5)))
    assert component_fingerprint(copied) == expected
    save('lifetime-control.json', {'status': 'TECHNICAL_CHECK_PASSED',
         'distinct_storage_and_exact_state': True, 'checkpoint_refs_released': True,
         'forward_state_unchanged': True, 'fingerprint': expected})


def infer():
    timer = arm('strict_load_and_coordinate_controls', 180)
    start = time.monotonic()
    finished = threading.Event()

    def memory_guard():
        while not finished.wait(.25):
            value = peak()
            if value > 8*1024**3:
                save('memory-reject.json', {'peak_bytes': value, 'limit_bytes': 8*1024**3})
                os._exit(124)

    threading.Thread(target=memory_guard, daemon=True).start()
    manifest = json.loads((OUT / 'model-assets.json').read_text())
    from install_roma_0279 import MODELS
    expected = MODELS
    assert manifest['source_commit'] == '77f8d68803526dcddfd9b7a46bc76125bdc25f15'
    assert len(manifest['models']) == 2
    rights = json.loads((ROOT / 'assets/private/dense-foundation-preflight-0277/publisher-rights.json').read_text())
    for record, (name, license_id, size, url) in zip(manifest['models'], expected):
        assert record['id'] == record['path'] == name and record['license_id'] == license_id
        assert record['source'] == url
        assert record['bytes'] == size and (OUT / name).stat().st_size == size
        assert 'local_head_reconstruction_validation' in record['allowed_uses']
        assert len(record['sha256']) == 64 and digest(OUT / name) == record['sha256']
        right_name = 'storage_license' if license_id == 'MIT' else 'dinov2_license'
        assert record['rights_source'] == 'notices/'+right_name+'.txt'
        assert (OUT / record['rights_source']).read_text(encoding='utf8') == rights[right_name]
    source_review = json.loads((ROOT / 'assets/private/dense-foundation-preflight-0277/source-contract-review.json').read_text())
    for record in source_review['reviewed_files']:
        assert digest(OUT / 'vendor' / record['path']) == record['sha256']
    from headfoundry.manifest import validate_input_assets
    inputs = json.loads((OUT / 'input-assets.json').read_text())
    assert inputs['training_allowed'] is False and inputs['upload_allowed'] is False
    errors = validate_input_assets(inputs, OUT)
    if errors:
        raise ValueError(str(errors))
    for name, sha in IMAGE_HASHES.items():
        assert digest(OUT / (name+'.png')) == sha

    def deny(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            raise PermissionError('model network access forbidden')
        if event == 'open' and isinstance(args[0], (str, bytes)):
            name = os.fsdecode(args[0]).lower()
            if name.endswith('.stl') or 'known-motion.npz' in name or 'real-case-002' in name:
                raise PermissionError('inference cannot read evaluation geometry')

    sys.addaudithook(deny)
    import torch
    import torchvision
    from PIL import Image
    assert torch.__version__ == '2.10.0+cpu' and torchvision.__version__ == '0.25.0+cpu'
    torch.set_num_threads(4)
    torch.set_num_interop_threads(4)
    torch.set_float32_matmul_precision('highest')
    lifetime_control(torch)
    torch.manual_seed(278)
    from romatch import roma_outdoor
    checkpoints = [torch.load(OUT / name, map_location='cpu', weights_only=True,
                              mmap=True) for name, _, _, _ in expected]
    model = roma_outdoor(device='cpu', weights=checkpoints[0],
                         dinov2_weights=checkpoints[1], use_custom_corr=False,
                         do_compile=False)
    model.eval()
    descriptor = model.encoder.dinov2_vitl14[0]
    states = [full_state(torch, model, checkpoints[0]),
              full_state(torch, descriptor, checkpoints[1])]
    assert descriptor not in list(model.modules())
    fingerprints = [component_fingerprint(model), component_fingerprint(descriptor)]
    before_release = memory_usage()
    references = [weakref.ref(value) for checkpoint in checkpoints for value in checkpoint.values()]
    del checkpoints
    gc.collect()
    assert all(ref() is None for ref in references)
    after_release = memory_usage()
    assert fingerprints == [component_fingerprint(model), component_fingerprint(descriptor)]
    save('checkpoint-release.json', {'before': before_release, 'after': after_release,
         'observed_working_set_change_bytes': after_release['working_bytes']-before_release['working_bytes'],
         'checkpoint_tensor_weakrefs_dead': True, 'fingerprints_unchanged': True,
         'component_fingerprints': fingerprints})
    control = pixel_controls(torch, model)
    save('conformance.json', {'status': 'TECHNICAL_CHECK_PASSED', 'components': states,
         'coordinate_controls': control, 'load_seconds': time.monotonic()-start,
         'peak_bytes': peak(), 'torch': torch.__version__, 'torchvision': torchvision.__version__,
         'physical_accuracy': 'UNVERIFIED'})
    timer.cancel()
    timer = arm('single_full_forward', 180)
    start = time.monotonic()
    with Image.open(OUT / 'pos.png') as a, Image.open(OUT / 'neg.png') as b:
        warp, certainty = model.match(a.convert('RGB'), b.convert('RGB'), device='cpu')
    forward_seconds = time.monotonic()-start
    assert tuple(warp.shape) == (864, 1728, 4) and tuple(certainty.shape) == (864, 1728)
    assert bool(torch.isfinite(warp).all()) and bool(torch.isfinite(certainty).all())
    assert float(certainty.min()) >= 0 and float(certainty.max()) <= 1
    yy, xx = torch.meshgrid(torch.linspace(-1+1/864, 1-1/864, 864),
                            torch.linspace(-1+1/864, 1-1/864, 864), indexing='ij')
    grid = torch.stack((xx, yy), -1)
    source_error = max(float((warp[:, :864, :2]-grid).abs().max()),
                       float((warp[:, 864:, 2:]-grid).abs().max()))*864/2
    assert source_error <= .001
    assert fingerprints == [component_fingerprint(model), component_fingerprint(descriptor)]
    np.savez_compressed(OUT / 'dense-output.npz', warp=warp.cpu().numpy(),
                        certainty=certainty.cpu().numpy())
    save('inference.json', {'status': 'TECHNICAL_CHECK_PASSED',
         'forward_seconds': forward_seconds, 'peak_bytes': peak(),
         'shape': list(warp.shape), 'source_grid_error_px': source_error,
         'model_state_unchanged': True, 'physical_accuracy': 'UNVERIFIED'})
    timer.cancel()
    finished.set()


def bilinear(field, native_xy):
    h, w = field.shape[:2]
    xy = (native_xy+.5)/[720, 1280]*[w, h]-.5
    assert (xy >= 0).all() and (xy <= [w-1, h-1]).all()
    low = np.floor(xy).astype(int)
    high = np.minimum(low+1, [w-1, h-1])
    fraction = xy-low
    if field.ndim == 3:
        fraction = fraction[:, None, :]
    fx, fy = fraction[..., 0], fraction[..., 1]
    return ((1-fx)*(1-fy)*field[low[:, 1], low[:, 0]]+
            fx*(1-fy)*field[low[:, 1], high[:, 0]]+
            (1-fx)*fy*field[high[:, 1], low[:, 0]]+
            fx*fy*field[high[:, 1], high[:, 0]])


def project(k, e, xyz):
    camera = xyz@e[:, :3].T+e[:, 3]
    value = camera@k.T
    return value[:, :2]/value[:, 2:], camera[:, 2]


def evaluate():
    from headfoundry.epipolar import robust_refine_pose, _triangulate
    timer = arm('physical_scoring', 120)
    truth_path = ROOT / 'assets/private/real-capture-pilot-v1/scan-motion-truth-0230-upright/known-motion.npz'
    assert digest(truth_path) == 'eea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942'
    truth = np.load(truth_path, allow_pickle=False)
    output = np.load(OUT / 'dense-output.npz', allow_pickle=False)
    k, xyz, ids = truth['intrinsic'], truth['vertices_mm'], truth['point_ids']
    results, estimated = {}, {}
    mapping = [('pos_to_neg', 4, 3, output['warp'][:, :864, 2:], output['certainty'][:, :864]),
               ('neg_to_pos', 3, 4, output['warp'][:, 864:, :2], output['certainty'][:, 864:])]
    for name, a, b, field, certainty in mapping:
        source = truth['visible'][a]
        rows = np.flatnonzero(source)
        first = truth['pixels'][a, rows]
        predicted = (bilinear(field, first)+1)*[720, 1280]/2-.5
        confidence = bilinear(certainty, first)
        common = truth['visible'][b, rows]
        held = common & (ids[rows] % 2 != 0)
        train = ((ids[rows] % 2 == 0) & (confidence >= .05) & np.isfinite(predicted).all(axis=1)
                 & (predicted >= 0).all(axis=1) & (predicted < [720, 1280]).all(axis=1))
        raw = np.linalg.norm(predicted[common]-truth['pixels'][b, rows[common]], axis=1)
        result = {'source_visible': len(rows), 'true_common': int(common.sum()),
                  'raw_common_p95_px': float(np.percentile(raw, 95)),
                  'training_count': int(train.sum()), 'held_count': int(held.sum()),
                  'low_confidence_common': int((common & (confidence < .05)).sum())}
        ea, eb = truth['extrinsics_mm'][a], truth['extrinsics_mm'][b]
        relative = np.column_stack((eb[:, :3]@ea[:, :3].T,
                                    eb[:, 3]-eb[:, :3]@ea[:, :3].T@ea[:, 3]))
        baseline = np.linalg.norm(relative[:, 3])
        canonical = xyz@ea[:, :3].T+ea[:, 3]
        true_uv, _ = project(k, relative, canonical[rows[common]])
        true_points = _triangulate(first[common], truth['pixels'][b, rows[common]],
                                   k@np.column_stack((np.eye(3), np.zeros(3))), k@relative)
        assert np.max(np.abs(true_uv-truth['pixels'][b, rows[common]])) < 1e-8
        assert np.max(np.linalg.norm(true_points-canonical[rows[common]], axis=1)) < 1e-6
        try:
            if min(train.sum(), held.sum()) < 24:
                raise ValueError('insufficient predeclared support')
            if min(np.ptp(first[train], axis=0).min(), np.ptp(first[held], axis=0).min()) < 50:
                raise ValueError('insufficient spatial span')
            fit = robust_refine_pose(first[train], predicted[train], k, k,
                    threshold_px=2., min_support_fraction=.6, min_parallax_deg=1.,
                    iterations=512, seed=278)
            e = np.asarray(fit['extrinsic'])
            e[:, 3] *= baseline
            uv, depth = project(k, e, canonical[rows[held]])
            camera_errors = np.linalg.norm(uv-truth['pixels'][b, rows[held]], axis=1)
            recovered = _triangulate(first[held], predicted[held],
                         k@np.column_stack((np.eye(3), np.zeros(3))), k@e)
            recovered_depth = recovered@e[:, :3].T+e[:, 3]
            finite_positive = bool(np.isfinite(recovered).all() and (recovered[:, 2] > 0).all()
                                    and (recovered_depth[:, 2] > 0).all() and (depth > 0).all())
            point_errors = np.linalg.norm(recovered-canonical[rows[held]], axis=1)
            camera_p95, point_p95 = float(np.percentile(camera_errors, 95)), float(np.percentile(point_errors, 95))
            passed = finite_positive and np.isfinite(point_p95) and camera_p95 <= 3 and point_p95 <= 2
            result.update(fit=fit, camera_p95_px=camera_p95,
                          point_p95_mm=point_p95 if np.isfinite(point_p95) else None,
                          finite_positive_depths=finite_positive, passed=bool(passed))
            estimated[name] = e
        except (ValueError, np.linalg.LinAlgError) as error:
            result.update(passed=False, pose_failure=str(error))
        results[name] = result
    cross = None
    if len(estimated) == 2:
        a, b = estimated['pos_to_neg'], estimated['neg_to_pos']
        composed = np.column_stack((b[:, :3]@a[:, :3], b[:, :3]@a[:, 3]+b[:, 3]))
        held = truth['visible'][4] & truth['visible'][3] & (ids % 2 != 0)
        source = xyz@truth['extrinsics_mm'][4, :, :3].T+truth['extrinsics_mm'][4, :, 3]
        uv, _ = project(k, composed, source[held])
        cross = float(np.percentile(np.linalg.norm(uv-truth['pixels'][4, held], axis=1), 95))
    save('result.json', {'status': 'PARTIAL_SUCCESS' if all(r['passed'] for r in results.values())
         and cross is not None and cross <= 3 else 'REJECT', 'directions': results,
         'cross_pose_p95_px': cross, 'known_calibration_and_metric_baseline': True,
         'surface_accuracy': 'UNVERIFIED', 'real_video_accuracy': 'UNVERIFIED',
         'head_mesh_produced': False, 'user_visual_acceptance': 'UNVERIFIED'})
    timer.cancel()


if __name__ == '__main__':
    try:
        {'infer': infer, 'evaluate': evaluate}[sys.argv[1]]()
    except Exception as error:
        save('failure-'+sys.argv[1]+'.json', {'type': type(error).__name__, 'error': str(error)})
        raise
