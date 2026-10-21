"""Strict released-state and CUDA admission only;never calls a model forward."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/private/batch-runtime-0294'
LOCK = json.loads((ROOT/'examples/alltracker-batch-0294-lock.json').read_text())
REPORT = {'status':'REJECT','model_forward_executed':False,'physical_quality':'UNVERIFIED'}
DONE = threading.Event()
DEADLINE = time.monotonic()+60


def save():
    (DEST/'admission.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')


def watchdog():
    while not DONE.wait(.25):
        if time.monotonic()>DEADLINE:
            REPORT['failure'] = 'admission phase60s cap'
            save()
            os._exit(124)


def blocked(*args,**kwargs):
    raise RuntimeError('network/default downloads forbidden after asset verification')


def digest(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file,'sha256').hexdigest()


def main():
    global DEADLINE
    started = time.monotonic()
    save()
    threading.Thread(target=watchdog,daemon=True).start()
    try:
        if json.loads((DEST/'provision.json').read_text())['status']!='TECHNICAL_CHECK_PASSED':
            raise ValueError('no complete verified installation')
        REPORT['versions'] = {w['name']:importlib.metadata.version(w['name']) for w in LOCK['wheels']}
        if any(REPORT['versions'][w['name']]!=w['version'] for w in LOCK['wheels']):
            raise ValueError('runtime version differs from locked wheel')
        for name,expected in LOCK['source_files'].items():
            if digest(DEST/'source'/name)!=expected:
                raise ValueError('source fingerprint mismatch')
        if digest(DEST/'alltracker.pth')!=LOCK['checkpoint']['sha256'] or digest(DEST/'weight-license.md')!=LOCK['weight_license']['sha256']:
            raise ValueError('checkpoint/rights mismatch')
        if not any(os.environ.get(name) for name in ('LOGNAME','USER','LNAME','USERNAME')):
            profile = os.environ.get('USERPROFILE')
            if not profile:
                raise ValueError('missing local process user identity')
            os.environ['USERNAME'] = Path(profile).name
            REPORT['restored_process_username_for_cache'] = True
        os.environ['TORCHINDUCTOR_CACHE_DIR'] = str(DEST/'inductor-cache')
        import torch
        import torchvision
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable;no CPU/other runtime fallback')
        props = torch.cuda.get_device_properties(0)
        free,total = torch.cuda.mem_get_info(0)
        a = torch.arange(256,dtype=torch.float32,device='cuda').reshape(16,16)
        result = a@torch.eye(16,dtype=torch.float32,device='cuda')
        torch.cuda.synchronize()
        if not torch.equal(result,a) or not torch.isfinite(result).all():
            raise ValueError('actual CUDA identity matmul failed')
        REPORT['cuda'] = {'name':props.name,'total_memory':props.total_memory,'free':free,
                          'total':total,'capability':[props.major,props.minor],
                          'torch_cuda':torch.version.cuda,'peak_reserved':torch.cuda.max_memory_reserved(),
                          'identity_matmul_exact':True,'seconds':time.monotonic()-started}
        save()
        DEADLINE = time.monotonic()+60
        socket.socket.connect = blocked
        urllib.request.urlopen = blocked
        torch.hub.load_state_dict_from_url = blocked
        sys.path.insert(0,str(DEST/'source'))
        from nets.alltracker import Net
        state = torch.load(DEST/'alltracker.pth',map_location='cpu',weights_only=True)['model']
        model = Net(seqlen=16,init_weights=False)
        expected = model.state_dict()
        if state.keys()!=expected.keys():
            raise ValueError('state keys do not exactly match full model')
        for name,value in state.items():
            if not isinstance(value,torch.Tensor) or value.shape!=expected[name].shape or value.dtype!=expected[name].dtype:
                raise ValueError('state shape/dtype mismatch:'+name)
            if value.is_floating_point() and (value.dtype!=torch.float32 or not torch.isfinite(value).all()):
                raise ValueError('nonfinite/nonFP32 state:'+name)
        loaded = model.load_state_dict(state,strict=True)
        if loaded.missing_keys or loaded.unexpected_keys:
            raise ValueError('strict state not complete')
        REPORT['state'] = {'keys':len(state),'parameters':sum(p.numel() for p in model.parameters()),
                           'parameter_tensors':sum(1 for _ in model.parameters()),
                           'all_finite':True,'all_floating_FP32':True,'strict':True,
                           'external_pretrained_downloads':0,
                           'seconds':time.monotonic()-(DEADLINE-60)}
        REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        DONE.set()
        REPORT['seconds'] = time.monotonic()-started
        save()
        print(json.dumps(REPORT),flush=True)


if __name__=='__main__':
    main()
