"""Known3D motion-model capacity, not a new reconstruction or camera fit."""
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
from headfoundry.epipolar import sampson_distance
from scan_motion_truth_0230 import fundamental_from_cameras

OUT=ROOT/'assets/private/real-capture-pilot-v1/scan-motion-truth-0230-upright'


def main():
    destination=OUT/'analysis-report.json'
    if destination.exists():
        raise FileExistsError('Preserve first known3D motion analysis')
    started=time.perf_counter()
    generation=json.loads((OUT/'generation-report.json').read_text(encoding='utf-8'))
    archive=OUT/'known-motion.npz'
    if generation['execution_status']!='TECHNICAL_CHECK_PASSED' or sha256_file(archive)!=generation['archive_sha256']:
        raise ValueError('Exact successful source generation required')
    data=np.load(archive,allow_pickle=False)
    points,ids=data['pixels'],data['point_ids']
    visible=data['visible']
    k,extrinsics=data['intrinsic'],data['extrinsics_normalized']
    rows=[]
    for view in range(1,len(points)):
        fundamental=fundamental_from_cameras(k,extrinsics[0],extrinsics[view])
        shared=visible[0]&visible[view]
        in_box=((points>=np.array([100,500]))&(points<np.array([620,820]))).all(axis=2)
        for scope,selected in (('all_shared_visible',shared),('fixed_roi_shared',shared&in_box[0]&in_box[view])):
            train=selected&(ids%2==0)
            validation=selected&(ids%2!=0)
            first,second=points[0,train],points[view,train]
            check_first,check_second=points[0,validation],points[view,validation]
            if selected.sum()<200 or min(train.sum(),validation.sum())<12 or (np.ptp(first,axis=0)<50).any():
                raise ValueError('Predeclared geometric sample coverage failed')
            cv2.setRNGSeed(228)
            homography,inliers=cv2.findHomography(first,second,cv2.USAC_MAGSAC,3.,maxIters=10000,confidence=.999)
            fitted_f,_=cv2.findFundamentalMat(first,second,cv2.FM_8POINT)
            if fitted_f is None or fitted_f.shape!=(3,3):
                raise ValueError('Known nonplanar8-point geometry failed')
            analytic=sampson_distance(fundamental,check_first,check_second)
            estimated=sampson_distance(fitted_f,check_first,check_second)
            if analytic.max()>1e-6 or np.percentile(estimated,95)>1e-3:
                raise ValueError('Known camera/point geometry inconsistency')
            count=0 if inliers is None else int(inliers.sum())
            record={'view':str(data['view_names'][view]),'scope':scope,'shared_points':int(selected.sum()),
                'context_points':int(train.sum()),'validation_points':int(validation.sum()),
                'homography_context_inliers':count,'homography_context_support':count/int(train.sum()),
                'coarse_context_gate_passed':count>=12 and count>=.5*int(train.sum()),
                'analytic_f_odd_sampson_max_px':float(analytic.max()),
                'fitted_f_odd_sampson_p95_px':float(np.percentile(estimated,95))}
            arrays={'context_ids':ids[train],'validation_ids':ids[validation],'fundamental_analytic':fundamental,
                'fundamental_fitted':fitted_f,'analytic_f_errors':analytic,'fitted_f_errors':estimated}
            if homography is not None:
                h=np.c_[check_first,np.ones(len(check_first))]@homography.T
                if np.any(abs(h[:,2])<1e-10):
                    raise ValueError('Fitted homography crosses known measurement horizon')
                predicted=h[:,:2]/h[:,2:]
                error=np.linalg.norm(predicted-check_second,axis=1)
                record.update(homography_odd_p95_px=float(np.percentile(error,95)),
                    homography_odd_fraction_within_3px=float(np.mean(error<=3)))
                arrays.update(homography=homography,homography_errors=error,homography_predicted=predicted)
                if scope=='fixed_roi_shared':
                    entry=generation['renders'][view]
                    path=OUT/entry['image']
                    if sha256_file(path)!=entry['image_sha256']:
                        raise ValueError('Original source render changed')
                    image=Image.open(path).convert('RGB')
                    draw=ImageDraw.Draw(image)
                    step=max(1,len(error)//80)
                    for observed,model in zip(check_second[::step],predicted[::step]):
                        x,y=observed
                        draw.ellipse((x-2,y-2,x+2,y+2),fill=(20,255,80))
                        draw.line([tuple(observed),tuple(model)],fill=(255,60,50))
                    draw.text((15,15),'SUPPLIED SCAN / TRUE CAMERA; NOT RECONSTRUCTED',fill='white')
                    image.save(OUT/f'{record["view"]}-true-points-vs-plane.png')
            rows.append(record)
            np.savez_compressed(OUT/f'{record["view"]}-{scope}-capacity.npz',**arrays)
            if time.perf_counter()-started>30:
                raise TimeoutError('Single geometric analysis budget exhausted')
    sheet=Image.new('RGB',(900,1140),(28,28,28))
    for index,entry in enumerate(generation['renders']):
        path=OUT/entry['image']
        if sha256_file(path)!=entry['image_sha256']:
            raise ValueError('Supplied-scan preview changed')
        image=Image.open(path).convert('RGB')
        image.thumbnail((300,535))
        x,y=(index%3)*300,(index//3)*570
        sheet.paste(image,(x,y+30))
        ImageDraw.Draw(sheet).text((x+5,y+5),entry['view']+' / SUPPLIED SCAN ONLY',fill='white')
    sheet.save(OUT/'source-only-known-motion-review.png')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','head_acceptance':'UNVERIFIED','results':rows,
        'generation_report_sha256':sha256_file(OUT/'generation-report.json'),'archive_sha256':sha256_file(archive),
        'analysis_tool_sha256':sha256_file(Path(__file__)),'elapsed_seconds':time.perf_counter()-started,
        'limits':'Exact declared motion of supplied scan, not real-video camera/pose or image-correspondence validation. Model-class capacity diagnostic only; no reconstructed head.'}
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
