"""Explicit pinned XFeat extraction for consented local validation; no downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

LOCK_PATH=Path(__file__).resolve().parents[1]/'examples/xfeat-asset-lock.json'


def verify(manifest_path, upstream):
    lock=json.loads(LOCK_PATH.read_text())
    for relative,digest in lock['sha256'].items():
        content=(upstream/relative).read_bytes()
        if relative.endswith('.py') or relative=='LICENSE':content=content.replace(b'\r\n',b'\n')
        if hashlib.sha256(content).hexdigest()!=digest:
            raise ValueError('asset hash mismatch: '+relative)
    document=json.loads(manifest_path.read_text(encoding='utf-8'))
    if document.get('purpose')!='local_head_reconstruction_validation' or not document.get('inputs'):
        raise ValueError('local validation manifest required')
    verified=[]
    for item in document['inputs']:
        consent=item.get('consent',{})
        if document['purpose'] not in item.get('allowed_uses',[]) or consent.get('biometric_processing') is not True:
            raise ValueError('missing local reconstruction consent')
        if not all(item.get(field) for field in ('source','license_id','retention_until','deletion_process')):
            raise ValueError('missing input rights provenance')
        if not all(consent.get(field) for field in ('subject_id','record_id','granted_at')):
            raise ValueError('missing consent provenance')
        path=manifest_path.parent/item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256'].lower():
            raise ValueError('input hash mismatch')
        verified.append((item,path))
    return lock,verified


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path);parser.add_argument('upstream',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('choose a new output directory')
    upstream=args.upstream.resolve();lock,inputs=verify(args.manifest,upstream)
    import torch
    import numpy as np
    from PIL import Image
    if torch.__version__!='2.8.0+cpu':raise ValueError('this diagnostic requires the reviewed torch 2.8.0+cpu runtime')
    sys.path.insert(0,str(upstream))
    from modules.xfeat import XFeat
    torch.set_num_threads(4);torch.manual_seed(15)
    state=torch.load(upstream/'weights/xfeat.pt',map_location='cpu',weights_only=True)
    extractor=XFeat(weights=state,top_k=4096)
    args.output.mkdir(parents=True,exist_ok=False)
    records=[]
    for index,(item,path) in enumerate(inputs):
        pixels=np.array(Image.open(path).convert('RGB'))
        result=extractor.detectAndCompute(extractor.parse_input(pixels))[0]
        result={key:value.cpu().numpy() for key,value in result.items()}
        filename=f'features-{index}.npz'
        np.savez_compressed(args.output/filename,**result)
        records.append(dict(id=item['id'],input_sha256=item['sha256'],file=filename,count=len(result['keypoints'])))
    report=dict(status='UNVERIFIED',asset=lock,runtime=torch.__version__,top_k=4096,records=records,
                limitations='Extracted keypoints are not verified tracks or accepted cameras.')
    (args.output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],records=records)))


if __name__=='__main__':main()
