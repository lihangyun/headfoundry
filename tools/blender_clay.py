"""Create a reproducible five-view Blender clay diagnostic from one OBJ."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


VIEWS = {"front": 0, "left35": 35, "left90": 90, "right35": -35, "right90": -90}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("obj", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    args = arguments()
    source = args.obj.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=str(source))
    meshes = [item for item in bpy.context.scene.objects if item.type == "MESH"]
    if not meshes:
        raise ValueError("OBJ contains no mesh objects")
    head = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for item in meshes:
            item.select_set(True)
        bpy.context.view_layer.objects.active = head
        bpy.ops.object.join()
    head.name = "HeadFoundry_Clay"

    # Current HeadFoundry OBJ convention is y-down/z-back; Blender is z-up/y-back.
    head.rotation_euler.x = math.radians(-90)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    corners = [head.matrix_world @ Vector(corner) for corner in head.bound_box]
    lower = Vector(tuple(min(point[index] for point in corners) for index in range(3)))
    upper = Vector(tuple(max(point[index] for point in corners) for index in range(3)))
    extent = upper - lower
    if min(extent) <= 0:
        raise ValueError("OBJ bounds must have three positive dimensions")
    scale = 2.0 / extent.z
    head.scale = (scale,) * 3
    head.location = -(lower + upper) * 0.5 * scale
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

    material = bpy.data.materials.new("Neutral_clay")
    material.diffuse_color = (0.72, 0.74, 0.78, 1.0)
    material.roughness = 0.82
    head.data.materials.clear()
    head.data.materials.append(material)
    for polygon in head.data.polygons:
        polygon.use_smooth = True

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Diagnostic_World")
    scene.world.color = (0.025, 0.025, 0.025)

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "Diagnostic_Camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.45
    scene.camera = camera

    for name, location, energy, size in (
        ("Key", (3.5, -4.0, 4.5), 900, 4.0),
        ("Fill", (-4.0, -2.0, 2.0), 500, 3.0),
        ("Rim", (0.0, 3.0, 4.0), 700, 3.0),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        look_at(light, Vector((0, 0, 0)))

    radius = 5.0
    for name, yaw in VIEWS.items():
        angle = math.radians(yaw)
        camera.location = (radius * math.sin(angle), -radius * math.cos(angle), 0.0)
        look_at(camera, Vector((0, 0, 0)))
        scene.render.filepath = str(output / f"{name}.png")
        bpy.ops.render.render(write_still=True)

    blend_path = output / "diagnostic.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    report = {
        "status": "UNVERIFIED",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "blender_version": bpy.app.version_string,
        "views": list(VIEWS),
        "coordinate_conversion": "HeadFoundry y-down/z-back to Blender z-up/y-back",
        "limitations": "Clay rendering is a visual diagnostic, not camera, identity, or likeness acceptance.",
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
