"""One fixed native video observation/camera trial;no medical geometry intake."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import cv2
import numpy as np
from PIL import Image,ImageDraw
from bounded_process import run
from headfoundry.manifest import validate_input_assets

OUT=ROOT/'assets/private/aliked-real-0344'
RUNTIME=ROOT/'assets/private/aliked-runtime-0342'
FRAMES=[240,300,630]
DEADLINE=1792755269.0  # 2026-10-23T11:34:29Z


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(name,data):
    path=OUT/name
    if path.parent!=OUT:raise ValueError('own flat receipts only')
    with path.open('x',encoding='utf8') as stream:json.dump(data,stream,indent=2,allow_nan=False)


def face_cue(rgb):
    rgb=rgb.astype(np.int16);mask=np.zeros(rgb.shape[:2],np.uint8)
    mask[500:820,100:620]=((rgb[:,:,0]-rgb[:,:,2])>12)[500:820,100:620]
    count,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    if count<2:raise ValueError('fixed source foreground cue empty')
    label=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    return cv2.erode((labels==label).astype(np.uint8),np.ones((8,8),np.uint8))


def admission():
    for folder in ('aliked-runtime-0342','aliked-physical-0343'):
        verify=json.loads((ROOT/'assets/private'/folder/'verification.json').read_text())
        if verify['status']!='TECHNICAL_CHECK_PASSED':raise ValueError('candidate admission missing')
        for name,digest in verify['files_sha256'].items():
            path=ROOT/name if folder=='aliked-runtime-0342' else ROOT/'assets/private'/folder/name
            if sha(path)!=digest:raise ValueError('frozen admission receipt changed:'+name)


def prepare():
    admission()
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    document=json.loads(manifest.read_text());records=[r for r in document['inputs'] if r['id']=='real-case-001-video']
    if (len(records)!=1 or document.get('training_allowed') is not False or document.get('upload_allowed') is not False
            or document.get('purpose')!='local_head_reconstruction_validation'
            or validate_input_assets(dict(document,inputs=records),manifest.parent)):
        raise ValueError('exact local case001 video authorization required')
    consent=manifest.parent/'provenance-confirmation.json';provenance=json.loads(consent.read_text())
    if provenance['manifest_sha256']!=sha(manifest) or not provenance['cases']['real-case-001']['scan_video_same_stage']:
        raise ValueError('consent/provenance binding fails')
    ledger_path=ROOT/'assets/private/video-observability-0252/report.json'
    ledger=json.loads(ledger_path.read_text());record=records[0];source=Path(record['path'])
    if record['sha256']!=ledger['source_sha256']:raise ValueError('video identity binding fails')
    capture=cv2.VideoCapture(str(source));ordinal=0;images={};rgb_records={};nn={}
    try:
        while True:
            ok,bgr=capture.read()
            if not ok:break
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            if rgb.shape!=(1280,720,3):raise ValueError('native dimensions changed')
            digest=hashlib.sha256(rgb.tobytes()).hexdigest()
            if ordinal>=len(ledger['frame_records']) or digest!=ledger['frame_records'][ordinal]['rgb_sha256']:
                raise ValueError('sequential RGB identity differs')
            if ordinal in FRAMES:
                camera=FRAMES.index(ordinal);name=f'view-{camera}.png';rgbname='rgb-'+name
                Image.fromarray(rgb).save(OUT/rgbname);Image.fromarray(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)).save(OUT/name)
                images[name]=sha(OUT/name);nn[rgbname]=sha(OUT/rgbname);rgb_records[str(ordinal)]=digest
                if camera==0:Image.fromarray(face_cue(rgb)*255).save(OUT/'cue.png')
            ordinal+=1
    finally:capture.release()
    if ordinal!=1041 or ordinal!=len(ledger['frame_records']) or len(images)!=3 or sha(source)!=record['sha256']:
        raise ValueError('complete sequential decode/source identity fails')
    sheet=Image.new('RGB',(720,465),(20,20,20));draw=ImageDraw.Draw(sheet)
    for camera,frame in enumerate(FRAMES):
        with Image.open(OUT/f'rgb-view-{camera}.png') as image:shown=np.array(image.convert('RGB'))
        if camera==0:
            cue=face_cue(shown);edge=cv2.morphologyEx(cue,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8));shown[edge>0]=[255,0,0]
        sheet.paste(Image.fromarray(shown).resize((240,427)),(camera*240,0));draw.text((camera*240+6,435),f'ordinal {frame}',fill='white')
    sheet.save(OUT/'inputs.png')
    write('inputs.json',{'images':dict(sorted(images.items())),'ordinals':FRAMES,'rgb_sha256':rgb_records,
        'manifest_sha256':sha(manifest),'consent_sha256':sha(consent),'ledger_sha256':sha(ledger_path),
        'source_sha256':record['sha256'],'frames_verified':ordinal,'rights':'local validation only,no upload/training',
        'scan_read':False,'case002_read':False,'cue_sha256':sha(OUT/'cue.png'),'nn_images':dict(sorted(nn.items()))})


def infer():
    # Trusted authorized RGB intake precedes strict model audit;no video/GT to NN.
    lock=json.loads((OUT/'inputs.json').read_text());images=[]
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    if sha(manifest)!=lock['manifest_sha256'] or sha(manifest.parent/'provenance-confirmation.json')!=lock['consent_sha256']:
        raise ValueError('intake rights binding changed')
    for name,digest in lock['nn_images'].items():
        if sha(OUT/name)!=digest:raise ValueError('authorized native RGB image changed')
        with Image.open(OUT/name) as image:images.append(np.array(image.convert('RGB'),dtype=np.float32).transpose(2,0,1)/255)
    if len(images)!=3 or any(a.shape!=(3,1280,720) for a in images):raise ValueError('fixed native tensor intake fails')
    import aliked_native_0342 as native
    def own_writes(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        mode,flags=args[1:3];writing=any(c in mode for c in 'wax+') if isinstance(mode,str) else bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and not Path(os.fsdecode(args[0])).resolve().is_relative_to(OUT.resolve()):
            raise PermissionError('fresh0344writes only')
    sys.addaudithook(own_writes);native.restrict_io()
    native.write=write  # ONLY receipt destination;numeric/source path OUT stays0342.
    torch,_numpy,ak,_lg,extractor,matcher,_full,fingerprint=native.models('real0344')
    initial=fingerprint()
    if initial!='e0bac0ab937fe9ccbe092c08fe6bebb2d8288bba24f71d3eda4cc68fcb5c8cce':raise ValueError('candidate state identity differs')
    digests={};fallback=[];features=[];pairs={};started=time.monotonic()
    def save(name,arrays):
        buffer=io.BytesIO();np.savez(buffer,**arrays);data=buffer.getvalue()
        with (OUT/name).open('xb') as stream:stream.write(data)
        digests[name]=hashlib.sha256(data).hexdigest()
    with torch.inference_mode():
        for camera,image in enumerate(images):
            result=native.features(torch,np,extractor,torch.from_numpy(image[None].copy()),ak,fallback)
            features.append(result);save(f'features-{camera}.npz',{k:v.numpy() for k,v in result.items()})
        for camera in (1,2):
            result=matcher({'image0':features[0],'image1':features[camera]})
            pairs[str(camera)]=native.validate_matches(torch,np,result,features[0],features[camera])
            m0,m1=result['matches0'][0].numpy(),result['matches1'][0].numpy();back=np.flatnonzero(m1>=0)
            if not np.array_equal(m0[m1[back]],back):raise ValueError('orphan reverse assignments')
            save(f'matches-{camera}.npz',{k:result[k][0].numpy() for k in ('matches0','matches1','matching_scores0','matching_scores1','matches','scores','prune0','prune1')})
    if fingerprint()!=initial:raise ValueError('model state changed during actual inference')
    write('inference.json',{'status':'TECHNICAL_CHECK_PASSED','pairs':pairs,'detector_behavior':fallback,
        'output_sha256':digests,'full_state_unchanged':initial,'seconds':time.monotonic()-started,
        'numeric_source_edits':False,'writer_redirect_only':True,'scope':'raw predictions,not physical/camera/head precision'})


def assemble():
    record=json.loads((OUT/'inference.json').read_text());lock=json.loads((OUT/'inputs.json').read_text())
    for name,digest in record['output_sha256'].items():
        if sha(OUT/name)!=digest:raise ValueError('raw sparse outputs changed')
    if sha(OUT/'cue.png')!=lock['cue_sha256']:raise ValueError('frozen source cue changed')
    with Image.open(OUT/'cue.png') as image:cue=np.asarray(image)>0
    q=np.load(OUT/'features-0.npz')['keypoints'][0].astype(float);pixel=np.floor(q+.5).astype(int)
    in_cue=cue[pixel[:,1],pixel[:,0]];all_xy=[q];raw={'source_q':q,'source_cue':in_cue};valid=in_cue.copy();counts={}
    for camera in (1,2):
        target=np.load(OUT/f'features-{camera}.npz')['keypoints'][0].astype(float)
        matches=np.load(OUT/f'matches-{camera}.npz')['matches0'];assigned=matches>=0
        if len(matches)!=len(q) or ((matches< -1)|(matches>=len(target))).any():raise ValueError('invalid frozen source assignment')
        uv=np.full_like(q,np.nan);uv[assigned]=target[matches[assigned]];all_xy.append(uv)
        raw.update({f'target_{camera}':uv,f'match_{camera}':matches,f'assigned_{camera}':assigned})
        counts[str(camera)]={'all_assignments':int(assigned.sum()),'source_cue_assignments':int((assigned&in_cue).sum()),
            'source_cue_unmatched':int((~assigned&in_cue).sum())}
        valid&=assigned
    all_xy=np.stack(all_xy);support=np.isfinite(all_xy).all(2)&(all_xy>=4).all(2)&(all_xy<=[715,1275]).all(2)
    valid&=support.all(0);raw.update(all_xy=all_xy,patch_supported=support,admitted_all=valid)
    np.savez_compressed(OUT/'raw-observations.npz',**raw)
    n=int(valid.sum());spans=[np.ptp(view[valid],axis=0).tolist() if n else [0,0] for view in all_xy]
    sheet=Image.new('RGB',(2160,1280))
    for camera in range(3):
        with Image.open(OUT/f'rgb-view-{camera}.png') as image:shown=image.convert('RGB')
        draw=ImageDraw.Draw(shown)
        for index,(x,y) in enumerate(all_xy[camera]):
            if np.isfinite([x,y]).all() and in_cue[index]:
                color='lime' if valid[index] else 'red';draw.ellipse((x-2,y-2,x+2,y+2),fill=color)
                if index%6==0:draw.text((x+3,y),str(index),fill=color)
        sheet.paste(shown,(camera*720,0))
    sheet.save(OUT/'tracks.png')
    passed=n>=48 and min(min(span) for span in spans)>=50
    write('coverage.json',{'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','source_detected':len(q),
        'source_cue_points':int(in_cue.sum()),'complete_patch_supported':n,'minimum':48,'spans_xy_px':spans,
        'pairs':counts,'raw_sha256':sha(OUT/'raw-observations.npz'),'physical_material_precision':'UNVERIFIED'})
    if not passed:raise ValueError('fixed three-view observation coverage fails')
    xy=all_xy[:,valid];ordered=sorted(range(n),key=lambda index:hashlib.sha256(f'331/hold/{index}'.encode()).digest())
    held=np.array(ordered[:int(n*.2)]);train=np.array(sorted(set(range(n))-set(held)))
    if len(held)<9 or len(train)<36:raise ValueError('whole-point train/held coverage fails')
    np.savez_compressed(OUT/'observations.npz',xy=xy,held=held,train=train,source_ids=np.flatnonzero(valid))


def controller(stage):
    if ROOT!=Path('C:/workspace/headfoundry').resolve() or time.time()>DEADLINE:raise ValueError('scope/time budget fails')
    if stage=='prepare':
        OUT.mkdir(exist_ok=False)
        for path in (ROOT,ROOT/'assets',ROOT/'assets/private',OUT):
            if getattr(path.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse target refused')
        (OUT/'tmp').mkdir();write('entry.json',{'source_sha256':sha(__file__),'registered':'c2aba31','started_utc':time.time()})
    if (OUT/(stage+'-worker.json')).exists():raise FileExistsError('one worker per stage')
    gates={'infer':'inputs-reviewed.json','assemble':'inference.json','initialize':'tracks-reviewed.json',
        'optimize':'initial.json','evaluate':'direct.json'}
    if stage in gates and not (OUT/gates[stage]).exists():raise ValueError('required previous gate absent')
    env=dict(os.environ);env.update(TEMP=str(OUT/'tmp'),TMP=str(OUT/'tmp'),PYTHONDONTWRITEBYTECODE='1',
        OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',HF_HUB_OFFLINE='1',
        TORCH_HOME=str(OUT/'tmp'),HF_HOME=str(OUT/'tmp'),XDG_CACHE_HOME=str(OUT/'tmp'))
    limits={'prepare':(120,2),'infer':(180,4),'assemble':(60,2),'initialize':(120,2),'optimize':(300,2),'evaluate':(60,2),'check':(60,2)}
    seconds,gib=limits[stage];executable=str(RUNTIME/'env/Scripts/python.exe') if stage=='infer' else sys.executable
    result=run([executable,str(Path(__file__)),stage+'-worker'],str(ROOT),env,OUT/(stage+'.log'),OUT/(stage+'-worker.json'),seconds,gib*1024**3)
    print(json.dumps(result,indent=2));return result['status']=='TECHNICAL_CHECK_PASSED'


if __name__=='__main__':
    stage=sys.argv[1]
    if stage.endswith('-worker'):
        name=stage[:-7];cv2.setNumThreads(4)
        if name in ('initialize','optimize','evaluate','check'):
            import sparse_camera_0344 as camera
            getattr(camera,name)()
        else:{'prepare':prepare,'infer':infer,'assemble':assemble}[name]()
    else:sys.exit(0 if controller(stage) else 1)
