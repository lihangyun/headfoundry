"""Bounded offline software entry only;no human data or physical-score claims."""
from pathlib import Path
import ctypes
import hashlib
import importlib.metadata as metadata
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/tapir-runtime-0307'
SOURCE = ROOT/'assets/private/tapir-preflight-0306'
SITE = OUT/'site-packages'
LOCK = ROOT/'examples/bootstapir-0307.asset-lock.json'


def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False))


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def validate_lock(lock):
    if lock['commercial_use'] is not True or lock['license_id'] != 'Apache-2.0':
        raise ValueError('unapproved rights')
    values = [lock.get(key) for key in ['license_sha256', 'readme_sha256', 'weights_sha256']]+list(lock.get('sources', {}).values())
    if len(values)!=6 or any(not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value) for value in values):
        raise ValueError('all six SHA256 identities must be64lowercase hex characters:'+str([(len(value),value) for value in values if isinstance(value,str) and len(value)!=64]))


def verify_sources(lock):
    validate_lock(lock)
    published = json.loads((SOURCE/'hf-metadata.json').read_text())
    weight = next(row for row in published if row.get('path')=='bootstapir_checkpoint_v2.pt')
    if lock['weights_sha256']!=weight['lfs']['oid'] or lock['weights_bytes']!=weight['size']:
        raise ValueError('checkpoint lock differs from captured publisher metadata')
    recorded = {row['path']:row['sha256'] for row in json.loads((SOURCE/'sources.json').read_text())['sources']}
    for path, expected in {**lock['sources'], 'LICENSE':lock['license_sha256'], 'README.md':lock['readme_sha256']}.items():
        if recorded.get(path)!=expected or digest(SOURCE/path) != expected:
            raise ValueError('source/license identity differs:'+path)


def setup():
    lock = json.loads(LOCK.read_text())
    verify_sources(lock)
    OUT.mkdir(exist_ok=False)
    temporary = OUT/'temporary'
    temporary.mkdir()
    started = time.time()
    state = {'status':'RUNNING', 'started':started, 'pid':os.getpid(), 'phase':'CPU package install'}
    write('setup.json', state)
    env = os.environ.copy()
    env.update(TEMP=str(temporary), TMP=str(temporary), UV_PYTHON_DOWNLOADS='never', UV_NATIVE_TLS='true', PYTHONDONTWRITEBYTECODE='1')
    uv = Path('C:/Users/lihan/.local/bin/uv.exe')
    commands = [
        [str(uv), '--no-cache', 'pip', 'install', '--python', sys.executable,
         '--target', str(SITE), '--no-deps', 'torch=='+lock['torch'], '--index-url', 'https://download.pytorch.org/whl/cpu'],
        [str(uv), '--no-cache', 'pip', 'install', '--python', sys.executable,
         '--target', str(SITE), '--no-deps', *lock['extra_packages']],
    ]
    try:
        for index, command in enumerate(commands):
            with (OUT/f'install-{index}.log').open('w') as log:
                subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=min(420, max(1, 900-(time.time()-started))))
        state['phase'] = 'hash-locked checkpoint download'
        write('setup.json', state)
        download_started = time.time()
        partial = OUT/'checkpoint.pt.part'
        total = 0
        with urllib.request.urlopen(lock['weights_url'], timeout=30) as response, partial.open('xb') as target:
            while chunk := response.read(1024**2):
                total += len(chunk)
                if total > lock['weights_bytes'] or time.time()-download_started > 600 or time.time()-started > 900:
                    raise TimeoutError('registered bytes/time budget exceeded')
                target.write(chunk)
        if total != lock['weights_bytes'] or digest(partial) != lock['weights_sha256']:
            raise ValueError('complete checkpoint identity differs')
        partial.rename(OUT/'checkpoint.pt')
        state.update(status='TECHNICAL_CHECK_PASSED', phase='setup only', seconds=time.time()-started,
                     weights_sha256=lock['weights_sha256'], bytes=total, inference=False)
    except Exception as error:
        state.update(status='REJECT', failure=type(error).__name__+':'+str(error), seconds=time.time()-started)
        write('setup.json', state)
        raise
    write('setup.json', state)
    print(json.dumps(state), flush=True)


def check():
    lock = json.loads(LOCK.read_text())
    verify_sources(lock)
    if digest(OUT/'checkpoint.pt') != lock['weights_sha256']:
        raise ValueError('checkpoint changed')
    sys.path[:0] = [str(SITE), str(SOURCE)]
    started = time.monotonic()
    state = {'status':'RUNNING', 'started_utc':time.time(), 'pid':os.getpid(), 'peak_working_set':0}
    stop = threading.Event()

    def fail(message, code):
        state.update(status='REJECT', failure=message, seconds=time.monotonic()-started)
        write('check.json', state)
        os._exit(code)

    class Memory(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ('peak', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]

    memory = Memory()
    memory.cb = ctypes.sizeof(memory)
    ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    measure = ctypes.windll.psapi.GetProcessMemoryInfo
    measure.argtypes = [ctypes.c_void_p, ctypes.POINTER(Memory), ctypes.c_ulong]

    def watch():
        while not stop.wait(.1):
            if not measure(handle, ctypes.byref(memory), memory.cb):
                fail('working-set measurement failed', 125)
            state['peak_working_set'] = int(memory.peak)
            if memory.peak > 6*1024**3:
                fail('6GiB working-set budget exceeded', 126)
            if time.monotonic()-started > 180:
                fail('180s software-check budget exceeded', 124)

    def private_guard(event, args):
        if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo'}:
            raise PermissionError('offline worker')
        if event == 'open' and isinstance(args[0], (str, os.PathLike)):
            path = Path(args[0]).resolve()
            if str(path).lower().endswith('.stl'):
                raise PermissionError('medical input denied')
            private = ROOT/'assets/private'
            if path.is_relative_to(private) and not (path.is_relative_to(OUT) or path.is_relative_to(SOURCE)):
                raise PermissionError('private case/source input denied')

    sys.addaudithook(private_guard)
    thread = threading.Thread(target=watch, daemon=True)
    thread.start()
    write('check.json', state)
    try:
        import socket
        denied = []
        for operation in [lambda: (ROOT/'assets/private/real-capture-pilot-v1/manifest.json').read_bytes(),
                          lambda: socket.getaddrinfo('example.invalid', 443)]:
            try:
                operation()
                raise ValueError('denial control did not deny')
            except PermissionError:
                denied.append(True)
        import numpy as np
        import torch
        from packaging.requirements import Requirement
        from tapnet.torch import tapir_model, utils
        if torch.__version__ != lock['torch'] or torch.version.cuda is not None:
            raise ValueError('CPU runtime identity differs')
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        torch.manual_seed(307)
        dependency_rows = []
        for distribution in metadata.distributions(path=[str(SITE)]):
            for declaration in distribution.requires or []:
                requirement = Requirement(declaration)
                if requirement.marker and not requirement.marker.evaluate({'extra':''}):
                    continue
                actual = metadata.version(requirement.name)
                if actual not in requirement.specifier:
                    raise ValueError('dependency constraint differs:'+declaration+' vs '+actual)
            dependency_rows.append({'name':distribution.metadata['Name'], 'version':distribution.version,
                                    'license':distribution.metadata.get('License-Expression') or distribution.metadata.get('License'),
                                    'path':str(distribution.locate_file(''))})
            for index, item in enumerate(distribution.files or []):
                if 'license' in str(item).lower() or 'copying' in str(item).lower() or 'notice' in str(item).lower():
                    source = Path(distribution.locate_file(item))
                    if source.is_file():
                        destination = OUT/'notices'/distribution.metadata['Name']/(str(index)+'-'+Path(item).name)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(source.read_bytes())
        write('dependencies.json', dependency_rows)
        if any(not row['license'] for row in dependency_rows):
            raise ValueError('dependency license metadata missing;review actual notices first')

        ramp = torch.tensor([[[[[100*t+10*y+x] for x in range(4)] for y in range(4)] for t in range(2)]], dtype=torch.float32)
        sample = utils.map_coordinates_3d(ramp, torch.tensor([[[1., 2.5, 1.5]]]))
        xy = torch.tensor([[[[[2.5, 1.5]], [[2.5, 1.5]]]]])
        sample2 = utils.map_coordinates_2d(ramp, xy)
        heat = torch.zeros((1, 1, 2, 4, 4))
        heat[:, :, :, 2, 1] = 1
        centers = utils.heatmaps_to_points(heat, (1, 2, 512, 512, 3))
        forced = utils.heatmaps_to_points(heat, (1, 2, 512, 512, 3), query_points=torch.tensor([[[1., 160.5, 112.5]]]))
        errors = [float(abs(sample.item()-121)), float(torch.max(torch.abs(sample2.flatten()-torch.tensor([21.,121.])))),
                  float(torch.max(torch.abs(centers-torch.tensor([192.,320.])))),
                  float(torch.max(torch.abs(forced[0,0,1]-torch.tensor([112.5,160.5]))))]
        original = np.array([[0.,0.],[200.25,300.75],[519.,599.]])
        resized = (original+.5)*np.array([512/520,512/600])
        inverse = resized*np.array([520/512,600/512])-.5
        errors.append(float(np.max(np.abs(original-inverse))))
        if max(errors)>1e-4 or np.max(np.abs(centers[0,0,0].numpy()-[320.,192.]))<1 or np.max(np.abs(inverse+.5-original))<.49:
            raise ValueError('independent raster/axis/time coordinate control failed')
        write('coordinates.json', {'max_error_px':max(errors), 'errors':errors, 'wrong_axis_rejected':True, 'missing_halfpixel_rejected':True})
        model = tapir_model.TAPIR(pyramid_level=1, num_pips_iter=4, extra_convs=True,
                                  use_casual_conv=False, initial_resolution=(256,256), feature_extractor_chunk_size=10).eval()
        checkpoint = torch.load(OUT/'checkpoint.pt', map_location='cpu', weights_only=True, mmap=True)
        template = model.state_dict()
        if set(checkpoint)!=set(template):
            raise ValueError('complete checkpoint keys differ')
        for name, tensor in checkpoint.items():
            if tensor.shape!=template[name].shape or tensor.dtype!=template[name].dtype or not bool(torch.isfinite(tensor).all()):
                raise ValueError('checkpoint tensor invalid:'+name)
        model.load_state_dict(checkpoint, strict=True)
        if not all(torch.equal(checkpoint[name], tensor) for name,tensor in model.state_dict().items()):
            raise ValueError('loaded state differs')
        rng = np.random.default_rng(307)
        frames = rng.integers(0,256,(4,512,512,3), dtype=np.uint8)
        queries = np.c_[np.zeros(8), rng.uniform(64,448,(8,2))].astype(np.float32)
        video = torch.from_numpy(frames).float()[None]/255*2-1
        query = torch.from_numpy(queries)[None]
        forward_start = time.monotonic()
        with torch.inference_mode():
            outputs = model(video, query, is_training=False, query_chunk_size=32)
        raw = {name:outputs[name].numpy() for name in ['tracks','occlusion','expected_dist']}
        if raw['tracks'].shape!=(1,8,4,2) or any(raw[name].shape!=(1,8,4) for name in ['occlusion','expected_dist']) or not all(np.isfinite(value).all() for value in raw.values()):
            raise ValueError('complete forward shape/finite contract failed')
        if not all(torch.equal(checkpoint[name], tensor) for name,tensor in model.state_dict().items()) or digest(OUT/'checkpoint.pt')!=lock['weights_sha256']:
            raise ValueError('state/checkpoint changed after inference')
        np.savez_compressed(OUT/'procedural-output.npz', **raw, queries=queries)
        state.update(status='TECHNICAL_CHECK_PASSED', seconds=time.monotonic()-started,
                     forward_seconds=time.monotonic()-forward_start, state_tensors=len(checkpoint),
                     parameters=sum(p.numel() for p in model.parameters()), coordinate_max_px=max(errors),
                     procedural_input_sha256=hashlib.sha256(frames.tobytes()).hexdigest(), source_and_state_unchanged=True,
                     input_denial_controls=len(denied), patient_pixels_read=False, physical_accuracy='UNVERIFIED', head=False)
    except Exception as error:
        state.update(status='REJECT', failure=type(error).__name__+':'+str(error), seconds=time.monotonic()-started)
        write('check.json', state)
        raise
    finally:
        stop.set()
        thread.join(timeout=1)
    write('check.json', state)
    print(json.dumps(state), flush=True)


if __name__=='__main__':
    if Path.cwd().resolve()!=ROOT or sys.flags.optimize:
        raise RuntimeError('explicit repository cwd/unoptimized guards required')
    {'setup':setup, 'check':check}[sys.argv[1]]()
