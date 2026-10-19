"""Same frozen known3D images/coarse points, two predeclared native recipes."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file
from direct_video_matches_0224 import PILOT,verify_inputs
from temporal_video_sfm_0220 import refine_step
from nonplanar_refinement_0233 import refine_nonplanar
from check_nonplanar_images_0233 import stats

PARENT=PILOT/'nonplanar-image-precision-0233'
SOURCE=PILOT/'scan-pattern-observations-0232'
OUT=PILOT/'native-observation-precision-0234'


def passes(error,eligible):
    return bool(eligible.sum()>=30 and eligible.mean()>=.5 and np.percentile(error[eligible],95)<=1.)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first native observation comparison')
    started=time.perf_counter()
    verify_inputs()
    parent=json.loads((PARENT/'controls.json').read_text(encoding='utf-8'))
    for name,key in (('temporal_video_sfm_0220.py','tracker_sha256'),('nonplanar_refinement_0233.py','refiner_sha256')):
        if sha256_file(PARENT/('executed-'+name))!=parent[key]:
            raise ValueError('Exact previous failed producer capsule missing')
    if sha256_file(SOURCE/'generation-report.json')!=parent['source_generation_sha256'] or sha256_file(SOURCE/'known-motion.npz')!=parent['known_geometry_sha256']:
        raise ValueError('Frozen geometry/images changed')
    if sha256_file(PARENT/'simulated-coarse-noise.npz')!=parent['noise_sha256']:
        raise ValueError('Coarse-noise input changed')
    if sha256_file(ROOT/'tools/nonplanar_context_0231.py')!=parent['context_helper_sha256']:
        raise ValueError('Context estimator changed')
    known=np.load(SOURCE/'known-motion.npz',allow_pickle=False)
    noise=np.load(PARENT/'simulated-coarse-noise.npz',allow_pickle=False)['target_noise']
    generation=json.loads((SOURCE/'generation-report.json').read_text(encoding='utf-8'))
    images,grays=[],[]
    for record in generation['renders']:
        path=SOURCE/record['image']
        if sha256_file(path)!=record['image_sha256']:
            raise ValueError('Original render changed')
        image=np.array(Image.open(path).convert('RGB'))
        images.append(image)
        grays.append(cv2.cvtColor(image,cv2.COLOR_RGB2GRAY))
    cv2.setNumThreads(4)
    OUT.mkdir()
    controls={'parent_controls_sha256':sha256_file(PARENT/'controls.json'),'tool_sha256':sha256_file(Path(__file__)),
        'local_refiner_sha256':sha256_file(ROOT/'tools/temporal_video_sfm_0220.py'),
        'F_wrapper_sha256':sha256_file(ROOT/'tools/nonplanar_refinement_0233.py'),
        'primary_variable':'native seeded precision, not repeated large-motion search',
        'next_gate_priority':'direct native only if all5 pass; else F-native only if all5 pass; no per-view fallback',
        'input_archives':{str(name):sha256_file(PARENT/(str(name)+'.npz')) for name in known['view_names'][1:]}}
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    records=[]
    sheet=Image.new('RGB',(900,1780),(28,28,28))
    ImageDraw.Draw(sheet).text((10,5),'SAME PATTERNED SUPPLIED SCAN / LOCAL OBSERVATION TEST / NOT RECONSTRUCTION',fill='white')
    for view,name in enumerate(known['view_names'][1:],start=1):
        saved=np.load(PARENT/(str(name)+'.npz'),allow_pickle=False)
        context=saved['context_population']
        source,initial=saved['source_points'],saved['coarse']
        direct,direct_keep,direct_fb,direct_patch=refine_step(grays[0],grays[view],source,initial)
        result=refine_nonplanar(grays[0],grays[view],known['pixels'][0,context]-.5,
            known['pixels'][view,context]-.5+noise[view,context],source,initial,refiner=refine_step)
        for key in ('fundamental','source_rectification','target_rectification','appearance_transfer'):
            if key not in result or not np.array_equal(result[key],saved[key]):
                raise ValueError('Non-refinement geometry changed during controlled comparison')
        truth=saved['truth']
        direct_error=np.linalg.norm(direct-truth,axis=1)
        error=np.linalg.norm(result['pixels']-truth,axis=1)
        keep=result['eligible']
        paired=keep&saved['eligible']
        direct_pass,F_pass=passes(direct_error,direct_keep),passes(error,keep)
        record={'view':str(name),'measurements':len(source),'direct_native_status':'TECHNICAL_CHECK_PASSED' if direct_pass else 'REJECT',
            'F_native_status':'TECHNICAL_CHECK_PASSED' if F_pass else 'REJECT','direct_native':stats(direct_error[direct_keep]),
            'F_native':stats(error[keep]),'direct_fraction':float(direct_keep.mean()),'F_fraction':float(keep.mean()),
            'old_F_same_eligible_ids':stats(saved['candidate_errors'][paired]),'native_F_same_eligible_ids':stats(error[paired]),
            'F_geometry_exactly_unchanged':True,'refinement_failure':result.get('refinement_failure')}
        records.append(record)
        np.savez_compressed(OUT/(str(name)+'.npz'),**{k:v for k,v in result.items() if k not in ('context','refinement_failure')},
            direct_pixels=direct,direct_eligible=direct_keep,direct_fb_error=direct_fb,direct_patch_error=direct_patch,
            direct_errors=direct_error,F_errors=error,measurement_ids=saved['measurement_ids'],paired_old=paired)
        for column,(endpoints,eligible,label) in enumerate(((saved['pixels'],saved['eligible'],'OLD F+SEARCH'),(result['pixels'],keep,'F+NATIVE'))):
            photo=Image.fromarray(images[view])
            draw=ImageDraw.Draw(photo)
            for xy,expected in zip(endpoints[eligible],truth[eligible]):
                x,y=xy
                draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),fill=(20,255,80))
                draw.line([tuple(xy),tuple(expected)],fill=(255,60,50))
            panel=photo.crop((100,490,620,850)).resize((450,315))
            x,y=column*450,(view-1)*350+40
            sheet.paste(panel,(x,y+20))
            ImageDraw.Draw(sheet).text((x+5,y),str(name)+' / '+label+' / n='+str(int(eligible.sum())),fill='white')
        print(json.dumps(record),flush=True)
        if time.perf_counter()-started>180:
            raise TimeoutError('One native observation comparison budget exhausted')
    sheet.save(OUT/'native-vs-search-review.png')
    direct_all=all(r['direct_native_status']=='TECHNICAL_CHECK_PASSED' for r in records)
    F_all=all(r['F_native_status']=='TECHNICAL_CHECK_PASSED' for r in records)
    selected='direct_native' if direct_all else 'F_native' if F_all else None
    report={'execution_status':'TECHNICAL_CHECK_PASSED','direct_native_all5':direct_all,'F_native_all5':F_all,
        'selected_for_next_gate':selected,'screen_status':'TECHNICAL_CHECK_PASSED' if selected else 'REJECT',
        'results':records,'elapsed_seconds':time.perf_counter()-started,
        'limits':'Controlled synthetic nonplanar observations only. Named whole-recipe selection, no per-view fallback or real head/camera acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'selected_for_next_gate':selected}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
