"""Single offline Apache geometry screen, no scan/camera conditioning."""
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file, validate_input_assets
from direct_geometry_capacity_0236 import evaluate_camera_only, population, projection_result, relative_pose_errors
from mapanything_assets_0248 import validate_assets
from mapanything_geometry_0249 import resize_transform, sample_points, convention_report
from mapanything_permissive_runtime_0248 import (ASSET, install_permissive_runtime,
    audit_imported_provenance, meta_parameter_construction, expand_verified_parameter_aliases)

PILOT = ROOT/'assets/private/real-capture-pilot-v1'
SOURCE = PILOT/'scan-motion-truth-0230-upright'
OUT = ASSET/'known-geometry-0249'
VIEWS = ['front', 'yaw-10', 'yaw+10', 'yaw-30', 'yaw+30', 'pitch+10']


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first geometry screen')
    started = time.perf_counter()
    manifest = json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    subset = dict(manifest, inputs=[x for x in manifest['inputs'] if x['id'] in
        ('real-case-001-video', 'real-case-001-skin')])
    confirmation = json.loads((PILOT/'provenance-confirmation.json').read_text(encoding='utf-8'))
    controls = json.loads((SOURCE/'controls.json').read_text(encoding='utf-8'))
    if (len(subset['inputs']) != 2 or validate_input_assets(subset, PILOT)
            or manifest['purpose'] != 'local_head_reconstruction_validation'
            or manifest['upload_allowed'] is not False or manifest['training_allowed'] is not False
            or controls['manifest_sha256'] != sha256_file(PILOT/'manifest.json')
            or confirmation['manifest_sha256'] != controls['manifest_sha256']
            or controls['confirmation_sha256'] != sha256_file(PILOT/'provenance-confirmation.json')
            or confirmation['cases']['real-case-001'] != dict(scan_units='millimeter', scan_video_same_stage=True)):
        raise ValueError('Case001-only rights/stage/units/source boundary failed')
    generation = json.loads((SOURCE/'generation-report.json').read_text(encoding='utf-8'))
    if (generation['execution_status'] != 'TECHNICAL_CHECK_PASSED'
            or generation['archive_sha256'] != sha256_file(SOURCE/'known-motion.npz')):
        raise ValueError('Unchanged coherent source required')
    known = np.load(SOURCE/'known-motion.npz', allow_pickle=False)
    if list(known['view_names']) != VIEWS or len(generation['renders']) != 6:
        raise ValueError('Frozen view order required')
    paths = []
    for name, entry in zip(VIEWS, generation['renders']):
        path = (SOURCE/entry['image']).resolve()
        if (not path.is_relative_to(SOURCE.resolve()) or entry['view'] != name
                or sha256_file(path) != entry['image_sha256']):
            raise ValueError('Frozen image identity changed')
        with Image.open(path) as image:
            if image.size != (720, 1280):
                raise ValueError('Frozen image dimensions required')
        paths.append(str(path))
    lock = json.loads((ASSET/'asset-lock.json').read_text(encoding='utf-8'))
    errors = validate_assets(lock, ASSET)
    if errors:
        raise ValueError(str(errors))
    truth_k = known['intrinsic'].copy()
    truth_k[:2, 2] -= .5
    truth_ks = np.repeat(truth_k[None], 6, axis=0)
    truth_e = known['extrinsics_normalized']
    oracle, _ = evaluate_camera_only(known, truth_ks, truth_e)
    point_oracles = []
    for view in range(1, 6):
        selected = population(known, (0, view))
        score, _, _ = projection_result(known['vertices_normalized'][selected], truth_k,
            truth_e[view], known['pixels'][view, selected]-.5)
        point_oracles.append(score)
    if oracle['status'] != 'TECHNICAL_CHECK_PASSED' or not all(x['passed'] and x['max_px'] < 1e-6 for x in point_oracles):
        raise ValueError('Exact camera and point oracles failed')
    OUT.mkdir()
    prereg = ROOT/'docs/experiment-0249-mapanything-known-geometry.md'
    (OUT/'executed-preregistration.md').write_bytes(prereg.read_bytes())
    def save(name, value):
        (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    save('controls.json', dict(preregistration_sha256=sha256_file(prereg),
        producer_sha256=sha256_file(Path(__file__)), helper_sha256=sha256_file(ROOT/'tools/mapanything_geometry_0249.py'),
        evaluator_sha256=sha256_file(ROOT/'tools/direct_geometry_capacity_0236.py'),
        asset_lock_sha256=sha256_file(ASSET/'asset-lock.json'),
        source_controls_sha256=sha256_file(SOURCE/'controls.json'), source_generation_sha256=sha256_file(SOURCE/'generation-report.json'),
        known_archive_sha256=sha256_file(SOURCE/'known-motion.npz'), image_inputs=paths,
        case002_read=False, bone_read=False, geometric_model_inputs=False, training=False, upload=False,
        device='cpu', precision='float32', threads=4, seed=18))
    save('oracle-report.json', dict(camera=oracle, points=point_oracles))
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TORCH_HOME'] = str(ASSET/'torch-cache')
    sys.dont_write_bytecode = True
    def audit(event, args):
        if event == 'socket.connect':
            raise PermissionError('Offline image-only inference; no network access')
    sys.addaudithook(audit)
    import torch
    from safetensors import safe_open
    from safetensors.torch import load_file
    torch.set_num_threads(4)
    torch.manual_seed(18)
    runtime = install_permissive_runtime()
    sys.path.insert(0, str(ASSET/'source/mapanything'))
    from mapanything.models import MapAnything
    from mapanything.utils.image import load_images
    config = json.loads((ASSET/'weights/config.json').read_text(encoding='utf-8'))
    config['encoder_config']['torch_hub_pretrained'] = False
    with meta_parameter_construction():
        model = MapAnything(**config)
    state = load_file(str(ASSET/'weights/model.safetensors'), device='cpu')
    with safe_open(str(ASSET/'weights/model.safetensors'), framework='pt', device='cpu') as archive:
        expanded, aliases = expand_verified_parameter_aliases(model, state, archive.metadata() or {})
    model.load_state_dict(expanded, strict=True, assign=True)
    model.eval()
    inputs = load_images(paths, resize_mode='fixed_mapping', norm_type='dinov2', patch_size=14, resolution_set=518)
    if len(inputs) != 6 or any(set(v) != {'img', 'true_shape', 'idx', 'instance', 'data_norm_type'} for v in inputs):
        raise ValueError('Only image and nongeometric image metadata allowed')
    hw = tuple(inputs[0]['img'].shape[-2:])
    transform, resized, crop = resize_transform((720, 1280), hw[::-1])
    for path, view in zip(paths, inputs):
        with Image.open(path) as image:
            image = image.convert('RGB').resize(resized, Image.Resampling.LANCZOS)
            image = image.crop((crop[0], crop[1], crop[0]+hw[1], crop[1]+hw[0]))
            tensor = torch.from_numpy(np.array(image).copy()).permute(2, 0, 1).float()/255
        tensor = (tensor-torch.tensor([.485, .456, .406])[:, None, None])/torch.tensor([.229, .224, .225])[:, None, None]
        if not torch.equal(tensor[None], view['img']):
            raise ValueError('Exact independent resize/crop/RGB-normalization replay failed')
    save('preprocessing.json', dict(processed_hw=hw, resized_wh=resized, crop_xy=crop,
        pixel_center_transform=transform.tolist(), exact_rgb_replay=True, verified_aliases=len(aliases),
        provenance_before=audit_imported_provenance(), dino_calls=runtime['dino_calls']))
    if time.perf_counter()-started > 180:
        raise TimeoutError('Pre-inference preparation budget exceeded')
    print('BEGIN_SINGLE_IMAGE_FORWARD_300_SECONDS', flush=True)
    inference_start = time.perf_counter()
    with torch.inference_mode():
        predictions = model.infer(inputs, memory_efficient_inference=True, minibatch_size=1,
            use_amp=False, apply_mask=False, mask_edges=False, apply_confidence_mask=False,
            use_multiview_confidence=False)
    elapsed = time.perf_counter()-inference_start
    arrays = {key: np.stack([v[key][0].cpu().numpy() for v in predictions]) for key in
        ('intrinsics', 'camera_poses', 'pts3d_cam', 'pts3d', 'ray_directions', 'conf', 'depth_z')}
    np.savez_compressed(OUT/'predictions.npz', **arrays)
    conventions = convention_report(arrays)
    extrinsics = np.linalg.inv(arrays['camera_poses'].astype(float))[:, :3]
    k = np.linalg.inv(transform)[None]@arrays['intrinsics']
    cameras, camera_arrays = evaluate_camera_only(known, k, extrinsics)
    joints, joint_arrays = [], {}
    for view in range(1, 6):
        selected = population(known, (0, view))
        front = known['pixels'][0, selected]-.5
        processed = np.c_[front, np.ones(len(front))]@transform.T
        points = sample_points(arrays['pts3d'][0], processed[:, :2])
        score, projected, residual = projection_result(points, k[view], extrinsics[view], known['pixels'][view, selected]-.5)
        joints.append(dict(view=VIEWS[view], prediction=score))
        joint_arrays[VIEWS[view]] = dict(point_ids=known['point_ids'][selected], points=points,
            predicted=projected, errors=residual, truth=known['pixels'][view, selected]-.5)
    for lane, records in (('camera', camera_arrays), ('joint', joint_arrays)):
        for name, record in records.items():
            np.savez_compressed(OUT/(lane+'-'+name+'.npz'), **record)
    sheet = Image.new('RGB', (900, 1780), (28, 28, 28))
    ImageDraw.Draw(sheet).text((10, 5), 'SUPPLIED SCAN CLAY / PREDICTED POINT PROJECTION / NOT A RECONSTRUCTED HEAD', fill='white')
    for view, name in enumerate(VIEWS[1:], start=1):
        for column, (lane, records) in enumerate((('CAMERA ONLY', camera_arrays), ('POINT MAP + POSE', joint_arrays))):
            image = Image.open(paths[view]).convert('RGB')
            draw = ImageDraw.Draw(image)
            record = records.get(name)
            if record is not None:
                pixels = record['predicted'][-1] if column == 0 else record['predicted']
                truth = record['truth'][-1] if column == 0 else record['truth']
                for expected, predicted in zip(truth[::max(1, len(truth)//100)], pixels[::max(1, len(truth)//100)]):
                    x, y = expected
                    draw.ellipse((x-2, y-2, x+2, y+2), fill=(20, 255, 80))
                    if np.isfinite(predicted).all():
                        draw.line([tuple(expected), tuple(predicted)], fill=(255, 60, 50))
            x, y = column*450, (view-1)*350+40
            sheet.paste(image.crop((100, 490, 620, 850)).resize((450, 315)), (x, y+20))
            ImageDraw.Draw(sheet).text((x+5, y), name+' / '+(lane if record is not None else 'SOURCE PAIR'), fill='white')
    sheet.save(OUT/'known-geometry-review.png')
    passed = (elapsed <= 300 and conventions['passed'] and cameras['status'] == 'TECHNICAL_CHECK_PASSED'
        and all(j['prediction']['passed'] for j in joints))
    report = dict(execution_status='TECHNICAL_CHECK_PASSED', screen_status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        head_acceptance='UNVERIFIED', camera_only=cameras, point_map_pose=joints, conventions=conventions,
        relative_pose_errors=relative_pose_errors(extrinsics, truth_e), inference_seconds=elapsed,
        elapsed_seconds=time.perf_counter()-started, predictions_sha256=sha256_file(OUT/'predictions.npz'),
        imported_provenance=audit_imported_provenance(),
        limits='Known3D supplied-scan clay only. No real-video head, scan accuracy or visual acceptance follows.')
    save('report.json', report)
    print(json.dumps({k: v for k, v in report.items() if k != 'imported_provenance'}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps(dict(status='REJECT', error=str(error)), indent=2), encoding='utf-8')
        raise
