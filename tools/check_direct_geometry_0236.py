"""One offline, image-only DA3-BASE check on frozen coherent source-scan renders."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file, validate_input_assets
from run_da3 import verify_assets
from direct_geometry_capacity_0236 import (RESIZE, camera_structure, evaluate_camera_only,
    population, projection_result, relative_pose_errors, unproject_samples)

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
SOURCE = PILOT / 'scan-motion-truth-0230-upright'
OUT = PILOT / 'direct-geometry-capacity-0236'
UPSTREAM = ROOT / 'assets/private/da3-upstream'
ASSETS = ROOT / 'assets/private/DA3-BASE'


def infer(pixels):
    # Caller verifies consent/source/model/runtime before reaching executable ML.
    # Same strict load and inference semantics as the existing square runner.
    import torch
    from omegaconf import OmegaConf
    from safetensors.torch import load_model
    sys.path.insert(0, str(UPSTREAM / 'src'))
    from depth_anything_3.cfg import create_object
    config = json.loads((ASSETS / 'config.json').read_text(encoding='utf-8'))
    if config['model_name'] != 'da3-base':
        raise ValueError('Exact reviewed model configuration required')
    torch.set_num_threads(4)
    torch.manual_seed(18)
    model = create_object(OmegaConf.create(config['config'])).eval()
    container = torch.nn.Module()
    container.add_module('model', model)
    load_model(container, str(ASSETS / 'model.safetensors'), strict=True, device='cpu')
    tensor = torch.from_numpy(np.stack(pixels)).permute(0, 3, 1, 2).float() / 255.
    tensor = (tensor - torch.tensor([.485, .456, .406])[None, :, None, None]) / torch.tensor([.229, .224, .225])[None, :, None, None]
    with torch.inference_mode():
        result = model(tensor[None], infer_gs=False, use_ray_pose=False, ref_view_strategy='first')
    arrays = {key: result[key][0].cpu().numpy() for key in ('depth', 'depth_conf', 'extrinsics', 'intrinsics')}
    if not all(np.isfinite(v).all() for v in arrays.values()) or (arrays['depth'] <= 0).any():
        raise ValueError('Finite cameras/depth/confidence and positive z-depth required')
    if arrays['depth'].shape != (6, 672, 378):
        raise ValueError('Unexpected rectangular prediction dimensions')
    return arrays


def joint_depth(known, k_processed, e, depth):
    k = np.linalg.inv(RESIZE)[None] @ k_processed
    structure = camera_structure(k, e)
    records, archives = [], {}
    for view in range(1, len(e)):
        selected = population(known, (0, view))
        source = known['pixels'][0, selected] - .5
        if selected.sum() < 200 or (np.ptp(source, axis=0) < 50).any():
            raise ValueError('Frozen joint observation support insufficient')
        resized = np.c_[source, np.ones(len(source))] @ RESIZE.T
        points = unproject_samples(depth[0], k_processed[0], e[0], resized[:, :2])
        score, pixels, errors = projection_result(points, k[view], e[view], known['pixels'][view, selected] - .5)
        name = str(known['view_names'][view])
        passed = structure['passed'] and score['passed']
        records.append({'view': name, 'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT', 'prediction': score})
        archives[name] = {'point_ids': known['point_ids'][selected], 'unprojected': points,
            'predicted': pixels, 'errors': errors, 'truth': known['pixels'][view, selected] - .5}
    return {'status': 'TECHNICAL_CHECK_PASSED' if all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT',
        'structure': structure, 'results': records}, archives


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first direct-geometry check')
    started = time.perf_counter()
    manifest = json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8'))
    confirmation = json.loads((PILOT / 'provenance-confirmation.json').read_text(encoding='utf-8'))
    source_control = json.loads((SOURCE / 'controls.json').read_text(encoding='utf-8'))
    if (manifest.get('purpose') != 'local_head_reconstruction_validation' or validate_input_assets(manifest, PILOT)
            or confirmation['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or source_control['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or source_control['confirmation_sha256'] != sha256_file(PILOT / 'provenance-confirmation.json')
            or confirmation['cases']['real-case-001']['scan_units'] != 'millimeter'):
        raise ValueError('Source rights/hash/stage/units confirmation failed')
    generation = json.loads((SOURCE / 'generation-report.json').read_text(encoding='utf-8'))
    if generation['execution_status'] != 'TECHNICAL_CHECK_PASSED' or sha256_file(SOURCE / 'known-motion.npz') != generation['archive_sha256']:
        raise ValueError('Successful unchanged known3D source required')
    known = np.load(SOURCE / 'known-motion.npz', allow_pickle=False)
    if list(known['view_names']) != ['front', 'yaw-10', 'yaw+10', 'yaw-30', 'yaw+30', 'pitch+10']:
        raise ValueError('Exact predeclared six-view order required')
    lock = verify_assets(UPSTREAM, ASSETS)
    images, processed = [], []
    for name, entry in zip(known['view_names'], generation['renders']):
        path = SOURCE / entry['image']
        if entry['view'] != name or sha256_file(path) != entry['image_sha256']:
            raise ValueError('Frozen source image identity changed')
        with Image.open(path) as image:
            if image.size != (720, 1280):
                raise ValueError('Exact source image dimensions required')
            pixels = np.array(image.convert('RGB'))
        images.append(pixels)
        processed.append(cv2.resize(pixels, (378, 672), interpolation=cv2.INTER_AREA))
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0236-direct-geometry-capacity.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    controls = {'asset': lock, 'source_controls_sha256': sha256_file(SOURCE / 'controls.json'),
        'source_generation_sha256': sha256_file(SOURCE / 'generation-report.json'),
        'known_archive_sha256': sha256_file(SOURCE / 'known-motion.npz'),
        'preregistration_sha256': sha256_file(prereg), 'producer_sha256': sha256_file(Path(__file__)),
        'evaluator_sha256': sha256_file(ROOT / 'tools/direct_geometry_capacity_0236.py'),
        'asset_checker_sha256': sha256_file(ROOT / 'tools/run_da3.py'),
        'original_hw': [1280, 720], 'processed_hw': [672, 378], 'resize_pixel_center_transform': RESIZE.tolist(),
        'input_geometry_or_cameras_to_model': False, 'device': 'cpu', 'precision': 'float32',
        'threads': 4, 'seed': 18, 'reference': 'first', 'use_ray_pose': False}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    # Oracle validates the same camera evaluator, plus exact source-point z-depth
    # unprojection (not a hidden dense oracle render or a model input).
    truth_k = known['intrinsic'].copy()
    truth_k[:2, 2] -= .5
    truth_ks = np.repeat(truth_k[None], 6, axis=0)
    truth_e = known['extrinsics_normalized']
    oracle, _ = evaluate_camera_only(known, truth_ks, truth_e)
    joint_oracle = []
    for view in range(1, 6):
        selected = population(known, (0, view))
        source = known['pixels'][0, selected] - .5
        z = (known['vertices_normalized'][selected] @ truth_e[0, :, :3].T + truth_e[0, :, 3])[:, 2]
        rays = np.c_[source, np.ones(len(source))] @ np.linalg.inv(truth_k).T
        world = (rays * z[:, None] - truth_e[0, :, 3]) @ truth_e[0, :, :3]
        score, _, _ = projection_result(world, truth_k, truth_e[view], known['pixels'][view, selected] - .5)
        joint_oracle.append(score)
    if oracle['status'] != 'TECHNICAL_CHECK_PASSED' or not all(s['passed'] and s['max_px'] < 1e-6 for s in joint_oracle):
        raise ValueError('Exact camera/point-z oracle failed before inference')
    (OUT / 'oracle-report.json').write_text(json.dumps({'camera': oracle, 'point_z_joint': joint_oracle}, indent=2), encoding='utf-8')
    print('Verified source rights, offline Apache assets and exact camera/depth oracles; infer once.', flush=True)
    infer_start = time.perf_counter()
    arrays = infer(processed)
    inference_seconds = time.perf_counter() - infer_start
    np.savez_compressed(OUT / 'predictions.npz', **arrays)
    k = np.linalg.inv(RESIZE)[None] @ arrays['intrinsics']
    cameras, camera_arrays = evaluate_camera_only(known, k, arrays['extrinsics'])
    joint, joint_arrays = joint_depth(known, arrays['intrinsics'], arrays['extrinsics'], arrays['depth'])
    for lane, records in (('camera', camera_arrays), ('joint', joint_arrays)):
        for name, record in records.items():
            np.savez_compressed(OUT / (lane + '-' + name + '.npz'), **record)
    sheet = Image.new('RGB', (900, 1780), (28, 28, 28))
    ImageDraw.Draw(sheet).text((10, 5), 'SUPPLIED SCAN CLAY / DIRECT GEOMETRY DIAGNOSTIC / NOT A RECONSTRUCTED HEAD', fill='white')
    for view, name in enumerate(known['view_names'][1:], start=1):
        for column, (lane, records) in enumerate((('CAMERA ONLY', camera_arrays), ('JOINT DEPTH+POSE', joint_arrays))):
            photo = Image.fromarray(images[view])
            draw = ImageDraw.Draw(photo)
            record = records.get(str(name))
            if record is not None:
                pixels = record['predicted'][-1] if column == 0 else record['predicted']
                truth = record['truth'][-1] if column == 0 else record['truth']
                step = max(1, len(pixels) // 100)
                for expected, predicted in zip(truth[::step], pixels[::step]):
                    x, y = expected
                    draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(20, 255, 80))
                    if np.isfinite(predicted).all():
                        draw.line([tuple(expected), tuple(predicted)], fill=(255, 60, 50))
            x, y = column * 450, (view - 1) * 350 + 40
            sheet.paste(photo.crop((100, 490, 620, 850)).resize((450, 315)), (x, y + 20))
            label = lane if record is not None else 'SOURCE PAIR (NOT INDEPENDENT)'
            ImageDraw.Draw(sheet).text((x + 5, y), str(name) + ' / ' + label, fill='white')
    sheet.save(OUT / 'direct-geometry-review.png')
    passed = cameras['status'] == joint['status'] == 'TECHNICAL_CHECK_PASSED'
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'screen_status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        'camera_only': cameras, 'joint_depth_pose': joint,
        'relative_pose_errors': relative_pose_errors(arrays['extrinsics'], truth_e),
        'inference_seconds': inference_seconds, 'elapsed_seconds': time.perf_counter() - started,
        'predictions_sha256': sha256_file(OUT / 'predictions.npz'),
        'limits': 'One known3D clay diagnostic, no real-video or generated full-head/scan/likeness acceptance.'}
    if time.perf_counter() - started > 180:
        report['screen_status'] = 'REJECT'
        report['budget_exceeded'] = True
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
