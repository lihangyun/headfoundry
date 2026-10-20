"""Known-motion silhouette/focal capacity oracle,never video reconstruction."""
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'tools'))
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.camera import project

BASE = ROOT/'assets/private/real-capture-pilot-v1'
FIXTURE = BASE/'scan-motion-truth-0230-upright'
OUT = ROOT/'assets/private/silhouette-focal-0254'


def source_lock():
    manifest = json.loads((BASE/'manifest.json').read_text())
    skin = [r for r in manifest['inputs'] if r['id'] == 'real-case-001-skin']
    confirmation = json.loads((BASE/'provenance-confirmation.json').read_text())
    controls = json.loads((FIXTURE/'controls.json').read_text())
    generation = json.loads((FIXTURE/'generation-report.json').read_text())
    if (len(skin) != 1 or manifest['training_allowed'] is not False or manifest['upload_allowed'] is not False
            or validate_input_assets(dict(manifest, inputs=skin), BASE)
            or confirmation['manifest_sha256'] != sha256_file(BASE/'manifest.json')
            or confirmation['cases']['real-case-001']['scan_units'] != 'millimeter'
            or controls['source_sha256'] != skin[0]['sha256']
            or generation['execution_status'] != 'TECHNICAL_CHECK_PASSED'
            or generation['archive_sha256'] != sha256_file(FIXTURE/'known-motion.npz')):
        raise ValueError('Exact authorized case001 source/fixture required')
    return skin[0], controls


def render():
    import bpy
    from headfoundry.scan import read_binary_stl
    from blender_camera_diagnostic import set_camera, projection_error
    started = time.perf_counter()
    source, controls = source_lock()
    if OUT.exists():
        raise FileExistsError('Preserve first masks')
    OUT.mkdir()
    data = np.load(FIXTURE/'known-motion.npz', allow_pickle=False)
    raw, faces = read_binary_stl(Path(source['path']))
    vertices = (raw-np.array(controls['center_mm']))/controls['radius_mm']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new('EXACT_SOURCE_NOT_HEAD_OUTPUT')
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    mesh.update()
    obj = bpy.data.objects.new('UNCHANGED_SUPPLIED_SCAN', mesh)
    bpy.context.scene.collection.objects.link(obj)
    material = bpy.data.materials.new('White_Occupancy')
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1, 1, 1, 1)
    emission.inputs['Strength'].default_value = 1
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    mesh.materials.append(material)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 720, 1280
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    rows = []
    for name, ext in zip(data['view_names'], data['extrinsics_normalized']):
        if time.perf_counter()-started > 180:
            raise TimeoutError('Mask-generation budget exceeded')
        set_camera(camera, data['intrinsic'], ext, 720, 1280)
        bpy.context.view_layer.update()
        replay = projection_error(scene, camera, vertices, data['intrinsic'], ext, 720, 1280)
        if replay['max_px'] > .05:
            raise ValueError('Camera replay failed')
        p = OUT/(str(name)+'-occupancy.png')
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        rows.append(dict(view=str(name), image=p.name, sha256=sha256_file(p), replay=replay))
    if sha256_file(Path(source['path'])) != source['sha256']:
        raise ValueError('Original source changed')
    (OUT/'render-report.json').write_text(json.dumps(dict(status='TECHNICAL_CHECK_PASSED',
        role='SUPPLIED_SCAN_CAPACITY_ORACLE_NOT_RECONSTRUCTION', renders=rows,
        producer_sha256=sha256_file(Path(__file__)), source_sha256=source['sha256'],
        fixture_sha256=sha256_file(FIXTURE/'known-motion.npz'),
        elapsed_seconds=time.perf_counter()-started, blender_version=bpy.app.version_string), indent=2))


def intersect_unions(a, b):
    return [(max(lo, start), min(hi, end)) for lo, hi in a for start, end in b
            if max(lo, start) < min(hi, end)-1e-10]


def cone_intervals(a, b, contours):
    """All positive source-depth intervals inside one target polygon-cone union."""
    import cv2
    edges = np.concatenate([np.c_[p, np.roll(p, -1, axis=0)] for p in contours])
    delta = edges[:, 2:]-edges[:, :2]
    lines = np.c_[-delta[:, 1], delta[:, 0],
        delta[:, 1]*edges[:, 0]-delta[:, 0]*edges[:, 1]]
    den = b@lines.T
    roots = np.full(den.shape, np.nan)
    np.divide(-(a@lines.T)[None, :], den, out=roots, where=abs(den) > 1e-13)
    z = a[2]+roots*b[:, 2:]
    u = (a[0]+roots*b[:, 0:1])/np.where(abs(z) > 1e-13, z, np.nan)
    v = (a[1]+roots*b[:, 1:2])/np.where(abs(z) > 1e-13, z, np.nan)
    length2 = np.sum(delta*delta, axis=1)
    along = ((u-edges[None, :, 0])*delta[None, :, 0]
             +(v-edges[None, :, 1])*delta[None, :, 1])/np.maximum(length2, 1e-30)
    valid = (roots > 0)&(z > 1e-10)&(along >= -1e-9)&(along <= 1+1e-9)&(length2[None, :] > 0)
    cv_contours = [np.asarray(p, np.float32).reshape(-1, 1, 2) for p in contours]
    result = []
    for i in range(len(b)):
        cuts = roots[i, valid[i]].tolist()
        if abs(b[i, 2]) > 1e-13 and -a[2]/b[i, 2] > 0:
            cuts.append(float(-a[2]/b[i, 2]))
        cuts = [0.]+sorted(set(cuts))+[np.inf]
        intervals = []
        for lo, hi in zip(cuts[:-1], cuts[1:]):
            if hi-lo < 1e-10:
                continue
            depth = (lo+hi)/2 if np.isfinite(hi) else lo+max(1., abs(lo))
            p = a+depth*b[i]
            if p[2] <= 1e-10:
                continue
            xy = tuple((p[:2]/p[2]).tolist())
            inside = sum(cv2.pointPolygonTest(c, xy, False) >= 0 for c in cv_contours)%2
            if inside:
                intervals.append((lo, hi))
        result.append(intervals)
    return result


def self_check():
    square = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
    a, b = np.array([2., 0, 1]), np.array([[-1., 0, 1]])
    plain = cone_intervals(a, b, [square])[0]
    assert np.allclose(plain, [[.5, np.inf]])
    hole = cone_intervals(a, b, [square, square*.25])[0]
    assert np.allclose(hole, [[.5, 1.4], [3, np.inf]])
    assert not intersect_unions(hole, [(1.5, 2.5)])
    assert np.allclose(cone_intervals(np.array([0., 0, -1]), np.array([[0., 0, 1]]), [square])[0], [[1, np.inf]])
    assert not cone_intervals(np.array([3., 3, 1]), np.array([[1., 1, 0]]), [square])[0]
    return dict(square=True, holes_preserved=True, disjoint_intersection=True, cheirality=True)


def polygons(mask):
    import cv2
    found, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return [c[:, 0].astype(float)+.5 for c in found]


def arc_samples(contours, count=512):
    pieces = [np.c_[p, np.roll(p, -1, axis=0)] for p in contours]
    edges = np.concatenate(pieces)
    length = np.linalg.norm(edges[:, 2:]-edges[:, :2], axis=1)
    cumulative = np.cumsum(length)
    if not len(cumulative) or cumulative[-1] <= 0:
        raise ValueError('No nondegenerate source perimeter')
    where = (np.arange(count)+.5)*cumulative[-1]/count
    ids = np.searchsorted(cumulative, where)
    previous = np.r_[0., cumulative[:-1]][ids]
    return edges[ids, :2]+((where-previous)/length[ids])[:, None]*(edges[ids, 2:]-edges[ids, :2])


def coherence(k, cameras, contours, samples):
    inv = np.linalg.inv(k)
    feasible = []
    for i, (source, pixels) in enumerate(zip(cameras, samples)):
        center = -source[:, :3].T@source[:, 3]
        rays = np.c_[pixels, np.ones(len(pixels))]@inv.T@source[:, :3]
        unions = [[(0., np.inf)] for _ in pixels]
        for j, target in enumerate(cameras):
            if i == j:
                continue
            a = k@(target[:, :3]@center+target[:, 3])
            b = rays@target[:, :3].T@k.T
            intervals = cone_intervals(a, b, contours[j])
            unions = [intersect_unions(u, v) for u, v in zip(unions, intervals)]
        feasible.append(np.array([bool(u) for u in unions]))
    feasible = np.array(feasible)
    return float(feasible.mean()), feasible


def run():
    import cv2
    from PIL import Image, ImageDraw
    from scipy.optimize import minimize_scalar
    started = time.perf_counter()
    if (OUT/'report.json').exists():
        raise FileExistsError('Refuse repeated experiment')
    source, _ = source_lock()
    checks = self_check()
    rendered = json.loads((OUT/'render-report.json').read_text())
    data = np.load(FIXTURE/'known-motion.npz', allow_pickle=False)
    k, truth = data['intrinsic'], data['extrinsics_normalized']
    if rendered['fixture_sha256'] != sha256_file(FIXTURE/'known-motion.npz'):
        raise ValueError('Rendered fixture changed')
    contours, samples, perimeters = [], [], []
    sheet = Image.new('RGB', (1080, 1320), (24, 24, 24))
    for i, entry in enumerate(rendered['renders']):
        path = OUT/entry['image']
        if sha256_file(path) != entry['sha256']:
            raise ValueError('Mask changed')
        with Image.open(path) as image:
            alpha = np.array(image.getchannel('A'))
        mask = alpha >= 128
        contours.append(polygons(mask))
        eroded = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1)
        samples.append(arc_samples(polygons(eroded)))
        perimeters.append(dict(target_contours=len(contours[-1]), foreground_pixels=int(mask.sum())))
        preview = Image.fromarray(np.repeat((mask*200).astype(np.uint8)[:, :, None], 3, axis=2))
        draw = ImageDraw.Draw(preview)
        for p in samples[-1][::4]:
            draw.ellipse((p[0]-1, p[1]-1, p[0]+1, p[1]+1), fill=(20, 255, 80))
        sheet.paste(preview.resize((360, 640)), (i%3*360, i//3*660+20))
        ImageDraw.Draw(sheet).text((i%3*360+4, i//3*660+3), entry['view']+' / SUPPLIED SCAN ONLY', fill='white')
    sheet.save(OUT/'mask-review.jpg', quality=90)
    trace = []
    def evaluate(f):
        if time.perf_counter()-started > 180:
            raise TimeoutError('Coherence budget exceeded')
        candidate_k, cameras = k.copy(), truth.copy()
        candidate_k[0, 0] = candidate_k[1, 1] = f
        cameras[:, :, 3] *= f/k[0, 0]
        score, feasible = coherence(candidate_k, cameras, contours, samples)
        trace.append(dict(focal_px=float(f), coherence=score))
        return 1-score
    true_score, true_flags = coherence(k, truth, contours, samples)
    result = dict(status='REJECT', true_coherence=true_score, self_checks=checks, perimeters=perimeters)
    archive = dict(true_feasible=true_flags, contour_samples=np.array(samples))
    replay = 0.
    for ext, pixels in zip(truth, data['pixels']):
        observed = cv2.projectPoints(data['vertices_normalized'], cv2.Rodrigues(ext[:, :3])[0], ext[:, 3], k, None)[0][:, 0]
        replay = max(replay, float(np.max(abs(observed-pixels))))
    if replay > 1e-5:
        raise ValueError('Original independent camera replay failed')
    if true_score >= .99:
        solved = minimize_scalar(evaluate, bounds=(400., 4000.), method='bounded', options=dict(maxiter=32, xatol=.1))
        recovered = k.copy()
        recovered[0, 0] = recovered[1, 1] = float(solved.x)
        cameras = truth.copy()
        cameras[:, :, 3] *= solved.x/k[0, 0]
        rows, all_errors = [], []
        for i, ext in enumerate(cameras):
            # Immutable visible populations from the source fixture;no new filtering.
            keep = data['visible'][i]
            pts = data['vertices_normalized'][keep]
            predicted = project(recovered@ext, pts)
            independent = cv2.projectPoints(pts, cv2.Rodrigues(ext[:, :3])[0], ext[:, 3], recovered, None)[0][:, 0]
            error = np.linalg.norm(predicted-data['pixels'][i, keep], axis=1)
            rows.append(dict(view=str(data['view_names'][i]), points=len(pts),
                p95_px=float(np.percentile(error, 95)), max_px=float(error.max()),
                replay_max_px=float(abs(predicted-independent).max()),
                proper_rotation=bool(np.allclose(ext[:, :3]@ext[:, :3].T, np.eye(3), atol=1e-8) and np.linalg.det(ext[:, :3]) > 0),
                positive_depth=bool(((data['vertices_normalized']@ext[:, :3].T+ext[:, 3])[:, 2] > 0).all())))
            archive[f'errors_{i}'] = error
            all_errors.append(error)
        result.update(optimized_focal_px=float(solved.x), truth_focal_px=float(k[0, 0]),
            optimizer_success=bool(solved.success), optimizer_message=str(solved.message), evaluations=int(solved.nfev),
            recovered_coherence=float(1-solved.fun), camera_results=rows)
        if solved.success and all(r['p95_px'] <= 3 and r['proper_rotation'] and r['positive_depth'] and r['replay_max_px'] <= 1e-5 for r in rows):
            result['status'] = 'TECHNICAL_CHECK_PASSED'
        archive.update(intrinsic=recovered, cameras=cameras)
    else:
        result['reason'] = 'Truth raster coherence prerequisite failed;no focal optimization'
    result.update(trace=trace, elapsed_seconds=time.perf_counter()-started,
        original_camera_replay_max_px=replay, source_sha256=source['sha256'],
        fixture_sha256=sha256_file(FIXTURE/'known-motion.npz'), producer_sha256=sha256_file(Path(__file__)),
        protocol_sha256=sha256_file(ROOT/'docs/experiment-0254-silhouette-focal-observability.md'),
        role='KNOWN_MOTION_ORACLE_NOT_REAL_CAMERA_OR_HEAD', case002_read=False, bone_read=False,
        real_video_inference=False, training=False, upload=False, head_acceptance='UNVERIFIED')
    np.savez_compressed(OUT/'results.npz', **archive)
    (OUT/'report.json').write_text(json.dumps(result, indent=2))
    (OUT/'executed-protocol.md').write_bytes((ROOT/'docs/experiment-0254-silhouette-focal-observability.md').read_bytes())
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    if '--render' in sys.argv:
        render()
    elif '--self-check' in sys.argv:
        print(json.dumps(self_check()))
    else:
        run()
