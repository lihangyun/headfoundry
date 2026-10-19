"""Controlled nonplanar pixel observations; no training or recovered subject head."""
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
from temporal_video_sfm_0220 import track_step
from nonplanar_refinement_0233 import refine_nonplanar

SOURCE=PILOT/'scan-pattern-observations-0232'
OUT=PILOT/'nonplanar-image-precision-0233'


def opaque_interior(pixels,alpha):
    pixels=np.asarray(pixels,float)
    alpha=np.asarray(alpha)
    if pixels.ndim!=2 or pixels.shape[1:]!=(2,) or alpha.ndim!=2 or alpha.dtype!=np.uint8 or not np.isfinite(pixels).all():
        raise ValueError('Finite pixel positions and uint8 alpha required')
    mask=cv2.erode((alpha==255).astype(np.uint8),np.ones((23,23),np.uint8),iterations=1)
    xy=np.rint(pixels).astype(int)
    inside=((xy>=0)&(xy<[alpha.shape[1],alpha.shape[0]])).all(axis=1)
    result=np.zeros(len(pixels),bool)
    result[inside]=mask[xy[inside,1],xy[inside,0]]>0
    return result


def stats(error):
    return {'count':len(error),'p50_px':float(np.median(error)) if len(error) else None,
        'p95_px':float(np.percentile(error,95)) if len(error) else None,'max_px':float(error.max()) if len(error) else None}


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first nonplanar image precision screen')
    started=time.perf_counter()
    verify_inputs()
    generation=json.loads((SOURCE/'generation-report.json').read_text(encoding='utf-8'))
    if generation['execution_status']!='TECHNICAL_CHECK_PASSED' or generation.get('all_geometry_fields_exactly_equal') is not True:
        raise ValueError('Successful fixed-geometry patterned reference required')
    if sha256_file(SOURCE/'known-motion.npz')!=generation['archive_sha256']:
        raise ValueError('Known geometry changed')
    known=np.load(SOURCE/'known-motion.npz',allow_pickle=False)
    truth_cv=known['pixels']-.5
    images,grays,interiors=[],[],[]
    for view,entry in enumerate(generation['renders']):
        path=SOURCE/entry['image']
        if entry['view']!=str(known['view_names'][view]) or sha256_file(path)!=entry['image_sha256']:
            raise ValueError('Known source image identity changed')
        image=np.array(Image.open(path).convert('RGBA'))
        images.append(image)
        grays.append(cv2.cvtColor(image[:,:,:3],cv2.COLOR_RGB2GRAY))
        interiors.append(opaque_interior(truth_cv[view],image[:,:,3]))
    cv2.setNumThreads(4)
    noise=np.random.default_rng(233).normal(0,1.5,truth_cv.shape)
    OUT.mkdir()
    np.savez_compressed(OUT/'simulated-coarse-noise.npz',target_noise=noise)
    controls={'source_generation_sha256':sha256_file(SOURCE/'generation-report.json'),
        'known_geometry_sha256':generation['archive_sha256'],'tool_sha256':sha256_file(Path(__file__)),
        'refiner_sha256':sha256_file(ROOT/'tools/nonplanar_refinement_0233.py'),
        'context_helper_sha256':sha256_file(ROOT/'tools/nonplanar_context_0231.py'),
        'tracker_sha256':sha256_file(ROOT/'tools/temporal_video_sfm_0220.py'),
        'noise_sha256':sha256_file(OUT/'simulated-coarse-noise.npz'),'noise_sigma_px':1.5,'seed':233,
        'pixel_convention':'known camera/projector pixel centers0.5; OpenCV coordinates=pixels-0.5',
        'partition':'global sample ID mod3==0 context, others measurement; no overlap',
        'population':'common visible, fixed image box in both views, opaque alpha eroded11px in both',
        'opencv_version':cv2.__version__,'numpy_version':np.__version__}
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    rows=[]
    sheet=Image.new('RGB',(900,1780),(28,28,28))
    ImageDraw.Draw(sheet).text((10,5),'PATTERNED SUPPLIED SCAN / OBSERVATION TEST ONLY / NOT RECONSTRUCTION',fill='white')
    for view in range(1,len(truth_cv)):
        common=known['visible'][0]&known['visible'][view]
        box=((known['pixels']>=np.array([100,500]))&(known['pixels']<np.array([620,820]))).all(axis=2)
        boxed=common&box[0]&box[view]
        population=boxed&interiors[0]&interiors[view]
        context=population&(known['point_ids']%3==0)
        measurement=population&~context
        if context.sum()<12 or measurement.sum()<30:
            raise ValueError('Predeclared nonplanar sample population missing')
        if np.intersect1d(known['point_ids'][context],known['point_ids'][measurement]).size:
            raise ValueError('Context/measurement identity leak')
        source_points=truth_cv[0,measurement]
        coarse=truth_cv[view,measurement]+noise[view,measurement]
        direct,direct_keep,direct_fb,direct_patch=track_step(grays[0],grays[view],source_points,initial=coarse)
        candidate=refine_nonplanar(grays[0],grays[view],truth_cv[0,context],truth_cv[view,context]+noise[view,context],source_points,coarse)
        # The refiner above never receives the exact target measurement truth.
        expected=truth_cv[view,measurement]
        raw_error=np.linalg.norm(coarse-expected,axis=1)
        direct_error=np.linalg.norm(direct-expected,axis=1)
        candidate_error=np.linalg.norm(candidate['pixels']-expected,axis=1)
        kept=candidate['eligible']
        paired=kept&direct_keep
        passed=kept.sum()>=30 and kept.mean()>=.5 and np.percentile(candidate_error[kept],95)<=1.
        row={'view':str(known['view_names'][view]),'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
            'common_visible':int(common.sum()),'fixed_box':int(boxed.sum()),'interior_population':int(population.sum()),
            'context_points':int(context.sum()),'measurement_points':int(measurement.sum()),
            'raw_all':stats(raw_error),'direct_eligible':stats(direct_error[direct_keep]),
            'candidate_eligible':stats(candidate_error[kept]),'candidate_fraction':float(kept.mean()),
            'raw_same_candidate_ids':stats(raw_error[kept]),'direct_paired':stats(direct_error[paired]),
            'candidate_paired':stats(candidate_error[paired]),'context':candidate.get('context'),
            'refinement_failure':candidate.get('refinement_failure')}
        rows.append(row)
        np.savez_compressed(OUT/(row['view']+'.npz'),**{k:v for k,v in candidate.items() if k not in ('context','refinement_failure')},
            common_visible=common,fixed_box_population=boxed,interior_population=population,
            context_population=context,measurement_population=measurement,measurement_ids=known['point_ids'][measurement],
            source_points=source_points,coarse=coarse,truth=expected,raw_errors=raw_error,
            direct_pixels=direct,direct_eligible=direct_keep,direct_fb_error=direct_fb,direct_patch_error=direct_patch,
            direct_errors=direct_error,candidate_errors=candidate_error,paired=paired)
        for column,(endpoints,eligible,label) in enumerate(((direct,direct_keep,'DIRECT LK'),(candidate['pixels'],kept,'F CONTEXT + FREE LK'))):
            photo=Image.fromarray(images[view][:,:,:3])
            draw=ImageDraw.Draw(photo)
            for xy,actual in zip(endpoints[eligible],expected[eligible]):
                x,y=xy
                draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),fill=(20,255,80))
                draw.line([tuple(xy),tuple(actual)],fill=(255,60,50))
            panel=photo.crop((100,490,620,850)).resize((450,315))
            x,y=column*450,(view-1)*350+40
            sheet.paste(panel,(x,y+20))
            summary=row['direct_eligible' if column==0 else 'candidate_eligible']
            ImageDraw.Draw(sheet).text((x+5,y),f'{row["view"]} {label}: n={summary["count"]}, p95={summary["p95_px"]}',fill='white')
        print(json.dumps(row),flush=True)
        if time.perf_counter()-started>180:
            raise TimeoutError('Single nonplanar observation budget exhausted')
    sheet.save(OUT/'nonplanar-observation-review.png')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in rows) else 'REJECT','results':rows,
        'elapsed_seconds':time.perf_counter()-started,
        'limits':'Synthetic patterned nonplanar interior points with simulated coarse errors; not raw learned-match, real skin, camera/head/scan-error acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'cases':len(rows)}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
