"""Same-point exact3D and real-image contextual F screen, no new reconstruction."""
import json
from pathlib import Path
import sys
import time

import numpy as np
import pycolmap

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file
from direct_video_matches_0224 import PILOT,verify_inputs
from localize_direct_features_0225 import OUT as REAL,SOURCE
from nonplanar_context_0231 import fit_context_fundamental,symmetric_line_errors

KNOWN=PILOT/'scan-motion-truth-0230-upright'
OUT=PILOT/'nonplanar-context-0231'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first nonplanar context screen')
    started=time.perf_counter()
    verify_inputs()
    OUT.mkdir()
    parent=json.loads((REAL/'controls.json').read_text(encoding='utf-8'))
    if any(sha256_file(SOURCE/p)!=h for p,h in parent['model_files_sha256'].items()):
        raise ValueError('Frozen source model changed')
    controls={'tool_sha256':sha256_file(Path(__file__)),'context_helper_sha256':sha256_file(ROOT/'tools/nonplanar_context_0231.py'),
        'known_motion_sha256':sha256_file(KNOWN/'known-motion.npz'),'real_parent_controls_sha256':sha256_file(REAL/'controls.json'),
        'model_files_sha256':parent['model_files_sha256'],'primary_variable':'independent context class homography to fundamental'}
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    records=[]
    def evaluate(name,kind,context_a,context_b,a,b,ids):
        matrix,inliers,record=fit_context_fundamental(context_a,context_b)
        record.update(name=name,kind=kind,measurements=len(ids),odd_measurements=int((ids%2!=0).sum()))
        payload={'context_source':context_a,'context_target':context_b,'context_inliers':inliers,
            'measurement_source':a,'measurement_target':b,'measurement_ids':ids}
        if matrix is not None:
            error=symmetric_line_errors(matrix,a,b)
            odd=ids%2!=0
            record.update(all_line_p95_px=float(np.percentile(error,95)),odd_line_p95_px=float(np.percentile(error[odd],95)))
            record['odd_line_gate_passed']=bool(np.percentile(error[odd],95)<=3)
            if not record['odd_line_gate_passed']:
                record['status']='REJECT'
            payload.update(fundamental=matrix,line_errors=error)
        np.savez_compressed(OUT/(name+'.npz'),**payload)
        records.append(record)
    known=np.load(KNOWN/'known-motion.npz',allow_pickle=False)
    for view,name in enumerate(known['view_names'][1:],start=1):
        pair=np.load(KNOWN/f'{name}-fixed_roi_shared-capacity.npz',allow_pickle=False)
        train,val=pair['context_ids'],pair['validation_ids']
        evaluate('known-'+str(name),'known3D',known['pixels'][0,train],known['pixels'][view,train],
            known['pixels'][0,val],known['pixels'][view,val],val)
    model=pycolmap.Reconstruction(SOURCE/'sparse/0')
    for source_frame,target_frame in ((612,624),(0,1040)):
        saved=np.load(REAL/f'frame-{target_frame:06d}-observations.npz',allow_pickle=False)
        image=model.find_image_with_name(f'frame-{source_frame:06d}.png')
        features=np.load(SOURCE/f'image-{image.image_id:03d}-features.npz',allow_pickle=False)
        a=features['keypoints'][features['mask_selected']]
        b=saved['target_keypoints'][saved['target_mask_selected']]
        matches=saved['all_feature_matches']
        context=np.ones(len(matches),bool)
        context[saved['triangulated_match_rows']]=False
        measured=matches[saved['triangulated_match_rows']][saved['unambiguous_triangulated_rows']]
        if np.intersect1d(matches[context,0],measured[:,0]).size or any(image.points2D[int(i)].has_point3D() for i in matches[context,0]):
            raise ValueError('Context leaked into triangulated measurements')
        if not np.array_equal(np.array([image.points2D[int(i)].point3D_id for i in measured[:,0]],np.int64),saved['point_ids']):
            raise ValueError('Point identity join failed')
        evaluate(f'real-{source_frame:06d}-{target_frame:06d}','real_development',a[matches[context,0]],b[matches[context,1]],
            a[measured[:,0]],b[measured[:,1]],saved['point_ids'])
    if time.perf_counter()-started>30:
        raise TimeoutError('One nonplanar context check exhausted budget')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','context_screen_status':'TECHNICAL_CHECK_PASSED' if all(
        r['status']=='TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT','results':records,
        'elapsed_seconds':time.perf_counter()-started,'limits':'Point-to-line context diagnostic, not2D reprojection, real cameras, complete head or likeness acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
