"""Bounded offline software admission,never a physical calibration claim."""
import importlib.metadata as md
import json
import os
from pathlib import Path
import socket
import sys
import time

from headfoundry.manifest import sha256_file
from acquire_geocalib_0314 import SOURCE,OUT as WEIGHT,verify_locked_asset

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/geocalib-software-0315'
SITE=OUT/'site'
VERSIONS={'torch':'2.6.0+cpu','torchvision':'0.21.0+cpu','kornia':'0.8.0',
          'kornia-rs':'0.1.8','sympy':'1.13.1'}

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def locked_sources():
    lock=json.loads((ROOT/'examples/geocalib-pinhole.asset-lock.json').read_text())
    verify_locked_asset(lock,WEIGHT/'geocalib-pinhole.tar')
    for row in json.loads((SOURCE/'fetched.json').read_text()):
        assert sha256_file(SOURCE/row['path'])==row['sha256'],row['path']
    for key,name in [('code_notice_sha256','LICENSE'),('weight_notice_sha256','LICENSE-WEIGHTS')]:
        assert sha256_file(SOURCE/'snapshot'/name)==lock[key]

def strict_state(model,state):
    import torch
    expected=model.state_dict()
    if set(expected)!=set(state):raise ValueError('state keys differ')
    for key,ref in expected.items():
        val=state[key]
        if not isinstance(val,torch.Tensor) or val.shape!=ref.shape or val.dtype!=ref.dtype:
            raise ValueError('state shape/dtype differs:'+key)
        if not torch.isfinite(val).all():raise ValueError('nonfinite state:'+key)
    model.load_state_dict(state,strict=True)
    assert all(torch.equal(t,state[k]) for k,t in model.state_dict().items())

def offline():
    def deny(*args,**kwargs):raise RuntimeError('network disabled for offline model worker')
    socket.create_connection=deny
    socket.socket.connect=deny
    socket.socket.connect_ex=deny

def worker():
    start=time.monotonic()
    locked_sources()
    sys.path.insert(0,str(SITE))
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    distributions={canonicalize_name(d.metadata['Name']):d for d in md.distributions()}
    # Overlay wins even if the main environment contains another SymPy version.
    distributions.update({canonicalize_name(d.metadata['Name']):d for d in md.distributions(path=[str(SITE)])})
    deps=[]
    for name,version in VERSIONS.items():
        d=distributions[name]
        assert d.version==version,(name,d.version)
        notices=[]
        for file in d.files or []:
            if ('license' in str(file).lower() or 'copying' in str(file).lower()) and len(file.parts)<5:
                p=Path(d.locate_file(file))
                if p.is_file():notices.append(dict(path=str(p.relative_to(OUT)),sha256=sha256_file(p)))
        assert notices,('missing installed notices',name)
        for raw in d.requires or []:
            r=Requirement(raw)
            if r.marker is not None and not r.marker.evaluate({'extra':''}):continue
            got=distributions.get(canonicalize_name(r.name))
            assert got is not None and got.version in r.specifier,(name,raw,None if got is None else got.version)
        deps.append(dict(name=name,version=version,license=d.metadata.get('License'),notices=notices))
    write('dependencies.json',deps)
    offline()
    import torch
    import numpy as np
    torch.set_num_threads(4)
    torch.set_grad_enabled(False)
    torch.hub.load_state_dict_from_url=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('no weight download'))
    sys.path.insert(0,str(SOURCE/'snapshot'))
    from geocalib.geocalib import GeoCalib
    from geocalib.utils import ImagePreprocessor
    from geocalib.camera import Pinhole
    model=GeoCalib().eval()
    checkpoint=torch.load(WEIGHT/'geocalib-pinhole.tar',map_location='cpu',weights_only=True)
    state=checkpoint['model']
    parameters=dict(model.named_parameters());buffers=dict(model.named_buffers())
    inventory=[dict(name=k,shape=list(t.shape),dtype=str(t.dtype),numel=t.numel(),
                    kind='parameter' if k in parameters else 'buffer') for k,t in state.items()]
    write('state-inventory.json',inventory)
    pkey=next(k for k,t in state.items() if k in parameters and t.ndim>0)
    bkey=next(k for k in state if k in buffers)
    controls=[]
    for name in ['missing_parameter','missing_buffer','extra','shape','dtype','nan']:
        bad=dict(state)
        if name=='missing_parameter':del bad[pkey]
        elif name=='missing_buffer':del bad[bkey]
        elif name=='extra':bad['unexpected.extra']=torch.zeros(1)
        elif name=='shape':bad[pkey]=state[pkey].flatten()[:1]
        elif name=='dtype':bad[pkey]=state[pkey].double()
        else:bad[pkey]=state[pkey].clone();bad[pkey].flatten()[0]=float('nan')
        try:strict_state(model,bad)
        except ValueError:controls.append(name)
        else:raise AssertionError('bad state accepted:'+name)
    strict_state(model,state)
    write('strict-load.json',dict(status='TECHNICAL_CHECK_PASSED',items=len(state),
        parameters=sum(t.numel() for t in parameters.values()),buffers=len(buffers),
        all_state_equal=True,negative_controls=controls,torch_load_weights_only=True))
    del checkpoint,state
    h,w=259,343
    yy,xx=np.mgrid[:h,:w]
    rgb=np.stack([xx/(w-1),yy/(h-1),((xx//29+yy//23)%2)*.6+.2],-1).astype('float32')
    image=torch.from_numpy(rgb.transpose(2,0,1).copy())[None]
    processor=ImagePreprocessor({'resize':320,'edge_divisible_by':32})
    data=processor(image)
    scales=data['scales'].numpy().astype('float64')
    rh,rw=processor.get_new_image_size(h,w)
    ih,iw=data['image'].shape[-2:]
    left=(rw-iw+1)//2;top=(rh-ih+1)//2
    transform=np.array([[scales[0],0,.5*scales[0]-.5-left],
                        [0,scales[1],.5*scales[1]-.5-top],[0,0,1.]])
    k=np.array([[421.,0,171.],[0,421.,129.],[0,0,1.]])
    rays=np.array([[-.2,-.1,1],[.15,.3,1],[0,0,1.]]).T
    pixels=k@rays
    independent=pixels.copy()
    independent[0]=(pixels[0]+.5)*scales[0]-.5-left
    independent[1]=(pixels[1]+.5)*scales[1]-.5-top
    err=float(np.max(abs(transform@pixels-independent)))
    assert err<=1e-9
    model_k=Pinhole(torch.tensor([iw,ih,421.,421.,iw/2,ih/2])[None]).double()
    strict_native=np.linalg.inv(transform)@model_k.K.numpy()[0]
    legacy=model_k.undo_scale_crop(data).K.numpy()[0]
    write('coordinates.json',dict(native_wh=[w,h],resize_wh=[rw,rh],model_wh=[iw,ih],
        actual_crop_left_top=[left,top],pixel_transform=transform.tolist(),
        projection_replay_max_px=err,upstream_native_K=legacy.tolist(),
        pixel_resampling_native_K=strict_native.tolist(),difference=(strict_native-legacy).tolist(),
        physical_convention='UNVERIFIED;both recorded;not fitted to patient'))
    torch.manual_seed(315)
    write('forward-started.json',dict(seed=315,epoch=time.time(),count=1))
    begin=time.monotonic()
    pred=model(data)
    elapsed=time.monotonic()-begin
    tensors={name:t.detach().cpu().numpy() for name,t in pred.items() if isinstance(t,torch.Tensor)}
    tensors['camera_parameters']=pred['camera']._data.numpy()
    tensors['gravity_vector']=pred['gravity'].vec3d.numpy()
    for name,t in tensors.items():assert np.isfinite(t).all(),name
    assert (tensors['focal_uncertainty']>0).all()
    assert (pred['camera'].f>0).all()
    assert abs(torch.linalg.norm(pred['gravity'].vec3d).item()-1)<1e-5
    np.savez_compressed(OUT/'procedural-forward.npz',**tensors,input_rgb=rgb)
    write('result.json',dict(status='TECHNICAL_CHECK_PASSED',scope='offline software only',
        inference_seconds=elapsed,total_seconds=time.monotonic()-start,outputs={k:list(v.shape) for k,v in tensors.items()},
        focal_model_px=pred['camera'].f.tolist(),focal_uncertainty_model_px=tensors['focal_uncertainty'].tolist(),
        forward_count=1,nn_physical_camera_accuracy='UNVERIFIED',head_or_medical_accuracy='UNVERIFIED'))
    print((OUT/'result.json').read_text())

def main():
    from bounded_process import run
    OUT.mkdir(exist_ok=False)
    locked_sources()
    write('started.json',dict(epoch=time.time(),main_packages=[dict(name=d.metadata['Name'],version=d.version) for d in md.distributions()]))
    env=os.environ.copy();env.update(UV_CACHE_DIR=str(OUT/'cache'),PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1',TORCH_HOME=str(OUT/'torch-cache'))
    uv='C:/Users/lihan/.local/bin/uv.exe'
    base=[uv,'--no-cache','pip','install','--python',sys.executable,'--target',str(SITE),'--no-deps','--only-binary',':all:']
    for i,(packages,index) in enumerate([(['torch==2.6.0+cpu','torchvision==0.21.0+cpu'],'https://download.pytorch.org/whl/cpu'),
            (['kornia==0.8.0','kornia-rs==0.1.8','sympy==1.13.1'],'https://pypi.org/simple')]):
        r=run(base+packages+['--index-url',index],str(ROOT),env,OUT/f'install-{i}.log',OUT/f'install-{i}.json',360,4*1024**3)
        assert r['status']=='TECHNICAL_CHECK_PASSED',r
    result=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',300,3*1024**3)
    print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:worker()
    else:main()
