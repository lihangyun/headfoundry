"""Fixed two-pair original RoMa inference; no medical geometry."""
import ctypes,gc,hashlib,json,os,sys,threading,time,weakref
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/roma-video-0383'
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(OUT/'vendor'))
sys.path.append(str(ROOT/'.venv/Lib/site-packages'))  # Reuse installed cv2 after isolated runtime packages.
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
    from install_roma_0383 import MODELS
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
    inputs=json.loads((OUT/'inputs.json').read_text())
    assert inputs['frames_verified']==1041 and inputs['ordinals']==[240,300,630]
    for name,sha in inputs['images'].items():assert digest(OUT/name)==sha

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
    from check_state_fingerprint import state_fingerprint
    expected_fingerprints = [state_fingerprint({name: value.detach().cpu().numpy()
                             for name, value in checkpoint.items()}) for checkpoint in checkpoints]
    assert fingerprints == expected_fingerprints
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
    forwards=[]
    for camera in (1,2):
        timer=arm('fixed_forward_'+str(camera),180)
        start=time.monotonic()
        with Image.open(OUT/'view-0.png') as a, Image.open(OUT/f'view-{camera}.png') as b:
            warp,certainty=model.match(a.convert('RGB'),b.convert('RGB'),device='cpu')
        seconds=time.monotonic()-start
        save(f'forward-{camera}.json',dict(raw_shape=list(warp.shape),certainty_shape=list(certainty.shape),seconds=seconds,peak_bytes=peak()))
        assert tuple(warp.shape)==(1,864,1728,4) and tuple(certainty.shape)==(1,864,1728)
        warp,certainty=warp[0],certainty[0]
        assert bool(torch.isfinite(warp).all()) and bool(torch.isfinite(certainty).all())
        assert float(certainty.min())>=0 and float(certainty.max())<=1
        np.savez_compressed(OUT/f'dense-{camera}.npz',warp=warp.cpu().numpy(),certainty=certainty.cpu().numpy())
        yy,xx=torch.meshgrid(torch.linspace(-1+1/864,1-1/864,864),torch.linspace(-1+1/864,1-1/864,864),indexing='ij')
        grid=torch.stack((xx,yy),-1)
        error=max(float((warp[:,:864,:2]-grid).abs().max()),float((warp[:,864:,2:]-grid).abs().max()))*864/2
        assert error<=.001 and peak()<=8*1024**3
        forwards.append(dict(camera=camera,seconds=seconds,source_grid_error_px=error))
        del warp,certainty,grid,xx,yy;gc.collect();timer.cancel()
    assert fingerprints==[component_fingerprint(model),component_fingerprint(descriptor)]
    save('inference.json',dict(status='TECHNICAL_CHECK_PASSED',forwards=forwards,peak_bytes=peak(),physical_accuracy='UNVERIFIED'))
    finished.set()

if __name__=='__main__':
    try:infer()
    except Exception as error:
        save('inference-failure.json',dict(status='REJECT',type=type(error).__name__,error=str(error)));raise
