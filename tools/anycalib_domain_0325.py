"""One fixed owned known-camera conditional test;no actual subject reconstruction."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

import numpy as np
from PIL import Image,ImageDraw

from anycalib_adapter import native_intrinsics,validate_state,fingerprint
from bounded_process import run
from prepare_makehuman_head import extract_head

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/anycalib-domain-0325'
SOURCE=ROOT/'assets/private/anycalib-source-0322'
RUNTIME=ROOT/'assets/private/anycalib-runtime-0324'
ASSET=ROOT/'assets/private/anycalib-asset-0323/anycalib_edit.pt'
NAMES=['room','front','plus60','minus60']


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf8')


def prepare():
    lock=json.loads((ROOT/'examples/makehuman-base-asset-lock.json').read_text())
    if lock['license_id']!='CC0-1.0':raise ValueError('base rights missing')
    (OUT/'assets').mkdir();(OUT/'inputs').mkdir()
    for name,expected in lock['sha256'].items():
        path=lock['source_path'] if name=='base.obj' else name
        url=f"https://raw.githubusercontent.com/makehumancommunity/makehuman/{lock['revision']}/{path}"
        with urllib.request.urlopen(url,timeout=30) as response:content=response.read(8*1024**2+1)
        if len(content)>8*1024**2 or hashlib.sha256(content).hexdigest()!=expected:raise ValueError('generic base/grant identity')
        (OUT/'assets'/name).write_bytes(content)
    vertices,faces,indices=extract_head((OUT/'assets/base.obj').read_text(),include_eye_helpers=True)
    vertices-=(vertices.max(0)+vertices.min(0))/2;vertices*=2/np.ptp(vertices[:,1])
    np.savez_compressed(OUT/'generic-head.npz',vertices=vertices,faces=faces,source_indices=indices)
    with (OUT/'generic-head.obj').open('x') as stream:
        for vertex in vertices:stream.write('v '+' '.join(map(str,vertex))+'\n')
        for face in faces:stream.write('f '+' '.join(str(int(i)+1) for i in face)+'\n')
    command=['C:/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','--python-exit-code','1',
             '--python',str(ROOT/'tools/blender_anycalib_0325.py'),'--',str(OUT)]
    subprocess.run(command,cwd=ROOT,check=True,timeout=150,creationflags=subprocess.CREATE_NO_WINDOW)
    if not (OUT/'truth.json').is_file():raise ValueError('no completed render sentinel')
    images={name:sha(OUT/'inputs'/(name+'.png')) for name in NAMES}
    save('images.json',images)
    sheet=Image.new('RGB',(540,1000),'white');draw=ImageDraw.Draw(sheet)
    for i,name in enumerate(NAMES):
        with Image.open(OUT/'inputs'/(name+'.png')) as image:
            if image.size!=(720,1280):raise ValueError('native render dimensions')
            tile=image.convert('RGB').resize((270,480))
        x,y=(i%2)*270,(i//2)*500;sheet.paste(tile,(x,y+20));draw.text((x+4,y+4),name,fill='black')
    sheet.save(OUT/'inputs.png')
    save('prepared.json',{'status':'TECHNICAL_CHECK_PASSED','base':lock,'images':images,
                         'source_identity':sha(ROOT/'tools/blender_anycalib_0325.py')})


def inference():
    allowed_images={OUT/'inputs'/(name+'.png') for name in NAMES}
    def audit(event,args):
        if event in ['socket.connect','socket.getaddrinfo','subprocess.Popen','os.system']:raise PermissionError('offline domain worker')
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            path=Path(os.fsdecode(args[0])).resolve();mode=args[1]
            reading=not isinstance(mode,str) or not any(flag in mode for flag in ('w','a','x'))
            if not reading:return
            if path.suffix.lower() in ['.stl','.mp4','.mov','.avi','.jpg','.jpeg','.png'] and path not in allowed_images:
                raise PermissionError('unapproved media read')
            if (ROOT/'assets/private') in path.parents and path not in allowed_images|{OUT/'images.json'} and not any(
                path.is_relative_to(parent) for parent in [SOURCE,RUNTIME,ASSET.parent,OUT/'tmp']):
                raise PermissionError('unrelated private/truth/geometry read')
    sys.addaudithook(audit)
    sys.path[:0]=[str(RUNTIME/'site'),str(SOURCE/'snapshot')]
    import torch
    from anycalib import AnyCalib
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
    model=AnyCalib(model_id=None,fallback_to_sac=False).eval()
    state=torch.load(ASSET,map_location='cpu',weights_only=True,mmap=True)
    validate_state(state,model.state_dict());model.load_state_dict(state,strict=True)
    expected='82a4929d5371797bb888864e0c3c90b5c8b48d95f8105c44dd30b294b6b818bd'
    if fingerprint(model.state_dict())!=expected:raise ValueError('loaded state differs from0324')
    hashes=json.loads((OUT/'images.json').read_text());outputs={}
    for name in NAMES:
        path=OUT/'inputs'/(name+'.png')
        if sha(path)!=hashes[name]:raise ValueError('fixed input changed')
        with Image.open(path) as im:rgb=np.array(im.convert('RGB'),dtype=np.float32)/255
        image=torch.from_numpy(rgb).permute(2,0,1);torch.manual_seed(324);start=time.monotonic()
        with torch.inference_mode():pred=model.predict(image,'pinhole')
        elapsed=time.monotonic()-start
        arrays={key:value.detach().numpy() for key,value in pred.items() if isinstance(value,torch.Tensor)}
        arrays['pred_size']=np.array(pred['pred_size']);np.savez_compressed(OUT/(name+'-raw.npz'),**arrays)
        raw_hashes={key:hashlib.sha256(value.tobytes()).hexdigest() for key,value in arrays.items()}
        outputs[name]={'success':bool(pred['success']),'edge_params':arrays['intrinsics'].tolist(),
            'working_information':arrays['intrinsics_icovs'].tolist(),'pred_size':list(pred['pred_size']),
            'raw_field_hashes':raw_hashes,'seconds':elapsed,
            'norm_error':float(np.abs(np.linalg.norm(arrays['rays'],axis=1)-1).max())}
        save('predictions.json',outputs)
        if not bool(pred['success']) or not all(np.isfinite(v).all() for v in arrays.values()) or outputs[name]['norm_error']>1e-5:
            raise ValueError('invalid explicit complete output:'+name)
        native_intrinsics(arrays['intrinsics'])
    if fingerprint(model.state_dict())!=expected:raise ValueError('model state changed')
    save('inference-complete.json',{'status':'TECHNICAL_CHECK_PASSED','scope':'four predictions only;independent scoring required',
        'state_fingerprint':expected,'network_denied':True,'human_and_truth_read_denied':True})


def score():
    truth=json.loads((OUT/'truth.json').read_text());predictions=json.loads((OUT/'predictions.json').read_text())
    yy,xx=np.mgrid[330:951:25j,140:581:25j];pixels=np.c_[xx.ravel(),yy.ravel()]
    rows={};raw={}
    for name in NAMES:
        correct=np.array(truth['contexts'][name]['edge_K']);correct[:2,2]-=.5
        rays=np.c_[(pixels-correct[:2,2])/[correct[0,0],correct[1,1]],np.ones(len(pixels))]
        params=np.array(predictions[name]['edge_params'])
        source_scale=np.array([238/720,420/1271],np.float32);source_shift=np.array([0,-4*source_scale[1]],np.float32)
        exact_scale=np.array([238/720,420/1271]);exact_shift=np.array([0,-4*420/1271])
        working=np.r_[params[:2]*source_scale,params[2:]*source_scale+source_shift]
        exact=np.r_[working[:2]/exact_scale,(working[2:]-exact_shift)/exact_scale]
        results={}
        for mapping,edge in [('upstream',params),('exact_resampling',exact)]:
            k=native_intrinsics(edge);projected=rays@k.T;projected=projected[:,:2]/projected[:,2:]
            errors=np.linalg.norm(projected-pixels,axis=1);relative=np.abs(edge[:2]/1200-1)
            results[mapping]={'p95_px':float(np.percentile(errors,95)),'max_px':float(errors.max()),
                 'focal_relative_errors':relative.tolist(),'native_K':k.tolist(),
                 'passed':bool(np.percentile(errors,95)<=3 and (relative<=.02).all())}
            raw[name+'_'+mapping]=errors
        rows[name]=results
    control=rays@correct.T;control=control[:,:2]/control[:,2:]
    if np.abs(control-pixels).max()>1e-7:raise ValueError('trueKprojection sanity')
    wrong=correct.copy();wrong[0,2]+=50;bad=rays@wrong.T
    if np.percentile(np.linalg.norm(bad[:,:2]/bad[:,2:]-pixels,axis=1),95)<=3:raise ValueError('wrongKnot rejected')
    passed=all(mapping['passed'] for name,row in rows.items() if name!='room' for mapping in row.values())
    np.savez_compressed(OUT/'scores.npz',pixels=pixels,**raw)
    save('result.json',{'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
       'scope':'conditional generic-head intrinsic test,not real-person camera/head/medical accuracy','contexts':rows,
       'physical_head_SE3_medical':'UNVERIFIED'})
    print(json.dumps(rows,indent=2))


if __name__=='__main__':
    mode=sys.argv[1]
    if mode in ['prepare','predict']:
        if mode=='prepare':OUT.mkdir(exist_ok=False);(OUT/'tmp').mkdir()
        else:
            if (OUT/'infer-worker.json').exists() or not (OUT/'prepared.json').exists():raise ValueError('no repeat/incomplete input')
            entry=json.loads((ROOT/'assets/private/anycalib-software-0324/entry.json').read_text())
            for row in entry['protected']:
                if sha(Path(row['path']))!=row['sha256']:raise ValueError('protected change')
            if sha(ASSET)!=entry['asset_sha']:raise ValueError('model bytes changed')
            for row in json.loads((SOURCE/'result.json').read_text())['responses']+json.loads((SOURCE/'notices.json').read_text()):
                if sha(SOURCE/row['path'])!=row['sha256']:raise ValueError('source/grant changed')
        env=os.environ.copy();env.update({key:'4' for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']})
        env.update(PYTHONDONTWRITEBYTECODE='1',XFORMERS_DISABLED='1',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TORCH_HOME=str(OUT/'torch-cache'))
        stage='make-inputs' if mode=='prepare' else 'infer'
        record=run([sys.executable,str(Path(__file__).resolve()),stage],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),180,(3 if mode=='prepare' else 5)*1024**3)
        print(json.dumps(record,indent=2))
        if record['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)
        if mode=='predict':score()
    elif mode=='make-inputs':prepare()
    elif mode=='infer':inference()
    else:raise ValueError('unknown mode')
