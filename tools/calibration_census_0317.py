"""Fixed-band native input census;not a camera estimator."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image,ImageDraw
from headfoundry.manifest import sha256_file,validate_input_assets

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/calibration-census-0317'

def segments(bgr):
    gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(gray,80,160)
    edges[192:,43:677]=0
    lines=cv2.HoughLinesP(edges,1,np.pi/180,60,minLineLength=120,maxLineGap=8)
    return np.empty((0,4),int) if lines is None else lines.reshape(-1,4)

def worker():
    start=time.monotonic();cv2.setNumThreads(4)
    black=np.zeros((1280,720,3),np.uint8)
    assert not len(segments(black))
    center=black.copy();cv2.line(center,(360,300),(360,900),(255,255,255),2)
    assert not len(segments(center))
    outer=black.copy();cv2.line(outer,(20,300),(20,900),(255,255,255),2)
    assert len(segments(outer))>0
    manifest_path=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    records=[r for r in manifest['inputs'] if r['id']=='real-case-001-video']
    assert len(records)==1 and manifest['training_allowed'] is False and manifest['upload_allowed'] is False
    assert not validate_input_assets(dict(manifest,inputs=records),manifest_path.parent)
    source=Path(records[0]['path']);assert sha256_file(source)==records[0]['sha256']
    old=json.loads((ROOT/'assets/private/video-observability-0252/report.json').read_text())
    expected=old['frame_records'];assert len(expected)==1041
    capture=cv2.VideoCapture(str(source));assert capture.isOpened()
    rows=[];chosen={}
    try:
        while True:
            assert time.monotonic()-start<=110,'registered inner budget'
            ok,bgr=capture.read()
            if not ok:break
            ordinal=len(rows);assert ordinal<1041 and bgr.shape==(1280,720,3)
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            digest=hashlib.sha256(rgb.tobytes()).hexdigest()
            assert expected[ordinal]['ordinal']==ordinal and expected[ordinal]['rgb_sha256']==digest
            found=segments(bgr)
            lengths=np.linalg.norm(found[:,:2]-found[:,2:],axis=1)
            score=float(lengths.max()) if len(lengths) else 0.
            rows.append(dict(ordinal=ordinal,rgb_sha256=digest,segments=found.tolist(),max_length=score))
            slot=min(7,ordinal*8//1041)
            if slot not in chosen or score>chosen[slot][0]:
                display=Image.fromarray(rgb);draw=ImageDraw.Draw(display)
                for xy in found:draw.line(tuple(map(int,xy)),fill='orange',width=3)
                draw.rectangle((43,192,676,1279),outline='cyan',width=2)
                display.thumbnail((180,320));chosen[slot]=(score,ordinal,display)
    finally:capture.release()
    assert len(rows)==1041 and sha256_file(source)==records[0]['sha256']
    sheet=Image.new('RGB',(720,688),'#171d25');draw=ImageDraw.Draw(sheet)
    for slot,(score,ordinal,im) in chosen.items():
        x,y=slot%4*180,slot//4*344
        sheet.paste(im,(x,y+23));draw.text((x+2,y+3),f'{ordinal} / max {score:.1f}px',fill='white')
    sheet.save(OUT/'candidates.jpg',quality=90)
    result=dict(status='TECHNICAL_CHECK_PASSED',scope='fixed-band line census only',frames=1041,
        frames_with_segments=sum(bool(row['segments']) for row in rows),segments=sum(len(row['segments']) for row in rows),
        selected_ordinals=[item[1] for item in chosen.values()],source_sha256=records[0]['sha256'],
        sheet_sha256=sha256_file(OUT/'candidates.jpg'),all1041hashes_match=True,seconds=time.monotonic()-start,
        camera_calibration='UNVERIFIED',actual_head_or_medical_accuracy='UNVERIFIED',training=False,upload=False,scans_read=False,case002_content_read=False)
    (OUT/'frames.json').write_text(json.dumps(rows))
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:worker()
    else:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
        result=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',120,2*1024**3)
        print(json.dumps(result))
