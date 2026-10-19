"""Blender source-only preview in raw STL axes; no anatomical alignment or fit."""
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 1:
        raise ValueError("Provide one local intake directory")
    output = (ROOT / args[0]).resolve()
    if not output.is_relative_to(ROOT / "assets/private"):
        raise ValueError("Private project output required")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    errors = validate_input_assets(manifest, output)
    if errors:
        raise ValueError(errors)
    target = output / "scan-preview"
    target.mkdir()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Scan_Intake_World")
    scene.world.color = (.08, .08, .08)
    material = bpy.data.materials.new("Neutral_Scan_Clay")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (.5, .5, .5, 1)
    shader.inputs["Roughness"].default_value = .8
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.4
    scene.camera = camera
    lights = []
    for energy, size in ((500, 4.), (900, 2.)):
        bpy.ops.object.light_add(type="AREA")
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        lights.append(light)
    views = {"positive-X": (1, 0, 0), "negative-X": (-1, 0, 0),
             "positive-Y": (0, 1, 0), "negative-Y": (0, -1, 0),
             "positive-Z": (0, 0, 1), "negative-Z": (0, 0, -1)}
    records, started = [], time.perf_counter()
    for case in manifest["cases"]:
        files = {kind: Path(case["files"][kind]) for kind in ("skin", "bone")}
        meshes = {kind: read_binary_stl(path) for kind, path in files.items()}
        # One display similarity for both scans preserves their original relation.
        points = np.concatenate([mesh[0] for mesh in meshes.values()])
        center = (points.max(0) + points.min(0)) / 2
        radius = float(np.ptp(points, axis=0).max() / 2)
        if radius <= 0:
            raise ValueError("Empty scan extent")
        for kind, (vertices, faces) in meshes.items():
            mesh = bpy.data.meshes.new("Original_Scan_Triangles")
            mesh.from_pydata(((vertices - center) / radius).tolist(), [], faces.tolist())
            mesh.update()
            head = bpy.data.objects.new("Unmodified_" + kind, mesh)
            scene.collection.objects.link(head)
            mesh.materials.append(material)
            for polygon in mesh.polygons:
                polygon.use_smooth = True
            for name, direction in views.items():
                if time.perf_counter() - started > 300:
                    raise TimeoutError("Stop at five-minute intake preview budget")
                camera.location = Vector(direction) * 4
                camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
                bpy.context.view_layer.update()
                lights[0].location = camera.location
                lights[0].rotation_euler = camera.rotation_euler
                lights[1].location = camera.location + camera.matrix_world.to_3x3() @ Vector((-2, 2, -1))
                lights[1].rotation_euler = (-lights[1].location).to_track_quat("-Z", "Y").to_euler()
                path = target / f"{case['id']}-{kind}-{name}.png"
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                records.append({"case": case["id"], "kind": kind, "view": name, "image": path.name,
                                "image_sha256": sha256_file(path), "source_sha256": sha256_file(files[kind]),
                                "display_center_source_units": center.tolist(), "display_radius_source_units": radius,
                                "camera_world_matrix": [list(row) for row in camera.matrix_world]})
            bpy.data.objects.remove(head, do_unlink=True)
            bpy.data.meshes.remove(mesh)
    result = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
              "renders": records, "blender_version": bpy.app.version_string,
              "renderer_sha256": sha256_file(Path(__file__)), "elapsed_seconds": time.perf_counter() - started,
              "limits": "Source previews in raw axes, normalized only for display. No repair, anatomy alignment, camera estimation, scan accuracy or reconstruction acceptance."}
    (target / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
