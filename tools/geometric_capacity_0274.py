"""Source-only calibrated capacity oracle, never a video-reconstructed head."""
import json
import os
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.camera import project
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.epipolar import _triangulate, robust_refine_pose, sampson_distance

OUT = ROOT/'assets/private/geometric-capacity-0274'
PILOT = ROOT/'assets/private/real-capture-pilot-v1'
FIXTURE = PILOT/'scan-motion-truth-0230-upright'
FIXTURE_SHA = 'eea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942'
VIEWS = [('front','front'), ('pos','yaw+30'), ('neg','yaw-30')]


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def deadline(start=None, budget=180):
    if time.time() > json.loads((OUT/'phase.json').read_text())['deadline_epoch']:
        raise TimeoutError('Whole registered phase deadline')
    if start is not None and time.perf_counter()-start > budget:
        raise TimeoutError('Registered stage deadline')


def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0]).lower().replace('\\','/')
        if any(x in name for x in ('.stl','known-motion','scan-motion-truth','case002','/oracle','/controls.json')):
            raise PermissionError('Source geometry/pose truth excluded from inference and fit')
    if event in ('socket.connect','socket.getaddrinfo'):
        raise PermissionError('Offline worker')


def source_scene():
    from headfoundry.scan import read_binary_stl
    manifest = json.loads((PILOT/'manifest.json').read_text(encoding='utf-8'))
    selected = [x for x in manifest['inputs'] if x['id']=='real-case-001-skin']
    if len(selected)!=1 or validate_input_assets(dict(manifest,inputs=selected),PILOT):
        raise ValueError('Selected source rights/hash')
    confirmation=json.loads((PILOT/'provenance-confirmation.json').read_text(encoding='utf-8'))
    if (confirmation['manifest_sha256']!=sha256_file(PILOT/'manifest.json')
            or confirmation['cases']['real-case-001']['scan_units']!='millimeter'):
        raise ValueError('Source confirmation/units')
    if sha256_file(FIXTURE/'known-motion.npz')!=FIXTURE_SHA:
        raise ValueError('Successful immutable fixture changed')
    controls=json.loads((FIXTURE/'controls.json').read_text())
    vertices,faces=read_binary_stl(Path(selected[0]['path']))
    if selected[0]['sha256']!=controls['source_sha256']:
        raise ValueError('Source fixture identity')
    vertices=(vertices-np.asarray(controls['center_mm']))/controls['radius_mm']
    truth=np.load(FIXTURE/'known-motion.npz',allow_pickle=False)
    replay=(truth['vertices_mm']-np.asarray(controls['center_mm']))/controls['radius_mm']
    if np.abs(replay-truth['vertices_normalized']).max()>1e-9:
        raise ValueError('Original-mm/normalized source replay')
    return vertices,faces,truth,controls


def render():
    import bpy
    from blender_camera_diagnostic import set_camera,projection_error
    started=time.perf_counter();deadline()
    vertices,faces,truth,controls=source_scene()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh=bpy.data.meshes.new('UNCHANGED_SUPPLIED_SCAN');mesh.from_pydata(vertices.tolist(),[],faces.tolist());mesh.update()
    obj=bpy.data.objects.new('SOURCE_NOT_RECONSTRUCTION',mesh);bpy.context.scene.collection.objects.link(obj)
    for polygon in mesh.polygons:polygon.use_smooth=True
    material=bpy.data.materials.new('Fixed_Persistent_Evaluation_Texture');material.use_nodes=True
    nodes,links=material.node_tree.nodes,material.node_tree.links;nodes.clear()
    coordinates=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='3D'
    noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.5
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.15,.15,.15,1);ramp.color_ramp.elements[1].color=(.75,.75,.75,1)
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1;output=nodes.new('ShaderNodeOutputMaterial')
    links.new(coordinates.outputs['Object'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs['Emission'],output.inputs['Surface']);mesh.materials.append(material)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=720;scene.render.resolution_y=1280
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True;scene.view_settings.view_transform='Standard'
    bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera
    rows=[];names=truth['view_names'].tolist();k=truth['intrinsic']
    first=truth['extrinsics_normalized'][names.index('front')]
    points0=truth['vertices_normalized']@first[:,:3].T+first[:,3]
    numerical=[]
    for short,name in VIEWS:
        deadline(started);index=names.index(name);e=truth['extrinsics_normalized'][index]
        set_camera(camera,k,e,720,1280);bpy.context.view_layer.update()
        replay=projection_error(scene,camera,vertices,k,e,720,1280)
        if replay['max_px']>.05:raise ValueError('Blender pinhole replay')
        scene.render.filepath=str(OUT/(short+'.png'));bpy.ops.render.render(write_still=True)
        rows.append({'view':short,'sha256':sha256_file(OUT/(short+'.png')),'projection_replay':replay})
        if short!='front':
            relative=np.c_[e[:,:3]@first[:,:3].T,e[:,3]-(e[:,:3]@first[:,:3].T)@first[:,3]]
            common=truth['visible'][names.index('front')]&truth['visible'][index]
            p=truth['pixels'][names.index('front'),common];q=truth['pixels'][index,common]
            exact_error=np.abs(project(k@relative,points0[common])-q).max()
            replay3d=_triangulate(p,q,k@np.c_[np.eye(3),np.zeros(3)],k@relative)
            metric_error=np.linalg.norm(replay3d-points0[common],axis=1).max()*controls['radius_mm']
            wrong=relative.copy();wrong[1,3]+=.1
            negative=float(np.percentile(np.linalg.norm(project(k@wrong,points0[common])-q,axis=1),95))
            if exact_error>1e-8 or metric_error>1e-6 or negative<=3:raise ValueError('Independent evaluator controls')
            numerical.append({'view':short,'true_relative_replay_max_px':float(exact_error),
                              'true_triangulation_max_mm':float(metric_error),'wrong_translation_p95_px':negative})
    save('input-calibration.json',{'intrinsic':k.tolist(),'width':720,'height':1280,'given_not_estimated':True})
    save('render-report.json',{'role':'SOURCE_SCAN_NOT_RECONSTRUCTION','fixture_sha256':FIXTURE_SHA,
        'source_sha256':controls['source_sha256'],'renders':rows,'evaluator_controls':numerical,
        'elapsed_seconds':time.perf_counter()-started})


def foreground(points,alpha):
    xy=np.floor(points+.5).astype(int);valid=(xy[:,0]>=0)&(xy[:,0]<720)&(xy[:,1]>=0)&(xy[:,1]<1280)
    result=np.zeros(len(points),bool);result[valid]=alpha[xy[valid,1],xy[valid,0]]>=128
    return result


def infer():
    started=time.perf_counter()
    sys.addaudithook(guard)
    import torch
    from PIL import Image
    from safetensors.torch import load_file
    from transformers import EfficientLoFTRConfig,EfficientLoFTRImageProcessor
    from aligned_index_0274 import AlignedIndexMatcher,check_actual_contracts
    import ctypes
    def memory_bytes():
        class Memory(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(name,ctypes.c_size_t)
                for name in ('peak','working','poolpeak','pool','nonpagepeak','nonpage','page','pagepeak')]
        value=Memory();value.cb=ctypes.sizeof(value)
        ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(Memory),ctypes.c_ulong]
        if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(value),value.cb):
            raise OSError('Working set query failed')
        return int(value.peak)
    deadline();torch.set_num_threads(8)
    model_root=OUT/'model';record=json.loads((OUT/'asset-verification.json').read_text())
    for name,expected in record['files'].items():
        if sha256_file(model_root/name)!=expected:raise ValueError('Pinned model/config changed')
    model=AlignedIndexMatcher(EfficientLoFTRConfig.from_json_file(model_root/'config.json'))
    state=load_file(model_root/'model.safetensors',device='cpu');expected=model.state_dict()
    if state.keys()!=expected.keys():raise ValueError('Strict state keys')
    for key,value in state.items():
        if value.shape!=expected[key].shape or value.dtype!=expected[key].dtype or not torch.isfinite(value).all():
            raise ValueError('Strict finite state shape/dtype: '+key)
    model.load_state_dict(state,strict=True);model.eval();del state,expected
    save('actual-index-controls.json',check_actual_contracts(model))
    processor=EfficientLoFTRImageProcessor.from_pretrained(model_root,local_files_only=True)
    first=Image.open(OUT/'front.png').convert('RGBA');rows=[]
    for name in ['pos','neg']:
        deadline(started);second=Image.open(OUT/(name+'.png')).convert('RGBA')
        inputs=processor([first.convert('RGB'),second.convert('RGB')],size={'height':672,'width':384},return_tensors='pt')
        if inputs['pixel_values'].shape[:2]!=(1,2):raise ValueError('Single-pair batch only')
        with torch.inference_mode():outputs=model(**inputs)
        points=outputs.keypoints[0].cpu().numpy().astype(np.float64)*[720,1280]
        scores=outputs.matching_scores[0].cpu().numpy();indices=outputs.matches[0].cpu().numpy()
        if not np.isfinite(points).all() or not np.isfinite(scores).all():raise ValueError('Nonfinite output')
        valid=(indices>=0).all(0)&(scores>.2).all(0)
        eligible=valid&foreground(points[0],np.array(first)[:,:,3])&foreground(points[1],np.array(second)[:,:,3])
        np.savez_compressed(OUT/(name+'-matches.npz'),points=points,scores=scores,indices=indices,valid=valid,eligible=eligible)
        peak=memory_bytes()
        if peak>4_000_000_000:raise MemoryError('Registered peak working set')
        rows.append({'view':name,'slots':points.shape[1],'eligible':int(eligible.sum()),'peak_bytes':peak})
    deadline(started)
    save('inference.json',{'status':'TECHNICAL_CHECK_PASSED','strict_finite_full_state':True,'rows':rows,
        'elapsed_seconds':time.perf_counter()-started,'peak_bytes':memory_bytes(),'offline':True})


def fit():
    sys.addaudithook(guard);started=time.perf_counter();deadline()
    k=np.array(json.loads((OUT/'input-calibration.json').read_text())['intrinsic']);rows=[];extrinsics=[]
    for name in ['pos','neg']:
        deadline(started);raw=np.load(OUT/(name+'-matches.npz'),allow_pickle=False);a,b=raw['points'][:,raw['eligible']]
        even=np.arange(len(a))%2==0
        if min(even.sum(),(~even).sum())<24 or not (np.ptp(np.array([a,b]),axis=1)>=80).all():
            raise ValueError('Registered support/span precondition: '+name)
        result=robust_refine_pose(a[even],b[even],k,k,threshold_px=2.,min_support_fraction=.6,
                                 min_parallax_deg=1.,iterations=512,seed=274)
        e=np.asarray(result['extrinsic']);extrinsics.append(e)
        errors=sampson_distance(result['fundamental'],a[~even],b[~even])
        # Store all held errors even on failure; never prune held observations.
        np.savez_compressed(OUT/(name+'-fit.npz'),extrinsic=e,even=even,held_errors=errors)
        rows.append({'view':name,'train':int(even.sum()),'held':int((~even).sum()),
                     'held_sampson_p95_px':float(np.percentile(errors,95)),'fit':result})
    np.savez_compressed(OUT/'estimated-cameras.npz',extrinsics=np.array(extrinsics),intrinsic=k)
    deadline(started)
    save('fit.json',{'status':'TECHNICAL_CHECK_PASSED' if all(r['held_sampson_p95_px']<=3 for r in rows) else 'REJECT',
        'scope':'Given calibration/unit baselines,not physical acceptance','rows':rows,'elapsed_seconds':time.perf_counter()-started})


def evaluate():
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    started=time.perf_counter();deadline();vertices,faces,truth,controls=source_scene()
    fit_report=json.loads((OUT/'fit.json').read_text());estimated=np.load(OUT/'estimated-cameras.npz',allow_pickle=False)
    names=truth['view_names'].tolist();origin=names.index('front');e0=truth['extrinsics_normalized'][origin]
    points0=truth['vertices_normalized']@e0[:,:3].T+e0[:,3];k=truth['intrinsic'];inverse=np.linalg.inv(k)
    tree=BVHTree.FromPolygons(vertices.tolist(),faces.tolist(),all_triangles=True);radius=controls['radius_mm']
    center0=-e0[:,:3].T@e0[:,3]
    def baseline(index):
        target=truth['extrinsics_normalized'][index];r=target[:,:3]@e0[:,:3].T
        return np.linalg.norm(target[:,3]-r@e0[:,3])
    scale=baseline(names.index('yaw+30'))
    if abs(scale-baseline(names.index('yaw-30')))>1e-10:raise ValueError('One symmetric gauge required')
    rows=[]
    for j,(short,name) in enumerate(VIEWS[1:]):
        deadline(started);index=names.index(name);e=estimated['extrinsics'][j].copy();e[:,3]*=scale
        selected=truth['visible'][origin]&truth['visible'][index]
        predicted=project(k@e,points0[selected]);expected=truth['pixels'][index,selected]
        error=np.linalg.norm(predicted-expected,axis=1)
        proper=np.max(np.abs(e[:,:3]@e[:,:3].T-np.eye(3)))<1e-6 and abs(np.linalg.det(e[:,:3])-1)<1e-6
        positive=bool(((points0[selected]@e[:,:3].T+e[:,3])[:,2]>0).all())
        raw=np.load(OUT/(short+'-matches.npz'),allow_pickle=False);a,b=raw['points'][:,raw['eligible']]
        a,b=a[1::2],b[1::2];xyz=[];common=[];missing=0;target=truth['extrinsics_normalized'][index]
        center=-target[:,:3].T@target[:,3]
        for pixel in a:
            ray=e0[:,:3].T@(inverse@np.r_[pixel,1]);hit=tree.ray_cast(Vector(center0),Vector(ray))[0]
            if hit is None:missing+=1;xyz.append([np.nan]*3);common.append(False);continue
            p=np.asarray(hit);xyz.append(e0[:,:3]@p+e0[:,3])
            second=tree.ray_cast(Vector(center),Vector(p-center))[0]
            common.append(second is not None and np.linalg.norm(np.asarray(second)-p)*radius<=.01)
        common=np.array(common,bool);xyz=np.array(xyz);triangulated=_triangulate(a,b,k@np.c_[np.eye(3),np.zeros(3)],k@e)
        point_error=np.linalg.norm(triangulated[common]-xyz[common],axis=1)*radius
        point_finite=np.isfinite(point_error).all() and len(point_error)>=20
        p95=float(np.percentile(error,95));metric95=float(np.percentile(point_error,95)) if point_finite else None
        common_fraction=float(common.mean())
        passed=proper and positive and p95<=3 and missing==0 and common_fraction>=.95 and point_finite and metric95<=2
        np.savez_compressed(OUT/(short+'-evaluation.npz'),original_ids=truth['point_ids'][selected],
            camera_error_px=error,predicted_pixels=predicted,true_pixels=expected,common=common,
            held_source=a,held_target=b,triangulated=triangulated,point_error_mm=point_error)
        rows.append({'view':short,'original_visible_ids':int(selected.sum()),'camera_p95_px':p95,
            'camera_max_px':float(error.max()),'proper_rotation':bool(proper),'positive_depths':positive,
            'held_matches':len(a),'source_misses':missing,'true_common_fraction':common_fraction,
            'point_p95_mm':metric95,'point_max_mm':float(point_error.max()) if point_finite else None,
            'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT'})
    deadline(started)
    passed=fit_report['status']=='TECHNICAL_CHECK_PASSED' and all(r['status']=='TECHNICAL_CHECK_PASSED' for r in rows)
    save('evaluation.json',{'status':'TECHNICAL_CHECK_PASSED' if passed else 'REJECT','rows':rows,
        'scope':'Given-K source-only camera/point capacity,NOT video camera or reconstructed head',
        'one_common_baseline_gauge':float(scale),'no_fitted_truth_alignment':True,'elapsed_seconds':time.perf_counter()-started,
        'actual_video_camera':'UNVERIFIED','head_surface_visual':'UNVERIFIED'})


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    try:globals()[args[0]]()
    except Exception as exc:
        if OUT.exists():save('failure.json',{'status':'REJECT','stage':args[0] if args else 'missing','error':repr(exc)})
        raise
