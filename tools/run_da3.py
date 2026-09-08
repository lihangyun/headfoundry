"""Run only the reviewed DA3-BASE checkpoint locally, without Hub/API/export services."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
import time

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'src'))
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.inputs import validate_multiview

LOCK_PATH=PROJECT/'examples/da3-base-asset-lock.json'


def source_digest(upstream):
    digest=hashlib.sha256()
    files=sorted(p for p in (upstream/'src/depth_anything_3').rglob('*') if p.suffix in ('.py','.yaml'))
    for path in files:
        digest.update(path.relative_to(upstream).as_posix().encode()+b'\0')
        digest.update(hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).digest())
    return digest.hexdigest()


def verify(manifest, upstream, assets):
    document=json.loads(manifest.read_text(encoding='utf-8'))
    if document.get('purpose')!='local_head_reconstruction_validation':
        raise ValueError('only consented local validation is enabled')
    errors=validate_input_assets(document,manifest.parent)
    capture=validate_multiview(document.get('inputs',[]))
    if errors or capture['status']!='TECHNICAL_CHECK_PASSED':
        raise ValueError('input rights/capture rejected: '+str(errors or capture['errors']))
    lock=json.loads(LOCK_PATH.read_text())
    if lock.get('asset_id')!='depth-anything/DA3-BASE' or lock.get('license_id')!='Apache-2.0':
        raise ValueError('only the reviewed Apache-2.0 DA3-BASE asset is allowed')
    for name,digest in lock['model_sha256'].items():
        if sha256_file(assets/name)!=digest:raise ValueError('model asset hash mismatch: '+name)
    license_digest=hashlib.sha256((upstream/'LICENSE').read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if license_digest!=lock['source_license_sha256_lf'] or source_digest(upstream)!=lock['source_tree_sha256']:
        raise ValueError('DA3 source/license hash mismatch')
    for package,version in lock['runtime'].items():
        if metadata.version(package)!=version:raise ValueError('unreviewed DA3 runtime: '+package)
    return document,lock


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','upstream','assets','output'):parser.add_argument(name,type=Path)
    parser.add_argument('--ray-pose',action='store_true',help='explicit alternate camera decoder, same locked weights')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('choose a new output directory')
    document,lock=verify(args.manifest,args.upstream,args.assets)
    # Imports capable of model execution happen only after all rights/asset checks.
    import cv2
    import numpy as np
    import torch
    from PIL import Image
    from omegaconf import OmegaConf
    from safetensors.torch import load_model
    sys.path.insert(0,str(args.upstream.resolve()/'src'))
    from depth_anything_3.cfg import create_object
    config=json.loads((args.assets/'config.json').read_text())
    if config['model_name']!='da3-base':raise ValueError('unexpected model configuration')
    torch.set_num_threads(4);torch.manual_seed(18)
    model=create_object(OmegaConf.create(config['config'])).eval()
    # The official checkpoint deduplicates tied LayerNorm parameters. The
    # safetensors loader restores those aliases while strictly checking weights.
    container=torch.nn.Module();container.add_module('model',model)
    load_model(container,str(args.assets/'model.safetensors'),strict=True,device='cpu')
    pixels=[];sizes=[]
    for record in document['inputs']:
        with Image.open(args.manifest.parent/record['path']) as im:
            if im.size!=(record['width_px'],record['height_px']):raise ValueError('decoded image size differs from capture manifest')
            if im.width!=im.height:raise ValueError('this diagnostic currently requires square photos; no implicit crop')
            sizes.append([im.height,im.width])
            pixels.append(cv2.resize(np.asarray(im.convert('RGB')),(504,504),interpolation=cv2.INTER_AREA))
    # Matches upstream upper-bound resize and ImageNet normalization for square inputs.
    tensor=torch.from_numpy(np.stack(pixels)).permute(0,3,1,2).float()/255.
    tensor=(tensor-torch.tensor([.485,.456,.406])[None,:,None,None])/torch.tensor([.229,.224,.225])[None,:,None,None]
    print('verified local DA3-BASE; beginning CPU FP32 inference',flush=True);start=time.perf_counter()
    with torch.inference_mode():
        result=model(tensor[None],infer_gs=False,use_ray_pose=args.ray_pose,ref_view_strategy='first')
    arrays={key:result[key][0].cpu().numpy() for key in ('depth','depth_conf','extrinsics','intrinsics')}
    if not all(np.isfinite(value).all() for value in arrays.values()):raise ValueError('non-finite model output')
    elapsed=time.perf_counter()-start
    args.output.mkdir(parents=True,exist_ok=False)
    np.savez_compressed(args.output/'predictions.npz',**arrays)
    report=dict(status='UNVERIFIED',asset=lock,input_ids=[r['id'] for r in document['inputs']],
                input_sha256=[r['sha256'] for r in document['inputs']],original_sizes_hw=sizes,
                processed_size_hw=[504,504],camera_convention='opencv_camera_from_world_x_right_y_down_z_forward',
                runtime_seconds=elapsed,device='cpu',precision='float32',use_ray_pose=args.ray_pose,reference_view='first',
                extrinsics=arrays['extrinsics'].tolist(),intrinsics_processed=arrays['intrinsics'].tolist(),
                output_sha256=sha256_file(args.output/'predictions.npz'),
                limitations='Model prediction only; no calibrated scan, held-out camera test, head or visual acceptance.')
    with (args.output/'report.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
    print(json.dumps(dict(status=report['status'],runtime_seconds=elapsed,shapes={k:list(v.shape) for k,v in arrays.items()})))


if __name__=='__main__':main()
