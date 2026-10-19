"""Scientific views of the actual video-only sparse cloud; no surface completion."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import pycolmap

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
SOURCE = PILOT / "initialization-sfm-0221"
IMAGES = PILOT / "video-sfm-0219/images"


def main():
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Input rights/hash validation failed")
    controls = json.loads((SOURCE / "controls.json").read_text(encoding="utf-8"))
    if controls["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
        raise ValueError("Parent inputs changed")
    output = SOURCE / "sparse-review"
    output.mkdir()
    model = pycolmap.Reconstruction(SOURCE / "sparse/0")
    points = np.array([model.points3D[i].xyz for i in sorted(model.points3D)])
    center = (points.min(0) + points.max(0)) / 2
    radius = float(np.linalg.norm(points - center, axis=1).max())
    sheet = Image.new("RGB", (1200, 1080), (28, 28, 28))
    rows = []
    for column, frame in enumerate((0, 144, 408)):
        name = f"frame-{frame:06d}.png"
        record = next(r for r in controls["frames"] if r["name"] == name)
        path = IMAGES / name
        if sha256_file(path) != record["image_sha256"]:
            raise ValueError("Review photo changed")
        image = model.find_image_with_name(name)
        if image is None:
            raise ValueError("Review frame is not registered")
        extrinsic = image.cam_from_world().matrix()
        intrinsic = model.cameras[image.camera_id].calibration_matrix()
        photo = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(photo)
        errors = []
        for observed in image.points2D:
            if not observed.has_point3D():
                continue
            p = extrinsic[:, :3] @ model.points3D[observed.point3D_id].xyz + extrinsic[:, 3]
            h = intrinsic @ p
            pixel = h[:2] / h[2]
            errors.append(float(np.linalg.norm(pixel - observed.xy)))
            x, y = pixel
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 70, 40))
        photo.thumbnail((400, 710))
        sheet.paste(photo, (column * 400, 25))
        ImageDraw.Draw(sheet).text((column * 400 + 5, 5), f"frame {frame}: actual 3D reprojection", fill="white")
        cam = (points - center) @ extrinsic[:, :3].T
        pixels = cam[:, :2] / radius * 170 + [200, 160]
        cloud = Image.new("RGB", (400, 320), (28, 28, 28))
        pen = ImageDraw.Draw(cloud)
        depth_range = max(float(np.ptp(cam[:, 2])), 1e-12)
        for index in np.argsort(-cam[:, 2]):
            x, y = pixels[index]
            gray = int(110 + 140 * (cam[:, 2].max() - cam[index, 2]) / depth_range)
            pen.ellipse((x - 1.4, y - 1.4, x + 1.4, y + 1.4), fill=(gray, gray, gray))
        sheet.paste(cloud, (column * 400, 755))
        ImageDraw.Draw(sheet).text((column * 400 + 5, 735), f"All {len(points)} points; orthographic; NO FACES", fill="white")
        rows.append({"frame": frame, "observed_points": len(errors),
                     "training_reprojection_p95_px": float(np.percentile(errors, 95))})
    sheet.save(output / "video-and-sparse-cloud.png")
    with (output / "sparse-cloud.ply").open("w", encoding="ascii") as stream:
        stream.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\nproperty double x\nproperty double y\nproperty double z\nend_header\n")
        for point in points:
            stream.write(" ".join(format(float(value), ".17g") for value in point) + "\n")
    (output / "report.json").write_text(json.dumps({"technical_status": "TECHNICAL_CHECK_PASSED",
        "visual_head_acceptance": "UNVERIFIED", "points": len(points), "surface_faces": 0,
        "source_archive_sha256": sha256_file(SOURCE / "model-0-cameras-points.npz"),
        "tool_sha256": sha256_file(Path(__file__)), "views": rows,
        "limits": "Actual video-only sparse geometry in arbitrary scale. Every point shown without trimming; same display scale across views. Reprojection uses training observations. No complete head, anatomical/scan accuracy or held-out acceptance."}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
