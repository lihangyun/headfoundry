"""Known-surface camera oracle only; no real video inference or shape fitting."""
import json
from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl

PILOT = ROOT/'assets/private/real-capture-pilot-v1'
SOURCE = PILOT/'scan-motion-truth-0230-upright'
OUT = ROOT/'assets/private/direct-photometric-pose-0251'


def project(points, extrinsic, intrinsic):
    camera = points@extrinsic[:, :3].T+extrinsic[:, 3]
    if not np.isfinite(camera).all() or (camera[:, 2] <= 0).any():
        raise ValueError('Positive finite camera depth required')
    h = camera@intrinsic.T
    return h[:, :2]/h[:, 2:]


def sh9(normals):
    x, y, z = np.asarray(normals, float).T
    return np.column_stack([np.ones(len(x)), x, y, z, x*y, x*z, y*z, x*x-y*y, 3*z*z-1])


def luminance(path):
    with Image.open(path) as image:
        rgb = np.array(image.convert('RGB'), dtype=float)/255.
    linear = np.where(rgb <= .04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
    return linear@np.array([.2126, .7152, .0722])


def sample(image, pixels):
    if (not np.isfinite(pixels).all() or (pixels < 0).any()
            or (pixels > np.array(image.shape[::-1])-1).any()):
        raise ValueError('Every photometric sample must stay supported;no row pruning')
    return map_coordinates(image, pixels[:, ::-1].T, order=1, mode='constant', cval=np.nan, prefilter=False)


def self_check():
    rng = np.random.default_rng(251)
    normals = rng.normal(size=(100, 3))
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    a = sh9(normals)
    truth = a@rng.normal(size=9)
    error = float(np.max(abs(a@np.linalg.lstsq(a, truth, rcond=None)[0]-truth)))
    if error > 1e-12:
        raise ValueError('Lighting variable projection algebra failed')
    image = np.arange(100, dtype=float).reshape(10, 10)
    if abs(sample(image, np.array([[2.25, 3.5]]))[0]-37.25) > 1e-12:
        raise ValueError('Pixel-center sampling fixture failed')
    return dict(lighting_replay_max=error, bilinear_replay=True)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first experiment')
    started = time.perf_counter()
    checks = self_check()
    manifest = json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    confirmation = json.loads((PILOT/'provenance-confirmation.json').read_text(encoding='utf-8'))
    control = json.loads((SOURCE/'controls.json').read_text(encoding='utf-8'))
    generation = json.loads((SOURCE/'generation-report.json').read_text(encoding='utf-8'))
    assets = [x for x in manifest['inputs'] if x['id'] == 'real-case-001-skin']
    if (len(assets) != 1 or validate_input_assets(dict(manifest, inputs=assets), PILOT)
            or manifest['purpose'] != 'local_head_reconstruction_validation'
            or manifest['upload_allowed'] is not False or manifest['training_allowed'] is not False
            or sha256_file(PILOT/'manifest.json') != confirmation['manifest_sha256']
            or control['manifest_sha256'] != confirmation['manifest_sha256']
            or control['confirmation_sha256'] != sha256_file(PILOT/'provenance-confirmation.json')
            or confirmation['cases']['real-case-001'] != dict(scan_units='millimeter', scan_video_same_stage=True)
            or assets[0]['sha256'] != control['source_sha256']
            or generation['execution_status'] != 'TECHNICAL_CHECK_PASSED'
            or sha256_file(SOURCE/'known-motion.npz') != generation['archive_sha256']):
        raise ValueError('Exact authorized source and known3D generation required')
    known = np.load(SOURCE/'known-motion.npz', allow_pickle=False)
    if list(known['view_names']) != ['front', 'yaw-10', 'yaw+10', 'yaw-30', 'yaw+30', 'pitch+10']:
        raise ValueError('Exact view order required')
    raw, faces = read_binary_stl(assets[0]['path'])
    normal = np.cross(raw[faces[:, 1]]-raw[faces[:, 0]], raw[faces[:, 2]]-raw[faces[:, 0]])
    vertex_normals = np.zeros_like(raw)
    for corner in range(3):
        np.add.at(vertex_normals, faces[:, corner], normal)
    lengths = np.linalg.norm(vertex_normals, axis=1)
    vertex_normals /= np.maximum(lengths[:, None], 1e-30)
    ids, bary = known['source_triangle_ids'], known['source_barycentric']
    normals = np.einsum('ni,nij->nj', bary, vertex_normals[faces[ids]])
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-30)
    k = known['intrinsic'].copy()
    k[:2, 2] -= .5
    points = known['vertices_normalized']
    truth_e = known['extrinsics_normalized']
    oracle = max(float(np.max(abs(project(points, e, k)-(known['pixels'][i]-.5)))) for i, e in enumerate(truth_e))
    if oracle > 1e-8:
        raise ValueError('Exact camera pixel oracle failed')
    paths = []
    for name, entry in zip(known['view_names'], generation['renders']):
        path = (SOURCE/entry['image']).resolve()
        if (not path.is_relative_to(SOURCE.resolve()) or entry['view'] != name
                or sha256_file(path) != entry['image_sha256']):
            raise ValueError('Fixed render hash failed')
        paths.append(path)
    OUT.mkdir()
    prereg = ROOT/'docs/experiment-0251-direct-photometric-pose-capacity.md'
    (OUT/'executed-preregistration.md').write_bytes(prereg.read_bytes())
    controls = dict(producer_sha256=sha256_file(Path(__file__)), preregistration_sha256=sha256_file(prereg),
        manifest_sha256=control['manifest_sha256'], confirmation_sha256=control['confirmation_sha256'],
        source_sha256=control['source_sha256'], generation_sha256=sha256_file(SOURCE/'generation-report.json'),
        known_archive_sha256=generation['archive_sha256'], geometry_is_supplied_oracle=True,
        true_camera_is_perturbed_for_local_seed=True, scan_free_inference=False, case002_read=False,
        training=False, upload=False, self_checks=checks, exact_projection_oracle_max_px=oracle)
    (OUT/'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    boxed = ((known['pixels'] >= [100, 500]) & (known['pixels'] < [620, 820])).all(axis=2)
    results, archives = [], {}
    sheet = Image.new('RGB', (900, 1780), (26, 26, 26))
    ImageDraw.Draw(sheet).text((5, 5), 'KNOWN SCAN GEOMETRY / PHOTOMETRIC CAMERA ORACLE / NOT A RECONSTRUCTED HEAD', fill='white')
    for view in range(1, 6):
        if time.perf_counter()-started > 120:
            raise TimeoutError('Predeclared total budget exhausted')
        selected = known['visible'][[0, view]].all(axis=0) & boxed[[0, view]].all(axis=0)
        if (lengths[selected] <= 1e-8).any():
            raise ValueError('Undefined selected normal')
        fit = selected & (known['point_ids']%2 == 0)
        held = selected & ~fit
        if min(fit.sum(), held.sum()) < 200 or (np.ptp(known['pixels'][view, fit], axis=0) < 50).any():
            raise ValueError('Fixed sample support insufficient')
        a = sh9(normals[fit])
        if np.linalg.matrix_rank(a) != 9:
            raise ValueError('Illumination design rank failed')
        inverse = np.linalg.pinv(a)
        image = luminance(paths[view])
        initial = truth_e[view].copy()
        initial[:, :3] = Rotation.from_rotvec([.035, -.035, .020]).as_matrix()@initial[:, :3]
        initial[:, 3] += [.030, -.020, .060]
        def camera(q):
            return np.c_[Rotation.from_rotvec(q[:3]*.02).as_matrix()@initial[:, :3], initial[:, 3]+q[3:]*.03]
        def residual(q):
            if time.perf_counter()-started > 120:
                raise TimeoutError('Photometric fit budget exhausted')
            observed = sample(image, project(points[fit], camera(q), k))
            return observed-a@(inverse@observed)
        solution = least_squares(residual, np.zeros(6), bounds=(-6, 6), jac='3-point',
            max_nfev=60, ftol=1e-8, xtol=1e-8, gtol=1e-8, loss='linear')
        final = camera(solution.x)
        truth = known['pixels'][view, held]-.5
        before, after = project(points[held], initial, k), project(points[held], final, k)
        before_error, after_error = np.linalg.norm(before-truth, axis=1), np.linalg.norm(after-truth, axis=1)
        light = inverse@sample(image, project(points[fit], final, k))
        irradiance = sh9(normals[selected])@light
        photo = sample(image, after)-sh9(normals[held])@light
        bounded = bool((abs(solution.x) >= 6-1e-5).any())
        passed = bool(solution.success and not bounded and (irradiance > 0).all() and np.percentile(after_error, 95) <= 3)
        result = dict(view=str(known['view_names'][view]), status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
            fit_count=int(fit.sum()), held_count=int(held.sum()), initial_p95_px=float(np.percentile(before_error, 95)),
            final_p50_px=float(np.median(after_error)), final_p95_px=float(np.percentile(after_error, 95)),
            max_px=float(after_error.max()), held_luminance_rms=float(np.sqrt(np.mean(photo**2))),
            optimizer_success=bool(solution.success), message=solution.message, nfev=solution.nfev,
            bound_hit=bounded, positive_irradiance=bool((irradiance > 0).all()), q=solution.x.tolist())
        results.append(result)
        archives[str(view)+'-point_ids'] = known['point_ids'][held]
        archives[str(view)+'-fit_ids'] = known['point_ids'][fit]
        archives[str(view)+'-truth'] = truth
        archives[str(view)+'-before'] = before
        archives[str(view)+'-after'] = after
        archives[str(view)+'-extrinsic'] = final
        archives[str(view)+'-light'] = light
        print(json.dumps(result), flush=True)
        for column, pixels in enumerate((before, after)):
            panel = Image.open(paths[view]).convert('RGB')
            draw = ImageDraw.Draw(panel)
            step = max(1, len(truth)//100)
            for expected, predicted in zip(truth[::step], pixels[::step]):
                x, y = expected
                draw.ellipse((x-2, y-2, x+2, y+2), fill=(30, 255, 60))
                draw.line([tuple(expected), tuple(predicted)], fill=(255, 55, 50))
            x, y = column*450, 40+(view-1)*350
            sheet.paste(panel.crop((100, 490, 620, 850)).resize((450, 315)), (x, y+20))
            ImageDraw.Draw(sheet).text((x+5, y), result['view']+(' INITIAL' if column == 0 else ' FITTED'), fill='white')
    sheet.save(OUT/'camera-only-review.png')
    np.savez_compressed(OUT/'predictions.npz', **archives)
    report = dict(execution_status='TECHNICAL_CHECK_PASSED',
        screen_status='TECHNICAL_CHECK_PASSED' if all(x['status'] == 'TECHNICAL_CHECK_PASSED' for x in results) else 'REJECT',
        head_acceptance='UNVERIFIED', elapsed_seconds=time.perf_counter()-started, results=results,
        predictions_sha256=sha256_file(OUT/'predictions.npz'),
        limits='Known source geometry,focal and local truth-perturbed pose oracle. Not scan-free camera inference or a reconstructed head.')
    if report['elapsed_seconds'] > 120:
        report['screen_status'] = 'REJECT'
    (OUT/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists():
            (OUT/'failure.json').write_text(json.dumps(dict(status='REJECT', error=str(error)), indent=2), encoding='utf-8')
        raise
