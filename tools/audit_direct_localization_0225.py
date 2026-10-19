"""Pairwise pixel diagnostic only; never changes failed direct localization."""
import json
from pathlib import Path

import numpy as np
import pycolmap

from headfoundry.manifest import sha256_file
from audit_reserved_localization_0222 import epipolar_validation
from localize_direct_features_0225 import OUT, SOURCE


def main():
    destination=OUT/'rigidity-audit.json'
    if destination.exists():
        raise FileExistsError('Preserve first exact-index rigidity audit')
    controls=json.loads((OUT/'controls.json').read_text(encoding='utf-8'))
    if any(sha256_file(SOURCE/p)!=h for p,h in controls['model_files_sha256'].items()):
        raise ValueError('Frozen model changed')
    model=pycolmap.Reconstruction(SOURCE/'sparse/0')
    results=[]
    for source_frame,target_frame in controls['source_target_pairs']:
        path=OUT/f'frame-{target_frame:06d}-observations.npz'
        saved=np.load(path,allow_pickle=False)
        image=model.find_image_with_name(f'frame-{source_frame:06d}.png')
        matches=saved['all_feature_matches'][saved['triangulated_match_rows']][saved['unambiguous_triangulated_rows']]
        pixels=np.array([image.points2D[int(a)].xy for a,_ in matches])
        ids=np.array([image.points2D[int(a)].point3D_id for a,_ in matches],np.int64)
        if not np.array_equal(ids,saved['point_ids']):
            raise ValueError('Exact source index/identity join failed')
        result=epipolar_validation(pixels,saved['pixels'],ids,saved['intrinsic'])
        result.update(source_frame=source_frame,target_frame=target_frame,observations_sha256=sha256_file(path))
        results.append(result)
    report={'status':'UNVERIFIED','results':results,'tool_sha256':sha256_file(Path(__file__)),
        'limits':'Saved descriptor pixel pairs only; no change to rejected localization/head status.'}
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('all_symmetric_line_errors_px','essential_matrix')} for r in results]))


if __name__=='__main__':
    main()
