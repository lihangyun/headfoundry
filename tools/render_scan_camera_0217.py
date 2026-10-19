"""Known source-scan overlays for0217, including rejected camera diagnostics."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
SOURCE = PILOT / "camera-baseline-0217"
CALIBRATION = SOURCE / "calibration"
OUTPUT = CALIBRATION / "scan-projection-review"
sys.path.insert(0, str(ROOT / "src"))
from headfoundry.manifest import sha256_file, validate_input_assets


def render():
    import bpy
    import numpy as np
    from mathutils import Vector
    from headfoundry.scan import read_binary_stl
    sys.path.insert(0, str(ROOT / "tools"))
    from blender_camera_diagnostic import set_camera, projection_error

    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source input validation failed")
    source = Path(next(a for a in manifest["inputs"] if a["id"] == "real-case-001-skin")["path"])
    report = json.loads((CALIBRATION / "report.json").read_text(encoding="utf-8"))
    if sha256_file(source) != report["source_sha256"] or sha256_file(CALIBRATION / "cameras.npz") != report["cameras_sha256"]:
        raise ValueError("Source or camera archive changed")
    cameras = np.load(CALIBRATION / "cameras.npz", allow_pickle=False)
    OUTPUT.mkdir()
    vertices, faces = read_binary_stl(source)
    vertices *= .001  # Display in meters; camera translations receive the same scale.
    center = (vertices.max(0) + vertices.min(0)) / 2
    radius = float(np.linalg.norm(vertices - center, axis=1).max())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new("Original_Millimeter_Scan_At_Meter_Scale")
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    mesh.update()
    head = bpy.data.objects.new("UNCHANGED_SOURCE_SCAN", mesh)
    bpy.context.scene.collection.objects.link(head)
    material = bpy.data.materials.new("Neutral_Clay")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (.35, .35, .35, 1)
    shader.inputs["Roughness"].default_value = .8
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
    scene.world = bpy.data.worlds.new("Diagnostic_World")
    scene.world.color = (.035, .035, .035)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    lights = []
    for energy, size in ((10., radius * 3), (30., radius * 1.5)):
        bpy.ops.object.light_add(type="AREA")
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        lights.append(light)
    results = []
    for frame, intrinsic, raw_extrinsic in zip(cameras["frame_indices"], cameras["intrinsics"], cameras["extrinsics"]):
        extrinsic = raw_extrinsic.copy()
        extrinsic[:, 3] *= .001
        set_camera(camera, intrinsic, extrinsic, 720, 1280)
        bpy.context.view_layer.update()
        lights[0].location, lights[0].rotation_euler = camera.location, camera.rotation_euler
        lights[1].location = camera.location + camera.matrix_world.to_3x3() @ Vector((-2 * radius, 1.5 * radius, -radius))
        lights[1].rotation_euler = (Vector(center) - lights[1].location).to_track_quat("-Z", "Y").to_euler()
        replay = projection_error(scene, camera, vertices, intrinsic, extrinsic, 720, 1280)
        if replay["max_px"] > .05:
            raise ValueError("Blender projection replay failed")
        path = OUTPUT / f"frame-{frame:06d}-scan.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        results.append({"frame": int(frame), "image": path.name, "sha256": sha256_file(path), "projection_replay": replay})
    (OUTPUT / "render-report.json").write_text(json.dumps({"status": "TECHNICAL_CHECK_PASSED",
        "source_only": True, "camera_screen_status": report["screen_status"], "renders": results,
        "source_sha256": report["source_sha256"], "cameras_sha256": report["cameras_sha256"],
        "renderer_sha256": sha256_file(Path(__file__)), "blender_version": bpy.app.version_string,
        "limits": "Unchanged source scan through experimental cameras; not recovered head geometry or camera acceptance."}, indent=2), encoding="utf-8")


def assemble():
    from PIL import Image, ImageDraw
    report = json.loads((OUTPUT / "render-report.json").read_text(encoding="utf-8"))
    derived = json.loads((SOURCE / "derived-manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(derived, SOURCE):
        raise ValueError("Video frames changed")
    target = OUTPUT / "front-and-oblique-scan-overlays.png"
    if target.exists():
        raise FileExistsError("Preserve original review layout")
    sheet = Image.new("RGB", (960, 3 * 600), (28, 28, 28))
    for row, frame in enumerate((0, 208, 555)):
        entry = next(r for r in report["renders"] if r["frame"] == frame)
        path = OUTPUT / entry["image"]
        if sha256_file(path) != entry["sha256"]:
            raise ValueError("Source scan render changed")
        photo_path = next(a["path"] for a in derived["inputs"] if a["id"] == f"frame-{frame:06d}")
        photo, scan = Image.open(photo_path).convert("RGBA"), Image.open(path).convert("RGBA")
        alpha = scan.getchannel("A").point(lambda p: int(p * .35))
        overlay = scan.copy()
        overlay.putalpha(alpha)
        images = (photo, Image.alpha_composite(Image.new("RGBA", scan.size, (28, 28, 28, 255)), scan),
                  Image.alpha_composite(photo, overlay))
        for column, (image, label) in enumerate(zip(images, ("VIDEO", "UNCHANGED SCAN", "CAMERA OVERLAY"))):
            image.thumbnail((320, 570))
            sheet.paste(image.convert("RGB"), (column * 320, row * 600 + 25))
            ImageDraw.Draw(sheet).text((column * 320 + 5, row * 600 + 5), f"frame {frame}: {label}", fill="white")
    sheet.save(target)


if __name__ == "__main__":
    assemble() if "--assemble" in sys.argv else render()
