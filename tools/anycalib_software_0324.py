"""Fixed isolated software trial;not physical camera/head admission."""
import hashlib
from html.parser import HTMLParser
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time
import traceback
import urllib.parse
import urllib.request

import numpy as np

from bounded_process import run

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/private/anycalib-source-0322'
ASSET=ROOT/'assets/private/anycalib-asset-0323/anycalib_edit.pt'
OUT=ROOT/'assets/private/anycalib-software-0324'
RUNTIME=ROOT/'assets/private/anycalib-runtime-0324'


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf8')


def setup():
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):
            if tag=='a':self.links.extend(value for key,value in attrs if key=='href')
    wheels=[]
    for package,filename in [('torch','torch-2.6.0+cpu-cp312-cp312-win_amd64.whl'),('sympy','sympy-1.13.1-py3-none-any.whl')]:
        url='https://download.pytorch.org/whl/cpu/'+package+'/'
        index_path=OUT/(package+'-index.html')
        if index_path.exists():content=index_path.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=30) as response:content=response.read(2*1024**2+1)
        if len(content)>2*1024**2:raise ValueError('wheel index budget')
        if not index_path.exists():index_path.write_bytes(content)
        parser=Links();parser.feed(content.decode());matches=[]
        for link in parser.links:
            parsed=urllib.parse.urlsplit(urllib.parse.urljoin(url,link))
            if urllib.parse.unquote(parsed.path.rsplit('/',1)[-1])==filename:matches.append(parsed)
        if len(matches)!=1:raise ValueError('fixed wheel not unique:'+filename)
        parsed=matches[0];expected=urllib.parse.parse_qs(parsed.fragment).get('sha256',[''])[0]
        if len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected):raise ValueError('wheel SHA missing')
        allowed_hosts=['download.pytorch.org','download-r2.pytorch.org']
        if package=='sympy' and parsed.hostname=='files.pythonhosted.org':
            with urllib.request.urlopen('https://pypi.org/pypi/sympy/1.13.1/json',timeout=20) as response:
                package_metadata=response.read(256*1024+1)
            if len(package_metadata)>256*1024:raise ValueError('PyPI metadata budget')
            records=[row for row in json.loads(package_metadata)['urls'] if row['filename']==filename]
            if len(records)!=1 or records[0]['digests']['sha256']!=expected or records[0]['url']!=urllib.parse.urlunsplit(parsed._replace(fragment='')):
                raise ValueError('PyTorch-index/PyPI fixed wheel identity conflicts')
            (OUT/'sympy-pypi.json').write_bytes(package_metadata)
            allowed_hosts.append('files.pythonhosted.org')
        if parsed.scheme!='https' or parsed.hostname not in allowed_hosts:
            raise ValueError('nonofficial wheel URL')
        url=urllib.parse.urlunsplit(parsed._replace(fragment=''))
        path=RUNTIME/'wheels'/filename;path.parent.mkdir(exist_ok=True)
        digest=hashlib.sha256();count=0
        reused=path.exists()
        if reused:
            count=path.stat().st_size
            if sha(path)!=expected:raise ValueError('existing wheel SHA differs')
        else:
            with urllib.request.urlopen(url,timeout=30) as response,path.open('xb') as stream:
                while True:
                    block=response.read(1024**2)
                    if not block:break
                    count+=len(block)
                    if count+sum(row['bytes'] for row in wheels)>320*1024**2:raise ValueError('wheel byte budget')
                    stream.write(block);digest.update(block)
            if digest.hexdigest()!=expected:raise ValueError('wheel checksum mismatch')
        wheels.append({'path':str(path),'url':url,'bytes':count,'sha256':expected,'reused_verified_bytes':reused})
    save('wheels.json',wheels)
    import subprocess
    command=['C:/Users/lihan/.local/bin/uv.exe','pip','install','--no-index','--no-deps','--no-cache',
             '--python',sys.executable,'--target',str(RUNTIME/'site'),*[row['path'] for row in wheels]]
    subprocess.run(command,cwd=ROOT,check=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    distributions=list(importlib.metadata.distributions(path=[str(RUNTIME/'site')]))
    installed=[{'name':dist.metadata['Name'],'version':dist.version,'license':dist.metadata.get('License'),
                'requirements':dist.requires,'files':len(list(dist.files or []))}
               for dist in distributions]
    notices=[]
    for dist in distributions:
        for item in dist.files or []:
            if any(token in str(item).lower() for token in ['license','notice']) or str(item).endswith('.dist-info/RECORD'):
                path=Path(dist.locate_file(item))
                if path.is_file():notices.append({'path':str(path.relative_to(RUNTIME)),'bytes':path.stat().st_size,'sha256':sha(path)})
    size=sum(path.stat().st_size for path in RUNTIME.rglob('*') if path.is_file())
    if size>2*1024**3:raise ValueError('runtime disk budget')
    save('installed.json',{'packages':installed,'bytes':size,'preserved_notice_and_RECORD_files':notices})


def software():
    reads=[]
    allowed=[SOURCE,RUNTIME,OUT,ASSET.parent]
    def audit(event,args):
        if event in ['socket.connect','socket.getaddrinfo','subprocess.Popen','os.system']:
            raise PermissionError('offline software worker:'+event)
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            reading=not isinstance(mode,str) or not any(flag in mode for flag in ('w','a','x'))
            if reading and (ROOT/'assets/private') in path.parents:
                if not any(path.is_relative_to(parent) for parent in allowed):raise PermissionError('unrelated private read denied')
                reads.append(str(path.relative_to(ROOT)).replace('\\','/'))
    sys.addaudithook(audit)
    sys.path[:0]=[str(RUNTIME/'site'),str(SOURCE/'snapshot')]
    import torch
    import sympy
    from anycalib import AnyCalib
    from anycalib.cameras.pinhole import Pinhole
    from anycalib_adapter import validate_state,fingerprint,native_intrinsics
    if torch.__version__!='2.6.0+cpu' or sympy.__version__!='1.13.1':raise ValueError('runtime version mismatch')
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(324)
    torch.use_deterministic_algorithms(True)
    model=AnyCalib(model_id=None,fallback_to_sac=False).cpu().eval()
    expected=model.state_dict()
    state=torch.load(ASSET,map_location='cpu',weights_only=True,mmap=True)
    validate_state(state,expected)
    selected=min(state,key=lambda name:state[name].numel())
    bad=[]
    missing=dict(state);missing.pop(selected);bad.append(('missing',missing))
    bad.append(('extra',{**state,'unrecognized':torch.zeros(1)}))
    bad.append(('shape',{**state,selected:state[selected].reshape(-1) if state[selected].ndim>1 else state[selected].reshape(-1,1)}))
    bad.append(('dtype',{**state,selected:state[selected].double()}))
    for name,value in [('nan',float('nan')),('inf',float('inf'))]:
        tensor=state[selected].clone();tensor.reshape(-1)[0]=value;bad.append((name,{**state,selected:tensor}))
    rejected=[]
    for name,invalid in bad:
        try:validate_state(invalid,expected)
        except ValueError:rejected.append(name)
        else:raise ValueError('invalid state accepted:'+name)
    checkpoint_fingerprint=fingerprint(state)
    model.load_state_dict(state,strict=True)
    loaded=fingerprint(model.state_dict())
    if checkpoint_fingerprint!=loaded:raise ValueError('loaded value bytes differ')
    save('state.json',{'items':len(state),'parameters':sum(p.numel() for p in model.parameters()),
        'persistent_buffer_names':[name for name,_ in model.named_buffers()],
        'fingerprint':loaded,'negative_controls':rejected,
        'schema':[{ 'name':name,'shape':list(value.shape),'dtype':str(value.dtype)} for name,value in state.items()]})
    # Independent FP64 non-square/off-center pinhole arithmetic,not neural truth.
    camera=Pinhole();params=np.array([1200.,1250.,347.5,631.5])
    yy,xx=np.mgrid[0:1280:71,0:720:53];pixels=np.c_[xx.ravel()+.5,yy.ravel()+.5]
    rays=np.c_[(pixels-params[2:])/params[:2],np.ones(len(pixels))];rays/=np.linalg.norm(rays,axis=1)[:,None]
    fitted,info=camera.fit(torch.from_numpy(pixels),torch.from_numpy(rays))
    replay,valid=camera.project(fitted,torch.from_numpy(rays))
    if int(info)!=0 or not valid.all() or np.abs(replay.numpy()-pixels).max()>1e-7:raise ValueError('FP64 ray fit replay')
    import cv2
    xyz=np.array([[.1,.2,1.],[-.3,.1,1.7],[.2,-.15,1.3]])
    rotation=cv2.Rodrigues(np.array([.1,-.2,.03]))[0];translation=np.array([.02,.03,.2])
    kk=native_intrinsics(params);native,_=cv2.projectPoints(xyz,cv2.Rodrigues(rotation)[0],translation,kk,None)
    edge,_=camera.project(torch.from_numpy(params),torch.from_numpy(xyz@rotation.T+translation))
    cv_error=float(np.abs(edge.numpy()-.5-native[:,0]).max())
    if cv_error>1e-7:raise ValueError('OpenCV edge/native replay')
    target=model.compute_target_size(102400,1280/720)
    if target!=(420,238):raise ValueError('native target integer size')
    _,scale,shift=model.set_im_size(torch.zeros(1,3,1280,720),target)
    exact_scale=np.array([238/720,420/1271]);exact_shift=np.array([0,-4*420/1271])
    transformed=camera.scale_and_shift(torch.from_numpy(params),scale,shift)
    truth_transformed=np.r_[params[:2]*exact_scale,params[2:]*exact_scale+exact_shift]
    affine_error=float(np.abs(transformed.numpy()-truth_transformed).max())
    bound=float(16*np.finfo(np.float32).eps*max(1280,np.abs(params).max()))
    reversed_=camera.reverse_scale_and_shift(transformed,scale,shift)
    if affine_error>bound or np.abs(reversed_.numpy()-params).max()>1e-7:raise ValueError('integer crop/scale Ktransfer')
    save('coordinates.json',{'fp64_replay_px':float(np.abs(replay.numpy()-pixels).max()),'opencv_replay_px':cv_error,
        'target':list(target),'crop_top':4,'crop_total_h':9,'scale':scale.tolist(),'shift':shift.tolist(),
        'affine_error_px':affine_error,'fp32_roundoff_bound_px':bound,'output_information_basis':'working-grid intrinsics,not native calibrated covariance'})
    y,x=np.mgrid[0:1280,0:720];x=x/719;y=y/1279
    rgb=np.stack([.2+.5*x+.04*np.sin(23*y),.2+.5*y+.04*np.cos(19*x),
                  .4+.18*np.sin(11*x+7*y)],axis=0).astype(np.float32)
    image=torch.from_numpy(rgb)
    forward_start=time.monotonic()
    with torch.inference_mode():prediction=model.predict(image,cam_id='pinhole')
    elapsed=time.monotonic()-forward_start
    arrays={name:value.detach().cpu().numpy() for name,value in prediction.items() if isinstance(value,torch.Tensor)}
    arrays['pred_size']=np.array(prediction['pred_size'])
    np.savez_compressed(OUT/'raw-forward.npz',**arrays)
    if not bool(prediction['success']):raise ValueError('explicit calibration success false;no placeholder admission')
    if not all(np.isfinite(array).all() for array in arrays.values()):raise ValueError('nonfinite output')
    intrinsics=native_intrinsics(arrays['intrinsics'])
    n=int(np.prod(prediction['pred_size']))
    if arrays['rays'].shape!=(n,3) or arrays['tangent_coords'].shape!=(n,2) or arrays['intrinsics_icovs'].shape!=(4,4):
        raise ValueError('complete forward output shape')
    norm_error=float(np.abs(np.linalg.norm(arrays['rays'],axis=1)-1).max())
    if norm_error>1e-5:raise ValueError('invalid unit ray')
    after=fingerprint(model.state_dict())
    if after!=loaded:raise ValueError('state changed during software forward')
    modules={name:str(Path(module.__file__).resolve()) for name,module in list(sys.modules.items())
             if getattr(module,'__file__',None) and name.split('.')[0] in ['torch','sympy','anycalib']}
    save('imports.json',modules)
    save('read-audit.json',{'private_reads':sorted(set(reads)),'network_denied':True,'subprocess_denied':True,'native_sandbox':False})
    save('result.json',{'status':'TECHNICAL_CHECK_PASSED','scope':'strict software and unlabelled procedural forward only',
        'forward_seconds':elapsed,'output_edge_params':arrays['intrinsics'].tolist(),'native_K':intrinsics.tolist(),
        'norm_error':norm_error,'state_fingerprint_before_after':after,'physical_camera_head_medical':'UNVERIFIED'})


def controller(resume=False):
    if resume:
        if (json.loads((OUT/'failure.json').read_text())['error']!="ValueError('nonofficial wheel URL')"
                or (OUT/'software-worker.json').exists() or (RUNTIME/'site').exists()):
            raise ValueError('only the pre-install host-selection stop can resume')
        for name in ['setup-worker.json','setup.log','failure.json']:
            (OUT/name).rename(OUT/('first-'+name))
    else:
        OUT.mkdir(exist_ok=False);RUNTIME.mkdir(exist_ok=False)
        for parent in [OUT,RUNTIME]:(parent/'tmp').mkdir()
    before=json.loads((SOURCE/'verification.json').read_text())
    for row in before['protected']:
        if sha(Path(row['path']))!=row['sha256']:raise ValueError('protected input changed')
    public=json.loads((ROOT/'examples/anycalib-edit-asset-lock.json').read_text())
    if sha(ASSET)!=public['checkpoint']['sha256']:raise ValueError('asset changed')
    for row in json.loads((SOURCE/'result.json').read_text())['responses']+json.loads((SOURCE/'notices.json').read_text()):
        if sha(SOURCE/row['path'])!=row['sha256']:raise ValueError('source/grant/notice changed')
    save('repair-entry.json' if resume else 'entry.json',{'protected':before['protected'],'source_sha':public['revision'],'asset_sha':sha(ASSET),
        'epoch':time.time(),'main_packages_before':sorted((d.metadata['Name'],d.version) for d in importlib.metadata.distributions())})
    env=os.environ.copy();env.update({key:'4' for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']})
    env.update(PYTHONDONTWRITEBYTECODE='1',XFORMERS_DISABLED='1',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),
               TORCH_HOME=str(OUT/'torch-cache'),HF_HOME=str(OUT/'hf-cache'),UV_CACHE_DIR=str(RUNTIME/'uv-cache'))
    for stage,seconds,gib in [('setup',600,.75),('software',240,5)]:
        if resume and stage=='setup':seconds-=json.loads((OUT/'first-setup-worker.json').read_text())['seconds']
        record=run([sys.executable,str(Path(__file__).resolve()),stage],str(ROOT),env,
            OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,int(gib*1024**3))
        print(stage,json.dumps(record),flush=True)
        if record['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)


if __name__=='__main__':
    if len(sys.argv)==1:controller()
    elif sys.argv[1:]==['resume-setup']:controller(True)
    else:
        try:
            if sys.argv[1:] == ['setup']:setup()
            elif sys.argv[1:] == ['software']:software()
            else:raise ValueError('unknown stage')
        except Exception as error:
            save('failure.json',{'error':repr(error),'epoch':time.time(),'physical_camera_head_medical':'UNVERIFIED'})
            traceback.print_exc();sys.exit(1)
