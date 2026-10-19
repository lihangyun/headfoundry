"""Blender source-only known3D diagnostic: no photo fit, training or completion."""
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file,validate_input_assets
from headfoundry.scan import read_binary_stl
from headfoundry.camera import project
from blender_camera_diagnostic import set_camera,projection_error
from scan_motion_truth_0230 import look_at_origin,sample_surface

PILOT=ROOT/'assets/private/real-capture-pilot-v1'
FIRST=PILOT/'scan-motion-truth-0230'
OUT=PILOT/'scan-motion-truth-0230-upright'
PATTERNED='--patterned' in sys.argv
if PATTERNED:
    OUT=PILOT/'scan-pattern-observations-0232'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first scan motion diagnostic')
    started=time.perf_counter()
    manifest=json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    confirmation=json.loads((PILOT/'provenance-confirmation.json').read_text(encoding='utf-8'))
    if validate_input_assets(manifest,PILOT) or confirmation['manifest_sha256']!=sha256_file(PILOT/'manifest.json'):
        raise ValueError('Source rights/hash/stage confirmation failed')
    if confirmation['cases']['real-case-001']['scan_units']!='millimeter':
        raise ValueError('Explicit millimeter confirmation required')
    source=Path(next(a for a in manifest['inputs'] if a['id']=='real-case-001-skin')['path'])
    raw,faces=read_binary_stl(source)
    center=(raw.max(0)+raw.min(0))/2
    radius=float(np.ptp(raw,axis=0).max()/2)
    vertices=(raw-center)/radius
    points,triangle_ids,bary=sample_surface(vertices,faces)
    points_mm=np.einsum('ni,nij->nj',bary,raw[faces[triangle_ids]])
    if not np.allclose(points*radius+center,points_mm,atol=1e-9,rtol=0):
        raise ValueError('Similarity inverse point replay failed')
    original=np.load(FIRST/'known-motion.npz',allow_pickle=False)
    if (not np.array_equal(triangle_ids,original['source_triangle_ids'])
            or not np.array_equal(bary,original['source_barycentric'])
            or not np.array_equal(points,original['vertices_normalized'])):
        raise ValueError('Axis repair must reuse exact original samples')
    intrinsic=np.array([[1083.257881738314,0,360],[0,1083.257881738314,640],[0,0,1.]])
    specs=[('front',0,0),('yaw-10',-10,0),('yaw+10',10,0),('yaw-30',-30,0),('yaw+30',30,0),('pitch+10',0,10)]
    extrinsics=[]
    for _,yaw,pitch in specs:
        y,p=np.deg2rad([yaw,pitch])
        location=6*np.array([np.sin(y)*np.cos(p),np.sin(p),np.cos(y)*np.cos(p)])
        extrinsics.append(look_at_origin(location))
    extrinsics=np.array(extrinsics)
    raw_extrinsics=extrinsics.copy()
    raw_extrinsics[:,:,3]=extrinsics[:,:,3]*radius-np.einsum('vij,j->vi',extrinsics[:,:,:3],center)
    OUT.mkdir()
    controls={'source_sha256':sha256_file(source),'manifest_sha256':sha256_file(PILOT/'manifest.json'),
        'confirmation_sha256':sha256_file(PILOT/'provenance-confirmation.json'),
        'tool_sha256':sha256_file(Path(__file__)),'geometry_helper_sha256':sha256_file(ROOT/'tools/scan_motion_truth_0230.py'),
        'camera_helper_sha256':sha256_file(ROOT/'tools/blender_camera_diagnostic.py'),
        'center_mm':center.tolist(),'radius_mm':radius,'samples':len(points),'seed':230,
        'views':specs,'intrinsic':intrinsic.tolist(),'visibility_tolerance_mm':.01,
        'source_axes':'case001 visually verified +Y up,+Z face; OpenCV camera y down',
        'first_wrong_axis_controls_sha256':sha256_file(FIRST/'controls.json'),
        'first_wrong_axis_archive_sha256':sha256_file(FIRST/'known-motion.npz'),
        'units':'original STL mm; normalized display similarity only','role':'SOURCE_DIAGNOSTIC_NOT_RECONSTRUCTION'}
    controls['appearance']='object-coordinate noise48/detail2/roughness0.5,ramp0.15-0.75,emission1,Standard,RGBA' if PATTERNED else 'neutral source clay'
    (OUT/'controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
    # Two sheets on one ray: the back material point must not inherit front visibility.
    check_vertices=[(-2,-2,0),(2,-2,0),(0,2,0),(-2,-2,-1),(2,-2,-1),(0,2,-1)]
    check=BVHTree.FromPolygons(check_vertices,[(0,1,2),(3,4,5)],all_triangles=True)
    check_hit=check.ray_cast(Vector((0,0,5)),Vector((0,0,-1)))[0]
    if check_hit is None or np.linalg.norm(np.array(check_hit))>1e-6 or np.linalg.norm(np.array(check_hit)-[0,0,-1])<.99:
        raise ValueError('First-hit occlusion self-check failed')
    tree=BVHTree.FromPolygons(vertices.tolist(),faces.tolist(),all_triangles=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh=bpy.data.meshes.new('EXACT_SOURCE_SCAN')
    mesh.from_pydata(vertices.tolist(),[],faces.tolist())
    mesh.update()
    head=bpy.data.objects.new('SUPPLIED_SCAN_NOT_RECONSTRUCTED',mesh)
    bpy.context.scene.collection.objects.link(head)
    material=bpy.data.materials.new('Neutral_Source_Clay')
    material.use_nodes=True
    shader=material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.4,.4,.4,1)
    shader.inputs['Roughness'].default_value=.8
    if PATTERNED:
        nodes,links=material.node_tree.nodes,material.node_tree.links
        nodes.clear()
        coordinates=nodes.new('ShaderNodeTexCoord')
        noise=nodes.new('ShaderNodeTexNoise')
        noise.noise_dimensions='3D'
        noise.inputs['Scale'].default_value=48
        noise.inputs['Detail'].default_value=2
        noise.inputs['Roughness'].default_value=.5
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(.15,.15,.15,1)
        ramp.color_ramp.elements[1].color=(.75,.75,.75,1)
        emission=nodes.new('ShaderNodeEmission')
        emission.inputs['Strength'].default_value=1
        output=nodes.new('ShaderNodeOutputMaterial')
        links.new(coordinates.outputs['Object'],noise.inputs['Vector'])
        links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],emission.inputs['Color'])
        links.new(emission.outputs['Emission'],output.inputs['Surface'])
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth=True
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x,scene.render.resolution_y=720,1280
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    if PATTERNED:
        scene.render.image_settings.color_mode='RGBA'
        scene.render.film_transparent=True
        scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('Diagnostic_World')
    scene.world.color=(.04,.04,.04)
    bpy.ops.object.camera_add()
    camera=bpy.context.object
    scene.camera=camera
    lights=[]
    for energy,size in ((500,3),(700,2)):
        bpy.ops.object.light_add(type='AREA')
        light=bpy.context.object
        light.data.energy,light.data.size=energy,size
        lights.append(light)
    projected,visibility,gaps,rows=[],[],[],[]
    for view_index,((name,_,_),extrinsic,raw_extrinsic) in enumerate(zip(specs,extrinsics,raw_extrinsics)):
        if time.perf_counter()-started>180:
            raise TimeoutError('Single source motion generation budget exhausted')
        depth=(vertices@extrinsic[:,:3].T+extrinsic[:,3])[:,2]
        if depth.min()<=0 or abs(np.linalg.det(extrinsic[:,:3])-1)>1e-8:
            raise ValueError('Invalid declared camera')
        pixels=project(intrinsic@extrinsic,points)
        raw_pixels=project(intrinsic@raw_extrinsic,points_mm)
        replay_mm=float(abs(pixels-raw_pixels).max())
        if replay_mm>1e-8:
            raise ValueError('Original-mm camera projection differs')
        location=-extrinsic[:,:3].T@extrinsic[:,3]
        hit_gap=np.full(len(points),np.inf)
        for index,point in enumerate(points):
            hit,_,_,_=tree.ray_cast(Vector(location),Vector(point-location))
            if hit is not None:
                hit_gap[index]=np.linalg.norm(np.asarray(hit)-point)*radius
        visible=(hit_gap<=.01)&(pixels[:,0]>=0)&(pixels[:,0]<720)&(pixels[:,1]>=0)&(pixels[:,1]<1280)
        projected.append(pixels)
        visibility.append(visible)
        gaps.append(hit_gap)
        set_camera(camera,intrinsic,extrinsic,720,1280)
        bpy.context.view_layer.update()
        for index,light in enumerate(lights):
            light.location=camera.location+camera.matrix_world.to_3x3()@Vector(((-2 if index else 0),1 if index else 0,-1))
            light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
        replay=projection_error(scene,camera,vertices,intrinsic,extrinsic,720,1280)
        if replay['max_px']>.05:
            raise ValueError('Independent Blender camera replay failed')
        path=OUT/f'{name}-supplied-scan.png'
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        rows.append({'view':name,'image':path.name,'image_sha256':sha256_file(path),
            'visible_points':int(visible.sum()),'mm_projection_replay_max_px':replay_mm,'blender_projection_replay':replay})
    archive=OUT/'known-motion.npz'
    np.savez_compressed(archive,point_ids=np.arange(len(points)),vertices_normalized=points,vertices_mm=points_mm,
        source_triangle_ids=triangle_ids,source_barycentric=bary,pixels=np.array(projected),visible=np.array(visibility),
        hit_gap_mm=np.array(gaps),intrinsic=intrinsic,extrinsics_normalized=extrinsics,extrinsics_mm=raw_extrinsics,
        view_names=np.array([s[0] for s in specs]))
    if sha256_file(source)!=controls['source_sha256']:
        raise ValueError('Original scan changed')
    report={'execution_status':'TECHNICAL_CHECK_PASSED','head_acceptance':'UNVERIFIED','role':'SOURCE_DIAGNOSTIC_NOT_RECONSTRUCTION',
        'occlusion_self_check':'TECHNICAL_CHECK_PASSED','renders':rows,'archive_sha256':sha256_file(archive),
        'source_unchanged':True,'elapsed_seconds':time.perf_counter()-started,'blender_version':bpy.app.version_string,
        'limits':'Declared cameras on an unchanged supplied scan; not video-recovered cameras or subject reconstruction.'}
    if PATTERNED:
        reference=OUT.parent/'scan-motion-truth-0230-upright/known-motion.npz'
        previous,current=np.load(reference,allow_pickle=False),np.load(archive,allow_pickle=False)
        if set(previous.files)!=set(current.files) or any(not np.array_equal(previous[key],current[key]) for key in previous.files):
            raise ValueError('Diagnostic appearance mode changed geometry/camera/visibility arrays')
        report.update(geometry_reference_sha256=sha256_file(reference),all_geometry_fields_exactly_equal=True,
            limits='Synthetic patterned supplied scan for local observation validation only; no training, recovered subject texture, real cameras or reconstructed head.')
    (OUT/'generation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT/'failure.json').exists():
            (OUT/'failure.json').write_text(json.dumps({'status':'REJECT','error':str(error)},indent=2),encoding='utf-8')
        raise
