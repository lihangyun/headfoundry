"""Fixed batch-only upsample equivalence/capacity;no human input/head output."""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request

from check_batch_admission_0294 import ROOT,DEST,LOCK,digest,blocked

OUT = ROOT/'assets/private/batch-upsample-0294'
REPORT = {'status':'REJECT','physical_quality':'UNVERIFIED'}
DONE = threading.Event()
DEADLINE = time.monotonic()+60
os.environ.setdefault('USERNAME',Path(os.environ['USERPROFILE']).name)
os.environ['TORCHINDUCTOR_CACHE_DIR'] = str(DEST/'inductor-cache')
import torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0,str(DEST/'source'))
from nets import alltracker as model_module
from nets.blocks import bilinear_sampler


class SampledCorrelation:
    """Distribute the linear dot over bilinear sampling;keep every query pixel."""
    def __init__(self,fmap1,fmap2,corr_levels,corr_radius):
        self.b,self.c,self.h,self.w = fmap1.shape
        self.reference = fmap1.flatten(2)
        self.targets = []
        self.radius = corr_radius
        for _ in range(corr_levels):
            self.targets.append(fmap2)
            fmap2 = F.interpolate(fmap2,scale_factor=.5,mode='area')

    def __call__(self,coords,dilation=None):
        xy = coords.permute(0,2,3,1).reshape(self.b,-1,2)
        if dilation is None:
            dilation = torch.ones(self.b,1,self.h,self.w,device=coords.device)
        dilation = dilation.reshape(self.b,-1,1,1)
        axis = torch.linspace(-self.radius,self.radius,2*self.radius+1,device=coords.device)
        delta = torch.stack(torch.meshgrid(axis,axis,indexing='ij'),dim=-1).reshape(1,1,-1,2)
        n,k = self.h*self.w,delta.shape[2]
        out = torch.empty(self.b,len(self.targets)*k,n,device=coords.device,dtype=torch.float32)
        # ponytail: fixed512query chunks bound temporary memory;no pixels are dropped.
        for level,target in enumerate(self.targets):
            for start in range(0,n,512):
                stop = min(start+512,n)
                grid = xy[:,start:stop,None,:]/(2**level)+delta*dilation[:,start:stop]
                sampled = bilinear_sampler(target,grid)
                score = (sampled*self.reference[:,:,start:stop,None]).sum(dim=1)/math.sqrt(self.c)
                out[:,level*k:(level+1)*k,start:stop] = score.transpose(1,2)
        return out.reshape(self.b,-1,self.h,self.w)


def save():
    (OUT/'report.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')


def phase(name,seconds):
    global DEADLINE
    REPORT['phase'] = name
    DEADLINE = time.monotonic()+seconds
    save()
    print(json.dumps({'phase':name}),flush=True)


def watchdog():
    while not DONE.wait(.25):
        if time.monotonic()>DEADLINE:
            REPORT['failure'] = 'phase deadline exceeded'
            save()
            os._exit(124)


ORIGINAL_UPSAMPLE = model_module.Net.upsample_data


def batch_upsample(self,flow,mask):
    if torch.is_grad_enabled():
        raise RuntimeError('batch upsampling is inference-only;training not authorized')
    n,channels,h,w = flow.shape
    if channels!=2 or mask.shape!=(n,576,h,w) or n<1:
        raise ValueError('invalid upsample tensor shape')
    output = flow.new_empty((n,2,8*h,8*w))
    # ponytail: fixed batch1 changes allocation,not any temporal model computation.
    for start in range(n):
        output[start:start+1].copy_(ORIGINAL_UPSAMPLE(self,flow[start:start+1],mask[start:start+1]))
    return output


def operator_controls():
    from convex_upsampling import scalar_oracle
    rng = np.random.default_rng(293)
    values = np.arange(24,dtype=np.float32).reshape(2,2,2,3)/32-.25
    logits = rng.uniform(-2,2,(2,576,2,3)).astype(np.float32)
    expected = scalar_oracle(values,logits)
    a,b = torch.from_numpy(values).cuda(),torch.from_numpy(logits).cuda()
    actual = batch_upsample(None,a,b).cpu().numpy()
    oracle_delta = float(np.abs(actual-expected).max())
    if oracle_delta>1e-5:
        raise ValueError('independent CUDA subpixel oracle failed')
    del a,b,actual
    generator = torch.Generator(device='cuda').manual_seed(293)
    a = torch.rand((16,2,160,96),device='cuda',generator=generator)*4-2
    b = torch.rand((16,576,160,96),device='cuda',generator=generator)*8-4
    peaks = {}
    for name,function in (('original',ORIGINAL_UPSAMPLE),('batch1',batch_upsample)):
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        output = function(None,a,b)
        torch.cuda.synchronize()
        peaks[name] = {'seconds':time.monotonic()-started,'peak_reserved':torch.cuda.max_memory_reserved(),
                       'peak_allocated':torch.cuda.max_memory_allocated()}
        if not torch.isfinite(output).all():
            raise ValueError('nonfinite CUDA operator output')
        if name=='original':
            reference = output.cpu()
        else:
            difference = output.cpu()-reference
        del output
    delta = torch.linalg.vector_norm(difference,dim=1)
    if float(delta.max())>.001:
        raise ValueError('native CUDA operator differs beyond.001px')
    return {'oracle_values':expected.size,'oracle_max_delta_px':oracle_delta,
            'native_values':reference.numel(),'native_vector_pixels':delta.numel(),
            'native_max_vector_delta_px':float(delta.max()),'resources':peaks}


def frames(h,w,length=16):
    generator = torch.Generator(device='cuda').manual_seed(293)
    base = torch.rand((1,3,h,w),device='cuda',generator=generator)*255
    return torch.stack([torch.roll(base,(t//2,t),(2,3)) for t in range(length)],dim=1)


def forward(model,images,kind):
    model_module.CorrBlock = SampledCorrelation
    model_module.Net.upsample_data = ORIGINAL_UPSAMPLE if kind=='original' else batch_upsample
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    with torch.inference_mode():
        flow,confidence,_,_ = model.forward_sliding(images,iters=4,is_training=False)
    torch.cuda.synchronize()
    for tensor in (flow,confidence):
        if tensor.shape!=(1,images.shape[1],2,*images.shape[-2:]) or not torch.isfinite(tensor).all():
            raise ValueError('invalid full-network output shape/finite values')
    return flow,confidence,{'seconds':time.monotonic()-started,'peak_reserved':torch.cuda.max_memory_reserved(),
                            'values_per_output':flow.numel(),'shape':list(flow.shape)}


def peak_working_set():
    class Counters(ctypes.Structure):
        _fields_ = [('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in
            ('peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
    data = Counters()
    data.cb = ctypes.sizeof(data)
    kernel,psapi = ctypes.WinDLL('kernel32'),ctypes.WinDLL('psapi')
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_ulong]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(data),data.cb):
        raise RuntimeError('worker memory counter unavailable')
    return data.peak


def main():
    OUT.mkdir(exist_ok=False)
    start = time.monotonic()
    threading.Thread(target=watchdog,daemon=True).start()
    try:
        if json.loads((DEST/'admission.json').read_text())['status']!='TECHNICAL_CHECK_PASSED':
            raise ValueError('strict runtime/state not admitted')
        for name,expected in LOCK['source_files'].items():
            if digest(DEST/'source'/name)!=expected:
                raise ValueError('source changed')
        if digest(DEST/'alltracker.pth')!=LOCK['checkpoint']['sha256']:
            raise ValueError('checkpoint changed')
        socket.socket.connect = blocked
        urllib.request.urlopen = blocked
        torch.hub.load_state_dict_from_url = blocked
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.cuda.set_per_process_memory_fraction(7*2**30/torch.cuda.get_device_properties(0).total_memory)
        admission = json.loads((DEST/'admission.json').read_text())['state']
        if admission['keys']!=236 or admission['parameters']!=16476962 or admission['parameter_tensors']!=235:
            raise ValueError('unexpected full architecture count')
        phase('operator',120)
        with torch.inference_mode():
            REPORT['operator'] = operator_controls()
        save()
        model = model_module.Net(seqlen=16,init_weights=False)
        model.load_state_dict(torch.load(DEST/'alltracker.pth',map_location='cpu',weights_only=True)['model'],strict=True)
        model = model.eval().cuda()
        phase('paired-network',180)
        images = frames(256,384)
        first,first_conf,base_info = forward(model,images,'original')
        second,second_conf,new_info = forward(model,images,'batch1')
        delta = torch.linalg.vector_norm(second-first,dim=2)
        REPORT['equivalence'] = {'all_flow_pixels':delta.numel(),'max_vector_delta_px':float(delta.max()),
                                 'confidence_max_delta':float((second_conf-first_conf).abs().max()),
                                 'visibility_decision_flips':int(((first_conf.prod(dim=2)>=.6)!=(second_conf.prod(dim=2)>=.6)).sum()),
                                 'original_upsample':base_info,'batch1_upsample':new_info}
        np.savez_compressed(OUT/'equivalence-deltas.npz',flow_vector_delta=delta.numpy(),confidence_delta=(second_conf-first_conf).numpy())
        save()
        if float(delta.max())>.001 or float((second_conf-first_conf).abs().max())>1e-5 or REPORT['equivalence']['visibility_decision_flips']!=0:
            raise ValueError('complete-network pixel equivalence exceeds.001px')
        del images,first,second,first_conf,second_conf,delta
        phase('native-capacity',180)
        torch.cuda.empty_cache()
        native_images = frames(1280,720,length=11)
        flow,confidence,info = forward(model,native_images,'batch1')
        info['peak_worker_working_set'] = peak_working_set()
        info['flow_sha256'] = hashlib.sha256(flow.numpy().tobytes()).hexdigest()
        REPORT['native'] = info
        if info['seconds']>180 or info['peak_reserved']>7*2**30 or info['peak_worker_working_set']>8*2**30:
            raise ValueError('native resource budget failed')
        REPORT['status'] = 'TECHNICAL_CHECK_PASSED'
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
    finally:
        DONE.set()
        REPORT['seconds'] = time.monotonic()-start
        save()
        print(json.dumps(REPORT),flush=True)


if __name__=='__main__':
    main()
