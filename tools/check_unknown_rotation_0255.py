"""Constrained unknown-rotation capacity;isolated2D fit then oracle evaluation."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import minimize

from check_silhouette_focal_0254 import (
    ROOT, FIXTURE, OUT as PREVIOUS, arc_samples, coherence, polygons,
    self_check as interval_checks, source_lock,
)
from headfoundry.manifest import sha256_file
from headfoundry.camera import project
from scan_motion_truth_0230 import look_at_origin

OUT = ROOT/'assets/private/unknown-rotation-0255'
PROTOCOL = ROOT/'docs/experiment-0255-unknown-rotation-silhouettes.md'
HELPER = ROOT/'tools/check_silhouette_focal_0254.py'
INITIAL = np.r_[np.log(1.5), np.array([
    [-15, 2, 3], [15, -2, -3], [-40, 2, -3], [40, -2, 3], [0, 15, 3]
]).ravel()/45.]
BOUNDS = [(np.log(.4), np.log(4.))]+[(-80/45, 80/45), (-40/45, 40/45), (-30/45, 30/45)]*5


def cameras_from_parameters(parameters):
    p = np.asarray(parameters, float)
    if p.shape != (16,) or not np.isfinite(p).all():
        raise ValueError('Finite16-parameter camera state required')
    focal = 1000*np.exp(p[0])
    if not 100 <= focal <= 10000:
        raise ValueError('Invalid camera focal')
    k = np.array([[focal, 0, 360], [0, focal, 640], [0, 0, 1.]])
    cameras = [look_at_origin([0., 0, 1])]
    for yaw, pitch, roll in np.deg2rad(p[1:].reshape(5, 3)*45):
        center = np.array([np.sin(yaw)*np.cos(pitch), np.sin(pitch), np.cos(yaw)*np.cos(pitch)])
        ext = look_at_origin(center)
        c, s = np.cos(roll), np.sin(roll)
        rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
        ext[:, :3] = rz@ext[:, :3]
        ext[:, 3] = [0., 0, 1.]
        cameras.append(ext)
    return k, np.array(cameras)


def self_check():
    checks = interval_checks()
    k, cameras = cameras_from_parameters(INITIAL)
    for ext in cameras:
        assert np.allclose(ext[:, :3]@ext[:, :3].T, np.eye(3), atol=1e-12)
        assert np.isclose(np.linalg.det(ext[:, :3]), 1.)
        assert np.isclose(np.linalg.norm(-ext[:, :3].T@ext[:, 3]), 1.)
    assert project(k@cameras[0], np.array([[0., .1, 0]]))[0, 1] < 640
    try:
        cameras_from_parameters(np.full(16, np.nan))
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid camera accepted')
    return dict(checks, proper_unit_radius=True, source_up=True, invalid_camera_rejected=True)


def prepare():
    source_lock()
    if OUT.exists():
        raise FileExistsError('Preserve first prepared attempt')
    previous = json.loads((PREVIOUS/'report.json').read_text())
    rendered = json.loads((PREVIOUS/'render-report.json').read_text())
    if previous['status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('Successful0254 prerequisite required')
    arrays, rows, samples = {}, [], []
    for i, entry in enumerate(rendered['renders']):
        p = PREVIOUS/entry['image']
        if sha256_file(p) != entry['sha256']:
            raise ValueError('Exact mask changed')
        with Image.open(p) as image:
            mask = np.array(image.getchannel('A')) >= 128
        found = polygons(mask)
        samples.append(arc_samples(polygons(cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1))))
        for j, contour in enumerate(found):
            arrays[f'contour_{i}_{j}'] = contour
        rows.append(dict(view=entry['view'], contours=len(found), mask_sha256=entry['sha256']))
    samples = np.array(samples)
    with np.load(PREVIOUS/'results.npz', allow_pickle=False) as old:
        if not np.array_equal(samples, old['contour_samples']):
            raise ValueError('Fixed source sample changed')
    arrays['samples'] = samples
    OUT.mkdir()
    np.savez_compressed(OUT/'silhouette-input.npz', **arrays)
    (OUT/'executed-protocol.md').write_bytes(PROTOCOL.read_bytes())
    (OUT/'controls.json').write_text(json.dumps(dict(rows=rows,
        sanitized_fields=sorted(arrays), inputs_sha256=sha256_file(OUT/'silhouette-input.npz'),
        helper_sha256=sha256_file(HELPER), producer_sha256=sha256_file(Path(__file__)),
        protocol_sha256=sha256_file(OUT/'executed-protocol.md'), initial_parameters=INITIAL.tolist(),
        exact0254_samples=True, oracle_arrays_exported=False), indent=2))
    print(json.dumps(dict(prepared=True, sanitized_fields=sorted(arrays), exact0254_samples=True)))


def install_guard():
    private, allowed = (ROOT/'assets/private').resolve(), OUT.resolve()
    def guard(event, args):
        if event != 'open' or not args or isinstance(args[0], int):
            return
        try:
            p = Path(os.fsdecode(args[0])).resolve()
        except (ValueError, TypeError):
            return
        if p.suffix.lower() == '.stl' or (p.is_relative_to(private) and not p.is_relative_to(allowed)):
            raise PermissionError('Oracle/private source content denied to fit worker')
    sys.addaudithook(guard)
    for p in (FIXTURE/'known-motion.npz', ROOT/'tmp/absent-denied-fixture.stl'):
        try:
            p.open('rb')
        except PermissionError:
            continue
        raise AssertionError('Worker oracle guard failed')


def fit():
    if (OUT/'fit-report.json').exists() or (OUT/'trace.jsonl').exists():
        raise FileExistsError('No second fit attempt')
    controls = json.loads((OUT/'controls.json').read_text())
    if (controls['inputs_sha256'] != sha256_file(OUT/'silhouette-input.npz')
            or controls['helper_sha256'] != sha256_file(HELPER)
            or controls['producer_sha256'] != sha256_file(Path(__file__))):
        raise ValueError('Frozen input/producer changed')
    checks = self_check()
    install_guard()
    cv2.setNumThreads(4)
    with np.load(OUT/'silhouette-input.npz', allow_pickle=False) as data:
        if sorted(data.files) != controls['sanitized_fields']:
            raise ValueError('Unexpected worker input fields')
        samples = data['samples'].copy()
        contours = [[data[f'contour_{i}_{j}'].copy() for j in range(row['contours'])]
                    for i, row in enumerate(controls['rows'])]
    started, best, calls = time.perf_counter(), None, 0
    def cost(parameters):
        nonlocal best, calls
        if time.perf_counter()-started > 900:
            raise TimeoutError('Unknown-pose900s budget reached')
        k, cameras = cameras_from_parameters(parameters)
        score, flags = coherence(k, cameras, contours, samples)
        calls += 1
        entry = dict(evaluation=calls, elapsed_seconds=time.perf_counter()-started,
            coherence=score, per_view=flags.mean(axis=1).tolist(), parameters=parameters.tolist())
        with (OUT/'trace.jsonl').open('a') as stream:
            stream.write(json.dumps(entry)+'\n')
        if best is None or score > best['coherence']:
            best = entry
            np.savez_compressed(OUT/'best-fit.npz', intrinsic=k, cameras=cameras,
                parameters=parameters, feasible=flags)
        if calls == 1 or calls%20 == 0:
            print(json.dumps(dict(evaluation=calls, coherence=score,
                best_coherence=best['coherence'], elapsed_seconds=entry['elapsed_seconds'])), flush=True)
        return 1-score
    try:
        solved = minimize(cost, INITIAL.copy(), method='Powell', bounds=BOUNDS,
            options=dict(xtol=1e-3, ftol=1e-5, maxfev=400, maxiter=10))
        termination = dict(success=bool(solved.success), message=str(solved.message), evaluations=int(solved.nfev))
        np.savez_compressed(OUT/'solver-terminal.npz', parameters=solved.x)
    except TimeoutError as error:
        termination = dict(success=False, message=str(error), evaluations=calls)
    if best is None:
        raise ValueError('No completed cost evaluation')
    result = dict(termination=termination, selected_by='Strictly highest coherence;first on ties;no oracle errors',
        best=best, elapsed_seconds=time.perf_counter()-started, self_checks=checks,
        worker_oracle_denial_checked=True, true3d_read_in_fit=False,
        inputs_sha256=controls['inputs_sha256'], role='CONSTRAINED_UNKNOWN_ROTATION_CAPACITY_NOT_HEAD')
    (OUT/'fit-report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


def evaluate():
    if (OUT/'report.json').exists():
        raise FileExistsError('Preserve first evaluation')
    source_lock()
    fitted = json.loads((OUT/'fit-report.json').read_text())
    data = np.load(FIXTURE/'known-motion.npz', allow_pickle=False)
    final = np.load(OUT/'best-fit.npz', allow_pickle=False)
    rows, archive = [], {}
    for label, k, cameras in [('initial', *cameras_from_parameters(INITIAL)),
                             ('final', final['intrinsic'], final['cameras'])]:
        scale = float(data['intrinsic'][0, 0]/(6*k[0, 0]))
        for i, ext in enumerate(cameras):
            mask = data['visible'][i]
            points = data['vertices_normalized'][mask]*scale
            prediction = project(k@ext, points)
            independent = cv2.projectPoints(points, cv2.Rodrigues(ext[:, :3])[0], ext[:, 3], k, None)[0][:, 0]
            errors = np.linalg.norm(prediction-data['pixels'][i, mask], axis=1)
            rotation = ext[:, :3]@data['extrinsics_normalized'][i, :, :3].T
            angle = np.rad2deg(np.arccos(np.clip((np.trace(rotation)-1)/2, -1, 1)))
            row = dict(stage=label, view=str(data['view_names'][i]), points=int(mask.sum()),
                p95_px=float(np.percentile(errors, 95)), max_px=float(errors.max()),
                projection_replay_max_px=float(abs(prediction-independent).max()), rotation_error_degrees=float(angle),
                proper_rotation=bool(np.allclose(ext[:, :3]@ext[:, :3].T, np.eye(3), atol=1e-8) and np.linalg.det(ext[:, :3]) > 0),
                positive_depth=bool(((data['vertices_normalized']*scale@ext[:, :3].T+ext[:, 3])[:, 2] > 0).all()),
                evaluation_global_scale=scale, focal_px=float(k[0, 0]))
            rows.append(row)
            archive[f'{label}_{i}_errors'], archive[f'{label}_{i}_pixels'] = errors, prediction
    passed = fitted['termination']['success'] and fitted['best']['coherence'] >= .99 and all(
        r['p95_px'] <= 3 and r['proper_rotation'] and r['positive_depth']
        and r['projection_replay_max_px'] <= 1e-5 for r in rows if r['stage'] == 'final')
    result = dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT', camera_results=rows,
        termination=fitted['termination'], best_coherence=fitted['best']['coherence'],
        role='CONSTRAINED_UNKNOWN_ROTATION_CAPACITY_NOT_REAL_CAMERA_OR_HEAD',
        fixture_sha256=sha256_file(FIXTURE/'known-motion.npz'), producer_sha256=sha256_file(Path(__file__)),
        fit_report_sha256=sha256_file(OUT/'fit-report.json'), final_sha256=sha256_file(OUT/'best-fit.npz'),
        case002_read=False, bone_read=False, real_video_inference=False, training=False, upload=False,
        head_acceptance='UNVERIFIED')
    np.savez_compressed(OUT/'evaluation.npz', **archive)
    (OUT/'report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'fit', 'evaluate', 'self-check'))
    args = parser.parse_args()
    if args.phase == 'self-check':
        print(json.dumps(self_check()))
    else:
        globals()[args.phase]()
