"""Known-source capacity oracle,never a reconstructed head or real-video fitter."""

import argparse
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.camera import project
from scan_motion_truth_0230 import look_at_origin
from scan_surface_metric_0237 import apply_similarity

OUT = ROOT / "assets/private/opend4rt-known3d-0264"
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
REFERENCE = PILOT / "scan-motion-truth-0230-upright"
CROP = np.array([0, 320, 720, 960])
KEY_VIEWS = [0, 2, 4, 2, 0, 1, 3, 1, 0, 5, 0]
ANGLES = np.array([[0,0],[10,0],[30,0],[10,0],[0,0],[-10,0],[-30,0],[-10,0],[0,0],[0,10],[0,0]])


def scope():
    lock = json.loads((ROOT / "examples/opend4rt-known3d-0264.asset-lock.json").read_text())
    if (lock["purpose"] != "local_known3d_capacity_validation_only" or lock["forward_allowed"] is not True
            or lock["source_license"] != "Apache-2.0" or lock["checkpoint_license"] != "Apache-2.0"
            or lock["renderer_only_asset_ids"] != ["real-case-001-skin"]
            or any(lock[k] is not False for k in ["training_allowed", "upload_allowed",
                                                  "real_video_inference_allowed", "head_fitting_allowed"])):
        raise ValueError("Unapproved source/model/data scope")
    return lock


def skin_only(manifest):
    selected = [x for x in manifest["inputs"] if x["id"] == "real-case-001-skin"]
    if (len(selected) != 1 or manifest["purpose"] != "local_head_reconstruction_validation"
            or manifest.get("training_allowed") is not False or manifest.get("upload_allowed") is not False):
        raise ValueError("Exact case001-only validation scope required")
    return {**manifest, "inputs": selected}


def similarity(source, target):
    a, b = np.asarray(source, float), np.asarray(target, float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("All finite paired3D points required")
    x, y = a-a.mean(0), b-b.mean(0)
    if np.linalg.svd(x, compute_uv=False)[-1] <= np.linalg.svd(x, compute_uv=False)[0] * 1e-6:
        raise ValueError("Degenerate global alignment")
    u, values, vt = np.linalg.svd(y.T @ x / len(a))
    sign = np.array([1., 1., np.linalg.det(u @ vt)])
    rotation = (u * sign) @ vt
    scale = float(values @ sign / np.mean(np.sum(x*x, axis=1)))
    transform = np.eye(4)
    transform[:3,:3] = scale * rotation
    transform[:3,3] = b.mean(0) - scale * rotation @ a.mean(0)
    apply_similarity(a, transform)  # Existing strict positive/proper/uniform guard.
    return transform


def controls():
    from unittest.mock import patch
    directory = OUT / "controls"
    directory.mkdir()
    for name in ["allowed", "heldout"]:
        (directory / name).write_bytes(name.encode())
    base = dict(source="synthetic_selfcheck", license_id="test_only", retention_until="2099-01-01",
                deletion_process="delete_selfcheck", allowed_uses=["local_head_reconstruction_validation"],
                consent=dict(subject_id="synthetic", record_id="selfcheck", granted_at="2026-10-20", biometric_processing=True))
    records = [dict(base, id=identity, path=name, sha256=sha256_file(directory/name))
               for identity,name in [("real-case-001-skin","allowed"),("heldout-case","heldout")]]
    manifest = dict(schema_version=1, purpose="local_head_reconstruction_validation", inputs=records,
                    training_allowed=False, upload_allowed=False)
    visited = []
    def guarded(path):
        visited.append(Path(path).name)
        if Path(path).name == "heldout":
            raise AssertionError("Held-out file opened")
        return sha256_file(path)
    with patch("headfoundry.manifest.sha256_file", side_effect=guarded):
        if validate_input_assets(skin_only(manifest), directory) or visited != ["allowed"]:
            raise ValueError("Case-scope sentinel failed")
    a = np.array([[0,0,0],[3,0,0],[0,4,0],[0,0,5],[2,1,4]], float)
    known = np.array([[0,-2,0,7],[2,0,0,-3],[0,0,2,5],[0,0,0,1]], float)
    b = apply_similarity(a, known)
    np.testing.assert_allclose(apply_similarity(a, similarity(a,b)), b, atol=1e-10)
    np.testing.assert_allclose(apply_similarity(b, np.linalg.inv(known)), a, atol=1e-10)
    bad = np.diag([-1,1,1,1])
    try: apply_similarity(a,bad)
    except ValueError: pass
    else: raise AssertionError("Reflection accepted")
    xy = np.array([[101.25,402.75],[650.5,880.125]])
    uv = (xy-CROP[:2]) / (CROP[2:]-CROP[:2]-1)
    np.testing.assert_allclose(uv*(CROP[2:]-CROP[:2]-1)+CROP[:2], xy, atol=1e-10)
    report = dict(status="TECHNICAL_CHECK_PASSED", heldout_sentinel_not_read=True,
                  global_similarity_and_inverse=True, reflection_rejected=True, native_raster_roundtrip=True)
    (OUT / "controls.json").write_text(json.dumps(report, indent=2))


def render():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from headfoundry.scan import read_binary_stl
    from blender_camera_diagnostic import set_camera, projection_error
    lock = scope()
    if bpy.app.version_string != lock["blender"]:
        raise ValueError("Unexpected renderer")
    if json.loads((OUT/"controls.json").read_text()).get("heldout_sentinel_not_read") is not True:
        raise ValueError("Required holdout control missing")
    started = time.perf_counter()
    manifest_path = PILOT / "manifest.json"
    manifest = skin_only(json.loads(manifest_path.read_text(encoding="utf-8")))
    confirmation = json.loads((PILOT/"provenance-confirmation.json").read_text())
    if (validate_input_assets(manifest,PILOT) or confirmation["manifest_sha256"] != sha256_file(manifest_path)
            or confirmation["cases"]["real-case-001"] != {"scan_units":"millimeter","scan_video_same_stage":True}):
        raise ValueError("Case001 source rights/unit/stage mismatch")
    source = PILOT / manifest["inputs"][0]["path"]
    source_sha = sha256_file(source)
    if sha256_file(REFERENCE/"known-motion.npz") != lock["known_motion_sha256"]:
        raise ValueError("Changed successful benchmark")
    reference = np.load(REFERENCE/"known-motion.npz",allow_pickle=False)
    controls_record = json.loads((REFERENCE/"controls.json").read_text())
    if source_sha != controls_record["source_sha256"]:
        raise ValueError("Wrong evaluation source")
    raw,faces = read_binary_stl(source)
    center,radius = (raw.max(0)+raw.min(0))/2,float(np.ptp(raw,axis=0).max()/2)
    vertices = (raw-center)/radius
    points = reference["vertices_normalized"]
    replay = np.einsum("ni,nij->nj",reference["source_barycentric"],raw[faces[reference["source_triangle_ids"]]])
    np.testing.assert_allclose(replay,reference["vertices_mm"],atol=1e-9,rtol=0)
    np.testing.assert_allclose(points*radius+center,replay,atol=1e-9,rtol=0)
    probe = BVHTree.FromPolygons([(-2,-2,0),(2,-2,0),(0,2,0),(-2,-2,-1),(2,-2,-1),(0,2,-1)],[(0,1,2),(3,4,5)],all_triangles=True)
    hit = probe.ray_cast(Vector((0,0,5)),Vector((0,0,-1)))[0]
    if hit is None or np.linalg.norm(hit)>1e-6:
        raise ValueError("First-hit occlusion control failed")
    tree = BVHTree.FromPolygons(vertices.tolist(),faces.tolist(),all_triangles=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mesh = bpy.data.meshes.new("UnchangedEvaluationSource")
    mesh.from_pydata(vertices.tolist(),[],faces.tolist());mesh.update()
    obj = bpy.data.objects.new("SOURCE_SCAN_NOT_RECONSTRUCTION",mesh);scene.collection.objects.link(obj)
    for polygon in mesh.polygons: polygon.use_smooth=True
    material = bpy.data.materials.new("FixedProceduralEvaluationAppearance");material.use_nodes=True
    nodes,links = material.node_tree.nodes,material.node_tree.links;nodes.clear()
    coordinates,noise,ramp,emission,output = [nodes.new(x) for x in ["ShaderNodeTexCoord","ShaderNodeTexNoise","ShaderNodeValToRGB","ShaderNodeEmission","ShaderNodeOutputMaterial"]]
    noise.noise_dimensions="3D";noise.inputs["Scale"].default_value=48;noise.inputs["Detail"].default_value=2;noise.inputs["Roughness"].default_value=.5
    ramp.color_ramp.elements[0].color=(.15,.15,.15,1);ramp.color_ramp.elements[1].color=(.75,.75,.75,1)
    emission.inputs["Strength"].default_value=1
    for a,b in [(coordinates.outputs["Object"],noise.inputs["Vector"]),(noise.outputs["Fac"],ramp.inputs["Fac"]),(ramp.outputs["Color"],emission.inputs["Color"]),(emission.outputs["Emission"],output.inputs["Surface"])]: links.new(a,b)
    mesh.materials.append(material)
    scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA";scene.render.film_transparent=True;scene.view_settings.view_transform="Standard"
    scene.world=bpy.data.worlds.new("EvaluationWorld");scene.world.color=(.04,.04,.04)
    bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera
    pixels,visible,extrinsics,rows = [],[],[],[]
    k = reference["intrinsic"]
    for frame in range(32):
        if time.perf_counter()-started>180: raise TimeoutError("Original render budget exhausted")
        if frame==31: pose=reference["extrinsics_normalized"][0].copy()
        elif frame%3==0: pose=reference["extrinsics_normalized"][KEY_VIEWS[frame//3]].copy()
        else:
            a,b=frame//3,frame%3/3
            yaw,pitch=np.deg2rad((1-b)*ANGLES[a]+b*ANGLES[a+1])
            pose=look_at_origin(6*np.array([np.sin(yaw)*np.cos(pitch),np.sin(pitch),np.cos(yaw)*np.cos(pitch)]))
        xy=project(k@pose,points);location=-pose[:,:3].T@pose[:,3]
        if ((vertices@pose[:,:3].T+pose[:,3])[:,2].min()<=0
                or not np.isclose(np.linalg.det(pose[:,:3]),1,atol=1e-8)):
            raise ValueError("Invalid positive-depth/proper known camera")
        gap=np.full(5000,np.inf)
        for index,point in enumerate(points):
            hit=tree.ray_cast(Vector(location),Vector(point-location))[0]
            if hit is not None: gap[index]=np.linalg.norm(np.asarray(hit)-point)*radius
        mask=(gap<=.01)&(xy[:,0]>=0)&(xy[:,0]<720)&(xy[:,1]>=0)&(xy[:,1]<1280)
        if np.any(mask & ((xy[:,0]<0)|(xy[:,0]>=720)|(xy[:,1]<320)|(xy[:,1]>=960))):
            raise ValueError("Visible source IDs outside fixed crop")
        if frame<=30 and frame%3==0:
            key=KEY_VIEWS[frame//3]
            np.testing.assert_allclose(xy,reference["pixels"][key],atol=1e-9,rtol=0)
            if not np.array_equal(mask,reference["visible"][key]): raise ValueError("Key visibility changed")
        set_camera(camera,k,pose,720,1280);bpy.context.view_layer.update()
        camera_replay=projection_error(scene,camera,vertices,k,pose,720,1280)
        if camera_replay["max_px"]>.05: raise ValueError("Independent camera replay failed")
        image=OUT/f"frame-{frame:02d}.png";scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
        rows.append(dict(frame=frame,image=image.name,sha256=sha256_file(image),visible=int(mask.sum()),camera_replay=camera_replay))
        pixels.append(xy);visible.append(mask);extrinsics.append(pose)
    np.savez_compressed(OUT/"render-truth.npz",pixels=pixels,visible=visible,extrinsics=extrinsics,
                        points_normalized=points,points_mm=replay,center_mm=center,radius_mm=radius,intrinsic=k)
    if sha256_file(source)!=source_sha: raise ValueError("Original source changed")
    (OUT/"render.json").write_text(json.dumps(dict(status="TECHNICAL_CHECK_PASSED",role="SOURCE_ORACLE_NOT_RECONSTRUCTION",source_sha256=source_sha,
        reference_sha256=lock["known_motion_sha256"],rows=rows,seconds=time.perf_counter()-started,
        truth_sha256=sha256_file(OUT/"render-truth.npz"),case002_read=False,
        manifest_sha256=sha256_file(manifest_path),confirmation_sha256=sha256_file(PILOT/"provenance-confirmation.json"),
        renderer_sha256=sha256_file(Path(__file__))),indent=2))


def prepare():
    import cv2
    lock=scope()
    if np.__version__!=lock["image_preparation"]["numpy"] or cv2.__version__!=lock["image_preparation"]["opencv"]:
        raise ValueError("Unexpected image-preparation runtime")
    started=time.perf_counter();record=json.loads((OUT/"render.json").read_text())
    if sha256_file(OUT/"render-truth.npz")!=record["truth_sha256"]: raise ValueError("Changed oracle truth")
    truth=np.load(OUT/"render-truth.npz",allow_pickle=False);ids=np.flatnonzero(truth["visible"][0])
    if len(ids)!=2355: raise ValueError("Changed initialized population")
    video=[]
    for row in record["rows"]:
        path=OUT/row["image"]
        if sha256_file(path)!=row["sha256"]: raise ValueError("Changed rendered input")
        image=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
        image=cv2.cvtColor(image,cv2.COLOR_BGRA2RGB)[320:960,:720]
        video.append(cv2.resize(image,(256,256),interpolation=cv2.INTER_AREA))
    uv=((truth["pixels"][0,ids]-CROP[:2])/(CROP[2:]-CROP[:2]-1)).astype(np.float32)
    np.savez_compressed(OUT/"input.npz",video=np.array(video),uv=uv,aspect=np.array([720/640],np.float32))
    np.savez_compressed(OUT/"evaluation-truth.npz",ids=ids,target_xy=truth["pixels"][:,ids]-CROP[:2],visible=truth["visible"][:,ids],
        target_camera0_mm=truth["points_normalized"][ids]@truth["extrinsics"][0,:,:3].T*truth["radius_mm"]+truth["extrinsics"][0,:,3]*truth["radius_mm"],
        all_original_ids=np.arange(5000))
    (OUT/"input-lock.json").write_text(json.dumps(dict(input_sha256=sha256_file(OUT/"input.npz"),expected_keys=["aspect","uv","video"],points=2355,frames=32)))
    (OUT/"preparation.json").write_text(json.dumps(dict(status="TECHNICAL_CHECK_PASSED",input_sha256=sha256_file(OUT/"input.npz"),
        truth_sha256=sha256_file(OUT/"evaluation-truth.npz"),query_count=len(ids),uninitialized_original_ids=5000-len(ids),seconds=time.perf_counter()-started),indent=2))


def compare_batch_head(single, chunked, expected_shape):
    import torch
    if (tuple(single.shape)!=expected_shape or chunked.shape!=single.shape
            or single.dtype!=torch.float32 or chunked.dtype!=torch.float32
            or not torch.isfinite(single).all() or not torch.isfinite(chunked).all()):
        raise ValueError("Invalid finite FP32 diagnostic head")
    a,b=single.double(),chunked.double();delta=(a-b).abs()
    mismatch=~torch.isclose(single,chunked,atol=1e-6,rtol=1e-6)
    details=dict(shape=list(a.shape),all_component_max_abs=float(delta.max()),
                 old_1e6_mismatch_components=int(mismatch.sum()),old_1e6_pass=False)
    try: torch.testing.assert_close(single,chunked,atol=1e-6,rtol=1e-6)
    except AssertionError as error: details["old_1e6_message"]=str(error)
    else: details["old_1e6_pass"]=True
    return details


def infer(result_dir=OUT, batch_diagnostic=False):
    result_dir = Path(result_dir)
    (result_dir/"inference-live.json").write_text(json.dumps(dict(pid=os.getpid(),run_token=os.environ["HF0264_RUN_TOKEN"])))
    import torch
    import yaml
    from check_opend4rt_loader_0262 import check_sources,peak_working_set
    from opend4rt_storage_0264 import load_model,verify_bound
    started=time.perf_counter();lock=scope();check_sources()
    if (torch.__version__,np.__version__,yaml.__version__)!=("2.10.0+cpu","2.2.5","6.0.3"): raise ValueError("Unexpected inference runtime")
    torch.set_num_threads(8);torch.set_num_interop_threads(1)
    sys.path.insert(0,str(ROOT/"assets/private/opend4rt-loader-0262/upstream"))
    from src.model.d4rt import D4RTModel
    input_lock=json.loads((OUT/"input-lock.json").read_text())
    if sha256_file(OUT/"input.npz")!=input_lock["input_sha256"]: raise ValueError("Changed worker input")
    data=np.load(OUT/"input.npz",allow_pickle=False)
    if (sorted(data.files)!=["aspect","uv","video"] or data["video"].shape!=(32,256,256,3)
            or data["video"].dtype!=np.uint8 or data["uv"].shape!=(2355,2)
            or data["uv"].dtype!=np.float32 or data["aspect"].shape!=(1,)):
        raise ValueError("Unexpected worker support")
    config=yaml.safe_load((ROOT/"assets/private/opend4rt-loader-0262/model.yaml").read_text())["model"]
    if config["encoder"]["pretrained"]["enabled"] is not False: raise ValueError("Extra initializer forbidden")
    with torch.device("meta"): model=D4RTModel(config)
    model,weights=load_model(model,OUT/"model")
    if weights["source_sha256"]!=lock["checkpoint_sha256"] or len(weights["tensors"])!=627 or weights["bytes"]!=4649733172: raise ValueError("Wrong full model")
    video=torch.from_numpy(data["video"]).permute(0,3,1,2)[None].float()/255
    aspect=torch.from_numpy(data["aspect"])[None]
    uv=torch.from_numpy(data["uv"])
    if not torch.isfinite(uv).all() or not ((uv>=0)&(uv<=1)).all() or float(aspect[0,0])!=1.125: raise ValueError("Invalid normalized source queries")
    output={};control_errors={};raw_controls={};control_details={}
    with torch.inference_mode():
        memory=model.encode_video(video,aspect)
        times=torch.tensor([0,3,6,9,12,15,18,21,31])
        for mode in ["local","reference"]:
            q=dict(u=uv[:9,0][None],v=uv[:9,1][None],t_src=torch.zeros((1,9),dtype=torch.long),t_tgt=times[None],t_cam=(times if mode=="local" else torch.zeros_like(times))[None])
            single=model.decode_queries(video,q,memory)
            parts=[model.decode_queries(video,{k:v[:,i:i+3] for k,v in q.items()},memory) for i in range(0,9,3)]
            if batch_diagnostic:
                for key,value in q.items(): raw_controls[mode+"_query_"+key]=value.cpu().numpy()
                for key in single:
                    raw_controls[mode+"_single_"+key]=single[key].cpu().numpy()
                    raw_controls[mode+"_chunked_"+key]=torch.cat([p[key] for p in parts],1).cpu().numpy()
                # Persist exact values/names before any check can stop this worker.
                np.savez_compressed(result_dir/"batch-control-raw.npz",**raw_controls)
                expected={"xyz_3d":(1,9,3),"uv_2d":(1,9,2),"visibility":(1,9),
                          "displacement":(1,9,3),"normal":(1,9,3),"confidence":(1,9)}
                if set(single)!=set(expected) or any(set(p)!=set(expected) for p in parts):
                    raise ValueError("Unexpected diagnostic output heads")
            for key in single:
                chunked=torch.cat([p[key] for p in parts],1)
                if batch_diagnostic:
                    details=compare_batch_head(single[key],chunked,expected[key])
                    if key=="visibility": details["visibility_call_disagreements"]=int(((single[key]>0)!=(chunked>0)).sum())
                    control_details[mode+"_"+key]=details
                    (result_dir/"batch-control.json").write_text(json.dumps(dict(
                        scope="diagnostic_not_physical_quality_gate",heads=control_details,
                        raw_sha256=sha256_file(result_dir/"batch-control-raw.npz")),indent=2))
                else:
                    torch.testing.assert_close(single[key],chunked,atol=1e-6,rtol=1e-6)
                control_errors[mode+"_"+key]=float((single[key]-chunked).abs().max())
        # Both modes' raw controls now exist before the complete canonical schedule.
        for mode in ["local","reference"]:
            u,v=uv[:,0].repeat_interleave(32),uv[:,1].repeat_interleave(32)
            target=torch.arange(32).repeat(len(uv));pieces={}
            for start in range(0,len(u),512):
                if time.perf_counter()-started>1200: raise TimeoutError("Original inference budget exhausted")
                end=min(start+512,len(u));t=target[start:end]
                query=dict(u=u[start:end][None],v=v[start:end][None],t_src=torch.zeros((1,end-start),dtype=torch.long),t_tgt=t[None],t_cam=(t if mode=="local" else torch.zeros_like(t))[None])
                prediction=model.decode_queries(video,query,memory)
                for key,value in prediction.items():
                    if not torch.isfinite(value).all(): raise ValueError("Nonfinite model output")
                    pieces.setdefault(key,[]).append(value[0].cpu().numpy())
                if start%10240==0:
                    (result_dir/"inference-progress.json").write_text(json.dumps(dict(mode=mode,completed=end,total=len(u),seconds=time.perf_counter()-started,peak_working_set_bytes=peak_working_set())))
            for key,parts in pieces.items():
                values=np.concatenate(parts,0);values=values.reshape(2355,32,*values.shape[1:])
                output[mode+"_"+key]=np.swapaxes(values,0,1)
    verify_bound(model,weights)
    if peak_working_set()>=7_000_000_000: raise RuntimeError("Working-set budget exceeded")
    np.savez_compressed(result_dir/"predictions.npz",**output)
    (result_dir/"inference.json").write_text(json.dumps(dict(status="TECHNICAL_CHECK_PASSED",scope="execution_not_accuracy",input_sha256=input_lock["input_sha256"],
        prediction_sha256=sha256_file(result_dir/"predictions.npz"),all_model_bytes_unchanged=True,all_model_values_finite=True,
        actual_chunk_controls=control_errors,seconds=time.perf_counter()-started,peak_working_set_bytes=peak_working_set(),model_points=2355,frames=32),indent=2))


def evaluate(result_dir=OUT):
    result_dir=Path(result_dir)
    record=json.loads((OUT/"preparation.json").read_text());execution=json.loads((result_dir/"inference.json").read_text())
    if (sha256_file(OUT/"evaluation-truth.npz")!=record["truth_sha256"] or sha256_file(OUT/"input.npz")!=execution["input_sha256"]
            or sha256_file(result_dir/"predictions.npz")!=execution["prediction_sha256"]): raise ValueError("Changed evaluation evidence")
    truth=np.load(OUT/"evaluation-truth.npz",allow_pickle=False);pred=np.load(result_dir/"predictions.npz",allow_pickle=False)
    for key in pred.files:
        if not np.isfinite(pred[key]).all(): raise ValueError("Nonfinite full output")
    xy=pred["local_uv_2d"]*np.array([719,639]);errors=np.linalg.norm(xy-truth["target_xy"],axis=-1)
    transform=similarity(pred["reference_xyz_3d"][0],truth["target_camera0_mm"])
    aligned=apply_similarity(pred["reference_xyz_3d"].reshape(-1,3),transform).reshape(32,2355,3)
    distances=np.linalg.norm(aligned-truth["target_camera0_mm"][None],axis=-1)
    rows=[]
    for frame in range(32):
        visible=truth["visible"][frame];hidden=~visible;called=pred["local_visibility"][frame]>0
        row=dict(frame=frame,visible_count=int(visible.sum()),occluded_count=int(hidden.sum()),p95_px=float(np.percentile(errors[frame,visible],95)),
                 max_px=float(errors[frame,visible].max()),visible_recall=float(called[visible].mean()),
                 occluded_recall=float((~called[hidden]).mean()) if hidden.any() else None,
                 point3d_p95_mm=float(np.percentile(distances[frame,visible],95)),point3d_max_mm=float(distances[frame,visible].max()),
                 all_required_depths_positive=bool((pred["local_xyz_3d"][frame,visible,2]>0).all()))
        row["passed"]=bool(row["p95_px"]<=1 and row["max_px"]<=3 and row["visible_recall"]>=.95
            and (row["occluded_recall"] is None or row["occluded_recall"]>=.95) and row["point3d_p95_mm"]<=2 and row["all_required_depths_positive"])
        rows.append(row)
    np.savez_compressed(result_dir/"errors.npz",pixel_errors=errors,point3d_errors_mm=distances,ids=truth["ids"],visible=truth["visible"])
    passed=all(r["passed"] for r in rows[1:]) and rows[0]["point3d_p95_mm"]<=2
    report=dict(status="TECHNICAL_CHECK_PASSED" if passed else "REJECT",scope="known_source_conditional_capacity_only",rows=rows,
        initialized_ids=2355,uninitialized_original_ids=2645,all_true_visible_pairs_scored=int(truth["visible"][1:].sum()),
        all_true_occluded_pairs_scored=int((~truth["visible"][1:]).sum()),fixed_global_similarity=transform.tolist(),
        camera="UNVERIFIED",head="UNVERIFIED",real_video="UNVERIFIED",no_training_or_upload=True)
    (result_dir/"report.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("action",choices=["controls","render","prepare","infer","evaluate"])
    arguments=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    action=parser.parse_args(arguments).action;started=time.perf_counter();scope()
    try: globals()[action]()
    except BaseException as error:
        (OUT/(action+"-failure.json")).write_text(json.dumps(dict(status="REJECT",error_type=type(error).__name__,error=str(error),seconds=time.perf_counter()-started),indent=2))
        raise
