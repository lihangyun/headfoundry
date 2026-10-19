"""Known2D truth screen, not a head reconstruction or training pipeline."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

from headfoundry.manifest import sha256_file
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from direct_video_matches_0224 import PILOT, BASE, UPSTREAM, verify_inputs
from extract_xfeat import load_lighterglue
from temporal_video_sfm_0220 import track_step

OUT = PILOT / 'pixel-precision-0226'


def evaluate_pixels(source, raw, refined, eligible, homography):
    source,raw,refined = [np.asarray(x,float) for x in (source,raw,refined)]
    eligible,homography = np.asarray(eligible),np.asarray(homography,float)
    if (source.ndim!=2 or source.shape[1:]!=(2,) or raw.shape!=source.shape or refined.shape!=source.shape
            or eligible.shape!=(len(source),) or eligible.dtype!=bool or homography.shape!=(3,3)
            or not all(np.isfinite(x).all() for x in (source,raw,refined[eligible],homography))):
        raise ValueError('Matching finite endpoints, eligibility and known homography required')
    homogeneous=np.c_[source,np.ones(len(source))]@homography.T
    if np.any(abs(homogeneous[:,2])<1e-12):
        raise ValueError('Known transform sends measured source points to infinity')
    truth=homogeneous[:,:2]/homogeneous[:,2:]
    raw_errors=np.linalg.norm(raw-truth,axis=1)
    refined_errors=np.linalg.norm(refined-truth,axis=1)
    def stats(errors):
        return {'count':len(errors),'p50_px':float(np.median(errors)) if len(errors) else None,
                'p95_px':float(np.percentile(errors,95)) if len(errors) else None,
                'max_px':float(errors.max()) if len(errors) else None}
    gate=len(source)>0 and eligible.sum()>=30 and eligible.mean()>=.5 and np.percentile(refined_errors[eligible],95)<=1.
    return {'status':'TECHNICAL_CHECK_PASSED' if gate else 'REJECT',
            'baseline_all':stats(raw_errors),'baseline_same_eligible_ids':stats(raw_errors[eligible]),
            'candidate_eligible':stats(refined_errors[eligible]),'eligible_fraction':float(eligible.mean()) if len(source) else 0.},truth,raw_errors,refined_errors


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first precision screen')
    started=time.perf_counter()
    base,asset=verify_inputs()
    import torch
    torch.set_num_threads(4)
    torch.manual_seed(219)
    cv2.setNumThreads(4)
    matcher,matcher_lock=load_lighterglue(UPSTREAM)
    sys.path.insert(0,str(UPSTREAM))
    from modules.xfeat import XFeat
    extractor=XFeat(weights=torch.load(UPSTREAM/'weights/xfeat.pt',map_location='cpu',weights_only=True),top_k=4096)
    affine=np.eye(3)
    affine[:2]=cv2.getRotationMatrix2D((360,640),3,.97)
    affine[:2,2]+=[4.2,-3.1]
    transforms={'identity':np.eye(3),'translation':np.array([[1.,0,2.3],[0,1,-1.7],[0,0,1]]),
                'affine':affine,'projective':np.array([[1.,.015,0],[-.01,1,0],[.00008,-.00006,1]])}
    controls={'manifest_sha256':sha256_file(PILOT/'manifest.json'),'source_controls_sha256':sha256_file(BASE/'controls.json'),
        'feature_asset':asset,'matcher_asset':matcher_lock,'frames':[0,144,408,612],
        'transforms':{k:v.tolist() for k,v in transforms.items()},'tool_sha256':sha256_file(Path(__file__)),
        'tracking_helper_sha256':sha256_file(ROOT/'tools/temporal_video_sfm_0220.py'),
        'baseline':'all descriptor matches; no pose/truth filter','candidate':'descriptor-seeded forward/backward LK; unchanged eligibility',
        'limits':'Local synthetic2D validation only. No images uploaded or model trained.'}
    OUT.mkdir()
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    def extract(pixels,mask):
        result=extractor.detectAndCompute(extractor.parse_input(pixels))[0]
        xy=np.rint(result['keypoints'].cpu().numpy()).astype(int)
        inside=((xy>=0)&(xy<[720,1280])).all(axis=1)
        keep=np.zeros(len(xy),bool)
        keep[inside]=mask[xy[inside,1],xy[inside,0]]>0
        selected=torch.from_numpy(keep)
        return {'keypoints':result['keypoints'][selected][None],
                'descriptors':result['descriptors'][selected][None],
                'image_size':torch.tensor([[720,1280]],dtype=torch.float32)}
    records=[]
    sheet=Image.new('RGB',(1000,1440),(28,28,28))
    with torch.inference_mode():
        for row,frame in enumerate(controls['frames']):
            item=next(r for r in base['frames'] if r['frame']==frame)
            pixels=np.array(Image.open(BASE/'images'/item['name']).convert('RGB'))
            mask=np.asarray(Image.open(BASE/'masks'/(item['name']+'.png')))
            source=extract(pixels,mask)
            source_points=source['keypoints'][0].cpu().numpy()
            gray=cv2.cvtColor(pixels,cv2.COLOR_RGB2GRAY)
            for name,homography in transforms.items():
                target_pixels=cv2.warpPerspective(pixels,homography,(720,1280),flags=cv2.INTER_LINEAR)
                target_mask=cv2.warpPerspective(mask,homography,(720,1280),flags=cv2.INTER_NEAREST)
                target=extract(target_pixels,target_mask)
                matches=matcher({'image0':source,'image1':target})['matches'][0].cpu().numpy()
                original=source_points[matches[:,0]]
                raw=target['keypoints'][0].cpu().numpy()[matches[:,1]]
                target_gray=cv2.cvtColor(target_pixels,cv2.COLOR_RGB2GRAY)
                refined,eligible,fb,patch=track_step(gray,target_gray,original,initial=raw)
                # Known truth is consulted only here, after eligibility is frozen.
                score,truth,raw_error,refined_error=evaluate_pixels(original,raw,refined,eligible,homography)
                score.update(frame=frame,transform=name,source_features=len(source_points),
                    target_features=target['keypoints'].shape[1],source_image_sha256=item['image_sha256'],
                    source_mask_sha256=item['mask_sha256'])
                records.append(score)
                prefix=f'frame-{frame:06d}-{name}'
                np.savez_compressed(OUT/(prefix+'.npz'),source=original,raw=raw,refined=refined,eligible=eligible,
                    fb_error=fb,patch_error=patch,matches=matches,truth=truth,raw_error=raw_error,refined_error=refined_error,homography=homography)
                Image.fromarray(target_pixels).save(OUT/(prefix+'.png'))
                if name=='projective':
                    for column,(endpoints,selected,label) in enumerate(((raw,np.ones(len(raw),bool),'raw'),(refined,eligible,'seeded LK'))):
                        photo=Image.fromarray(target_pixels)
                        draw=ImageDraw.Draw(photo)
                        for xy,expected in zip(endpoints[selected],truth[selected]):
                            x,y=xy
                            draw.line([tuple(xy),tuple(expected)],fill=(255,50,50),width=2)
                            draw.ellipse((x-2,y-2,x+2,y+2),fill=(20,255,80))
                        panel=photo.crop((100,490,620,850)).resize((500,335))
                        sheet.paste(panel,(500*column,360*row+25))
                        p95=score['baseline_all' if column==0 else 'candidate_eligible']['p95_px']
                        ImageDraw.Draw(sheet).text((500*column+5,360*row+5),f'{frame} projective {label}: {selected.sum()} pts; p95={p95:.3f}px' if p95 is not None else 'No eligible points',fill='white')
                print(json.dumps(score),flush=True)
                if time.perf_counter()-started>180:
                    raise TimeoutError('Single precision measurement budget exhausted')
    sheet.save(OUT/'projective-pixel-review.png')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT','results':records,
        'elapsed_seconds':time.perf_counter()-started,'controls_sha256':sha256_file(OUT/'controls.json'),
        'limits':'Known2D warps only; no real3D/camera/head/scan or subject-generalization acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'cases':len(records)}),flush=True)


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
