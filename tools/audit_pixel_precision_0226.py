"""Unavailable true-initialization diagnostic; never a deployable matcher."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from headfoundry.manifest import sha256_file
from measure_pixel_precision_0226 import BASE, OUT, ROOT
from temporal_video_sfm_0220 import track_step


def main():
    destination=OUT/'oracle-initialization-audit.json'
    if destination.exists():
        raise FileExistsError('Preserve first unavailable-input diagnostic')
    controls=json.loads((OUT/'controls.json').read_text(encoding='utf-8'))
    if sha256_file(ROOT/'tools/temporal_video_sfm_0220.py')!=controls['tracking_helper_sha256']:
        raise ValueError('Refinement implementation changed')
    cv2.setNumThreads(4)
    rows=[]
    for frame in (0,612):
        path=OUT/f'frame-{frame:06d}-projective.npz'
        data=np.load(path,allow_pickle=False)
        source=np.array(Image.open(BASE/'images'/f'frame-{frame:06d}.png').convert('RGB'))
        target=np.array(Image.open(OUT/f'frame-{frame:06d}-projective.png').convert('RGB'))
        regenerated=cv2.warpPerspective(source,data['homography'],(720,1280),flags=cv2.INTER_LINEAR)
        if not np.array_equal(target,regenerated):
            raise ValueError('Known target pixel regeneration failed')
        original=data['source']
        predicted,eligible,fb,patch=track_step(cv2.cvtColor(source,cv2.COLOR_RGB2GRAY),
            cv2.cvtColor(target,cv2.COLOR_RGB2GRAY),original,initial=data['truth'])
        errors=np.linalg.norm(predicted-data['truth'],axis=1)
        common=eligible & data['eligible']
        rows.append({'frame':frame,'original_observation_sha256':sha256_file(path),
            'target_regeneration_exact':True,'oracle_eligible':int(eligible.sum()),'paired_count':int(common.sum()),
            'descriptor_seed_p95_on_paired_px':float(np.percentile(data['refined_error'][common],95)),
            'oracle_seed_p95_on_paired_px':float(np.percentile(errors[common],95)),
            'paired_endpoint_difference_p95_px':float(np.percentile(np.linalg.norm(predicted[common]-data['refined'][common],axis=1),95))})
        np.savez_compressed(OUT/f'frame-{frame:06d}-oracle-audit.npz',predicted=predicted,eligible=eligible,
            fb_error=fb,patch_error=patch,errors=errors,paired=common)
    report={'status':'UNVERIFIED','results':rows,'tool_sha256':sha256_file(Path(__file__)),
        'limits':'Uses true target positions as initialization. Not a real-use model or promotable accuracy result; no new camera/head.'}
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
