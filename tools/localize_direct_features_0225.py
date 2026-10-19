"""Fixed-model direct-feature localization, no long-chain optical flow or fitting."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
import pycolmap

from headfoundry.manifest import sha256_file
from direct_video_matches_0224 import PILOT, BASE, UPSTREAM, OUT as SOURCE, verify_inputs
from extract_xfeat import load_lighterglue
from localize_reserved_frames_0222 import estimate_reserved_pose

FIRST = PILOT / "direct-localization-0225"
OUT = PILOT / "direct-localization-0225-unique-identities"


def unique_identity_mask(ids):
    ids=np.asarray(ids)
    if ids.ndim!=1 or not np.issubdtype(ids.dtype,np.integer):
        raise ValueError('Integer3D point IDs required')
    _,inverse,counts=np.unique(ids,return_inverse=True,return_counts=True)
    return counts[inverse]==1


def foreground_mask(pixels):
    rb = pixels[:,:,0].astype(float) - pixels[:,:,2]
    roi = np.zeros(pixels.shape[:2],np.uint8)
    roi[500:820,100:620] = rb[500:820,100:620] > 12
    count,labels,stats,_ = cv2.connectedComponentsWithStats(roi,connectivity=4)
    if count <= 1:
        raise ValueError("No conservative face interior")
    chosen = int(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))
    mask = cv2.erode((labels==chosen).astype(np.uint8)*255,np.ones((3,3),np.uint8),iterations=8)
    if np.count_nonzero(mask)<1000:
        raise ValueError("Insufficient face interior")
    return mask


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first direct localization run")
    started=time.perf_counter()
    verify_inputs()
    first_controls=json.loads((FIRST/'controls.json').read_text(encoding='utf-8'))
    if sha256_file(FIRST/'executed-runner.py')!=first_controls['tool_sha256']:
        raise ValueError('Original failed producer source required for one repaired replay')
    import torch
    torch.set_num_threads(4)
    torch.manual_seed(219)
    matcher,matcher_lock=load_lighterglue(UPSTREAM)
    sys.path.insert(0,str(UPSTREAM))
    from modules.xfeat import XFeat
    extractor=XFeat(weights=torch.load(UPSTREAM/'weights/xfeat.pt',map_location='cpu',weights_only=True),top_k=4096)
    model_paths=sorted((SOURCE/'sparse/0').glob('*.bin'))+[SOURCE/'model-0-cameras-points.npz']
    hashes={str(p.relative_to(SOURCE)):sha256_file(p) for p in model_paths}
    model=pycolmap.Reconstruction(SOURCE/'sparse/0')
    cloud=np.array([p.xyz for p in model.points3D.values()])
    intake=json.loads((PILOT/'report.json').read_text(encoding='utf-8'))
    case=next(c for c in intake['cases'] if c['id']=='real-case-001')
    OUT.mkdir()
    controls={'model_files_sha256':hashes,'manifest_sha256':sha256_file(PILOT/'manifest.json'),
        'tool_sha256':sha256_file(Path(__file__)),'matcher_asset':matcher_lock,'source_target_pairs':[[612,624],[0,1040]],
        'pose_helper_sha256':sha256_file(Path(__file__).with_name('localize_reserved_frames_0222.py')),
        'source_controls_sha256':sha256_file(SOURCE/'controls.json'),'partition':'even point3D IDs pose; odd validation'}
    controls.update(first_attempt_failure_sha256=sha256_file(FIRST/'failure.json'),
        identity_guard='Before pose/residuals, drop all rows of matched3D IDs occurring more than once; never pick a best copy')
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    results=[]
    sheet=Image.new('RGB',(720,690),(28,28,28))
    with torch.inference_mode():
        for column,(source_frame,target_frame) in enumerate(((612,624),(0,1040))):
            image=model.find_image_with_name(f'frame-{source_frame:06d}.png')
            if image is None:
                raise ValueError('Preselected source image missing from model')
            saved_path=SOURCE/f'image-{image.image_id:03d}-features.npz'
            saved=np.load(saved_path,allow_pickle=False)
            source_keypoints=saved['keypoints'][saved['mask_selected']]
            if len(image.points2D)!=len(source_keypoints) or not np.allclose(
                    np.array([p.xy for p in image.points2D]),source_keypoints+.5,atol=1e-5,rtol=0):
                raise ValueError('Descriptor-index/COLMAP pixel-center identity failed')
            source={'keypoints':torch.from_numpy(source_keypoints)[None],
                'descriptors':torch.from_numpy(saved['descriptors'][saved['mask_selected']])[None],
                'image_size':torch.tensor([[720,1280]],dtype=torch.float32)}
            item=next(r for r in case['video']['frames'] if r['frame']==target_frame)
            path=PILOT/case['id']/item['path']
            if sha256_file(path)!=item['sha256']:
                raise ValueError('Exact target image changed')
            pixels=np.array(Image.open(path).convert('RGB'))
            mask=foreground_mask(pixels)
            Image.fromarray(mask).save(OUT/f'frame-{target_frame:06d}-mask.png')
            detected=extractor.detectAndCompute(extractor.parse_input(pixels))[0]
            locations=np.rint(detected['keypoints'].cpu().numpy()).astype(int)
            valid=((locations>=0)&(locations<[720,1280])).all(axis=1)
            keep=np.zeros(len(locations),bool)
            keep[valid]=mask[locations[valid,1],locations[valid,0]]>0
            selected=torch.from_numpy(keep)
            target={k:detected[k][selected][None] for k in ('keypoints','descriptors')}
            target['image_size']=torch.tensor([[720,1280]],dtype=torch.float32)
            result=matcher({'image0':source,'image1':target})
            matches=result['matches'][0].cpu().numpy()
            ids,xyz,uv,accepted=[],[],[],[]
            target_keypoints=target['keypoints'][0].cpu().numpy()
            for index,(a,b) in enumerate(matches):
                point=image.points2D[int(a)]
                if point.has_point3D():
                    ids.append(point.point3D_id)
                    xyz.append(model.points3D[point.point3D_id].xyz)
                    uv.append(target_keypoints[b]+.5)
                    accepted.append(index)
            ids=np.array(ids,np.int64)
            xyz=np.array(xyz,float).reshape(-1,3)
            uv=np.array(uv,float).reshape(-1,2)
            triangulated_ids=ids.copy()
            unique=unique_identity_mask(ids)
            ids,xyz,uv=ids[unique],xyz[unique],uv[unique]
            intrinsic=model.cameras[image.camera_id].calibration_matrix()
            pose,predicted,score=estimate_reserved_pose(xyz,uv,ids,intrinsic,cloud)
            score.update(source_frame=source_frame,target_frame=target_frame,source_image_id=image.image_id,
                selected_target_features=int(keep.sum()),all_matches=len(matches),existing_3d_matches=len(ids),
                triangulated_matches_before_identity_guard=len(triangulated_ids),ambiguous_identity_match_rows=int((~unique).sum()),
                untriangulated_matches=len(matches)-len(triangulated_ids),intrinsic=intrinsic.tolist(),target_image_sha256=item['sha256'],
                reference_features_sha256=sha256_file(saved_path))
            results.append(score)
            np.savez_compressed(OUT/f'frame-{target_frame:06d}-observations.npz',point_ids=ids,vertices=xyz,pixels=uv,
                all_feature_matches=matches,triangulated_match_rows=accepted,
                triangulated_point_ids_before_identity_guard=triangulated_ids,unambiguous_triangulated_rows=np.flatnonzero(unique),
                target_keypoints=detected['keypoints'].cpu().numpy(),target_descriptors=detected['descriptors'].cpu().numpy(),
                target_mask_selected=keep,intrinsic=intrinsic,**({'extrinsic':pose} if pose is not None else {}))
            photo=Image.fromarray(pixels)
            draw=ImageDraw.Draw(photo)
            for row,(x,y) in enumerate(uv):
                draw.ellipse((x-2,y-2,x+2,y+2),fill=(255,190,20) if ids[row]%2==0 else (20,255,80))
                if predicted is not None:
                    draw.line([(x,y),tuple(predicted[row])],fill=(255,50,50))
            photo.save(OUT/f'frame-{target_frame:06d}-validation.png')
            photo.thumbnail((360,640))
            sheet.paste(photo,(360*column,35))
            ImageDraw.Draw(sheet).text((360*column+5,8),f'{target_frame}: {score["status"]}',fill='white')
            if time.perf_counter()-started>60:
                raise TimeoutError('One direct localization budget exhausted')
    sheet.save(OUT/'development-sentinel-review.png')
    unchanged=all(sha256_file(SOURCE/p)==h for p,h in hashes.items())
    if not unchanged:
        raise ValueError('Frozen source model changed')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in results) else 'REJECT',
        'model_unchanged':unchanged,'results':results,'elapsed_seconds':time.perf_counter()-started,
        'limits':'Direct-match development sentinels already seen. No complete head, independent case or anatomical/scan acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'screen_status':report['screen_status'],'results':[{k:v for k,v in r.items() if k!='errors_px'} for r in results]}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
