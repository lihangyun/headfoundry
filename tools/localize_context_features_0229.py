"""Frozen3D versus independently-contextualized real pixels, without new matching."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image,ImageDraw
import pycolmap

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file
from direct_video_matches_0224 import PILOT,BASE,verify_inputs
from localize_direct_features_0225 import OUT as PARENT,SOURCE
from context_rectification_0228 import refine_context_rectified
from localize_reserved_frames_0222 import estimate_reserved_pose
from audit_reserved_localization_0222 import epipolar_validation

OUT=PILOT/'context-localization-0229'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first real context-localization screen')
    started=time.perf_counter()
    verify_inputs()
    pilot=json.loads((PILOT/'report.json').read_text(encoding='utf-8'))
    case=next(c for c in pilot['cases'] if c['id']=='real-case-001')
    parent=json.loads((PARENT/'controls.json').read_text(encoding='utf-8'))
    if any(sha256_file(SOURCE/p)!=h for p,h in parent['model_files_sha256'].items()):
        raise ValueError('Frozen reference model changed')
    synthetic=json.loads((PILOT/'context-precision-0228/report.json').read_text(encoding='utf-8'))
    fixed=json.loads((PILOT/'context-precision-0228/controls.json').read_text(encoding='utf-8'))
    if synthetic['screen_status']!='TECHNICAL_CHECK_PASSED' or fixed['refiner_sha256']!=sha256_file(ROOT/'tools/context_rectification_0228.py'):
        raise ValueError('Exact synthetic-passed measurement implementation required')
    if fixed['tracking_helper_sha256']!=sha256_file(ROOT/'tools/temporal_video_sfm_0220.py'):
        raise ValueError('Tracking helper changed after controlled precision check')
    model=pycolmap.Reconstruction(SOURCE/'sparse/0')
    cloud=np.array([p.xyz for p in model.points3D.values()])
    OUT.mkdir()
    controls={'tool_sha256':sha256_file(Path(__file__)),'refiner_sha256':fixed['refiner_sha256'],
        'tracking_helper_sha256':fixed['tracking_helper_sha256'],'model_files_sha256':parent['model_files_sha256'],
        'parent_controls_sha256':sha256_file(PARENT/'controls.json'),'source_target_pairs':[[612,624],[0,1040]],
        'context_rule':'untriangulated source feature IDs only; exclude all pose/validation and aliases',
        'camera_rule':'fixed3D/K; original even/odd point-ID pose/validation split'}
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    cv2.setNumThreads(4)
    results=[]
    sheet=Image.new('RGB',(720,690),(28,28,28))
    for column,(source_frame,target_frame) in enumerate(controls['source_target_pairs']):
        original_path=PARENT/f'frame-{target_frame:06d}-observations.npz'
        saved=np.load(original_path,allow_pickle=False)
        image=model.find_image_with_name(f'frame-{source_frame:06d}.png')
        features=np.load(SOURCE/f'image-{image.image_id:03d}-features.npz',allow_pickle=False)
        source_pixels=features['keypoints'][features['mask_selected']]
        target_pixels=saved['target_keypoints'][saved['target_mask_selected']]
        if not np.allclose(np.array([p.xy for p in image.points2D]),source_pixels+.5,atol=1e-5,rtol=0):
            raise ValueError('Source feature index coordinates changed')
        matches=saved['all_feature_matches']
        context=np.ones(len(matches),bool)
        context[saved['triangulated_match_rows']]=False
        measured_matches=matches[saved['triangulated_match_rows']][saved['unambiguous_triangulated_rows']]
        if any(image.points2D[int(a)].has_point3D() for a,_ in matches[context]):
            raise ValueError('Triangulated identity leaked into context')
        if np.intersect1d(matches[context,0],measured_matches[:,0]).size:
            raise ValueError('Context/measurement feature populations overlap')
        ids=np.array([image.points2D[int(a)].point3D_id for a,_ in measured_matches],np.int64)
        if not np.array_equal(ids,saved['point_ids']) or not np.allclose(target_pixels[measured_matches[:,1]]+.5,saved['pixels'],atol=1e-5,rtol=0):
            raise ValueError('Exact target/point identity join failed')
        photo_item=next(r for r in case['video']['frames'] if r['frame']==target_frame)
        path=PILOT/case['id']/photo_item['path']
        if sha256_file(path)!=photo_item['sha256']:
            raise ValueError('Frozen target image changed')
        source_image=cv2.imread(str(BASE/'images'/f'frame-{source_frame:06d}.png'))
        target_image=cv2.imread(str(path))
        source_points=source_pixels[measured_matches[:,0]]
        measured=refine_context_rectified(cv2.cvtColor(source_image,cv2.COLOR_BGR2GRAY),cv2.cvtColor(target_image,cv2.COLOR_BGR2GRAY),
            source_pixels[matches[context,0]],target_pixels[matches[context,1]],source_points,saved['pixels']-.5)
        eligible=measured['eligible']
        intrinsic=saved['intrinsic']
        pose,predicted,score=estimate_reserved_pose(saved['vertices'][eligible],measured['pixels'][eligible]+.5,ids[eligible],intrinsic,cloud)
        rigidity=epipolar_validation(source_points[eligible]+.5,measured['pixels'][eligible]+.5,ids[eligible],intrinsic)
        score.update(source_frame=source_frame,target_frame=target_frame,raw_unique_measurements=len(ids),
            context_pairs=int(context.sum()),retained_measurements=int(eligible.sum()),
            context=measured.get('context'),context_failure=measured.get('context_failure'),
            pixel_rigidity=rigidity,observations_sha256=sha256_file(original_path),target_image_sha256=photo_item['sha256'])
        results.append(score)
        np.savez_compressed(OUT/f'frame-{target_frame:06d}-observations.npz',
            **{k:v for k,v in measured.items() if k not in ('context','context_failure')},
            original_point_ids=ids,vertices=saved['vertices'],source_points=source_points,
            context_match_rows=np.flatnonzero(context),measurement_feature_pairs=measured_matches,
            **({'extrinsic':pose} if pose is not None else {}))
        photo=Image.open(path).convert('RGB')
        draw=ImageDraw.Draw(photo)
        for row,(x,y) in enumerate(measured['pixels'][eligible]):
            draw.ellipse((x-2,y-2,x+2,y+2),fill=(255,190,20) if ids[eligible][row]%2==0 else (20,255,80))
            if predicted is not None:
                draw.line([(x,y),tuple(predicted[row]-.5)],fill=(255,50,50))
        photo.save(OUT/f'frame-{target_frame:06d}-validation.png')
        photo.thumbnail((360,640))
        sheet.paste(photo,(360*column,35))
        ImageDraw.Draw(sheet).text((360*column+5,8),f'{target_frame}: {score["status"]}',fill='white')
        if time.perf_counter()-started>30:
            raise TimeoutError('One real refinement/localization budget exhausted')
    sheet.save(OUT/'context-sentinel-review.png')
    unchanged=all(sha256_file(SOURCE/p)==h for p,h in parent['model_files_sha256'].items())
    if not unchanged:
        raise ValueError('Frozen model changed during localization')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in results) else 'REJECT','model_unchanged':unchanged,
        'results':results,'elapsed_seconds':time.perf_counter()-started,
        'limits':'Already seen real development sentinels, not fresh holdout/anatomical/scan/head acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'results':[{k:v for k,v in r.items() if k not in ('errors_px','pixel_rigidity')} for r in results]}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
