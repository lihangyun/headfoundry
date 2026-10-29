"""One fixed transfer of existing0332camera photometry to archived0385seed."""
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import sparse
from scipy.optimize import least_squares
from bounded_process import run
from direct_patch_camera import residual as photo_residual
from short_track_camera import intrinsics, project, write

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets

BASE = ROOT/'assets/private/real-photo-0387'
OUT = BASE
CLOSED = ROOT/'assets/private/closed-experiments'
DEADLINE = 1793285300
OFFSETS = np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def functions(source, wanted):
    nodes = [n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    assert {n.name for n in nodes} == set(wanted)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-functions','exec'),globals())


def load():
    old = CLOSED/'0383-roma-video/evidence.zip'
    assert sha(old) == '75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266'
    with zipfile.ZipFile(old) as archive:
        source = archive.read('source/roma_video_0383.py')
    assert hashlib.sha256(source).hexdigest() == '837dd7de95f0f60f714275fe59acedd8993c2b0e0793137304b911acdb7bdf1a'
    functions(source,['face_cue','prepare','evaluate'])
    shared = ROOT/'tools/dense_photo_0332.py'
    assert sha(shared) == '1875ffd4091735fdac38de748a5a81ed899f181fe9046b46f678ca20223e15be'
    functions(shared.read_text(),['camera_values','cameras','optimize','read_images','read_audit'])


def intake():
    load()
    original = CLOSED/'0385-archive-geometry/evidence.zip'
    assert sha(original) == '7e5bc84d7e3cff0c5fab9078e8c61e6632b923bdc0d46d30c6a3b0f1822af1ec'
    index = json.loads(original.with_name('index.json').read_text())
    assert all(sha(path)==digest for path,digest in index['protected'].items())
    write(BASE/'protected.json',index['protected'])
    with zipfile.ZipFile(original) as archive:
        for name in ('observations.npz','initial.npz','initial.json','split.json'):
            (BASE/name).write_bytes(archive.read(name))
        (BASE/'baseline-result.json').write_bytes(archive.read('result.json'))
    prepare()
    rgbmeta=json.loads((BASE/'inputs.json').read_text())
    write(BASE/'rgb-inputs.json',rgbmeta)
    grayhashes={}
    for camera in range(3):
        path=BASE/f'view-{camera}.png'
        Image.open(path).convert('L').save(path)
        grayhashes[path.name]=sha(path)
    write(BASE/'inputs.json',dict(images=grayhashes,conversion='Pillow RGB to L, native dimensions, /255 at read',
                                 original_rgb=rgbmeta['images']))
    assert sha(BASE/'observations.npz')=='9784ddc07cbba5b2d96e07959d6d196cc6e782609347878a4a9c04fdc602a57e'


def overlap_and_bounds():
    obs=dict(np.load(BASE/'observations.npz')); report={}
    for label in ('initial','final'):
        path=BASE/(label+'.npz')
        if not path.exists():continue
        state=dict(np.load(path)); k,poses=state['K'],state['poses']
        if label=='initial':
            rho=1/state['points'][:,2]; gains=np.zeros(3); biases=np.zeros(3)
        else:
            x=state['values']; rho=np.exp(x[16:]); gains=np.r_[0.,x[12],x[14]];biases=np.r_[0.,x[13],x[15]]
        pixels=obs['xy'][0,obs['train'],None,:]+OFFSETS
        _,warps=photo_residual(read_images(),pixels,rho,poses,gains,biases,np.log(k[0,0]))
        samples=[pixels,*warps]; records=[]
        for camera,xy in enumerate(samples):
            # Bilinear sample uses four integer texels; count held centers whose
            # own bilinear texels overlap any training sample. No mask is made.
            texels=set()
            for x,y in np.floor(xy.reshape(-1,2)).astype(int):
                texels.update(((x,y),(x+1,y),(x,y+1),(x+1,y+1)))
            overlapping=[]
            for i in obs['held']:
                x,y=np.floor(obs['xy'][camera,i]).astype(int)
                if texels & {(x,y),(x+1,y),(x,y+1),(x+1,y+1)}:
                    overlapping.append(int(obs['source_ids'][i]))
            records.append(overlapping)
        report[label]=dict(held_center_texel_overlap_source_ids=records)
        if label=='final':
            report[label].update(lower_distance=(state['values']-state['lower']).tolist(),
                                 upper_distance=(state['upper']-state['values']).tolist())
    write(BASE/'support-and-bounds.json',report)


def direct():
    global OUT
    load(); read_audit()
    try:
        optimize()
    except Exception as error:
        write(BASE/'direct-failure.json',dict(type=type(error).__name__,error=str(error)))
        if (BASE/'final.npz').exists():overlap_and_bounds()
        raise
    overlap_and_bounds()
    folder=BASE/'evaluation';folder.mkdir(exist_ok=False)
    (folder/'observations.npz').write_bytes((BASE/'observations.npz').read_bytes())
    (folder/'initial.npz').write_bytes((BASE/'final.npz').read_bytes())
    OUT=folder
    try:
        evaluate()
    finally:
        OUT=BASE


def controller(stage):
    if time.time()>DEADLINE:raise RuntimeError('whole deadline')
    if stage=='intake':BASE.mkdir(exist_ok=False)
    receipt=BASE/(stage+'-worker.json')
    if receipt.exists():raise RuntimeError('one attempt only')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
    result=run([sys.executable,'-B',str(Path(__file__).resolve()),stage+'-worker'],str(ROOT),env,
               BASE/(stage+'.log'),receipt,min(120 if stage=='intake' else 300,DEADLINE-time.time()),2*1024**3)
    print(json.dumps(result,indent=2))
    if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)


def close_archive():
    protected=json.loads((BASE/'protected.json').read_text())
    assert all(sha(path)==digest for path,digest in protected.items())
    assert json.loads((BASE/'direct-worker.json').read_text())['exit']==1
    baseline=json.loads((BASE/'baseline-result.json').read_text())
    final=json.loads((BASE/'evaluation/result.json').read_text())
    photo=json.loads((BASE/'direct.json').read_text())
    result=dict(status='REJECT',baseline=baseline,final=final,photometric=photo,
                note='image residual reduction is not geometry improvement;no head/medical measurement')
    write(BASE/'result.json',result)
    destination=CLOSED/'0387-real-photo';destination.mkdir(exist_ok=False)
    allfiles=sorted(p for p in BASE.rglob('*') if p.is_file())
    keep={p.relative_to(BASE).as_posix():p for p in allfiles if not p.name.startswith('view-')}
    keep['source/real_photo_0387.py']=Path(__file__)
    target=destination/'evidence.zip'
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as archive:
        for name,path in keep.items():archive.write(path,name)
    members={name:dict(bytes=path.stat().st_size,sha256=sha(path)) for name,path in keep.items()}
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==row['sha256'] for name,row in members.items())
    index=dict(archive_sha256=sha(target),archive_bytes=target.stat().st_size,members=members,
               protected=protected,loose_files=len(allfiles),loose_bytes=sum(p.stat().st_size for p in allfiles),
               result=result)
    write(destination/'index.json',index)
    print(json.dumps({k:v for k,v in index.items() if k not in ('members','protected','result')},indent=2))


if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='archive':close_archive()
    elif stage.endswith('-worker'):{'intake':intake,'direct':direct}[stage[:-7]]()
    else:controller(stage)
