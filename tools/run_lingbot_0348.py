"""One owned-image prediction and separate physical evaluation."""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

import numpy as np
from PIL import Image
from lingbot_camera import crop_transform, native_camera

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'assets/private/dense-photo-0332'
OUT = ROOT / 'assets/private/lingbot-physical-0348'
HASHES = ('24a41defda99bdeab85917c8edd55ad5420b2f35a8c11a965338a2db46a07177',
          '4ea0b7fc2c4ffb6878b9fab0c4b420112fb4ed91126330e72cffc78c83ef6297',
          '6d8aae26e400ab53984b28e885e6dd589c80f7e77c4fae3eda6483f48c57cba4')


def infer():
    import torch
    from load_lingbot_0347 import worker
    def deny(*args, **kwargs):
        raise RuntimeError('network denied')
    tensors = []
    for index, digest in enumerate(HASHES):
        path = FIXTURE / f'view-{index}.png'
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('input identity mismatch')
        with Image.open(path) as im:
            if im.size != (720, 1280):
                raise ValueError('native size mismatch')
            _, _, resized, top = crop_transform(*im.size)
            im = im.convert('RGB').resize(resized, Image.Resampling.BICUBIC)
            pixels = np.asarray(im)[top:top+518].copy()
        tensors.append(torch.from_numpy(pixels).permute(2, 0, 1).float()/255)
    with patch.object(socket.socket, 'connect', deny):
        model = worker(record=False)
        images = torch.stack(tensors)
        torch.cuda.reset_peak_memory_stats()
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            result = model.inference_streaming(images, num_scale_frames=3,
                        keyframe_interval=1, output_device=torch.device('cpu'))
        torch.cuda.synchronize()
        arrays = {key: result[key].float().cpu().numpy()
                  for key in ('pose_enc', 'depth', 'depth_conf')}
        np.savez_compressed(OUT / 'predictions.npz', **arrays)
        (OUT / 'prediction.json').write_text(json.dumps({
            'sha256': hashlib.sha256((OUT/'predictions.npz').read_bytes()).hexdigest(),
            'cuda_peak_bytes': torch.cuda.max_memory_allocated(),
            'shapes': {key: value.shape for key, value in arrays.items()}
        }, indent=2), encoding='utf-8')


def project(k, pose, xyz):
    camera = xyz @ pose[:3, :3].T + pose[:3, 3]
    uv = camera @ k.T
    return uv[:, :2]/uv[:, 2:], camera[:, 2]


def align_and_score(ks, poses, truth_k, truth_poses, xyz, uv):
    centers = np.array([-p[:3, :3].T@p[:3, 3] for p in poses])
    truth_centers = np.array([-p[:3, :3].T@p[:3, 3] for p in truth_poses])
    gauge = truth_poses[0, :3, :3].T @ poses[0, :3, :3]
    displacement = (centers-centers[0])@gauge.T
    target = truth_centers-truth_centers[0]
    scale = float(np.sum(displacement*target)/np.sum(displacement**2))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('invalid similarity gauge')
    corrected_centers = scale*displacement + truth_centers[0]
    corrected = np.array(poses).copy()
    errors, depths, angles = [], [], []
    for i in range(3):
        rotation = poses[i, :3, :3]@gauge.T
        corrected[i, :3, :3] = rotation
        corrected[i, :3, 3] = -rotation@corrected_centers[i]
        prediction, depth = project(ks[i], corrected[i], xyz)
        errors.append(np.linalg.norm(prediction-uv[i], axis=1))
        depths.append(depth)
        angles.append(float(np.arccos(np.clip((np.trace(rotation@truth_poses[i,:3,:3].T)-1)/2, -1, 1))))
    return np.array(errors), np.array(depths), dict(scale=scale,
        camera_center_errors=np.linalg.norm(corrected_centers-truth_centers, axis=1).tolist(),
        rotation_errors_radians=angles)


def evaluate():
    with np.load(FIXTURE/'truth.npz', allow_pickle=False) as data:
        k, poses = data['K'], data['poses']
    with np.load(FIXTURE/'endpoint-truth.npz', allow_pickle=False) as data:
        xyz = data['truth_xyz']
        uv = np.stack([data['query'], data['truth_uv_1'], data['truth_uv_2']])
    replay = np.stack([project(k, p, xyz)[0] for p in poses])
    oracle_error = float(np.max(np.abs(replay-uv)))
    if oracle_error > 1e-7:
        raise ValueError(f'truth replay disagreement {oracle_error}')
    affine, (h, w), _, _ = crop_transform(720, 1280)
    cropped = np.einsum('ij,vnj->vni', affine, np.concatenate([uv, np.ones((*uv.shape[:2], 1))], axis=2))
    support = ((cropped[..., 0]>=1)&(cropped[..., 0]<w-1)&
               (cropped[..., 1]>=1)&(cropped[..., 1]<h-1)).all(axis=0)
    if not support.any():
        raise ValueError('no common crop support')
    with np.load(OUT/'predictions.npz', allow_pickle=False) as data:
        enc = data['pose_enc'][0]
    decoded = [native_camera(p, 720, 1280) for p in enc]
    ks = np.array([item[0] for item in decoded])
    predicted_poses = np.tile(np.eye(4), (3, 1, 1))
    predicted_poses[:, :3, :] = np.array([item[1] for item in decoded])
    errors, depths, alignment = align_and_score(ks, predicted_poses, k, poses, xyz, uv)
    control, _, _ = align_and_score(np.tile(k, (3,1,1)), poses, k, poses, xyz, uv)
    if np.max(control) > 1e-7:
        raise ValueError('truth-camera control failed')
    focal = np.abs(ks[:, [0,1], [0,1]]/k[[0,1],[0,1]]-1)
    p95 = np.percentile(errors[:, support], 95, axis=1)
    passed = bool(np.isfinite(errors[:,support]).all() and (depths[:,support]>0).all()
                  and (p95<=3).all() and (focal<=.02).all())
    report = dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        scope='owned procedural camera fixture only; not medical or real head',
        supported_ids=np.flatnonzero(support).tolist(), excluded_ids=np.flatnonzero(~support).tolist(),
        p95_native_pixels=p95.tolist(), focal_relative_errors=focal.tolist(),
        true_projection_replay_max=oracle_error, true_camera_control_max=float(np.max(control)),
        alignment=alignment)
    np.savez_compressed(OUT/'scores.npz', errors=errors, depths=depths, support=support, native_K=ks, poses=predicted_poses)
    (OUT/'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    if sys.argv[1:] == ['--infer']:
        infer()
    elif sys.argv[1:] == ['--evaluate']:
        evaluate()
    elif sys.argv[1:] == ['--bounded-evaluate']:
        from bounded_process import run
        if (OUT/'evaluation-worker.json').exists():
            raise SystemExit('evaluation already attempted; inspect saved evidence')
        print(json.dumps(run([sys.executable, str(Path(__file__).resolve()), '--evaluate'],
            ROOT, dict(os.environ), OUT/'evaluation.log',
            OUT/'evaluation-worker.json', 60, 1024**3)))
    elif not sys.argv[1:]:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        print(json.dumps(run([str(ROOT/'.venv-lingbot-0347/Scripts/python.exe'),
            str(Path(__file__).resolve()), '--infer'], ROOT, dict(os.environ),
            OUT/'inference.log', OUT/'inference-worker.json', 180, 16*1024**3)))
    else:
        raise SystemExit('unsupported arguments')
