"""Source-only3D tracker capacity oracle;never video-derived reconstruction."""

import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np

from check_recurrent_material_0258 import sha, to_model, from_model, infer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/recurrent-3d-0259"
BASE = ROOT / "assets/private/real-capture-pilot-v1"
REFERENCE = BASE / "scan-motion-truth-0230-upright"
REFERENCE_SHA = "eea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942"
SEQUENCE = [0, 2, 4, 2, 0, 1, 3, 1, 0, 5, 0]
OFFSET = np.array([0, 320])
EXTENT = np.array([720, 640])


def reference():
    assert sha(REFERENCE / "known-motion.npz") == REFERENCE_SHA
    return np.load(REFERENCE / "known-motion.npz", allow_pickle=False)


def render():
    import bpy
    from mathutils import Vector
    sys.path.insert(0, str(ROOT / "src"))
    from headfoundry.manifest import validate_input_assets
    from headfoundry.scan import read_binary_stl
    from headfoundry.camera import project
    from blender_camera_diagnostic import set_camera, projection_error

    started = time.perf_counter()
    if (OUT / "render.json").exists():
        raise FileExistsError("Preserve first render")
    doc = json.loads((BASE / "manifest.json").read_text())
    confirmation = json.loads((BASE / "provenance-confirmation.json").read_text())
    selected = [x for x in doc["inputs"] if x["id"] == "real-case-001-skin"]
    assert len(selected) == 1 and not doc["training_allowed"] and not doc["upload_allowed"]
    assert not validate_input_assets(dict(doc, inputs=selected), BASE)
    assert confirmation["manifest_sha256"] == sha(BASE / "manifest.json")
    assert confirmation["cases"]["real-case-001"]["scan_units"] == "millimeter"
    old = json.loads((REFERENCE / "controls.json").read_text())
    assert selected[0]["sha256"] == old["source_sha256"]
    raw, faces = read_binary_stl(Path(selected[0]["path"]))
    vertices = (raw - old["center_mm"]) / old["radius_mm"]
    data = reference()
    reconstructed_samples = np.einsum("ni,nij->nj", data["source_barycentric"],
                                     vertices[faces[data["source_triangle_ids"]]])
    assert np.max(np.abs(reconstructed_samples - data["vertices_normalized"])) < 1e-12
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new("UNCHANGED_SOURCE_ORACLE")
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    mesh.update()
    head = bpy.data.objects.new("SUPPLIED_SCAN_NOT_RECONSTRUCTED", mesh)
    bpy.context.scene.collection.objects.link(head)
    material = bpy.data.materials.new("FIXED_SYNTHETIC_MATERIAL_NOT_HUMAN_ALBEDO")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    coordinates = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 48
    noise.inputs["Detail"].default_value = 2
    noise.inputs["Roughness"].default_value = .5
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (.15, .15, .15, 1)
    ramp.color_ramp.elements[1].color = (.75, .75, .75, 1)
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(coordinates.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 720, 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    rows = []
    for i, name in enumerate(data["view_names"]):
        k, extrinsic = data["intrinsic"], data["extrinsics_normalized"][i]
        assert np.max(np.abs(project(k @ extrinsic, reconstructed_samples) - data["pixels"][i])) < 1e-8
        set_camera(camera, k, extrinsic, 720, 1280)
        bpy.context.view_layer.update()
        replay = projection_error(scene, camera, vertices, k, extrinsic, 720, 1280)
        assert replay["max_px"] <= .05
        path = OUT / f"{name}-patterned-source.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rows.append(dict(view=str(name), image=path.name, sha256=sha(path), replay=replay))
        assert time.perf_counter() - started <= 180
    assert sha(Path(selected[0]["path"])) == old["source_sha256"]
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="source_render_only", renders=rows,
                  source_sha256=old["source_sha256"], reference_sha256=REFERENCE_SHA,
                  seconds=time.perf_counter() - started, blender=bpy.app.version_string,
                  case002_read=False, bone_read=False, training=False, upload=False)
    (OUT / "render.json").write_text(json.dumps(report, indent=2))


def prepare():
    import cv2
    from PIL import Image
    started = time.perf_counter()
    data = reference()
    metadata = json.loads((OUT / "render.json").read_text())
    pixels, visible = data["pixels"], data["visible"]
    all_visible_pixels = pixels[visible] - OFFSET
    assert np.all(all_visible_pixels >= 0) and np.all(all_visible_pixels < EXTENT)
    ids = np.flatnonzero(visible[0])
    assert len(ids) == 2355
    images = []
    for row in metadata["renders"]:
        path = OUT / row["image"]
        assert sha(path) == row["sha256"]
        image = np.array(Image.open(path).convert("RGB"))[320:960, :720]
        assert image.shape == (640, 720, 3)
        images.append(cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR))
    queries = pixels[0, ids] - OFFSET
    assert np.max(np.abs(from_model(to_model(queries, EXTENT), EXTENT) - queries)) < 1e-10
    np.savez_compressed(OUT / "input.npz", video=np.array(images)[SEQUENCE],
                        queries_yx=to_model(queries, EXTENT).astype(np.float32))
    np.savez_compressed(OUT / "truth.npz", ids=data["point_ids"][ids],
                        target_xy=pixels[SEQUENCE][:, ids], visible=visible[SEQUENCE][:, ids])
    report = dict(status="TECHNICAL_CHECK_PASSED", reference_sha256=REFERENCE_SHA,
                  input_sha256=sha(OUT / "input.npz"), truth_sha256=sha(OUT / "truth.npz"),
                  initialized_points=len(ids), original_points=len(data["point_ids"]),
                  original_ids_without_initial_visibility=5000-len(ids),
                  visible_counts=visible[SEQUENCE][:, ids].sum(1).tolist(),
                  sequence=SEQUENCE, crop=[0, 320, 720, 960], seconds=time.perf_counter()-started,
                  worker_truth_keys_excluded=True)
    assert report["seconds"] <= 30
    (OUT / "preparation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def evaluate():
    prep = json.loads((OUT / "preparation.json").read_text())
    inference = json.loads((OUT / "inference.json").read_text())
    assert sha(OUT / "input.npz") == prep["input_sha256"] == inference["input_sha256"]
    assert sha(OUT / "truth.npz") == prep["truth_sha256"]
    assert sha(OUT / "predictions.npz") == inference["prediction_sha256"]
    data = reference()
    original = np.flatnonzero(data["visible"][0])
    with np.load(OUT / "truth.npz", allow_pickle=False) as truth:
        target, visible = truth["target_xy"], truth["visible"]
        assert np.array_equal(truth["ids"], data["point_ids"][original])
        assert np.array_equal(target, data["pixels"][SEQUENCE][:, original])
        assert np.array_equal(visible, data["visible"][SEQUENCE][:, original])
    with np.load(OUT / "predictions.npz", allow_pickle=False) as pred:
        tracks, predicted_visible = pred["tracks_xy"] + OFFSET, pred["visible"]
    assert tracks.shape == target.shape == (11, 2355, 2)
    assert predicted_visible.shape == visible.shape == (11, 2355)
    errors = np.linalg.norm(tracks-target, axis=-1)
    rows = []
    for i in range(11):
        observed, hidden = visible[i], ~visible[i]
        e = errors[i, observed]
        visible_recall = float(predicted_visible[i, observed].mean())
        occluded_recall = float((~predicted_visible[i, hidden]).mean()) if hidden.any() else None
        row = dict(frame=i, source_view=int(SEQUENCE[i]), true_visible=int(observed.sum()),
                   true_occluded=int(hidden.sum()), p95=float(np.quantile(e, .95)),
                   maximum=float(e.max()), visible_recall=visible_recall, occluded_recall=occluded_recall,
                   finite=bool(np.isfinite(tracks[i]).all()))
        row["passed"] = row["finite"] and row["p95"] <= 1 and row["maximum"] <= 3 and visible_recall >= .95 and (occluded_recall is None or occluded_recall >= .95)
        rows.append(row)
    np.savez_compressed(OUT / "evaluation.npz", ids=data["point_ids"][original], errors=errors,
                        truth_visible=visible, predicted_visible=predicted_visible)
    report = dict(status="TECHNICAL_CHECK_PASSED" if all(x["passed"] for x in rows[1:]) else "REJECT",
                  scope="conditional_source_only_3d_tracking", rows=rows, initialized_points=2355,
                  nonquery_visible_pairs=int(visible[1:].sum()), original_archive_sha256=REFERENCE_SHA,
                  input_sha256=sha(OUT / "input.npz"), truth_sha256=sha(OUT / "truth.npz"),
                  prediction_sha256=sha(OUT / "predictions.npz"), camera_status="UNVERIFIED",
                  head_status="UNVERIFIED", real_video_inference=False, training=False, upload=False)
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    # Blender's arguments precede --;ordinary Python uses the same action names.
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["render", "prepare", "infer", "evaluate"])
    args = parser.parse_args(argv)
    {"render": render, "prepare": prepare, "infer": lambda: infer(OUT, EXTENT),
     "evaluate": evaluate}[args.action]()
