"""Owned fixed known-camera input renderer;no model or patient data."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_camera_diagnostic import set_camera,projection_error

OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
K=np.array([[1200.,0,360],[0,1200,640],[0,0,1.]])
reports={}
for name,angle in [('room',0),('front',0),('plus60',60),('minus60',-60)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('BlueWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.06,.13,.24,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
    scene.view_settings.look='AgX - Medium High Contrast'
    if name=='room':
        vertices_all=[]
        panels=[([[-2,-2,2.5],[2,-2,2.5],[2,1.5,2.5],[-2,1.5,2.5]],(.5,.55,.6,1)),
                ([[-2,1.5,-1],[2,1.5,-1],[2,1.5,2.5],[-2,1.5,2.5]],(.4,.3,.2,1)),
                ([[-2,-2,-1],[-2,-2,2.5],[-2,1.5,2.5],[-2,1.5,-1]],(.3,.4,.45,1))]
        for i,(vertices,color) in enumerate(panels):
            mesh=bpy.data.meshes.new('Panel');mesh.from_pydata(vertices,[],[(0,1,2,3)]);mesh.update()
            item=bpy.data.objects.new('Panel',mesh);scene.collection.objects.link(item);vertices_all.extend(vertices)
            material=bpy.data.materials.new('Checker');material.use_nodes=True
            checker=material.node_tree.nodes.new('ShaderNodeTexChecker');checker.inputs['Scale'].default_value=6
            checker.inputs['Color1'].default_value=color;checker.inputs['Color2'].default_value=(.1,.13,.15,1)
            material.node_tree.links.new(checker.outputs['Color'],material.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
            mesh.materials.append(material)
        vertices=np.array(vertices_all)
    else:
        bpy.ops.wm.obj_import(filepath=str(OUT/'generic-head.obj'))
        objects=[item for item in scene.objects if item.type=='MESH']
        vertices=[]
        for item in objects:
            item.matrix_world=Matrix.Identity(4)
            vertices.extend([list(vertex.co) for vertex in item.data.vertices])
            material=bpy.data.materials.new('UntexturedSkin');material.use_nodes=True
            shader=material.node_tree.nodes['Principled BSDF']
            shader.inputs['Base Color'].default_value=(.55,.32,.22,1);shader.inputs['Roughness'].default_value=.7
            item.data.materials.clear();item.data.materials.append(material)
            for polygon in item.data.polygons:polygon.use_smooth=True
        vertices=np.array(vertices)
        original=np.load(OUT/'generic-head.npz')['vertices']
        if vertices.shape!=original.shape or np.abs(vertices-original).max()>5e-5:raise ValueError('OBJimport changed coordinates')
    for location,energy,size in [((-3,-3,-4),800,5),((3,0,-2),300,4)]:
        bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object
        light.data.energy=energy;light.data.size=size;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
    camera_data=bpy.data.cameras.new('KnownCamera');camera=bpy.data.objects.new('KnownCamera',camera_data)
    scene.collection.objects.link(camera);scene.camera=camera
    a=math.radians(angle);rotation=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    extrinsic=np.column_stack([rotation,[0,0,3.6]])
    set_camera(camera,K,extrinsic,720,1280);bpy.context.view_layer.update()
    replay=projection_error(scene,camera,vertices,K,extrinsic,720,1280)
    if replay['max_px']>.05:raise ValueError('Blender projection replay failed')
    path=OUT/'inputs'/(name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    reports[name]={'edge_K':K.tolist(),'extrinsic':extrinsic.tolist(),'projection_replay':replay,
                   'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(OUT/'truth.json').write_text(json.dumps({'blender':bpy.app.version_string,'contexts':reports},indent=2))
print('HEADFOUNDRY_0325_RENDER_COMPLETE')
