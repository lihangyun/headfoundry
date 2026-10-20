"""Continuous image-only ray witnesses for camera capacity,not a head model."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.sparse import coo_matrix

from check_silhouette_focal_0254 import (
    ROOT, FIXTURE, OUT as PREVIOUS, arc_samples, coherence, polygons,
    self_check as interval_checks, source_lock,
)
from headfoundry.camera import project
from headfoundry.manifest import sha256_file
from scan_motion_truth_0230 import look_at_origin

OUT = ROOT/'assets/private/silhouette-witness-0256'
PROTOCOL = ROOT/'docs/experiment-0256-continuous-silhouette-witnesses.md'
HELPER = ROOT/'tools/check_silhouette_focal_0254.py'
INITIAL = np.r_[np.log(1.5), np.array([
    [-15, 2, 3], [15, -2, -3], [-40, 2, -3], [40, -2, 3], [0, 15, 3]
]).ravel()/45.]
BOUNDS = np.array([(np.log(.4), np.log(4.))]+[(-80/45, 80/45), (-40/45, 40/45), (-30/45, 30/45)]*5)


def cameras(parameters):
    p = np.asarray(parameters, float)
    if p.shape != (16,) or not np.isfinite(p).all():
        raise ValueError('Finite16-parameter camera state required')
    focal = 1000*np.exp(p[0])
    if not 100 <= focal <= 10000:
        raise ValueError('Invalid focal')
    k = np.array([[focal, 0, 360], [0, focal, 640], [0, 0, 1.]])
    extrinsics = [look_at_origin([0., 0, 1])]
    for yaw, pitch, roll in np.deg2rad(p[1:].reshape(5, 3)*45):
        ext = look_at_origin([np.sin(yaw)*np.cos(pitch), np.sin(pitch), np.cos(yaw)*np.cos(pitch)])
        c, s = np.cos(roll), np.sin(roll)
        ext[:, :3] = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])@ext[:, :3]
        ext[:, 3] = [0., 0, 1.]
        extrinsics.append(ext)
    return k, np.array(extrinsics)


def sample_field(field, pixels):
    """Native center coordinates;outside-image positions never disappear."""
    uv = pixels-.5
    h, w = field.shape
    clip = np.clip(uv, [0, 0], [w-1, h-1])
    ij = np.minimum(np.floor(clip).astype(int), [w-2, h-2])
    x, y = ij[:, 0], ij[:, 1]
    a, b = (clip-ij).T
    value = ((1-a)*(1-b)*field[y, x]+a*(1-b)*field[y, x+1]
             +(1-a)*b*field[y+1, x]+a*b*field[y+1, x+1])
    return value+np.linalg.norm(uv-clip, axis=1)


def residual(parameters, samples, fields):
    k, ext = cameras(parameters[:16])
    n = samples.shape[1]
    depth = np.exp(parameters[16:].reshape(6, n))
    output = []
    for i in range(6):
        ray = np.c_[samples[i], np.ones(n)]@np.linalg.inv(k).T@ext[i, :, :3]
        center = -ext[i, :, :3].T@ext[i, :, 3]
        points = center+ray*depth[i, :, None]
        for j in range(6):
            if j == i:
                continue
            xyz = points@ext[j, :, :3].T+ext[j, :, 3]
            z = xyz[:, 2]
            pixels = xyz[:, :2]/np.maximum(z[:, None], .001)*k[0, 0]+[360, 640]
            output.append(np.c_[sample_field(fields[j], pixels), k[0, 0]*np.maximum(.001-z, 0)].ravel())
    result = np.concatenate(output)
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite continuous constraint')
    return result


def sparsity(n):
    rows, cols = [], []
    block = 0
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            rr = 2*n*block+np.arange(2*n)
            relevant = [0]
            for view in (i, j):
                if view:
                    relevant.extend(range(1+3*(view-1), 4+3*(view-1)))
            for c in relevant:
                rows.extend(rr.tolist())
                cols.extend([c]*len(rr))
            rows.extend(rr.tolist())
            cols.extend(np.repeat(16+i*n+np.arange(n), 2).tolist())
            block += 1
    return coo_matrix((np.ones(len(rows), bool), (rows, cols)), shape=(60*n, 16+6*n)).tocsr()


def self_check():
    checks = interval_checks()
    y, x = np.mgrid[:12, :14]
    field = 5.+2*x+3*y
    assert np.allclose(sample_field(field, np.array([[2.7, 4.2]])), [20.5])
    assert np.allclose(sample_field(field, np.array([[-1., 3.5]])), [15.5])
    k, ext = cameras(INITIAL)
    for e in ext:
        assert np.allclose(e[:, :3]@e[:, :3].T, np.eye(3), atol=1e-12)
        assert np.isclose(np.linalg.det(e[:, :3]), 1.)
    assert project(k@ext[0], np.array([[0., .1, 0]]))[0, 1] < 640
    try:
        cameras(np.full(16, np.nan))
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid camera accepted')
    samples = np.tile([[340., 620.], [380., 660.]], (6, 1, 1))
    identity = np.r_[np.log(1.5), np.zeros(15+12)]
    assert np.max(abs(residual(identity, samples, np.zeros((6, 1280, 720))))) < 1e-9
    negative = identity.copy()
    negative[1], negative[4] = -80/45, 80/45
    negative[16:] = np.log(10)
    assert residual(negative, samples, np.zeros((6, 1280, 720)))[1::2].max() > 0
    fields = np.tile((5.+2*x+3*y)[None], (6, 1, 1))
    state = np.r_[INITIAL, np.zeros(12)]
    value, pattern = residual(state, samples, fields), sparsity(2).toarray()
    for c in range(len(state)):
        moved = state.copy()
        moved[c] += 1e-6
        derivative = (residual(moved, samples, fields)-value)/1e-6
        assert np.max(abs(derivative[~pattern[:, c]]), initial=0.) < 1e-6
    return dict(checks, native_bilinear=True, outside_image_penalized=True,
        proper_camera=True, invalid_rejected=True, identity_zero=True,
        cheirality_penalty=True, sparse_dependency_replay=True)


def prepare():
    source_lock()
    if OUT.exists():
        raise FileExistsError('Preserve first continuous-witness attempt')
    prior = json.loads((PREVIOUS/'report.json').read_text())
    rendered = json.loads((PREVIOUS/'render-report.json').read_text())
    if prior['status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('Successful source-only prerequisite required')
    arrays, masks, samples, rows = {}, [], [], []
    for i, entry in enumerate(rendered['renders']):
        path = PREVIOUS/entry['image']
        if sha256_file(path) != entry['sha256']:
            raise ValueError('Source mask changed')
        with Image.open(path) as image:
            mask = (np.array(image.getchannel('A')) >= 128).astype(np.uint8)
        found = polygons(mask)
        masks.append(mask)
        samples.append(arc_samples(polygons(cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1))))
        for j, contour in enumerate(found):
            arrays[f'contour_{i}_{j}'] = contour
        rows.append(dict(view=entry['view'], contours=len(found), mask_sha256=entry['sha256']))
    arrays.update(masks=np.array(masks), samples=np.array(samples))
    with np.load(PREVIOUS/'results.npz', allow_pickle=False) as original:
        assert np.array_equal(arrays['samples'], original['contour_samples'])
    OUT.mkdir()
    np.savez_compressed(OUT/'silhouette-input.npz', **arrays)
    (OUT/'executed-protocol.md').write_bytes(PROTOCOL.read_bytes())
    (OUT/'controls.json').write_text(json.dumps(dict(rows=rows, sanitized_fields=sorted(arrays),
        input_sha256=sha256_file(OUT/'silhouette-input.npz'), producer_sha256=sha256_file(Path(__file__)),
        helper_sha256=sha256_file(HELPER), protocol_sha256=sha256_file(OUT/'executed-protocol.md'),
        initial_camera_parameters=INITIAL.tolist(), true3d_exported=False, exact0254_samples=True), indent=2))
    print(json.dumps(dict(prepared=True, fields=sorted(arrays), source_points_exported=False)))


def guard_worker():
    private, allowed = (ROOT/'assets/private').resolve(), OUT.resolve()
    def guard(event, args):
        if event != 'open' or not args or isinstance(args[0], int):
            return
        try:
            path = Path(os.fsdecode(args[0])).resolve()
        except (ValueError, TypeError):
            return
        if path.suffix.lower() == '.stl' or (path.is_relative_to(private) and not path.is_relative_to(allowed)):
            raise PermissionError('True3D/private oracle denied to image-only worker')
    sys.addaudithook(guard)
    for path in (FIXTURE/'known-motion.npz', ROOT/'tmp/absent-denied-fixture.stl'):
        try:
            path.open('rb')
        except PermissionError:
            continue
        raise AssertionError('Oracle isolation failed')


def fit():
    if (OUT/'fit-report.json').exists() or (OUT/'trace.jsonl').exists():
        raise FileExistsError('No second optimization')
    controls = json.loads((OUT/'controls.json').read_text())
    for p, key in ((OUT/'silhouette-input.npz', 'input_sha256'), (Path(__file__), 'producer_sha256'), (HELPER, 'helper_sha256')):
        if sha256_file(p) != controls[key]:
            raise ValueError('Frozen source/input changed')
    checks = self_check()
    guard_worker()
    cv2.setNumThreads(4)
    with np.load(OUT/'silhouette-input.npz', allow_pickle=False) as data:
        if sorted(data.files) != controls['sanitized_fields']:
            raise ValueError('Unexpected inference fields')
        masks, samples = data['masks'].copy(), data['samples'].copy()
        contours = [[data[f'contour_{i}_{j}'].copy() for j in range(row['contours'])]
                    for i, row in enumerate(controls['rows'])]
    if masks.shape != (6, 1280, 720) or samples.shape != (6, 512, 2) or not all(m.any() for m in masks):
        raise ValueError('Exact source mask/sample layout required')
    fields = np.array([cv2.distanceTransform(1-m, cv2.DIST_L2, cv2.DIST_MASK_PRECISE) for m in masks])
    n = samples.shape[1]
    initial = np.r_[INITIAL, np.zeros(6*n)]
    lower = np.r_[BOUNDS[:, 0], np.full(6*n, np.log(.1))]
    upper = np.r_[BOUNDS[:, 1], np.full(6*n, np.log(10))]
    started, calls, best = time.perf_counter(), 0, np.inf
    def cost(state):
        nonlocal calls, best
        if time.perf_counter()-started > 180:
            raise TimeoutError('Continuous witness180s fit budget reached')
        r = residual(state, samples, fields)
        calls += 1
        loss = float(.5*(r@r))
        record = dict(call=calls, elapsed_seconds=time.perf_counter()-started, cost=loss,
            mask_rms_px=float(np.sqrt(np.mean(r[::2]**2))), mask_max_px=float(r[::2].max()),
            camera_parameters=state[:16].tolist())
        with (OUT/'trace.jsonl').open('a') as stream:
            stream.write(json.dumps(record)+'\n')
        if loss < best:
            best = loss
            np.savez_compressed(OUT/'best-probe.npz', parameters=state)
        if calls == 1 or calls%100 == 0:
            print(json.dumps({k: v for k, v in record.items() if k != 'camera_parameters'}), flush=True)
        return r
    try:
        solved = least_squares(cost, initial, bounds=(lower, upper), method='trf',
            jac='2-point', jac_sparsity=sparsity(n), tr_solver='lsmr', x_scale='jac',
            loss='linear', max_nfev=60, ftol=1e-8, gtol=1e-8, xtol=1e-6)
        state = solved.x
        termination = dict(success=bool(solved.success), message=str(solved.message),
            nfev=int(solved.nfev), njev=int(solved.njev), optimality=float(solved.optimality),
            selected='Solver terminal state,not derivative probe')
    except TimeoutError as error:
        with np.load(OUT/'best-probe.npz', allow_pickle=False) as checkpoint:
            state = checkpoint['parameters'].copy()
        termination = dict(success=False, message=str(error), nfev=None,
            selected='Best residual probe for rejected diagnostic only')
    fit_seconds = time.perf_counter()-started
    k, ext = cameras(state[:16])
    final_r = residual(state, samples, fields)
    score, flags = coherence(k, ext, contours, samples)
    np.savez_compressed(OUT/'fit.npz', parameters=state, intrinsic=k, cameras=ext, residuals=final_r, feasible=flags)
    result = dict(termination=termination, fit_seconds=fit_seconds, residual_calls=calls,
        mask_rms_px=float(np.sqrt(np.mean(final_r[::2]**2))), mask_max_px=float(final_r[::2].max()),
        witness_target_positive=bool((final_r[1::2] == 0).all()), polygon_coherence=score,
        self_checks=checks, worker_denial_checked=True, true3d_read_in_fit=False,
        producer_sha256=controls['producer_sha256'], input_sha256=controls['input_sha256'],
        head_acceptance='UNVERIFIED')
    (OUT/'fit-report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


def evaluate():
    if (OUT/'report.json').exists():
        raise FileExistsError('Preserve initial independent evaluation')
    source_lock()
    fitted = json.loads((OUT/'fit-report.json').read_text())
    data = np.load(FIXTURE/'known-motion.npz', allow_pickle=False)
    final = np.load(OUT/'fit.npz', allow_pickle=False)
    rows, arrays = [], {}
    for stage, k, ext in [('initial', *cameras(INITIAL)), ('final', final['intrinsic'], final['cameras'])]:
        scale = float(data['intrinsic'][0, 0]/(6*k[0, 0]))
        for i, camera in enumerate(ext):
            keep = data['visible'][i]
            points = data['vertices_normalized'][keep]*scale
            predicted = project(k@camera, points)
            independent = cv2.projectPoints(points, cv2.Rodrigues(camera[:, :3])[0], camera[:, 3], k, None)[0][:, 0]
            errors = np.linalg.norm(predicted-data['pixels'][i, keep], axis=1)
            relative = camera[:, :3]@data['extrinsics_normalized'][i, :, :3].T
            rows.append(dict(stage=stage, view=str(data['view_names'][i]), points=int(keep.sum()),
                p95_px=float(np.percentile(errors, 95)), max_px=float(errors.max()),
                rotation_error_degrees=float(np.rad2deg(np.arccos(np.clip((np.trace(relative)-1)/2, -1, 1)))),
                proper_rotation=bool(np.allclose(camera[:, :3]@camera[:, :3].T, np.eye(3), atol=1e-8) and np.linalg.det(camera[:, :3]) > 0),
                positive_depth=bool(((data['vertices_normalized']*scale@camera[:, :3].T+camera[:, 3])[:, 2] > 0).all()),
                replay_max_px=float(abs(predicted-independent).max()), evaluation_global_scale=scale,
                focal_px=float(k[0, 0])))
            arrays[f'{stage}_{i}_pixels'], arrays[f'{stage}_{i}_errors'] = predicted, errors
    passed = fitted['termination']['success'] and fitted['polygon_coherence'] >= .99 and fitted['witness_target_positive'] and all(
        r['p95_px'] <= 3 and r['proper_rotation'] and r['positive_depth'] and r['replay_max_px'] <= 1e-5
        for r in rows if r['stage'] == 'final')
    np.savez_compressed(OUT/'evaluation.npz', **arrays)
    result = dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT', camera_results=rows,
        fit_summary=fitted, fixture_sha256=sha256_file(FIXTURE/'known-motion.npz'),
        producer_sha256=sha256_file(Path(__file__)), role='SILHOUETTE_CAMERA_CAPACITY_NOT_A_HEAD',
        case002_read=False, bone_read=False, real_video_inference=False, training=False, upload=False,
        head_acceptance='UNVERIFIED')
    (OUT/'report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'fit', 'evaluate', 'self-check'))
    phase = parser.parse_args().phase
    print(json.dumps(self_check())) if phase == 'self-check' else globals()[phase]()
