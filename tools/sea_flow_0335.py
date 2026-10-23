"""Bounded software-only pairwise-flow admission;no clinical input or quality claim."""
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

from bounded_process import run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/sea-raft-software-0335'
PREFLIGHT=ROOT/'assets/private/sea-raft-preflight-0334'
PYTHON=OUT/'env/Scripts/python.exe'
EXPECTED='cb8cfbf14c5e0f6734b64add383708b7ff68cc6089a0007c67165d4761346102'

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def write(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False))

def acquire():
    model=OUT/'model.safetensors'
    if model.exists() or PYTHON.exists():raise ValueError('fresh acquisition only')
    url='https://huggingface.co/MemorySlices/Tartan-C-T-TSKH-spring540x960-M/resolve/eb97ef34ba5d856c3fa2cdcd073150c057ac8b69/model.safetensors'
    started=time.monotonic();partial=OUT/'model.partial'
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-fixed-public-asset'}),timeout=30) as response,partial.open('xb') as stream:
        while block:=response.read(1024*1024):
            if time.monotonic()-started>180:raise TimeoutError('fixed model transport budget')
            stream.write(block)
            if stream.tell()>78778760:raise ValueError('model length exceeds publisher identity')
    if partial.stat().st_size!=78778760 or sha(partial)!=EXPECTED:raise ValueError('model byte identity fails')
    partial.rename(model)
    write('asset.json',{'url':url,'bytes':model.stat().st_size,'sha256':sha(model),'license':'publisher bsd-3-clause',
          'source_commit':'9137517ba24e628442aec097d3afe71d03503b75','acquired_utc':time.time()})
    uv=Path('C:/Users/lihan/.local/bin/uv.exe');env=os.environ.copy()
    env.update(UV_NO_CACHE='1',UV_CACHE_DIR=str(OUT/'cache/uv'),UV_PYTHON_DOWNLOADS='never')
    commands=[
        [str(uv),'venv',str(OUT/'env'),'--python',str(ROOT/'.venv/Scripts/python.exe')],
        [str(uv),'pip','install','--python',str(PYTHON),'--no-cache','--index-url','https://download.pytorch.org/whl/cpu','torch==2.10.0+cpu'],
        [str(uv),'pip','install','--python',str(PYTHON),'--no-cache','--no-deps','safetensors==0.7.0']]
    for command in commands:
        print(json.dumps(command),flush=True)
        subprocess.run(command,cwd=ROOT,env=env,check=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=max(1,540-(time.monotonic()-started)))

def metadata():
    rows=[]
    for dist in sorted(importlib.metadata.distributions(),key=lambda d:d.metadata['Name'].lower()):
        notices=[]
        for entry in dist.files or []:
            path=Path(dist.locate_file(entry)).resolve()
            if any(word in path.name.lower() for word in ('license','copying','notice')) and path.is_file():
                if not path.is_relative_to((OUT/'env').resolve()):raise ValueError('runtime notice outside own environment')
                notices.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
        rows.append({'name':dist.metadata['Name'],'version':dist.version,'license':dist.metadata.get('License'),
            'license_expression':dist.metadata.get('License-Expression'),'classifiers':dist.metadata.get_all('Classifier',[]),
            'notices':notices})
    write('runtime-metadata.json',rows)
    print(json.dumps([{'name':r['name'],'version':r['version'],'license':r['license'],'license_expression':r['license_expression'],
                      'notices':len(r['notices'])} for r in rows],indent=2))

def static_source_check():
    receipt=json.loads((PREFLIGHT/'receipt.json').read_text())
    for row in receipt:
        if sha(PREFLIGHT/row['path'])!=row['sha256']:raise ValueError('reviewed public source changed')
    paths=['raft.py','extractor.py','layer.py','update.py','corr.py','utils/utils.py'];records=[]
    for name in paths:
        old=ast.parse((PREFLIGHT/'source/core'/name).read_text());new=ast.parse((OUT/'source/core'/name).read_text())
        if name!='raft.py':
            if ast.dump(old,include_attributes=False)!=ast.dump(new,include_attributes=False):raise ValueError('unmodified numeric module changed')
        else:
            before=next(n for n in old.body if isinstance(n,ast.ClassDef));after=next(n for n in new.body if isinstance(n,ast.ClassDef))
            expected=ast.parse(ast.unparse(before))
            for node in ast.walk(expected):
                if isinstance(node,ast.keyword) and node.arg=='init_weight':node.value=ast.Constant(False)
            methods=lambda cls:{n.name:ast.dump(n,include_attributes=False) for n in cls.body if isinstance(n,ast.FunctionDef)}
            if methods(expected.body[0])!=methods(after):raise ValueError('numeric constructor/forward body changed')
            if len(after.bases)!=1 or ast.unparse(after.bases[0])!='nn.Module' or after.keywords:raise ValueError('unexpected wrapper change')
        records.append({'path':name,'original_sha256':sha(PREFLIGHT/'source/core'/name),'active_sha256':sha(OUT/'source/core'/name)})
    write('source-contract.json',{'status':'TECHNICAL_CHECK_PASSED','files':records,'scope':'only external initializer and unused hub wrapper disabled'})

def model_state():
    sys.dont_write_bytecode=True
    sys.path.append(str(ROOT/'.venv/Lib/site-packages'))
    import torch
    import numpy as np
    import scipy
    from PIL import Image
    from safetensors import safe_open
    from safetensors.torch import load_file
    if torch.__version__!='2.10.0+cpu' or not Path(torch.__file__).resolve().is_relative_to(OUT/'env'):
        raise ValueError('wrong isolated Torch runtime')
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(335)
    static_source_check()
    if sha(OUT/'model.safetensors')!=EXPECTED:raise ValueError('checkpoint changed before loading')
    private=ROOT/'assets/private';allowed_images={ROOT/f'assets/private/dense-photo-0332/view-{c}.png' for c in (0,1)}
    def audit(event,args):
        if event.startswith(('socket.','subprocess.','os.system')):raise PermissionError('offline model worker')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1];reading=not isinstance(mode,str) or 'r' in mode or '+' in mode
            if reading and (path.suffix.lower()=='.stl' or (private in path.parents and not(path.is_relative_to(OUT) or path.is_relative_to(PREFLIGHT) or path in allowed_images))):
                raise PermissionError('unrelated private/truth/clinical read denied')
    sys.addaudithook(audit)
    sys.path.insert(0,str(OUT/'source/core'))
    from raft import RAFT
    from types import SimpleNamespace
    config=json.loads((PREFLIGHT/'source/config/eval/spring-M.json').read_text());model=RAFT(SimpleNamespace(**config)).cpu().eval()
    state=load_file(str(OUT/'model.safetensors'),device='cpu');expected=model.state_dict()
    with safe_open(str(OUT/'model.safetensors'),framework='pt',device='cpu') as f:aliases=f.metadata() or {}
    def group(t):return (t.untyped_storage().data_ptr(),t.storage_offset(),tuple(t.shape),tuple(t.stride()),t.dtype)
    expanded=dict(state);used={}
    for name in set(expected)-set(expanded):
        target=aliases.get(name)
        if target not in state or target not in expected or group(expected[name])!=group(expected[target]):
            raise ValueError('missing state without exact declared model alias:'+name)
        expanded[name]=state[target];used[name]=target
    def validate(candidate):
        if set(candidate)!=set(expected):raise ValueError('full state key mismatch')
        for name,tensor in candidate.items():
            if tensor.shape!=expected[name].shape or tensor.dtype!=expected[name].dtype or not torch.isfinite(tensor).all():
                raise ValueError('full state shape/dtype/finite mismatch:'+name)
    validate(expanded)
    damaged=dict(expanded);damaged.pop(next(iter(damaged)))
    try:validate(damaged)
    except ValueError:pass
    else:raise AssertionError('missing state sentinel accepted')
    result=model.load_state_dict(expanded,strict=True)
    if result.missing_keys or result.unexpected_keys:raise ValueError('strict state load fails')
    for name,tensor in model.state_dict().items():
        if not torch.equal(tensor,expanded[name]):raise ValueError('postload full tensor mismatch')
    write('state.json',{'status':'TECHNICAL_CHECK_PASSED','physical_state_tensors':len(state),'logical_state_keys':len(expected),
        'declared_exact_aliases':used,'state_elements':sum(t.numel() for t in state.values()),'missing_sentinel_rejected':True,
        'torch':torch.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'model_sha256':sha(OUT/'model.safetensors'),
        'scope':'full state only;no physical matching claim'})
    return model,torch,np,Image

def controls():
    model,torch,np,_=model_state()
    from utils.utils import InputPadder,bilinear_sampler,coords_grid
    xy=coords_grid(1,9,17,device='cpu');q=torch.tensor([[[[1.25,2.5],[8.5,4.25]]]])
    actual=bilinear_sampler(xy,q)
    target=q.permute(0,3,1,2)
    if not torch.equal(actual,target):raise ValueError('exact dyadic native xy control fails')
    for h,w in ((1280,720),(129,163)):
        image=torch.arange(h*w,dtype=torch.float32).reshape(1,1,h,w);padder=InputPadder(image.shape)
        if not torch.equal(padder.unpad(padder.pad(image)[0]),image):raise ValueError('pad/unpad replay fails')
    write('controls.json',{'status':'TECHNICAL_CHECK_PASSED','exact_dyadic_xy':True,'pad_unpad':[[1280,720],[129,163]],
        'scope':'software contracts only;no learned accuracy'})

def forward(stage):
    model,torch,np,Image=model_state()
    if stage=='small':
        rng=np.random.default_rng(335);a=rng.integers(0,256,(128,160,3),dtype=np.uint8);b=np.roll(a,3,axis=1)
    else:
        inputs=json.loads((PREFLIGHT/'summary.json').read_text())
        fixed=json.loads((OUT/'fixed-owned-images.json').read_text())
        images=[]
        for name,identity in fixed.items():
            path=ROOT/'assets/private/dense-photo-0332'/name
            if sha(path)!=identity:raise ValueError('fixed owned input changed')
            images.append(np.asarray(Image.open(path).convert('RGB')))
        a,b=images
    tensors=[torch.from_numpy(image.copy()).permute(2,0,1)[None].float() for image in (a,b)]
    started=time.monotonic()
    with torch.no_grad():output=model(*tensors,iters=4,test_mode=True)
    seconds=time.monotonic()-started;records=[]
    if len(output['flow'])!=5 or len(output['info'])!=5 or output['nf'] is not None:raise ValueError('full stage output count fails')
    for key,channels in (('flow',2),('info',4)):
        for index,tensor in enumerate(output[key]):
            if tuple(tensor.shape)!=(1,channels,*a.shape[:2]) or tensor.dtype!=torch.float32 or not torch.isfinite(tensor).all():
                raise ValueError('native finite FP32 output contract fails')
            records.append({'key':key,'index':index,'shape':list(tensor.shape),'sha256':hashlib.sha256(tensor.contiguous().numpy().tobytes()).hexdigest()})
    if not torch.equal(output['final'],output['flow'][-1]):raise ValueError('final-stage identity fails')
    write(stage+'.json',{'status':'TECHNICAL_CHECK_PASSED','forward_seconds':seconds,'outputs':records,
          'scope':'software/finite/native capacity only;no learned physical accuracy'})
    np.savez_compressed(OUT/(stage+'-output.npz'),flow=output['final'].numpy(),info=output['info'][-1].numpy())

def controller(stage):
    if stage=='acquire':
        if (OUT/'entry.json').exists():raise ValueError('no repeated acquisition')
        write('entry.json',{'source_sha256':sha(Path(__file__)),'started_utc':time.time()})
        owned=json.loads((ROOT/'assets/private/dense-photo-0332/inputs.json').read_text())['images']
        write('fixed-owned-images.json',{name:owned[name] for name in ('view-0.png','view-1.png')})
    if stage in ('controls','small','native') and not (OUT/'rights-reviewed.json').exists():raise ValueError('runtime rights review required')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',
        PYTHONDONTWRITEBYTECODE='1',TORCH_HOME=str(OUT/'cache/torch'),XDG_CACHE_HOME=str(OUT/'cache'),HF_HUB_OFFLINE='1')
    executable=sys.executable if stage=='acquire' else str(PYTHON)
    limits={'acquire':600,'metadata':60,'controls':120,'small':60,'native':180}
    record=run([executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),limits[stage],4*1024**3)
    print(json.dumps(record,indent=2));return record['status']=='TECHNICAL_CHECK_PASSED'

if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        name=stage[:-7]
        if name in ('small','native'):forward(name)
        else:{'acquire':acquire,'metadata':metadata,'controls':controls}[name]()
    else:sys.exit(0 if controller(stage) else 1)
