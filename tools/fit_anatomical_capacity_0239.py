"""One real-scan identity-prior oracle; absolutely not video reconstruction."""
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl
from scan_motion_truth_0230 import sample_surface, look_at_origin
from scan_surface_metric_0237 import apply_similarity, triangle_tree, nearest_triangles, summary, backend_versions
from anatomical_capacity_0239 import fit_similarity, box_quadratic, barycentric_closest, mesh_guard
from blender_camera_diagnostic import set_camera, projection_error

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
REFERENCE = PILOT / 'fixed-scan-reference-0237-interface-replay'
READY = PILOT / 'anatomical-prior-readiness-0239'
LOCK = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
FAILED = PILOT / 'anatomical-capacity-0239'
OUT = PILOT / 'anatomical-capacity-0239-numerical-replay'


def closest_support(tree, points, center):
    positions, ids = [], []
    for point in points - center:
        location, _, face, _ = tree.find_nearest(Vector(point))
        if location is None or face is None:
            raise ValueError('Missing closest support; no observation trimming allowed')
        positions.append(np.asarray(location) + center)
        ids.append(face)
    return np.array(positions), np.array(ids, np.int64)


def visible_support(tree, points, center, radius):
    result = np.zeros(len(points), bool)
    for index, point in enumerate(points - center):
        for direction in ([0., 0., 1.], [1., 0., 1.], [-1., 0., 1.]):
            origin = np.array(direction) / np.linalg.norm(direction) * 6 * radius
            ray = point - origin
            distance = float(np.linalg.norm(ray))
            hit = tree.ray_cast(Vector(origin), Vector(ray / distance), distance + .02)
            if hit[0] is not None and abs(hit[3] - distance) <= .01:
                result[index] = True
                break
    return result


def render_variants(source, source_faces, prior, oracle, faces, center, radius):
    started = time.perf_counter()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 720, 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('Oracle_Not_Reconstruction_World')
    scene.world.color = (.08, .08, .08)
    material = bpy.data.materials.new('Shared_Neutral_Clay')
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.5, .5, .5, 1)
    shader.inputs['Roughness'].default_value = .8
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    lights = []
    for energy, size in ((500, 4.), (900, 2.)):
        bpy.ops.object.light_add(type='AREA')
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        lights.append(light)
    k = np.array([[1083.257881738314, 0, 360], [0, 1083.257881738314, 640], [0, 0, 1.]])
    records = []
    variants = [('supplied-source', source, source_faces), ('aligned-neutral-prior', prior, faces)]
    if oracle is not None:
        variants.append(('scan-fit-oracle-NOT-VIDEO', oracle, faces))
    for name, vertices, triangles in variants:
        display = (vertices - center) / radius
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(display.tolist(), [], triangles.tolist())
        mesh.update()
        head = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(head)
        mesh.materials.append(material)
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        for view, yaw in [('front', 0), ('yaw-45', -45), ('yaw+45', 45), ('yaw-90', -90), ('yaw+90', 90), ('back', 180)]:
            angle = np.deg2rad(yaw)
            e = look_at_origin(6 * np.array([np.sin(angle), 0, np.cos(angle)]))
            set_camera(camera, k, e, 720, 1280)
            bpy.context.view_layer.update()
            lights[0].location, lights[0].rotation_euler = camera.location, camera.rotation_euler
            lights[1].location = camera.location + camera.matrix_world.to_3x3() @ Vector((-2, 2, -1))
            lights[1].rotation_euler = (-lights[1].location).to_track_quat('-Z', 'Y').to_euler()
            replay = projection_error(scene, camera, display, k, e, 720, 1280)
            if replay['max_px'] > .001:
                raise ValueError('Common-camera oracle preview replay failed')
            path = OUT / (name + '-' + view + '.png')
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            records.append({'variant': name, 'view': view, 'image': path.name,
                'sha256': sha256_file(path), 'projection_replay': replay})
            if time.perf_counter() - started > 60:
                raise TimeoutError('Single oracle rendering budget exhausted')
        bpy.data.objects.remove(head, do_unlink=True)
        bpy.data.meshes.remove(mesh)
    return records


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first real-scan prior-capacity oracle')
    started = time.perf_counter()
    numerical = json.loads((FAILED / 'numerical-repair-reference.json').read_text(encoding='utf-8'))
    if (numerical['status'] != 'TECHNICAL_CHECK_PASSED'
            or numerical['original_objective_sha256'] != sha256_file(FAILED / 'fit-step-00.npz')
            or numerical['numeric_helper_sha256'] != sha256_file(ROOT / 'tools/anatomical_capacity_0239.py')):
        raise ValueError('Independent unchanged-objective numerical repair check required')
    manifest_path, confirmation_path = PILOT / 'manifest.json', PILOT / 'provenance-confirmation.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    confirmation = json.loads(confirmation_path.read_text(encoding='utf-8'))
    contract = json.loads((REFERENCE / 'contract.json').read_text(encoding='utf-8'))
    ready = json.loads((READY / 'report.json').read_text(encoding='utf-8'))
    review = json.loads((READY / 'review.json').read_text(encoding='utf-8'))
    if (validate_input_assets(manifest, PILOT) or manifest['purpose'] != 'local_head_reconstruction_validation'
            or confirmation['manifest_sha256'] != sha256_file(manifest_path)
            or confirmation['cases']['real-case-001']['scan_units'] != 'millimeter'
            or contract['manifest_sha256'] != sha256_file(manifest_path)
            or contract['confirmation_sha256'] != sha256_file(confirmation_path)
            or contract['review_status'] != 'TECHNICAL_CHECK_PASSED'
            or contract['regions_sha256'] != sha256_file(REFERENCE / 'regions.npz')
            or contract['review_sha256'] != sha256_file(REFERENCE / 'review.json')
            or contract['backend_versions'] != backend_versions()
            or ready['asset_lock_sha256'] != sha256_file(LOCK)
            or review['status'] != 'TECHNICAL_CHECK_PASSED'
            or review['readiness_report_sha256'] != sha256_file(READY / 'report.json')
            or ready['neutral_archive_sha256'] != sha256_file(READY / 'neutral-prior.npz')):
        raise ValueError('Original consent, fixed reference or native-prior readiness changed')
    asset = json.loads(LOCK.read_text(encoding='utf-8'))
    model = FlameIdentityModel.from_asset_record(asset, LOCK.parent)
    source_entry = next(a for a in manifest['inputs'] if a['id'] == 'real-case-001-skin')
    if source_entry['sha256'] != contract['source_sha256']:
        raise ValueError('Only frozen case001 skin source allowed')
    source, source_faces = read_binary_stl(source_entry['path'])
    reference = np.load(REFERENCE / 'regions.npz', allow_pickle=False)
    prepared = np.load(READY / 'neutral-prior.npz', allow_pickle=False)
    if not np.array_equal(prepared['vertices'], model.template) or not np.array_equal(prepared['faces'], model.faces):
        raise ValueError('Readiness/native model geometry mismatch')
    center = np.asarray(contract['numerical_center_mm'])
    radius = float(np.ptp(source, axis=0).max() / 2)
    group = reference['sample_group']
    train = (group > 0) & (np.arange(len(group)) % 2 == 0)
    targets = reference['sample_points_mm'][train]
    area = np.array([r['area_mm2'] for r in contract['regions']])
    weights = area[group[train] - 1]
    weights /= weights.mean()
    if len(targets) != 7168:
        raise ValueError('Frozen training quadrature changed')
    faces, native = model.faces, model.template
    source_tip = int(source[:, 2].argmax())
    if not np.any(reference['face_region'][np.any(source_faces == source_tip, axis=1)] == 1):
        raise ValueError('Maximal anterior source anchor is not in the fixed nasal scope')
    transform = np.diag([1000., 1000., 1000., 1.])
    transform[:3, 3] = source[source_tip] - native[native[:, 2].argmax()] * 1000
    OUT.mkdir()
    (OUT / 'executed-preregistration.md').write_bytes((ROOT / 'docs/experiment-0239-real-scan-prior-capacity.md').read_bytes())
    controls = {'role': 'SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION', 'source_sha256': source_entry['sha256'],
        'reference_contract_sha256': sha256_file(REFERENCE / 'contract.json'),
        'readiness_review_sha256': sha256_file(READY / 'review.json'), 'asset_lock_sha256': sha256_file(LOCK),
        'asset_attribution': asset['attribution'], 'producer_sha256': sha256_file(Path(__file__)),
        'numerics_sha256': sha256_file(ROOT / 'tools/anatomical_capacity_0239.py'),
        'metric_sha256': sha256_file(ROOT / 'tools/scan_surface_metric_0237.py'),
        'backend_versions': backend_versions(), 'identity_dimensions': 300, 'bound': 3., 'regularizer_mm2': 4.,
        'alignment_iterations': 10, 'identity_iterations': 5, 'initial_similarity': transform.tolist(),
        'video_or_case002_used': False, 'source_used_for_fit': True}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    alignment = []
    for iteration in range(10):
        current = apply_similarity(native, transform)
        closest, _ = closest_support(triangle_tree(current, faces, center), targets, center)
        transform = fit_similarity(closest, targets, weights) @ transform
        scale = float(np.linalg.norm(transform[:3, :3], axis=1).mean())
        rotation = transform[:3, :3] / scale
        angle = float(np.rad2deg(np.arccos(np.clip((np.trace(rotation) - 1) / 2, -1, 1))))
        if not 700 <= scale <= 1300 or angle > 15:
            raise ValueError('Single similarity outside predeclared pose/scale guard')
        alignment.append({'iteration': iteration, 'scale_mm_per_model_unit': scale, 'rotation_deg': angle})
        print(json.dumps({'alignment': alignment[-1]}), flush=True)
    prior = apply_similarity(native, transform)
    directions = np.einsum('ij,vjk->vik', transform[:3, :3], model.shape_directions)
    coefficients, current, history = np.zeros(300), prior.copy(), []
    for iteration in range(5):
        tree = triangle_tree(current, faces, center)
        closest, ids = closest_support(tree, targets, center)
        bary = barycentric_closest(closest, current[faces[ids]])
        base = np.einsum('ni,nij->nj', bary, prior[faces[ids]])
        interpolated = np.einsum('ni,nijk->njk', bary, directions[faces[ids]])
        matrix = (interpolated * np.sqrt(weights)[:, None, None]).reshape(-1, 300)
        rhs = ((targets - base) * np.sqrt(weights)[:, None]).ravel()
        h, g = matrix.T @ matrix + 4 * np.eye(300), matrix.T @ rhs
        if iteration == 0:
            original = np.load(FAILED / 'fit-step-00.npz', allow_pickle=False)
            if any(not np.array_equal(a, original[key]) for a, key in
                    ((h, 'hessian'), (g, 'linear'), (ids, 'closest_face'), (bary, 'barycentric'),
                     (targets, 'targets_mm'), (weights, 'weights'))):
                raise ValueError('Numerical repair changed first objective or source data')
        coefficients, qp = box_quadratic(h, g, coefficients)
        np.savez_compressed(OUT / f'fit-step-{iteration:02d}.npz', coefficients=coefficients,
            hessian=h, linear=g, closest_face=ids, barycentric=bary, targets_mm=targets, weights=weights)
        if not qp['converged']:
            raise ValueError('Fixed box-QP iteration budget did not meet KKT')
        current = apply_similarity(model.neutral_vertices(coefficients), transform)
        replay = prior + np.einsum('vck,k->vc', directions, coefficients)
        if abs(replay - current).max() > 1e-9:
            raise ValueError('Frozen similarity/identity field replay failed')
        distance, _ = nearest_triangles(triangle_tree(current, faces, center), targets, center)
        history.append({'iteration': iteration, 'qp': qp, 'train': summary(distance),
            'maximum_absolute_identity': float(abs(coefficients).max())})
        print(json.dumps({'identity': history[-1]}), flush=True)
        if time.perf_counter() - started > 180:
            raise TimeoutError('Single real-scan capacity fitting budget exhausted')
    guard = mesh_guard(current, prior, faces)
    source_tree = triangle_tree(source, source_faces, center)
    results = {}
    for name, vertices in [('aligned_neutral', prior), ('scan_fit_oracle', current)]:
        tree = triangle_tree(vertices, faces, center)
        distances, nearest_face = nearest_triangles(tree, reference['sample_points_mm'], center)
        reverse_points, reverse_face, reverse_bary = sample_surface(vertices, faces, 5000, 237)
        reverse, nearest_source = nearest_triangles(source_tree, reverse_points, center)
        closest, _ = closest_support(tree, targets, center)
        visible = visible_support(tree, closest, center, radius)
        stats = {label: summary(distances[group == index]) for index, label in enumerate(contract['sample_groups'])}
        odd = (group > 0) & ~train
        results[name] = {'source_to_surface': stats, 'full_reverse': summary(reverse),
            'odd_region_quadrature': {label: summary(distances[odd & (group == index)])
                for index, label in enumerate(contract['sample_groups']) if index > 0},
            'fit_nearest_firsthit_visible_fraction': float(visible.mean()),
            'hidden_supports': int((~visible).sum()),
            'all_face_regions_p95_2mm': all(stats[label]['p95_mm'] <= 2 for label in contract['sample_groups'][1:])}
        np.savez_compressed(OUT / (name + '-evaluation.npz'), source_distances_mm=distances,
            nearest_prior_face=nearest_face, reverse_mm=reverse, reverse_points_mm=reverse_points,
            reverse_face=reverse_face, reverse_barycentric=reverse_bary, nearest_source_face=nearest_source,
            fit_support_firsthit_visible=visible)
        np.savez_compressed(OUT / (name + '-SCAN-ORACLE-NOT-VIDEO.npz'), vertices=vertices, faces=faces)
        with (OUT / (name + '-SCAN-ORACLE-NOT-VIDEO.obj')).open('x', encoding='utf-8') as stream:
            stream.write('# SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION; original licensed FLAME2023 Open topology\n')
            for point in vertices:
                stream.write('v ' + ' '.join(f'{x:.12f}' for x in point) + '\n')
            for face in faces:
                stream.write('f ' + ' '.join(str(int(x) + 1) for x in face) + '\n')
    np.savez_compressed(OUT / 'replay.npz', coefficients=coefficients, frozen_model_to_scan=transform,
        prior=prior, oracle=current, faces=faces, training_population=train)
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'role': 'SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION', 'mesh_guard': guard, 'results': results,
        'diagnostic_capacity_status': 'TECHNICAL_CHECK_PASSED' if guard['passed'] and results['scan_fit_oracle']['all_face_regions_p95_2mm'] else 'REJECT',
        'alignment': alignment, 'identity_history': history, 'fit_seconds': time.perf_counter() - started,
        'source_uncertainty': contract['uncertainty'], 'native_boundary_edges': ready['boundary_edges'],
        'limits': 'Scan-fitted identity coefficients, not video-only output. Regional quadrature is not an independent subject. Hidden proximity, original open topology and source defects preclude anatomical/full-head acceptance.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if time.perf_counter() - started > 180:
        raise TimeoutError('Single fit/evaluation budget exhausted before rendering')
    renders = render_variants(source, source_faces, prior, current if guard['passed'] else None, faces, center, radius)
    (OUT / 'render-report.json').write_text(json.dumps({'role': report['role'], 'renders': renders,
        'oracle_rendered': guard['passed'], 'source_center_and_radius_common': True}, indent=2), encoding='utf-8')
    print(json.dumps({'diagnostic_capacity_status': report['diagnostic_capacity_status'], 'mesh_guard': guard,
        'results': results, 'fit_seconds': report['fit_seconds']}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
