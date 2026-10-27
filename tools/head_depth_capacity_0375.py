"""Fixed diagnostic only; supplied-scan truth never enters model inference."""
import hashlib
import json
import os
from pathlib import Path
import sys
from check_metric_bundle_0374 import ROOT, BASE, WEIGHT, main as verify_bundle

FIX = ROOT / 'assets/private/real-capture-pilot-v1/scan-motion-truth-0230-upright'
OUT = ROOT / 'assets/private/head-depth-0375'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def infer():
    verify_bundle()
    def audit(event, args):
        if event.startswith(('socket.', 'subprocess.', 'os.system')):
            raise PermissionError('offline inference')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            p = Path(os.fsdecode(args[0]))
            if p.name == 'known-motion.npz' or p.suffix.lower() == '.stl':
                raise PermissionError('truth forbidden during inference')
    sys.addaudithook(audit)
    import torch
    import cv2
    import numpy as np
    torch.set_num_threads(2)
    cv2.setNumThreads(2)
    sys.path.insert(0, str(BASE / 'source/metric_depth'))
    from depth_anything_v2.dpt import DepthAnythingV2
    from depth_anything_v2.util.transform import Resize, NormalizeImage, PrepareForNet
    from torchvision.transforms import Compose
    transform = Compose([
        Resize(width=518,height=518,resize_target=False,keep_aspect_ratio=True,
               ensure_multiple_of=14,resize_method='lower_bound',image_interpolation_method=cv2.INTER_CUBIC),
        NormalizeImage(mean=[.485,.456,.406],std=[.229,.224,.225]),PrepareForNet()])
    model = DepthAnythingV2(encoder='vits', features=64,
                           out_channels=[48,96,192,384], max_depth=20).eval()
    model.load_state_dict(torch.load(WEIGHT, weights_only=True, map_location='cpu'), strict=True)
    records = json.loads((FIX / 'generation-report.json').read_text())['renders']
    depths = []
    for item in records:
        path = FIX / item['image']
        if sha(path) != item['image_sha256']:
            raise ValueError('input identity mismatch')
        image = cv2.imread(str(path))
        if image.shape != (1280,720,3):
            raise ValueError('input shape mismatch')
        with torch.inference_mode():
            # Upstream infer_image selects CUDA independently of model.device.
            # Same official transform/interpolation, explicit registered CPU.
            tensor = transform({'image':cv2.cvtColor(image,cv2.COLOR_BGR2RGB)/255.0})['image']
            tensor = torch.from_numpy(tensor).unsqueeze(0).to('cpu')
            depth = model(tensor)
            depth = torch.nn.functional.interpolate(depth[:,None],(1280,720),mode='bilinear',align_corners=True)[0,0].numpy()
        if depth.shape != (1280,720) or not np.isfinite(depth).all() or (depth<=0).any():
            raise ValueError('invalid depth output')
        depths.append(depth)
        print(item['view'], float(depth.min()), float(depth.max()), flush=True)
    np.savez_compressed(OUT / 'predictions.npz', depth=np.stack(depths))
    (OUT / 'inputs.json').write_text(json.dumps(records, indent=2))


def evaluate():
    import numpy as np
    from check_dense_grid_contract import bilinear
    report = json.loads((FIX/'generation-report.json').read_text())
    if sha(FIX/'known-motion.npz') != report['archive_sha256']:
        raise ValueError('truth identity mismatch')
    truth = np.load(FIX/'known-motion.npz')
    depths = np.load(OUT/'predictions.npz')['depth']
    points, poses, k = truth['vertices_mm'], truth['extrinsics_mm'], truth['intrinsic']
    ids, pixels, visible = truth['point_ids'], truth['pixels'], truth['visible']
    scores = []; arrays = {}; oracle_max = 0.0
    for v, name in enumerate(truth['view_names']):
        mask = visible[v]
        selected = ids[mask]; uv = pixels[v,mask]
        predicted = bilinear(depths[v], uv, [720,1280])
        local = points[mask] @ poses[v,:,:3].T + poses[v,:,3]
        z = local[:,2]; even = selected%2==0; odd = ~even
        design = np.column_stack([predicted, np.ones(len(predicted))])
        coeff, _, rank, _ = np.linalg.lstsq(design[even], z[even], rcond=None)
        if rank != 2:
            raise ValueError('affine shape unidentifiable')
        constant = np.column_stack([np.ones(even.sum()), np.ones(even.sum())])
        if np.linalg.matrix_rank(constant) != 1:
            raise AssertionError('constant negative control')
        rays = np.column_stack([(uv-k[:2,2])/k[0,0], np.ones(len(uv))])
        corrected = design @ coeff
        reconstructed = (rays*corrected[:,None]-poses[v,:,3]) @ poses[v,:,:3]
        oracle = (rays*z[:,None]-poses[v,:,3]) @ poses[v,:,:3]
        oracle_max = max(oracle_max, float(np.max(np.linalg.norm(oracle-points[mask],axis=1))))
        error = np.linalg.norm(reconstructed-points[mask], axis=1)
        p95 = float(np.percentile(error[odd],95)); cross = {}
        for other in range(6):
            if other == v: continue
            joint = odd & visible[other,mask]
            if not joint.any(): raise ValueError('empty cross-view held population')
            target = reconstructed[joint] @ poses[other,:,:3].T + poses[other,:,3]
            if (target[:,2]<=0).any(): raise ValueError('nonpositive target depth')
            projection = target[:,:2]/target[:,2,None]*k[0,0]+k[:2,2]
            delta = np.linalg.norm(projection-pixels[other,mask][joint],axis=1)
            cross[str(truth['view_names'][other])] = dict(count=int(joint.sum()),p95_px=float(np.percentile(delta,95)))
        passed = coeff[0]>0 and (corrected>0).all() and p95<=2 and all(x['p95_px']<=3 for x in cross.values())
        scores.append(dict(view=str(name),status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
                           fit_count=int(even.sum()),held_count=int(odd.sum()),affine=coeff.tolist(),
                           point_p95_mm=p95,raw_axial_p95_mm=float(np.percentile(abs(predicted[odd]*1000-z[odd]),95)),cross=cross))
        arrays[str(name)+'_ids']=selected; arrays[str(name)+'_error_mm']=error
        arrays[str(name)+'_predicted_m']=predicted
        arrays[str(name)+'_true_axial_mm']=z
        arrays[str(name)+'_pixels']=uv
    if oracle_max>1e-8: raise AssertionError('oracle ray geometry mismatch')
    result = dict(status='TECHNICAL_CHECK_PASSED' if all(s['status']=='TECHNICAL_CHECK_PASSED' for s in scores) else 'REJECT',
                  views=scores,oracle_max_mm=oracle_max,scope='oracle-calibrated clay shape capacity,not video reconstruction',
                  prediction_sha256=sha(OUT/'predictions.npz'))
    np.savez_compressed(OUT/'errors.npz',**arrays)
    (OUT/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    if sys.argv[1:]==['infer']: infer()
    elif sys.argv[1:]==['evaluate']: evaluate()
    else:
        from bounded_process import run
        repair = sys.argv[1:] == ['device-repair']
        if repair:
            previous = json.loads((OUT/'worker.json').read_text())
            if previous['exit'] != 1 or (OUT/'predictions.npz').exists() or (OUT/'device-repair.json').exists():
                raise ValueError('repair requires terminal pre-output failure, once only')
        else:
            OUT.mkdir(exist_ok=False)
        env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1')
        result=run([str(ROOT/'.venv-metric0374/Scripts/python.exe'),__file__,'infer'],ROOT,env,
                   OUT/('device-repair.log' if repair else 'worker.log'),
                   OUT/('device-repair.json' if repair else 'worker.json'),292 if repair else 300,4*1024**3)
        print(result)
        sys.exit(0 if result['status']=='TECHNICAL_CHECK_PASSED' else 1)
