"""Point-disjoint known-transform context screen; no new model/camera inference."""
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
from context_rectification_0228 import refine_context_rectified

OUT=PILOT/'context-precision-0228'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first context precision screen')
    started=time.perf_counter()
    verify_inputs()
    cv2.setNumThreads(4)
    parent=json.loads((PARENT/'report.json').read_text(encoding='utf-8'))
    controls={'parent_report_sha256':sha256_file(PARENT/'report.json'),'tool_sha256':sha256_file(Path(__file__)),
        'refiner_sha256':sha256_file(ROOT/'tools/context_rectification_0228.py'),
        'tracking_helper_sha256':sha256_file(ROOT/'tools/temporal_video_sfm_0220.py'),
        'partition':'source feature index mod3==0 context, others measurement',
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
            raise ValueError('Original source changed')
        source=np.array(Image.open(source_path).convert('RGB'))
        target=np.array(Image.open(PARENT/(prefix+'.png')).convert('RGB'))
        if not np.array_equal(target,cv2.warpPerspective(source,saved['homography'],(720,1280),flags=cv2.INTER_LINEAR)):
            raise ValueError('Exact known target regeneration failed')
        context=saved['matches'][:,0]%3==0
        measured=~context
        if np.intersect1d(saved['matches'][context,0],saved['matches'][measured,0]).size:
            raise ValueError('Context identity leaked into measurement population')
        result=refine_context_rectified(cv2.cvtColor(source,cv2.COLOR_RGB2GRAY),cv2.cvtColor(target,cv2.COLOR_RGB2GRAY),
            saved['source'][context],saved['raw'][context],saved['source'][measured],saved['raw'][measured])
        score,truth,raw_error,errors=evaluate_pixels(saved['source'][measured],saved['raw'][measured],result['pixels'],result['eligible'],saved['homography'])
        common=saved['eligible'][measured]&result['eligible']
        score.update(frame=frame,transform=name,context=result.get('context'),context_failure=result.get('context_failure'),
            context_count=int(context.sum()),measurement_count=int(measured.sum()),paired_translation_count=int(common.sum()),
            translation_p95_same_eligible_ids_px=float(np.percentile(saved['refined_error'][measured][common],95)) if common.any() else None,
            context_p95_same_eligible_ids_px=float(np.percentile(errors[common],95)) if common.any() else None)
        records.append(score)
        np.savez_compressed(OUT/(prefix+'.npz'),**{k:v for k,v in result.items() if k not in ('context','context_failure')},
            context_partition=context,measurement_partition=measured,source_feature_indices=saved['matches'][:,0],
            truth=truth,raw_error=raw_error,refined_error=errors)
        print(json.dumps(score),flush=True)
        if time.perf_counter()-started>180:
            raise TimeoutError('Single independent-context precision budget exhausted')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT','results':records,
        'elapsed_seconds':time.perf_counter()-started,'limits':'Known2D warps only; measured points excluded from warp fit. No camera/head acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'cases':len(records)}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
