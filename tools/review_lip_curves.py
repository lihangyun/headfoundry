"""Native-frame scientific overlay for the local reconstruction observations."""
import json
import cv2
import numpy as np
from PIL import Image,ImageDraw
from prepare_lip_curves import ROOT,digest


def main():
    folder=ROOT/'assets/private/reconstruction-observations-v1'
    metadata=json.loads((folder/'manifest.json').read_text())
    data=folder/'lip-curves.npz'
    if digest(data)!=metadata['array_sha256']:raise ValueError('Curve identity mismatch')
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    if digest(manifest)!=metadata['manifest_sha256']:raise ValueError('Authorization manifest changed')
    document=json.loads(manifest.read_text())
    record=next(r for r in document['inputs'] if r['id']=='real-case-001-video')
    video=manifest.parent/record['path']
    if digest(video)!=metadata['source_sha256']:raise ValueError('Video identity mismatch')
    with np.load(data,allow_pickle=False) as z:curves={n:z[n] for n in metadata['curve_ids']}
    wanted={r['ordinal']:r['rgb_sha256'] for r in metadata['frames']}
    colors={'outer_upper':'yellow','outer_lower':'cyan','inner_upper':'magenta','inner_lower':'lime'}
    # Fixed same source crop for all views, before image review; zoom only.
    box=(180,620,520,860);zoom=2
    sheet=Image.new('RGB',(1360,3*510),'#202020');draw=ImageDraw.Draw(sheet)
    capture=cv2.VideoCapture(str(video));ordinal=0;count=0
    import hashlib
    try:
        while ordinal<=max(wanted):
            ok,bgr=capture.read()
            if not ok:raise ValueError('Premature EOF')
            if ordinal in wanted:
                rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                if hashlib.sha256(rgb.tobytes()).hexdigest()!=wanted[ordinal]:raise ValueError('Frame identity mismatch')
                original=Image.fromarray(rgb);annotated=original.copy();pen=ImageDraw.Draw(annotated)
                for name,values in curves.items():pen.line([tuple(p) for p in values[count]],fill=colors[name],width=1)
                for col,im in enumerate((original,annotated)):
                    sheet.paste(im.crop(box).resize((680,480),Image.Resampling.NEAREST),(col*680,count*510+30))
                draw.text((8,count*510+8),f'frame {ordinal}: original | predicted curves (UNVERIFIED)',fill='white')
                count+=1
            ordinal+=1
    finally:capture.release()
    if count!=3:raise ValueError('Missing required frame')
    output=folder/'lip-review.png'
    if output.exists():raise FileExistsError('Preserve previous review')
    sheet.save(output)
    report=dict(status='UNVERIFIED',frames=list(wanted),crop=box,zoom=zoom,colors=colors,
        source_sha256=metadata['source_sha256'],curve_sha256=metadata['array_sha256'],
        image_sha256=digest(output),scope='source observation review; no reconstruction')
    (folder/'lip-review.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(output)


if __name__=='__main__':main()
