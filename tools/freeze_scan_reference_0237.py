"""Source-only region proposal and metric QA. Never emits a reconstructed head."""
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
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl
from scan_motion_truth_0230 import look_at_origin, sample_surface
from scan_surface_metric_0237 import triangle_tree, nearest_triangles, summary
from blender_camera_diagnostic import set_camera, projection_error

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
PROPOSAL = PILOT / 'scan-region-proposal-0237.json'
OUT = PILOT / 'fixed-scan-reference-0237-interface-replay'


def inside(points, box):
    return ((points >= box[0]) & (points < box[1])).all(axis=1)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first source region proposal')
    started = time.perf_counter()
    manifest_path, confirmation_path = PILOT / 'manifest.json', PILOT / 'provenance-confirmation.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    confirmation = json.loads(confirmation_path.read_text(encoding='utf-8'))
    proposal = json.loads(PROPOSAL.read_text(encoding='utf-8'))
    source = Path(next(a for a in manifest['inputs'] if a['id'] == 'real-case-001-skin')['path'])
    if (validate_input_assets(manifest, PILOT) or manifest['purpose'] != 'local_head_reconstruction_validation'
            or confirmation['manifest_sha256'] != sha256_file(manifest_path)
            or confirmation['cases']['real-case-001']['scan_units'] != 'millimeter'
            or proposal['case_id'] != 'real-case-001' or proposal['units'] != 'millimeter'
            or sha256_file(source) != proposal['source_sha256']):
        raise ValueError('Rights, source, units or case mismatch')
    vertices, faces = read_binary_stl(source)
    center = (vertices.max(axis=0) + vertices.min(axis=0)) / 2
    radius = np.ptp(vertices, axis=0).max() / 2
    points, full_ids, full_bary = sample_surface(vertices, faces, 5000, 230)
    tree = triangle_tree(vertices, faces, center)
    analytic_vertices = np.array([[-100., -100., 0.], [100., -100., 0.], [0., 100., 0.]])
    analytic_tree = triangle_tree(analytic_vertices, np.array([[0, 1, 2]]), np.zeros(3))
    analytic_distance, _ = nearest_triangles(analytic_tree, np.array([[0., 0., 2.]]), np.zeros(3))
    closest_vertex = float(np.linalg.norm(analytic_vertices - [0., 0., 2.], axis=1).min())
    if not np.isclose(analytic_distance[0], 2., atol=1e-6) or closest_vertex < 100:
        raise ValueError('Triangle interior fixture failed or accidentally tested a vertex')
    centroid = vertices[faces].mean(axis=1)
    base = inside(centroid, proposal['base_box_mm'])
    eyes = np.zeros(len(faces), bool)
    for ellipse in proposal['closed_eye_ellipses_xy_mm']:
        eyes |= np.sum(((centroid[:, :2] - ellipse['center']) / ellipse['radii']) ** 2, axis=1) <= 1
    visible = np.zeros(len(faces), bool)
    # Query only source scope, with no candidate/error-dependent support changes.
    for index in np.flatnonzero(base & ~eyes):
        point = centroid[index] - center
        for direction in ([0., 0., 1.], [1., 0., 1.], [-1., 0., 1.]):
            origin = np.array(direction) / np.linalg.norm(direction) * radius * 6
            ray = point - origin
            distance = float(np.linalg.norm(ray))
            hit = tree.ray_cast(Vector(origin), Vector(ray / distance), distance + .02)
            if hit[0] is not None and abs(hit[3] - distance) <= .01:
                visible[index] = True
                break
        if time.perf_counter() - started > 180:
            raise TimeoutError('Source-only reference budget exhausted')
    valid = base & ~eyes & visible
    labels = np.zeros(len(faces), np.int16)
    names = [r['id'] for r in proposal['ordered_regions']] + [proposal['remaining_region']]
    for label, region in enumerate(proposal['ordered_regions'], start=1):
        labels[valid & (labels == 0) & inside(centroid, region['box_mm'])] = label
    labels[valid & (labels == 0)] = len(names)
    all_points, all_faces, all_bary, groups = [points], [full_ids], [full_bary], [np.zeros(5000, np.int16)]
    region_records = []
    area = np.linalg.norm(np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]],
        vertices[faces[:, 2]] - vertices[faces[:, 0]]), axis=1) / 2
    for label, name in enumerate(names, start=1):
        ids = np.flatnonzero(labels == label)
        if not len(ids):
            raise ValueError('Missing source region: ' + name)
        sampled, local_faces, bary = sample_surface(vertices, faces[ids], 2048, 237 + label - 1)
        all_points.append(sampled)
        all_faces.append(ids[local_faces])
        all_bary.append(bary)
        groups.append(np.full(2048, label, np.int16))
        region_records.append({'id': name, 'faces': len(ids), 'area_mm2': float(area[ids].sum()), 'samples': 2048})
    all_points = np.concatenate(all_points)
    self_distance, _ = nearest_triangles(tree, all_points, center)
    if self_distance.max() > .001:
        raise ValueError('Source-self triangle replay exceeds declared numeric precision')
    OUT.mkdir()
    np.savez_compressed(OUT / 'regions.npz', face_region=labels, base_scope=base,
        closed_eye_exclusion=eyes, source_centroid_visible=visible, sample_points_mm=all_points,
        sample_source_face=np.concatenate(all_faces), sample_barycentric=np.concatenate(all_bary),
        sample_group=np.concatenate(groups), self_distance_mm=self_distance)
    (OUT / 'executed-proposal.json').write_bytes(PROPOSAL.read_bytes())
    (OUT / 'executed-preregistration.md').write_bytes((ROOT / 'docs/experiment-0237-fixed-scan-surface-protocol.md').read_bytes())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 720, 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world = bpy.data.worlds.new('Reference_Only_World')
    scene.world.color = (.08, .08, .08)
    mesh = bpy.data.meshes.new('Unchanged_Source_Only')
    mesh.from_pydata(((vertices - center) / radius).tolist(), [], faces.tolist())
    mesh.update()
    head = bpy.data.objects.new('SOURCE_REFERENCE_NOT_RECONSTRUCTION', mesh)
    scene.collection.objects.link(head)
    colors = [( .26, .26, .26), (.95, .30, .08), (.85, .08, .15), (.08, .65, .90),
        (.10, .75, .20), (.90, .75, .08), (.60, .18, .85), (.10, .30, .85)]
    for name, color in zip(['outside_face_scope'] + names, colors):
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        shader = material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (*color, 1)
        shader.inputs['Roughness'].default_value = .8
        mesh.materials.append(material)
    for polygon, label in zip(mesh.polygons, labels):
        polygon.material_index, polygon.use_smooth = int(label), True
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    lights = []
    for energy, size in ((500, 4.), (900, 2.)):
        bpy.ops.object.light_add(type='AREA')
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        lights.append(light)
    intrinsic = np.array([[1083.257881738314, 0, 360], [0, 1083.257881738314, 640], [0, 0, 1.]])
    renders = []
    for name, yaw in [('front', 0), ('yaw-45', -45), ('yaw+45', 45), ('yaw-90', -90), ('yaw+90', 90), ('back', 180)]:
        angle = np.deg2rad(yaw)
        e = look_at_origin(6 * np.array([np.sin(angle), 0., np.cos(angle)]))
        set_camera(camera, intrinsic, e, 720, 1280)
        bpy.context.view_layer.update()
        lights[0].location, lights[0].rotation_euler = camera.location, camera.rotation_euler
        lights[1].location = camera.location + camera.matrix_world.to_3x3() @ Vector((-2, 2, -1))
        lights[1].rotation_euler = (-lights[1].location).to_track_quat('-Z', 'Y').to_euler()
        path = OUT / (name + '-source-region-proposal.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        replay = projection_error(scene, camera, (points[:1000] - center) / radius, intrinsic, e, 720, 1280)
        if replay['max_px'] > .001:
            raise ValueError('Source preview camera replay failed')
        renders.append({'view': name, 'image': path.name, 'sha256': sha256_file(path),
            'extrinsic_normalized': e.tolist(), 'projection_replay': replay})
        if time.perf_counter() - started > 180:
            raise TimeoutError('Source-only reference budget exhausted')
    contract = {'case_id': 'real-case-001', 'review_status': 'UNVERIFIED',
        'role': 'fixed source-surface diagnostic, not a reconstructed head or full-head acceptance mask',
        'source_path': str(source), 'source_sha256': sha256_file(source), 'units': 'millimeter',
        'manifest_sha256': sha256_file(manifest_path), 'confirmation_sha256': sha256_file(confirmation_path),
        'proposal_sha256': sha256_file(PROPOSAL), 'regions_sha256': sha256_file(OUT / 'regions.npz'),
        'producer_sha256': sha256_file(Path(__file__)), 'metric_sha256': sha256_file(ROOT / 'tools/scan_surface_metric_0237.py'),
        'preregistration_sha256': sha256_file(OUT / 'executed-preregistration.md'),
        'numerical_center_mm': center.tolist(), 'numeric_backend': 'Blender BVH epsilon0, centered millimeters, float32 geometry',
        'face_regions': ['outside_face_scope'] + names, 'sample_groups': ['full_source_including_unscoped'] + names,
        'regions': region_records, 'source_total_area_mm2': float(area.sum()),
        'scoped_face_area_fraction': float(area[valid].sum() / area.sum()),
        'analytic_interior_distance_mm': float(analytic_distance[0]), 'analytic_closest_vertex_mm': closest_vertex,
        'source_self_distance': summary(self_distance), 'uncertainty': proposal['uncertainty'],
        'renders': renders, 'elapsed_seconds': time.perf_counter() - started,
        'limits': 'Coarse face-scope review pending. Full source samples retain unscoped scalp/neck/eyes/artifacts; neither source self-fit nor this mask is video-head acceptance.'}
    (OUT / 'contract.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'TECHNICAL_CHECK_PASSED', 'review_status': 'UNVERIFIED',
        'source_self_max_mm': float(self_distance.max()), 'scoped_face_area_fraction': contract['scoped_face_area_fraction'],
        'elapsed_seconds': contract['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
