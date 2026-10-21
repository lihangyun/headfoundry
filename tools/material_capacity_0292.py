"""Separate source renderer,blind image worker and fixed truth evaluator;no head fit."""
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
import os
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))
OUT = ROOT/'assets/private/material-capacity-0292'
TRUTH = ROOT/'assets/private/real-capture-pilot-v1/scan-motion-truth-0230-upright'
SEQUENCE = ['front','yaw+10','yaw+30','yaw+10','front','yaw-10','yaw-30','yaw-10','front','pitch+10','front']


def sha(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file,'sha256').hexdigest()


def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')


def render():
    import bpy
    from headfoundry.manifest import validate_input_assets
    from headfoundry.scan import read_binary_stl
    from blender_camera_diagnostic import set_camera,projection_error
    started = time.monotonic()
    OUT.mkdir(exist_ok=False)
    pilot = TRUTH.parent
    manifest = json.loads((pilot/'manifest.json').read_text(encoding='utf-8'))
    confirmation = json.loads((pilot/'provenance-confirmation.json').read_text(encoding='utf-8'))
    selected = [a for a in manifest['inputs'] if a['id']=='real-case-001-skin']
    if len(selected)!=1 or validate_input_assets({**manifest,'inputs':selected},pilot):
        raise ValueError('selected skin rights/hash failed')
    if confirmation['manifest_sha256']!=sha(pilot/'manifest.json') or confirmation['cases']['real-case-001']['scan_units']!='millimeter':
        raise ValueError('explicit authorization/units failed')
    if sha(TRUTH/'known-motion.npz')!='eea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942':
        raise ValueError('fixed truth changed')
    controls = json.loads((TRUTH/'controls.json').read_text())
    source = Path(selected[0]['path'])
    if sha(source)!=controls['source_sha256']:
        raise ValueError('source does not match frozen truth')
    raw,faces = read_binary_stl(source)
    vertices = (raw-np.array(controls['center_mm'],dtype=raw.dtype))/controls['radius_mm']
    truth = np.load(TRUTH/'known-motion.npz',allow_pickle=False)
    replay = np.einsum('ni,nij->nj',truth['source_barycentric'],vertices.astype(float)[faces[truth['source_triangle_ids']]])
    if np.max(abs(replay-truth['vertices_normalized']))>1e-10:
        raise ValueError('all original material points changed')
    ids = np.flatnonzero(truth['visible'][0])
    if len(ids)!=2355:
        raise ValueError('query population changed')
    np.savez_compressed(OUT/'source-queries.npz',ids=truth['point_ids'][ids],xy=truth['pixels'][0,ids])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new('FIXED_EVALUATION_SOURCE')
    mesh.from_pydata(vertices.tolist(),[],faces.tolist())
    mesh.update()
    obj = bpy.data.objects.new('SUPPLIED_SCAN_NOT_RECONSTRUCTION',mesh)
    bpy.context.scene.collection.objects.link(obj)
    material = bpy.data.materials.new('Fixed_object_noise')
    material.use_nodes = True
    nodes,links = material.node_tree.nodes,material.node_tree.links
    nodes.clear()
    output,emission,noise,ramp,coords = [nodes.new(t) for t in
        ['ShaderNodeOutputMaterial','ShaderNodeEmission','ShaderNodeTexNoise','ShaderNodeValToRGB','ShaderNodeTexCoord']]
    noise.inputs['Scale'].default_value = 48
    noise.inputs['Detail'].default_value = 2
    noise.inputs['Roughness'].default_value = .5
    ramp.color_ramp.elements[0].color = (.15,.15,.15,1)
    ramp.color_ramp.elements[1].color = (.75,.75,.75,1)
    emission.inputs['Strength'].default_value = 1
    links.new(coords.outputs['Object'],noise.inputs['Vector'])
    links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'],emission.inputs['Color'])
    links.new(emission.outputs[0],output.inputs['Surface'])
    mesh.materials.append(material)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x,scene.render.resolution_y = 720,1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    rows = []
    for i,name in enumerate(truth['view_names'].tolist()):
        if time.monotonic()-started>180:
            raise TimeoutError('render180s')
        set_camera(camera,truth['intrinsic'],truth['extrinsics_normalized'][i],720,1280)
        bpy.context.view_layer.update()
        check = projection_error(scene,camera,vertices,truth['intrinsic'],truth['extrinsics_normalized'][i],720,1280)
        if check['max_px']>.05:
            raise ValueError('independent Blender projection failed')
        path = OUT/(name+'-evaluation-source.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rows.append({'view':name,'path':path.name,'sha256':sha(path),'projection':check})
    save('input.json',{'sequence':SEQUENCE,'images':rows,'query_sha256':sha(OUT/'source-queries.npz'),
                       'role':'SUPPLIED_SCAN_BENCHMARK_NOT_RECONSTRUCTION'})
    save('render.json',{'status':'TECHNICAL_CHECK_PASSED','rows':rows,'seconds':time.monotonic()-started,
                        'source_unchanged':sha(source)==controls['source_sha256']})


def worker():
    from PIL import Image
    from check_native_correlation_0291 import SampledCorrelation,model_module,torch,DEST,LOCK,blocked,peak_working_set
    import socket
    import urllib.request
    started = time.monotonic()
    finished = threading.Event()
    def watchdog():
        if not finished.wait(180):
            save('worker.json',{'status':'REJECT','failure':'worker180s cap'})
            os._exit(124)
    threading.Thread(target=watchdog,daemon=True).start()
    try:
        inputs = json.loads((OUT/'input.json').read_text())
        if inputs['sequence']!=SEQUENCE or sha(OUT/'source-queries.npz')!=inputs['query_sha256']:
            raise ValueError('immutable inputs changed')
        images = {}
        for row in inputs['images']:
            path = OUT/row['path']
            if sha(path)!=row['sha256']:
                raise ValueError('image hash changed')
            images[row['view']] = np.array(Image.open(path).convert('RGB'))
        query = np.load(OUT/'source-queries.npz',allow_pickle=False)
        xy = torch.from_numpy(query['xy']).float()
        if xy.shape!=(2355,2) or (xy<0).any() or (xy[:,0]>=720).any() or (xy[:,1]>=1280).any():
            raise ValueError('query support changed')
        grid = (xy/torch.tensor([719.,1279.])*2-1)[None,None]
        y,x = torch.meshgrid(torch.arange(1280),torch.arange(720),indexing='ij')
        ramp = torch.stack((x,y))[None].float()
        adapter = torch.nn.functional.grid_sample(ramp,grid,align_corners=True).squeeze().T
        adapter_error = float((adapter-xy).abs().max())
        if adapter_error>.001:
            raise ValueError('native subpixel adapter failed')
        if sha(DEST/'alltracker.pth')!=LOCK['checkpoint']['sha256']:
            raise ValueError('checkpoint changed')
        for name,expected in LOCK['source_files'].items():
            if sha(DEST/'source'/name)!=expected:
                raise ValueError('source changed')
        socket.socket.connect = blocked
        urllib.request.urlopen = blocked
        torch.hub.load_state_dict_from_url = blocked
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.cuda.set_per_process_memory_fraction(7*2**30/torch.cuda.get_device_properties(0).total_memory)
        model = model_module.Net(seqlen=16,init_weights=False)
        model.load_state_dict(torch.load(DEST/'alltracker.pth',map_location='cpu',weights_only=True)['model'],strict=True)
        model = model.eval().cuda()
        model_module.CorrBlock = SampledCorrelation
        rgbs = torch.from_numpy(np.stack([images[n] for n in SEQUENCE])).permute(0,3,1,2)[None].float().cuda()
        torch.cuda.reset_peak_memory_stats()
        with torch.inference_mode():
            flows,probabilities,_,_ = model.forward_sliding(rgbs,iters=4,is_training=False)
        torch.cuda.synchronize()
        if flows.shape!=(1,11,2,1280,720) or not torch.isfinite(flows).all() or not torch.isfinite(probabilities).all():
            raise ValueError('invalid dense outputs')
        sample_grid = grid.repeat(11,1,1,1)
        def sample(field):
            return torch.nn.functional.grid_sample(field[0],sample_grid,align_corners=True)[:,:,0].permute(0,2,1)
        points = sample(flows)+xy[None]
        probs = sample(probabilities)
        peak_gpu,peak_ram = torch.cuda.max_memory_reserved(),peak_working_set()
        if peak_gpu>7*2**30 or peak_ram>8*2**30:
            raise ValueError('worker resource cap')
        np.savez_compressed(OUT/'predictions.npz',ids=query['ids'],xy=points.numpy(),probabilities=probs.numpy())
        save('worker.json',{'status':'TECHNICAL_CHECK_PASSED','seconds':time.monotonic()-started,
                            'adapter_max_error_px':adapter_error,'peak_gpu_reserved':peak_gpu,'peak_working_set':peak_ram,
                            'prediction_sha256':sha(OUT/'predictions.npz'),'points':2355,'frames':11})
    finally:
        finished.set()


def evaluate():
    started = time.monotonic()
    if json.loads((OUT/'worker.json').read_text())['status']!='TECHNICAL_CHECK_PASSED':
        raise ValueError('no completed blind predictions')
    truth = np.load(TRUTH/'known-motion.npz',allow_pickle=False)
    pred = np.load(OUT/'predictions.npz',allow_pickle=False)
    ids = np.flatnonzero(truth['visible'][0])
    if not np.array_equal(pred['ids'],truth['point_ids'][ids]):
        raise ValueError('original IDs changed')
    order = [truth['view_names'].tolist().index(n) for n in SEQUENCE]
    target,visible = truth['pixels'][order][:,ids],truth['visible'][order][:,ids]
    errors = np.linalg.norm(pred['xy']-target,axis=2)
    estimated_visible = np.prod(pred['probabilities'],axis=2)>=.6
    rows = []
    for i,name in enumerate(SEQUENCE):
        e = errors[i,visible[i]]
        vr = float(estimated_visible[i,visible[i]].mean())
        hidden = ~visible[i]
        hr = float((~estimated_visible[i,hidden]).mean()) if hidden.any() else None
        row = {'frame':i,'view':name,'visible':int(visible[i].sum()),'occluded':int(hidden.sum()),
               'p95_px':float(np.percentile(e,95)),'max_px':float(e.max()),'visible_recall':vr,'occluded_recall':hr}
        row['passed'] = bool(np.isfinite(errors[i]).all() and row['p95_px']<=1 and row['max_px']<=3 and vr>=.95 and (hr is None or hr>=.95))
        rows.append(row)
    np.savez_compressed(OUT/'per-id-evaluation.npz',ids=pred['ids'],errors=errors,true_visible=visible,estimated_visible=estimated_visible,probabilities=pred['probabilities'])
    result = {'status':'TECHNICAL_CHECK_PASSED' if all(r['passed'] for r in rows[1:]) else 'REJECT',
              'physical_video_camera_head':'UNVERIFIED','rows':rows,'nonquery_visible_pairs':int(visible[1:].sum()),
              'nonquery_occluded_pairs':int((~visible[1:]).sum()),'seconds':time.monotonic()-started}
    save('evaluation.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    mode = sys.argv[-1]
    try:
        {'render':render,'worker':worker,'evaluate':evaluate}[mode]()
    except Exception as error:
        if OUT.exists():
            save(mode+'-failure.json',{'status':'REJECT','error':type(error).__name__+':'+str(error)})
        raise
