"""Single actual-video global-query trial;medical geometry never an input."""
from pathlib import Path
import hashlib
import io
import json
import os
import sys
import time
import zipfile

sys.dont_write_bytecode = True

import cv2
import numpy as np

from check_bootstapir_0307 import verify_sources, digest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/global-query-video-0308'
RUNTIME = ROOT/'assets/private/tapir-runtime-0307'
SOURCE = ROOT/'assets/private/tapir-preflight-0306'
FRAMES = list(range(0,1021,30))+[1040]
CAMERAS = [0,30,60,90,180,210,240,300,330,360,390,510,570,630]
ANCHORS = [90,240,390]


def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False))


def prepare():
    started = time.time()
    lock = json.loads((ROOT/'examples/bootstapir-0307.asset-lock.json').read_text())
    verify_sources(lock)
    admission = json.loads((RUNTIME/'check.json').read_text())
    if admission['status']!='TECHNICAL_CHECK_PASSED' or digest(RUNTIME/'checkpoint.pt')!=lock['weights_sha256']:
        raise ValueError('software/weight admission missing')
    original = ROOT/'assets/private/real-capture-pilot-v1'
    protection = json.loads((ROOT/'assets/private/closed-experiments/0304-anatomical-camera/precheck.json').read_text())
    for row in protection['protected']:
        if row['path'].endswith(('manifest.json','provenance-confirmation.json')) and digest(row['path'])!=row['expected']:
            raise ValueError('consent/provenance changed')
    manifest = json.loads((original/'manifest.json').read_text())
    item = next(row for row in manifest['inputs'] if row['id']=='real-case-001-video')
    if (manifest['training_allowed'] is not False or manifest['upload_allowed'] is not False
            or not item['consent']['biometric_processing']
            or item['license_id']!='private-user-authorized-local-validation-only'
            or 'local_head_reconstruction_validation' not in item['allowed_uses']):
        raise ValueError('authorized local purpose missing')
    if digest(item['path'])!=item['sha256']:
        raise ValueError('source video differs')
    archive = ROOT/'assets/private/closed-experiments/0303-semantic-video/evidence.zip'
    if digest(archive)!='0c1d4e82a60f6be70bf5d49edb0b0ed056eb085549a4a953e9b65be8df24ec26':
        raise ValueError('RGB ledger archive changed')
    with zipfile.ZipFile(archive) as source:
        ledger = json.loads(source.read('frames.json'))
    OUT.mkdir(exist_ok=False)
    video, rows, panels = [], [], []
    capture = cv2.VideoCapture(item['path'])
    try:
        for ordinal in range(1041):
            ok,bgr = capture.read()
            if not ok:
                raise ValueError('sequential source decode incomplete')
            if ordinal not in FRAMES:
                continue
            rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            actual = hashlib.sha256(rgb.tobytes()).hexdigest()
            if rgb.shape!=(1280,720,3) or ledger[ordinal]['ordinal']!=ordinal or actual!=ledger[ordinal]['rgb_sha256']:
                raise ValueError('native RGB/ordinal mismatch')
            crop = rgb[320:1040,:720]
            video.append(cv2.resize(crop,(512,512),interpolation=cv2.INTER_LINEAR))
            rows.append({'ordinal':ordinal,'rgb_sha256':actual})
            if ordinal in ANCHORS:
                cv2.imwrite(str(OUT/f'source-{ordinal:04d}.png'),bgr)
                panel = bgr[320:1040,:720].copy()
                for x in range(0,720,50):
                    cv2.line(panel,(x,0),(x,719),(120,120,120),1)
                    cv2.putText(panel,str(x),(x+2,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,255),1)
                for y in range(350,1040,50):
                    cv2.line(panel,(0,y-320),(719,y-320),(120,120,120),1)
                    cv2.putText(panel,str(y),(2,y-318),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,255),1)
                cv2.putText(panel,'native '+str(ordinal),(5,48),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,255),2)
                panels.append(panel)
    finally:
        capture.release()
    if len(video)!=36 or time.time()-started>60:
        raise ValueError('preparation count/time budget exceeded')
    np.save(OUT/'video.npy',np.stack(video))
    sheet = np.vstack([np.zeros((28,2160,3),np.uint8),np.hstack(panels)])
    cv2.putText(sheet,'SOURCE ONLY - NOT A RECONSTRUCTED HEAD',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1)
    cv2.imwrite(str(OUT/'source-rulers.jpg'),sheet)
    record = {'status':'PREPARED_UNVERIFIED','started_utc':started,'seconds':time.time()-started,
              'frames':FRAMES,'camera_frames':CAMERAS,'query_frames':ANCHORS,'source_rows':rows,
              'source_sha256':item['sha256'],'video_sha256':digest(OUT/'video.npy'),
              'crop':[0,320,720,1040],'model_resolution':[512,512],
              'source_hashes_matched':36,'training':False,'upload':False,'medical_read':False}
    write('prepared.json',record)
    print(json.dumps({key:value for key,value in record.items() if key!='source_rows'}),flush=True)


def freeze():
    metadata = json.loads((OUT/'prepared.json').read_text())
    selection = json.loads((OUT/'source-masks.json').read_text())
    if time.time()-selection['review_started_utc']>600 or digest(OUT/'video.npy')!=metadata['video_sha256']:
        raise ValueError('source review budget/input identity differs')
    queries, native, panels, counts = [], [], [], {}
    for frame in ANCHORS:
        row = selection['regions'][str(frame)]
        mask = np.zeros((1280,720),np.uint8)
        polygons = [np.array(p,np.int32) for p in row['skin']]
        cv2.fillPoly(mask,polygons,255)
        if row['exclude']:
            cv2.fillPoly(mask,[np.array(p,np.int32) for p in row['exclude']],0)
        mask = cv2.erode(mask,np.ones((11,11),np.uint8))
        x,y,width,height = cv2.boundingRect(np.concatenate(polygons))
        image = cv2.imread(str(OUT/f'source-{frame:04d}.png'))
        actual = hashlib.sha256(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).tobytes()).hexdigest()
        expected = next(r['rgb_sha256'] for r in metadata['source_rows'] if r['ordinal']==frame)
        if actual!=expected:
            raise ValueError('query source image changed')
        visible = image.copy()
        cv2.polylines(visible,polygons,True,(0,255,0),1)
        for hole in row['exclude']:
            cv2.polylines(visible,[np.array(hole,np.int32)],True,(0,0,255),1)
        count = 0
        for j in range(20):
            for i in range(20):
                xy = np.array([x-.5+(i+.5)*width/20,y-.5+(j+.5)*height/20])
                pixel = np.rint(xy).astype(int)
                if mask[pixel[1],pixel[0]]==0:
                    continue
                if not (0<=xy[0]<720 and 320<=xy[1]<1040):
                    raise ValueError('query outside fixed crop')
                raster = (xy-np.array([0,320])+.5)*512/720
                native.append([frame,*xy])
                queries.append([FRAMES.index(frame),raster[1],raster[0]])
                cv2.circle(visible,tuple(pixel),2,(0,255,255),-1)
                count += 1
        counts[str(frame)] = count
        cv2.imwrite(str(OUT/f'mask-{frame:04d}.png'),mask)
        panel = visible[320:1040,:720]
        cv2.putText(panel,str(frame)+' source queries='+str(count),(8,28),cv2.FONT_HERSHEY_SIMPLEX,.65,(0,0,255),2)
        panels.append(panel)
    np.savez_compressed(OUT/'queries.npz',tyx=np.array(queries,dtype=np.float32),native=np.array(native,dtype=np.float64))
    sheet = np.vstack([np.zeros((28,2160,3),np.uint8),np.hstack(panels)])
    cv2.putText(sheet,'FIXED SOURCE QUERY PIXELS - NOT A RECONSTRUCTED HEAD',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1)
    cv2.imwrite(str(OUT/'query-review.jpg'),sheet)
    record = {'status':'FROZEN_UNVERIFIED','frozen_utc':time.time(),'source_mask_sha256':digest(OUT/'source-masks.json'),
              'query_sha256':digest(OUT/'queries.npz'),'video_sha256':metadata['video_sha256'],
              'counts':counts,'total':len(queries),'grid':[20,20],'erosion_native_px':5,
              'review_seconds':time.time()-selection['review_started_utc'],'physical_identity':'UNVERIFIED'}
    write('frozen.json',record)
    print(json.dumps(record),flush=True)


def worker_guard():
    def guard(event,args):
        if event in {'socket.connect','socket.bind','socket.getaddrinfo'}:
            raise PermissionError('offline local-validation worker')
        if event=='open' and isinstance(args[0],(str,os.PathLike)):
            path = Path(args[0]).resolve()
            if str(path).lower().endswith('.stl'):
                raise PermissionError('medical geometry forbidden')
            if path.is_relative_to(ROOT/'assets/private') and not any(path.is_relative_to(base) for base in [OUT,RUNTIME,SOURCE]):
                raise PermissionError('unapproved private input forbidden')
    sys.addaudithook(guard)


def infer():
    worker_guard()
    metadata = json.loads((OUT/'prepared.json').read_text())
    frozen = json.loads((OUT/'frozen.json').read_text())
    lock = json.loads((ROOT/'examples/bootstapir-0307.asset-lock.json').read_text())
    verify_sources(lock)
    if digest(OUT/'video.npy')!=frozen['video_sha256'] or digest(OUT/'queries.npz')!=frozen['query_sha256'] or digest(OUT/'source-masks.json')!=frozen['source_mask_sha256']:
        raise ValueError('frozen actual inputs changed')
    if digest(RUNTIME/'checkpoint.pt')!=lock['weights_sha256'] or metadata['frames']!=FRAMES:
        raise ValueError('weight/frame identities differ')
    sys.path[:0] = [str(RUNTIME/'site-packages'),str(SOURCE)]
    import torch
    from tapnet.torch import tapir_model
    if torch.__version__!=lock['torch'] or torch.version.cuda is not None:
        raise ValueError('unapproved CPU runtime')
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(307)
    started = time.monotonic()
    write('inference-start.json',{'pid':os.getpid(),'started_utc':time.time(),'status':'RUNNING','actual_forwards':0})
    video = np.load(OUT/'video.npy',allow_pickle=False)
    with np.load(OUT/'queries.npz',allow_pickle=False) as arrays:
        query = arrays['tyx']
    if video.shape!=(36,512,512,3) or video.dtype!=np.uint8 or query.shape!=(frozen['total'],3):
        raise ValueError('input contract differs')
    model = tapir_model.TAPIR(pyramid_level=1,num_pips_iter=4,extra_convs=True,use_casual_conv=False,
                              initial_resolution=(256,256),feature_extractor_chunk_size=10).eval()
    checkpoint = torch.load(RUNTIME/'checkpoint.pt',weights_only=True,mmap=True,map_location='cpu')
    if set(checkpoint)!=set(model.state_dict()):
        raise ValueError('state keys differ')
    model.load_state_dict(checkpoint,strict=True)
    if not all(torch.equal(checkpoint[name],value) and bool(torch.isfinite(value).all()) for name,value in model.state_dict().items()):
        raise ValueError('full loaded state differs/nonfinite')
    forward = time.monotonic()
    write('inference-start.json',{'pid':os.getpid(),'started_utc':time.time(),'status':'FORWARD_STARTED','actual_forwards_started':1})
    with torch.inference_mode():
        result = model(torch.from_numpy(video).float()[None]/255*2-1,torch.from_numpy(query)[None],
                       is_training=False,query_chunk_size=32)
    raw = {name:result[name].numpy()[0] for name in ['tracks','occlusion','expected_dist']}
    count = frozen['total']
    if raw['tracks'].shape!=(count,36,2) or any(raw[name].shape!=(count,36) for name in ['occlusion','expected_dist']) or not all(np.isfinite(value).all() for value in raw.values()):
        raise ValueError('raw prediction contract failed')
    visible = ((1-torch.sigmoid(result['occlusion']))*(1-torch.sigmoid(result['expected_dist']))>.5).numpy()[0]
    np.savez_compressed(OUT/'raw-predictions.npz',**raw,visible=visible)
    if not all(torch.equal(checkpoint[name],value) for name,value in model.state_dict().items()) or digest(RUNTIME/'checkpoint.pt')!=lock['weights_sha256']:
        raise ValueError('source state changed after forward')
    write('inference.json',{'status':'TECHNICAL_CHECK_PASSED','actual_forwards':1,'frames':36,'queries':count,
                          'seconds':time.monotonic()-started,'forward_seconds':time.monotonic()-forward,
                          'raw_sha256':digest(OUT/'raw-predictions.npz'),'video_sha256':frozen['video_sha256'],
                          'queries_sha256':frozen['query_sha256'],'weights_sha256':lock['weights_sha256'],
                          'visible_per_frame':visible.sum(axis=0).tolist(),'physical_identity':'UNVERIFIED','head':False})
    print((OUT/'inference.json').read_text(),flush=True)


def camera():
    worker_guard()
    from check_cycle_camera_contract import check
    from short_track_camera import fit,split_observations
    control = check(OUT/'control')
    write('control-result.json',control)
    inference = json.loads((OUT/'inference.json').read_text())
    if digest(OUT/'raw-predictions.npz')!=inference['raw_sha256']:
        raise ValueError('raw predictions changed')
    raw = np.load(OUT/'raw-predictions.npz',allow_pickle=False)
    given = np.load(OUT/'queries.npz',allow_pickle=False)['native']
    pixels = raw['tracks'].astype(np.float64)*720/512+np.array([-.5,319.5])
    visible = raw['visible']
    data = {'frames':CAMERAS,'xy':{}}
    tracks,eligible,counts = [],set(),[]
    for query in range(len(given)):
        source_frame = int(given[query,0])
        track = []
        reasons = {'predicted_invisible':0,'outside_supplied_image':0,'model_observations':0,'supplied_queries':0}
        for frame in CAMERAS:
            slot = FRAMES.index(frame)
            vertex = (frame,query)
            point = pixels[query,slot]
            if frame==source_frame:
                data['xy'][vertex] = given[query,1:]
                track.append(vertex)
                reasons['supplied_queries'] += 1
            elif not visible[query,slot]:
                reasons['predicted_invisible'] += 1
            elif not (0<=point[0]<720 and 320<=point[1]<1040):
                reasons['outside_supplied_image'] += 1
            else:
                data['xy'][vertex] = point
                track.append(vertex)
                eligible.add(vertex)
                reasons['model_observations'] += 1
        included = len(track)>=3
        if included:
            tracks.append(track)
        counts.append({'query':query,'source_frame':source_frame,'views':len(track),'included':included,**reasons})
    write('observation-admission.json',{'all_queries':len(given),'retained_tracks':len(tracks),'queries':counts,
                                      'self_query_training_only':True,'physical_identity':'UNVERIFIED'})
    train,held = split_observations(data,tracks,eligible)
    if any(CAMERAS[int(row[0])]==int(given[tracks[int(row[1])][0][1],0]) for row in held):
        raise ValueError('supplied query leaked into held validation')
    write('retained-track-ids.json',[[int(vertex[1]) for vertex in track[:1]][0] for track in tracks])
    _,_,_,_,_,result = fit(data,tracks,OUT/'camera',held_eligible=eligible)
    write('camera-report.json',{'status':'PARTIAL_SUCCESS' if result['status']=='TECHNICAL_CHECK_PASSED' else 'REJECT',
                              'camera':result,'head':False,'physical_poses':'UNVERIFIED','medical_mm':'UNVERIFIED'})
    print((OUT/'camera-report.json').read_text(),flush=True)
    if result['status']!='TECHNICAL_CHECK_PASSED':
        raise SystemExit(1)


def run():
    from bounded_process import run as bounded
    metadata = json.loads((OUT/'prepared.json').read_text())
    if time.time()-metadata['started_utc']>1200:
        raise ValueError('insufficient remaining registered trial/closeout budget')
    env = os.environ.copy()
    temporary = OUT/'temporary'
    temporary.mkdir(exist_ok=False)
    env.update(TEMP=str(temporary),TMP=str(temporary),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
    for phase,seconds in [('infer',360),('camera',180)]:
        record = bounded([sys.executable,'-B',str(Path(__file__).resolve()),phase],ROOT,env,
                         OUT/(phase+'-worker.log'),OUT/(phase+'-worker.json'),seconds,6*1024**3)
        print(json.dumps({'phase':phase,**record}),flush=True)
        if record['status']!='TECHNICAL_CHECK_PASSED':
            write('report.json',{'status':'REJECT','failed_phase':phase,**record,'head':False,'physical_accuracy':'UNVERIFIED'})
            raise SystemExit(1)
    write('report.json',{'status':'PARTIAL_SUCCESS','scope':'conditional reprojection only;source visual review required','head':False})


def review():
    video = np.load(OUT/'video.npy',allow_pickle=False)
    raw = np.load(OUT/'raw-predictions.npz',allow_pickle=False)
    native = np.load(OUT/'queries.npz',allow_pickle=False)['native']
    representatives = []
    for frame in ANCHORS:
        ids = np.flatnonzero(native[:,0]==frame)
        representatives.extend(ids[[0,len(ids)//2,-1]].tolist())
    colors = cv2.applyColorMap(np.linspace(0,255,len(representatives)).astype(np.uint8),cv2.COLORMAP_TURBO)[:,0]
    panels = []
    for frame in ANCHORS+[120,420,600]:
        panel = cv2.cvtColor(video[FRAMES.index(frame)],cv2.COLOR_RGB2BGR)
        for index,query in enumerate(representatives):
            if frame in ANCHORS:
                if int(native[query,0])!=frame:
                    continue
                point = (native[query,1:]-np.array([0,320])+.5)*512/720-.5
                visible = True
            else:
                point = raw['tracks'][query,FRAMES.index(frame)]-.5
                visible = raw['visible'][query,FRAMES.index(frame)]
            pixel = tuple(np.rint(point).astype(int))
            color = tuple(int(value) for value in colors[index])
            cv2.circle(panel,pixel,4,color,-1 if visible else 1)
            cv2.putText(panel,str(query)+('v' if visible else '?'),(pixel[0]+5,pixel[1]-3),cv2.FONT_HERSHEY_SIMPLEX,.45,color,1)
        cv2.putText(panel,('SUPPLIED QUERY ' if frame in ANCHORS else 'RAW PREDICTION ')+str(frame),(5,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,0,255),1)
        panels.append(panel)
    sheet = np.vstack([np.zeros((28,1536,3),np.uint8),np.hstack(panels[:3]),np.hstack(panels[3:])])
    cv2.putText(sheet,'FIXED RAW TRACK REVIEW - NOT A RECONSTRUCTED HEAD',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),1)
    cv2.imwrite(str(OUT/'tracking-review.jpg'),sheet)
    write('review-ids.json',{'rule':'first/middle/last query per original source group,fixed before predictions',
                             'queries':representatives,'targets':[120,420,600],'physical_identity':'UNVERIFIED'})


if __name__=='__main__':
    if Path.cwd().resolve()!=ROOT or sys.flags.optimize:
        raise RuntimeError('explicit repository cwd/unoptimized guards required')
    {'prepare':prepare,'freeze':freeze,'run':run,'infer':infer,'camera':camera,'review':review}[sys.argv[1]]()
