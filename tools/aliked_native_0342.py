"""Fixed offline full-state/native software check;not a reconstruction pipeline."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/aliked-runtime-0342'
EXTRACTOR=ROOT/'assets/private/aliked-assets-0340/aliked-n16.pth'
MATCHER=ROOT/'assets/private/aliked-matcher-0341/aliked_lightglue.pth'
ASSETS={EXTRACTOR:'5be8704840ed662d9d8c561bf7279c222092674e7eb05fd0feab94899e9d82f2',
    MATCHER:'d975e965b105311a6143194852297dff4f02aea5cc2e10cecfed966ca0e22503'}
IMAGES=('24a41defda99bdeab85917c8edd55ad5420b2f35a8c11a965338a2db46a07177',
    '4ea0b7fc2c4ffb6878b9fab0c4b420112fb4ed91126330e72cffc78c83ef6297')

def write(name,data):
    path=OUT/name
    if path.exists():raise FileExistsError('immutable receipt exists:'+name)
    path.write_text(json.dumps(data,indent=2))

def restrict_io():
    allowed=[OUT.resolve(),(ROOT/'assets/private/aliked-preflight-0339').resolve()]
    private=(ROOT/'assets/private').resolve()
    def audit(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise PermissionError('offline model network denied')
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(args[0])).resolve()
        if path.suffix.lower() in ('.stl','.mp4') or path.is_relative_to(Path('C:/workspace/peek')) or path.is_relative_to(Path('C:/Users/lihan/Downloads')):
            raise PermissionError('unrelated/patient input denied')
        mode=args[1];flags=args[2]
        reading=('r' in mode or '+' in mode) if isinstance(mode,str) else (flags&3)!=os.O_WRONLY
        if reading and path.is_relative_to(private) and path not in ASSETS and not any(path.is_relative_to(a) for a in allowed):
            raise PermissionError('unrelated private input denied:'+str(path))
    sys.addaudithook(audit)

def renamed(state):
    result={};mapping={}
    for key,value in state.items():
        found=re.fullmatch(r'(self_attn|cross_attn)\.(\d+)\.(.+)',key)
        new=key
        if found:
            kind,index,tail=found.groups()
            if not 0<=int(index)<9:raise ValueError('attention index outside fixed model')
            new=f'transformers.{index}.{kind}.{tail}'
        if new in result:raise ValueError('state rename collision')
        result[new]=value;mapping[key]=new
    return result,mapping

def validate(torch,expected,state):
    if set(expected)!=set(state):raise ValueError('incomplete or extra state keys')
    for key,target in expected.items():
        value=state[key]
        if not isinstance(value,torch.Tensor) or value.shape!=target.shape or value.dtype!=target.dtype or value.device.type!='cpu' or not torch.isfinite(value).all():
            raise ValueError('invalid state tensor:'+key)

def models(stage):
    import numpy as np
    import torch
    from acquire_aliked_matcher_0341 import inspect_zip
    from check_state_fingerprint import state_fingerprint
    sys.path.insert(0,str(OUT/'source'))
    import lg0342.aliked as ak
    import lg0342.lightglue as lg
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(342)
    if torch.__version__!='2.10.0+cpu' or torch.cuda.is_available():raise ValueError('fixed CPU runtime required')
    source=ROOT/'assets/private/aliked-preflight-0339'
    pinned={r['name']:r['sha256'] for r in json.loads((source/'result.json').read_text())['files']}
    for original,filename in (('lg-lightglue_aliked.py','aliked.py'),('lg-lightglue_lightglue.py','lightglue.py'),('lg-lightglue_utils.py','utils.py')):
        if hashlib.sha256((OUT/'source/lg0342'/filename).read_bytes()).hexdigest()!=pinned[original]:raise ValueError('numeric source changed')
    states={};inspections={}
    for path,expected in ASSETS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('checkpoint bytes changed')
        inspections[path.name]=inspect_zip(path)
        states[path]=torch.load(path,map_location='cpu',weights_only=True)
    calls=[]
    def local_hub(url,*args,**kwargs):
        if url!='https://github.com/Shiaoming/ALIKED/raw/main/models/aliked-n16.pth':raise ValueError('unexpected pretrained identity')
        calls.append(url)
        if len(calls)!=1:raise ValueError('repeated model acquisition')
        return states[EXTRACTOR]
    original_hub=torch.hub.load_state_dict_from_url
    torch.hub.load_state_dict_from_url=local_hub
    try:extractor=ak.ALIKED(model_name='aliked-n16',max_num_keypoints=1024,detection_threshold=.2,nms_radius=2).eval()
    finally:torch.hub.load_state_dict_from_url=original_hub
    if len(calls)!=1:raise ValueError('unexpected loader calls')
    matcher=lg.LightGlue(features=None,input_dim=128,weights=None,n_layers=9,flash=False,mp=False,
        depth_confidence=-1,width_confidence=-1,filter_threshold=.1).eval()
    loaded,mapping=renamed(states[MATCHER])
    expected=matcher.state_dict();missing=set(expected)-set(loaded);derived=[]
    independent=np.array([.8+.1*np.exp(-4*i/9) for i in range(9)],dtype=np.float32)
    if not np.array_equal(expected['confidence_thresholds'].numpy(),independent):raise ValueError('derived confidence formula mismatch')
    if missing=={'confidence_thresholds'}:
        loaded['confidence_thresholds']=torch.from_numpy(independent.copy());derived=['confidence_thresholds']
    elif missing:raise ValueError('unsupported absent state:'+str(missing))
    full={'extractor':states[EXTRACTOR],'matcher':loaded}
    objects={'extractor':extractor,'matcher':matcher};reports={}
    for name,model in objects.items():
        state=full[name];validate(torch,model.state_dict(),state)
        model.load_state_dict(state,strict=True)
        before=state_fingerprint({k:v.detach().numpy() for k,v in state.items()})
        actual=state_fingerprint({k:v.detach().numpy() for k,v in model.state_dict().items()})
        if actual!=before:raise ValueError('post-load exact state bytes differ')
        reports[name]={'keys':len(state),'elements':sum(v.numel() for v in state.values()),'sha256':actual,
            'state':{k:{'shape':list(v.shape),'dtype':str(v.dtype),'sha256':hashlib.sha256(v.detach().numpy().tobytes()).hexdigest(),
                'role':'source-derived' if name=='matcher' and k in derived else 'asset'} for k,v in state.items()}}
    grid=np.column_stack((np.tile(np.arange(-2,3),5),np.repeat(np.arange(-2,3),5))).astype(np.float32)
    if not np.array_equal(extractor.dkd.hw_grid.numpy(),grid):raise ValueError('DKD nonbuffer grid mismatch')
    def fingerprint():
        arrays={name+'.'+key:value.detach().numpy() for name,model in objects.items() for key,value in model.state_dict().items()}
        arrays['extractor.dkd.hw_grid']=extractor.dkd.hw_grid.numpy()
        return state_fingerprint(arrays)
    report={'status':'TECHNICAL_CHECK_PASSED','models':reports,'matcher_key_mapping':mapping,
        'explicit_source_derived':derived,'nonbuffer_grid':grid.tolist(),'full_state_sha256':fingerprint(),
        'pickle_inspections':inspections,'numeric_source_edits':False,'network':'denied','scope':'software state only'}
    write(stage+'-state.json',report)
    return torch,np,ak,lg,extractor,matcher,full,fingerprint

def negative_state_controls(torch,np,extractor,matcher,full,fingerprint):
    checks=[]
    for name,model in (('extractor',extractor),('matcher',matcher)):
        state=full[name];key=next(k for k,v in state.items() if v.is_floating_point() and v.ndim>=2)
        faults={};missing=dict(state);missing.pop(key);faults['missing']=missing
        faults['shape']={**state,key:state[key].reshape(-1)}
        faults['dtype']={**state,key:state[key].double()}
        bad=state[key].clone();bad.flatten()[0]=float('nan');faults['nonfinite']={**state,key:bad}
        for kind,invalid in faults.items():
            try:validate(torch,model.state_dict(),invalid)
            except ValueError:checks.append(name+'/'+kind)
            else:raise AssertionError('invalid state accepted:'+kind)
    tensor=torch.tensor([1.])
    try:renamed({'self_attn.0.x':tensor,'transformers.0.self_attn.x':tensor})
    except ValueError:checks.append('rename collision')
    else:raise AssertionError('rename collision accepted')
    from check_state_fingerprint import state_fingerprint,check
    check()
    baseline=fingerprint()
    key=next(k for k,v in full['extractor'].items() if v.is_floating_point())
    value=full['extractor'][key].numpy().copy();value.flat[0]=np.nextafter(value.flat[0],np.float32(np.inf))
    if state_fingerprint({key:value})==state_fingerprint({key:full['extractor'][key].numpy()}):raise AssertionError('one-bit change missed')
    if fingerprint()!=baseline:raise AssertionError('controls altered live model')
    return {'rejected':checks,'postload_bit_change_detected':True,'live_state_unchanged':True}

def features(torch,np,extractor,image,ak,record):
    def observe(module,args):
        score=args[0].detach();nms=ak.simple_nms(score,module.radius).clone();r=module.radius
        nms[:,:,:r,:]=0;nms[:,:,:,:r]=0;nms[:,:,-r:,:]=0;nms[:,:,:,-r:]=0
        candidates=int((nms>module.scores_th).sum())
        record.append({'threshold':module.scores_th,'above_threshold_after_nms':candidates,
            'upstream_mean_fallback_triggered':candidates==0,'mean_score':float(score.mean())})
    hook=extractor.dkd.register_forward_pre_hook(observe)
    try:result=extractor.extract(image,resize=None)
    finally:hook.remove()
    for key,value in result.items():
        if not torch.isfinite(value).all():raise ValueError('nonfinite features:'+key)
    q=result['keypoints'][0];h,w=image.shape[-2:]
    if q.ndim!=2 or q.shape[1]!=2 or not len(q) or (q<0).any() or (q>q.new_tensor([w-1,h-1])).any():raise ValueError('invalid native keypoints')
    if result['descriptors'].shape!=(1,len(q),128):raise ValueError('descriptor shape mismatch')
    if not torch.equal(result['image_size'],q.new_tensor([[w,h]])):raise ValueError('native image size not retained')
    return result

def validate_matches(torch,np,result,a,b):
    m0=result['matches0'][0].numpy();m1=result['matches1'][0].numpy();m,n=len(a['keypoints'][0]),len(b['keypoints'][0])
    if m0.shape!=(m,) or m1.shape!=(n,) or not np.issubdtype(m0.dtype,np.integer) or not np.issubdtype(m1.dtype,np.integer):raise ValueError('invalid match shape/dtype')
    if ((m0< -1)|(m0>=n)).any() or ((m1< -1)|(m1>=m)).any():raise ValueError('invalid match indices')
    source=np.flatnonzero(m0>=0);target=m0[source]
    if len(np.unique(target))!=len(target) or not np.array_equal(m1[target],source):raise ValueError('nonmutual or duplicate assignments')
    pairs=np.column_stack((source,target))
    if not np.array_equal(result['matches'][0].numpy(),pairs):raise ValueError('compact pair index disagreement')
    for key in ('matching_scores0','matching_scores1','scores'):
        values=result[key][0]
        if not torch.isfinite(values).all():raise ValueError('nonfinite matcher score')
    if result['stop']!=9:raise ValueError('unexpected adaptive depth')
    return {'source_points':m,'target_points':n,'matched':len(pairs),'source_unmatched':int((m0<0).sum()),
        'target_unmatched':int((m1<0).sum()),'software_indices_valid':True,'physical_precision':'UNVERIFIED'}

def worker(stage):
    images=None
    if stage=='native':
        import numpy as np
        from PIL import Image
        images=[]
        for index,expected in enumerate(IMAGES):
            path=ROOT/f'assets/private/dense-photo-0332/view-{index}.png'
            if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('owned PNG changed')
            with Image.open(path) as img:images.append(np.array(img.convert('RGB'),dtype=np.float32).transpose(2,0,1)/255)
        if any(image.shape!=(3,1280,720) for image in images):raise ValueError('native image axes swapped')
    restrict_io()
    torch,np,ak,lg,extractor,matcher,full,fingerprint=models(stage)
    initial=fingerprint();fallback=[];start=time.monotonic()
    if stage=='controls':
        from check_sparse_match_software import check
        result={'operators':check(torch,ak,lg),'state':negative_state_controls(torch,np,extractor,matcher,full,fingerprint)}
    else:
        with torch.inference_mode():
            if stage=='small':
                generator=torch.Generator().manual_seed(342)
                image=torch.rand((1,3,64,96),generator=generator,dtype=torch.float32)
                a=features(torch,np,extractor,image,ak,fallback);b=a
            elif stage=='native':
                a=features(torch,np,extractor,torch.from_numpy(images[0][None].copy()),ak,fallback)
                np.save(OUT/'native-source-q.npy',a['keypoints'][0].numpy(),allow_pickle=False)
                np.savez(OUT/'native-source-features.npz',**{k:v.numpy() for k,v in a.items()})
                b=features(torch,np,extractor,torch.from_numpy(images[1][None].copy()),ak,fallback)
                np.savez(OUT/'native-target-features.npz',**{k:v.numpy() for k,v in b.items()})
            else:raise ValueError('unknown registered stage')
            matched=matcher({'image0':a,'image1':b})
            result=validate_matches(torch,np,matched,a,b)
            if stage=='native':
                arrays={k:matched[k][0].numpy() for k in ('matches0','matches1','matching_scores0','matching_scores1','matches','scores','prune0','prune1')}
                np.savez(OUT/'native-matches.npz',**arrays)
                result['output_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('native-*.np*')}
        result['detector_behavior']=fallback
    if fingerprint()!=initial:raise ValueError('inference/control altered model state')
    result.update(status='TECHNICAL_CHECK_PASSED',seconds=time.monotonic()-start,full_state_unchanged=initial,
        scope='software only,no true point/camera/mm/head precision score',completed_utc=time.time())
    write(stage+'-result.json',result);print(json.dumps(result))

if __name__=='__main__':
    if ROOT!=Path('C:/workspace/headfoundry').resolve():raise ValueError('unexpected repository')
    for path in (ROOT,ROOT/'assets',ROOT/'assets/private',OUT):
        if getattr(path.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse target refused')
    if len(sys.argv)==3 and sys.argv[1]=='worker':worker(sys.argv[2])
    else:
        from bounded_process import run
        stage=sys.argv[1];limits={'controls':(120,2*1024**3),'small':(60,2*1024**3),'native':(180,4*1024**3)}
        if stage not in limits or (OUT/(stage+'-worker.json')).exists():raise ValueError('unknown/repeated stage')
        if stage!='controls' and not (OUT/'controls-result.json').is_file():raise ValueError('controls must pass first')
        if stage=='native' and not (OUT/'small-result.json').is_file():raise ValueError('small software check required')
        seconds,memory=limits[stage];env=dict(os.environ)
        env.update(TEMP=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TORCH_HOME=str(OUT/'torch-home'),HF_HOME=str(OUT/'hf-home'),PYTHONDONTWRITEBYTECODE='1')
        result=run([str(OUT/'env/Scripts/python.exe'),str(Path(__file__).resolve()),'worker',stage],str(ROOT),env,
            OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,memory)
        print(json.dumps(result))
        if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)
