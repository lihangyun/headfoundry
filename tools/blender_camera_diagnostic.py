"""Render one OBJ through locked HeadFoundry cameras and photo backgrounds."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


VIEW_NAMES = ("front", "left30", "left90", "right30", "right90")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("obj", type=Path)
    parser.add_argument("cameras", type=Path)
    parser.add_argument("photos", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def set_camera(camera: bpy.types.Object, intrinsic: np.ndarray, extrinsic: np.ndarray,
               width: int, height: int) -> None:
    conversion = np.diag([1.0, -1.0, -1.0, 1.0])
    world_to_camera = np.eye(4)
    world_to_camera[:3] = extrinsic
    camera.matrix_world = Matrix((conversion @ world_to_camera).tolist()).inverted()
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "HORIZONTAL"
    camera.data.sensor_width = 36.0
    camera.data.lens = float(intrinsic[0, 0]) * camera.data.sensor_width / width
    camera.data.shift_x = (width * 0.5 - float(intrinsic[0, 2])) / width
    camera.data.shift_y = (float(intrinsic[1, 2]) - height * 0.5) / width
    camera.data.clip_start = 0.001
    camera.data.clip_end = 100.0


def projection_error(scene: bpy.types.Scene, camera: bpy.types.Object, vertices: np.ndarray,
                     intrinsic: np.ndarray, extrinsic: np.ndarray, width: int, height: int) -> dict:
    camera_points = vertices @ extrinsic[:, :3].T + extrinsic[:, 3]
    valid = camera_points[:, 2] > 1e-6
    indices = np.flatnonzero(valid)[:: max(1, valid.sum() // 2000)]
    projected = camera_points[indices] @ intrinsic.T
    expected = projected[:, :2] / projected[:, 2, None]
    actual = []
    for index in indices:
        ndc = world_to_camera_view(scene, camera, Vector(vertices[index]))
        actual.append((ndc.x * width, (1.0 - ndc.y) * height))
    errors = np.linalg.norm(np.asarray(actual) - expected, axis=1)
    return {"samples": len(errors), "p95_px": float(np.percentile(errors, 95)), "max_px": float(errors.max())}


def main() -> None:
    args = arguments()
    source, camera_path, photo_root, output = (
        args.obj.resolve(), args.cameras.resolve(), args.photos.resolve(), args.output.resolve()
    )
    if not source.is_file() or not camera_path.is_file() or not photo_root.is_dir():
        raise FileNotFoundError("OBJ, camera archive and photo directory must exist")
    photos = [photo_root / f"{name}.png" for name in VIEW_NAMES]
    missing = [str(path) for path in photos if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing photos: {missing}")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    archive = np.load(camera_path, allow_pickle=False)
    intrinsics = np.asarray(archive["intrinsics"], dtype=float)
    extrinsics = np.asarray(archive["extrinsics"], dtype=float)
    if intrinsics.shape != (5, 3, 3) or extrinsics.shape != (5, 3, 4):
        raise ValueError("expected five 3x3 intrinsics and five 3x4 world-to-camera matrices")

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
    vertices = np.array([head.matrix_world @ vertex.co for vertex in head.data.vertices], dtype=float)

    material = bpy.data.materials.new("Camera_diagnostic_clay")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.02, 0.42, 0.8, 1.0)
    shader.inputs["Roughness"].default_value = 0.78
    head.data.materials.clear()
    head.data.materials.append(material)
    for polygon in head.data.polygons:
        polygon.use_smooth = True

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    scene.view_settings.look = "AgX - Medium High Contrast"
    camera_data = bpy.data.cameras.new("Locked_Camera_Data")
    camera = bpy.data.objects.new("Locked_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    compositor = bpy.data.node_groups.new("Camera_Diagnostic_Compositor", "CompositorNodeTree")
    compositor.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.compositing_node_group = compositor

    bpy.ops.object.light_add(type="AREA")
    light = bpy.context.object
    light.name = "Camera_Fill"
    light.data.energy = 1200
    light.data.shape = "DISK"
    light.data.size = 4.0

    report = {
        "status": "UNVERIFIED",
        "source_sha256": digest(source),
        "camera_sha256": digest(camera_path),
        "photo_sha256": {path.stem: digest(path) for path in photos},
        "blender_version": bpy.app.version_string,
        "views": {},
        "limitations": "Locked-camera photo overlays are diagnostic evidence, not camera or likeness acceptance.",
    }
    for index, (name, photo) in enumerate(zip(VIEW_NAMES, photos)):
        image = bpy.data.images.load(str(photo), check_existing=False)
        width, height = image.size
        scene.render.resolution_x, scene.render.resolution_y = width, height
        scene.render.resolution_percentage = 100
        set_camera(camera, intrinsics[index], extrinsics[index], width, height)
        light.location = camera.location
        light.rotation_euler = camera.rotation_euler

        nodes, links = compositor.nodes, compositor.links
        nodes.clear()
        layers = nodes.new("CompositorNodeRLayers")
        background = nodes.new("CompositorNodeImage")
        background.image = image
        over = nodes.new("CompositorNodeAlphaOver")
        over.inputs["Factor"].default_value = 0.36
        composite = nodes.new("NodeGroupOutput")
        links.new(background.outputs[0], over.inputs["Background"])
        links.new(layers.outputs[0], over.inputs["Foreground"])
        links.new(over.outputs[0], composite.inputs["Image"])

        diagnostic = projection_error(
            scene, camera, vertices, intrinsics[index], extrinsics[index], width, height
        )
        if diagnostic["p95_px"] > 0.05:
            raise ValueError(f"{name} Blender camera projection mismatch: {diagnostic}")
        scene.render.filepath = str(output / f"{name}-overlay.png")
        bpy.ops.render.render(write_still=True)
        report["views"][name] = {"size": [width, height], "projection_replay": diagnostic}
        bpy.data.images.remove(image)

    bpy.ops.wm.save_as_mainfile(filepath=str(output / "camera-diagnostic.blend"))
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
