"""Blender-only fixed-camera white meshes for the frozen0208 oracle output.

Reuses the existing camera/replay helpers; no input images or shape fitting.
"""
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blender_camera_diagnostic import set_camera, projection_error, digest


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "artifacts/experiment-0208"
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    if not all(r["mesh_safe"] for r in report["results"]):
        raise ValueError("unsafe candidate; stop before white-mesh review")
    if (output / "render-report.json").exists():
        raise FileExistsError("preserve the first rendering run")
    cameras = np.load(output / "cameras.npz", allow_pickle=False)
    names = ("front", "left30", "left90", "right30", "right90")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Fixed_Diagnostic_World")
    scene.world.color = (.035, .035, .035)
    scene.view_settings.look = "AgX - Medium High Contrast"
    material = bpy.data.materials.new("Neutral_White_Mesh")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (.35, .35, .35, 1)
    shader.inputs["Roughness"].default_value = .78
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    lights = []
    for name, energy, size in (("Fill", 220, 4.), ("Key", 1100, 1.5)):
        bpy.ops.object.light_add(type="AREA")
        light = bpy.context.object
        light.name, light.data.energy, light.data.size = name, energy, size
        light.data.shape = "DISK"
        lights.append(light)
    started, records = time.perf_counter(), []
    for case in report["results"]:
        folder = output / f"case-{case['case']:02d}"
        target = folder / "clay"
        if target.exists():
            raise FileExistsError(target)
        target.mkdir()
        for version in ("truth", "prior", "candidate"):
            source = folder / f"{version}.obj"
            bpy.ops.wm.obj_import(filepath=str(source))
            head = bpy.context.selected_objects[0]
            head.matrix_world = Matrix.Identity(4)
            head.data.materials.clear()
            head.data.materials.append(material)
            for polygon in head.data.polygons:
                polygon.use_smooth = True
            vertices = np.array([v.co for v in head.data.vertices])
            for i, name in enumerate(names):
                if time.perf_counter()-started > 900:
                    raise TimeoutError("render budget exhausted; preserve partial output")
                k, e = cameras["intrinsics"][i], cameras["extrinsics"][i]
                set_camera(camera, k, e, 512, 512)
                bpy.context.view_layer.update()
                lights[0].location = camera.location
                lights[0].rotation_euler = camera.rotation_euler
                lights[1].location = camera.location + camera.matrix_world.to_3x3() @ Vector((-2, 1.5, -1))
                lights[1].rotation_euler = (-lights[1].location).to_track_quat("-Z", "Y").to_euler()
                replay = projection_error(scene, camera, vertices, k, e, 512, 512)
                if replay["max_px"] > .05:
                    raise ValueError("projection mismatch: " + str(replay))
                path = target / f"{version}-{name}.png"
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                records.append({"case": case["case"], "version": version, "view": name,
                                "source_sha256": digest(source), "image_sha256": digest(path),
                                "projection_replay": replay})
            if case["case"] == 0 and version == "candidate":
                bpy.ops.wm.save_as_mainfile(filepath=str(output / "diagnostic.blend"))
            mesh = head.data
            bpy.data.objects.remove(head, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        print("Completed fixed white meshes", case["case"], flush=True)
    result = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
              "blender_version": bpy.app.version_string, "renderer_sha256": digest(Path(__file__)),
              "elapsed_seconds": time.perf_counter()-started, "renders": records,
              "lighting": "same camera-relative neutral oblique key/fill; no mesh-dependent normalization",
              "limits": "Same-source synthetic oracle surfaces only. Skin exterior has no eyeballs; "
              "white meshes neither establish photo likeness nor certify anatomical/self-intersection safety."}
    (output / "render-report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
