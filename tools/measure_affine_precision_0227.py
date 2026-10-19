"""One affine-patch screen on frozen known-transform matches, not a camera fit."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file
from measure_pixel_precision_0226 import BASE, OUT as PARENT, evaluate_pixels
from direct_video_matches_0224 import PILOT, verify_inputs
from affine_patch_0227 import refine_affine_patches

OUT=PILOT/'affine-precision-0227'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first affine precision screen')
    started=time.perf_counter()
    verify_inputs()
    cv2.setNumThreads(4)
    parent=json.loads((PARENT/'report.json').read_text(encoding='utf-8'))
    controls={'parent_report_sha256':sha256_file(PARENT/'report.json'),'tool_sha256':sha256_file(Path(__file__)),
        'refiner_sha256':sha256_file(ROOT/'tools/affine_patch_0227.py'),'primary_variable':'local affine rather than translation-only patch model',
        'inputs':{f'frame-{r["frame"]:06d}-{r["transform"]}.npz':sha256_file(PARENT/f'frame-{r["frame"]:06d}-{r["transform"]}.npz') for r in parent['results']}}
    OUT.mkdir()
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    records=[]
    for record in parent['results']:
        frame,name=record['frame'],record['transform']
        prefix=f'frame-{frame:06d}-{name}'
        saved=np.load(PARENT/(prefix+'.npz'),allow_pickle=False)
        source_path=BASE/'images'/f'frame-{frame:06d}.png'
        if sha256_file(source_path)!=record['source_image_sha256']:
            raise ValueError('Source image changed')
        source=np.array(Image.open(source_path).convert('RGB'))
        target=np.array(Image.open(PARENT/(prefix+'.png')).convert('RGB'))
        if not np.array_equal(target,cv2.warpPerspective(source,saved['homography'],(720,1280),flags=cv2.INTER_LINEAR)):
            raise ValueError('Exact known target regeneration failed')
        result=refine_affine_patches(cv2.cvtColor(source,cv2.COLOR_RGB2GRAY),cv2.cvtColor(target,cv2.COLOR_RGB2GRAY),saved['source'],saved['raw'])
        score,truth,raw_error,errors=evaluate_pixels(saved['source'],saved['raw'],result['pixels'],result['eligible'],saved['homography'])
        score.update(frame=frame,transform=name,failure_counts={str(code):int((result['failure_codes']==code).sum()) for code in range(5)})
        records.append(score)
        np.savez_compressed(OUT/(prefix+'.npz'),**result,truth=truth,raw_error=raw_error,refined_error=errors)
        print(json.dumps(score),flush=True)
        if time.perf_counter()-started>180:
            raise TimeoutError('Single affine precision budget exhausted')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT','results':records,
        'elapsed_seconds':time.perf_counter()-started,'limits':'Known2D image warps only, not accepted cameras/anatomy/heads.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'cases':len(records)}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
