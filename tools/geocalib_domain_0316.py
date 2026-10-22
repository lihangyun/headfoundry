"""One frozen known-camera head-domain test;never a patient reconstruction."""
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))
from headfoundry.manifest import sha256_file

OUT=ROOT/'assets/private/geocalib-domain-0316'
NAMES=['room','front','left60','right60']

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def prepare():
    import numpy as np
    from prepare_makehuman_head import extract_head
    OUT.mkdir(exist_ok=False)
    write('started.json',dict(epoch=time.time(),deadline_utc='2026-10-22T15:59:00Z'))
    asset=OUT/'cc0';asset.mkdir()
    lock=json.loads((ROOT/'examples/makehuman-base-asset-lock.json').read_text())
    assert lock['license_id']=='CC0-1.0'
    for name,digest in lock['sha256'].items():
        source=lock['source_path'] if name=='base.obj' else name
        url=f"https://raw.githubusercontent.com/makehumancommunity/makehuman/{lock['revision']}/{source}"
        with urllib.request.urlopen(url,timeout=30) as response:
            data=response.read(8*1024**2+1)
        assert len(data)<=8*1024**2
        (asset/name).write_bytes(data)
        assert sha256_file(asset/name)==digest,(name,'hash mismatch')
    vertices,faces,_=extract_head((asset/'base.obj').read_text(),include_eye_helpers=True)
    vertices=(vertices-(vertices.min(0)+vertices.max(0))/2)/(vertices[:,1].max()-vertices[:,1].min())
    np.savez_compressed(OUT/'generic-mesh.npz',vertices=vertices,faces=faces)
    render_stage()

def render_stage(fixed=False):
    from bounded_process import run
    from PIL import Image,ImageDraw
    blend=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe')
    assert blend.is_file()
    env=os.environ.copy()
    for key,name in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('TEMP','temp'),('TMP','temp')]:
        folder=OUT/name;folder.mkdir(exist_ok=True);env[key]=str(folder)
    suffix='-fixed' if fixed else ''
    record=run([str(blend),'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__)),'--','render'],
        str(ROOT),env,OUT/f'render{suffix}.log',OUT/f'render-worker{suffix}.json',180,3*1024**3)
    assert record['status']=='TECHNICAL_CHECK_PASSED',record
    assert (OUT/'render.json').is_file(),'Blender exit code is not a render completion certificate'
    sheet=Image.new('RGB',(720,680),'#171d25')
    for i,name in enumerate(NAMES):
        im=Image.open(OUT/f'{name}.png').convert('RGB');im.thumbnail((180,640))
        sheet.paste(im,(i*180,25));ImageDraw.Draw(sheet).text((i*180+5,5),name,fill='white')
    sheet.save(OUT/'inputs.png')
    print(json.dumps(record))

def render():
    import bpy
    import numpy as np
    from mathutils import Vector
    from blender_camera_diagnostic import set_camera,projection_error
    mesh=np.load(OUT/'generic-mesh.npz',allow_pickle=False)
    vertices,faces=mesh['vertices'],mesh['faces']
    edge_k=np.array([[1200.,0,360.],[0,1200.,640.],[0,0,1.]])
    records=[]
    for name,yaw in zip(NAMES,[0,0,60,-60]):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene=bpy.context.scene
        scene.render.engine='BLENDER_EEVEE'
        scene.render.resolution_x=720;scene.render.resolution_y=1280
        scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG'
        scene.render.film_transparent=False
        scene.world=bpy.data.worlds.new('Owned blue background')
        scene.world.use_nodes=True
        background=scene.world.node_tree.nodes.get('Background')
        background.inputs['Color'].default_value=(.05,.18,.34,1)
        background.inputs['Strength'].default_value=.5
        def material(label,color):
            m=bpy.data.materials.new(label);m.use_nodes=True
            bsdf=m.node_tree.nodes.get('Principled BSDF')
            bsdf.inputs['Base Color'].default_value=(*color,1)
            bsdf.inputs['Roughness'].default_value=.8
            return m
        skin=material('Untextured CC0 clay',(.5,.32,.23))
        if name=='room':
            probes=[]
            for loc,size,color in [((0,1.5,4),(6,.1,10),(.5,.45,.4)),((0,-1.5,4),(6,.1,10),(.7,.7,.7)),
                    ((0,0,7),(6,3,.1),(.65,.6,.5)),((-2,0,4),(.1,3,6),(.4,.45,.5)),
                    ((2,0,4),(.1,3,6),(.5,.4,.35)),((-.7,.8,5),(.6,1.4,.8),(.3,.3,.3)),
                    ((.8,.9,4),(.8,1.2,.7),(.5,.35,.2))]:
                bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
                obj=bpy.context.object;obj.scale=size
                obj.data.materials.append(material('Owned room surface',color))
                probes.extend([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
            e=np.column_stack([np.eye(3),np.zeros(3)])
            probes=np.array(probes)
        else:
            data=bpy.data.meshes.new('Generic CC0 mesh')
            data.from_pydata(vertices.tolist(),[],faces.tolist());data.update()
            obj=bpy.data.objects.new('UNFITTED generic head',data)
            scene.collection.objects.link(obj);obj.data.materials.append(skin)
            for polygon in data.polygons:polygon.use_smooth=True
            theta=np.deg2rad(yaw);c,s=np.cos(theta),np.sin(theta)
            e=np.column_stack([np.array([[c,0,s],[0,1,0],[-s,0,c]]),[0,0,2.]])
            probes=vertices
        camera_data=bpy.data.cameras.new('Known camera')
        camera=bpy.data.objects.new('Known camera',camera_data)
        scene.collection.objects.link(camera);scene.camera=camera
        set_camera(camera,edge_k,e,720,1280)
        bpy.context.view_layer.update()
        for local,energy,size in [((-1.2,1.3,0),180,2),((1.2,.2,0),90,2)]:
            bpy.ops.object.light_add(type='AREA')
            light=bpy.context.object
            light.location=camera.location+camera.matrix_world.to_3x3()@Vector(local)
            target=Vector((0,0,4 if name=='room' else 0))
            light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
            light.data.energy=energy;light.data.size=size
        check=projection_error(scene,camera,probes,edge_k,e,720,1280)
        assert check['max_px']<.05,check
        scene.render.filepath=str(OUT/f'{name}.png')
        bpy.ops.render.render(write_still=True)
        records.append(dict(name=name,yaw=yaw,world_to_camera=e.tolist(),projection_replay=check,
                            image_sha256=sha256_file(OUT/f'{name}.png')))
    truth=edge_k.copy();truth[0,2]-=.5;truth[1,2]-=.5
    write('render.json',dict(source='CC0generic asset only;not a patient',blender=bpy.app.version_string,
        integer_center_K=truth.tolist(),edge_coordinate_K=edge_k.tolist(),views=records))

def predict():
    from bounded_process import run
    assert (OUT/'render.json').is_file() and not (OUT/'forward-started.json').exists()
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
    record=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),env,OUT/'worker.log',OUT/'worker.json',180,3*1024**3)
    print(json.dumps(record))

def worker():
    from geocalib_software_0315 import SITE,SOURCE,WEIGHT,locked_sources,strict_state,offline
    locked_sources()
    lock=json.loads((SITE.parent/'runtime-lock.json').read_text())
    for row in lock['files']:assert sha256_file(SITE/row['path'])==row['sha256'],row['path']
    sys.path.insert(0,str(SITE));offline()
    import torch
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(SOURCE/'snapshot'))
    from geocalib.geocalib import GeoCalib
    from geocalib.utils import ImagePreprocessor
    torch.set_num_threads(4);torch.set_grad_enabled(False)
    model=GeoCalib().eval()
    state=torch.load(WEIGHT/'geocalib-pinhole.tar',map_location='cpu',weights_only=True)['model']
    strict_state(model,state);del state
    truth=json.loads((OUT/'render.json').read_text())
    ktrue=np.array(truth['integer_center_K'])
    xx,yy=np.meshgrid(np.linspace(140,580,25),np.linspace(330,950,25))
    pixels=np.stack([xx.ravel(),yy.ravel(),np.ones(xx.size)])
    rays=np.linalg.inv(ktrue)@pixels
    processor=ImagePreprocessor({'resize':320,'edge_divisible_by':32})
    results=[]
    for index,name in enumerate(NAMES):
        row=truth['views'][index];assert sha256_file(OUT/f'{name}.png')==row['image_sha256']
        rgb=np.asarray(Image.open(OUT/f'{name}.png').convert('RGB'),dtype='float32')/255
        h,w=rgb.shape[:2]
        data=processor(torch.from_numpy(rgb.transpose(2,0,1).copy())[None])
        torch.manual_seed(316)
        write('forward-started.json',dict(count=index+1,seed=316,epoch=time.time()))
        start=time.monotonic();pred=model(data);seconds=time.monotonic()-start
        raw={key:t.numpy() for key,t in pred.items() if isinstance(t,torch.Tensor)}
        raw['camera_parameters']=pred['camera']._data.numpy();raw['gravity_vector']=pred['gravity'].vec3d.numpy()
        assert all(np.isfinite(t).all() for t in raw.values())
        np.savez_compressed(OUT/f'{name}-raw.npz',**raw)
        legacy=pred['camera'].undo_scale_crop(data).K.numpy()[0].astype(float)
        rh,rw=processor.get_new_image_size(h,w);ih,iw=data['image'].shape[-2:]
        sx,sy=rw/w,rh/h;left=(rw-iw+1)//2;top=(rh-ih+1)//2
        a=np.array([[sx,0,.5*sx-.5-left],[0,sy,.5*sy-.5-top],[0,0,1.]])
        resampling=np.linalg.inv(a)@pred['camera'].K.numpy()[0]
        scores={}
        for convention,k in [('upstream',legacy),('pixel_resampling',resampling)]:
            p=k@rays;p=p[:2]/p[2:]
            error=np.linalg.norm(p-pixels[:2],axis=0)
            focal=float(np.max(abs(k.diagonal()[:2]/1200-1)))
            vfov=float(np.rad2deg(2*np.arctan(h/(2*k[1,1]))))
            valid=bool(np.isfinite(k).all() and (k.diagonal()[:2]>0).all() and 5.001<vfov<149.999)
            scores[convention]=dict(K=k.tolist(),p95_px=float(np.percentile(error,95)),max_px=float(error.max()),
                relative_focal_error=focal,finite_positive_nonboundary=valid,
                passed=valid and float(np.percentile(error,95))<=3 and focal<=.02)
        results.append(dict(name=name,seconds=seconds,conventions=scores,
            focal_uncertainty_model_px=raw['focal_uncertainty'].tolist(),LM_stop_at=raw['stop_at'].tolist()))
        write('partial-results.json',results)
    passed=all(row['conventions'][c]['passed'] for row in results[1:] for c in row['conventions'])
    write('result.json',dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
        scope='conditional known-camera head-domain K only;not actual-video SE3/head',results=results,
        actual_head_or_medical_accuracy='UNVERIFIED',nn_forwards=len(results),no_patient_input=True))
    print((OUT/'result.json').read_text())

if __name__=='__main__':
    if 'render' in sys.argv:render()
    elif sys.argv[1:]==['rerender']:
        assert not (OUT/'forward-started.json').exists() and not list(OUT.glob('*.png')) and not (OUT/'render.json').exists()
        assert 'No module named' in (OUT/'render.log').read_text()
        render_stage(fixed=True)
    elif sys.argv[1:]==['worker']:worker()
    elif sys.argv[1:]==['predict']:predict()
    else:prepare()
