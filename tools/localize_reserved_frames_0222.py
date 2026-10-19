"""Frozen video-only point cloud versus future pixels; no model optimization."""
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
import pycolmap

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from temporal_video_sfm_0220 import resolve_keyframe_hashes, track_step

PILOT = ROOT / "assets/private/real-capture-pilot-v1"
SOURCE = PILOT / "initialization-sfm-0221"
OUT = PILOT / "reserved-localization-0222"


def estimate_reserved_pose(points, pixels, point_ids, intrinsic, cloud):
    points, pixels, cloud = np.asarray(points, float), np.asarray(pixels, float), np.asarray(cloud, float)
    point_ids, intrinsic = np.asarray(point_ids), np.asarray(intrinsic, float)
    if (points.ndim != 2 or points.shape[1:] != (3,) or pixels.shape != (len(points), 2)
            or point_ids.shape != (len(points),) or intrinsic.shape != (3, 3)
            or cloud.ndim != 2 or cloud.shape[1:] != (3,) or not len(cloud)
            or not all(np.isfinite(a).all() for a in (points, pixels, intrinsic, cloud))
            or not np.issubdtype(point_ids.dtype, np.integer)):
        raise ValueError("Finite matching3D/2D points, integer IDs and camera required")
    training = point_ids % 2 == 0
    validation = ~training
    record = {"status": "REJECT", "training_points": int(training.sum()),
              "validation_points": int(validation.sum())}
    if min(training.sum(), validation.sum()) < 30:
        return None, None, dict(record, reason="insufficient_frozen_track_support")
    cv2.setRNGSeed(222)
    ok, rotation, translation, inliers = cv2.solvePnPRansac(points[training], pixels[training], intrinsic, None,
        iterationsCount=10000, reprojectionError=3., confidence=.999, flags=cv2.SOLVEPNP_EPNP)
    if not ok or inliers is None or len(inliers) < 30:
        return None, None, dict(record, reason="insufficient_training_pose_inliers",
                                training_inliers=0 if inliers is None else len(inliers))
    selected = inliers.ravel()
    ok, rotation, translation = cv2.solvePnP(points[training][selected], pixels[training][selected], intrinsic,
        None, rotation, translation, True, flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:
        return None, None, dict(record, reason="training_pose_refinement_failed")
    matrix, _ = cv2.Rodrigues(rotation)
    extrinsic = np.c_[matrix, translation.ravel()]
    camera = points @ matrix.T + translation.ravel()
    projected = camera @ intrinsic.T
    pixels_predicted = projected[:, :2] / projected[:, 2:]
    errors = np.linalg.norm(pixels_predicted - pixels, axis=1)
    minimum_depth = float((cloud @ matrix.T + translation.ravel())[:, 2].min())
    span = np.ptp(pixels[validation], axis=0)
    gates = {"validation_p95_below_3px": bool(np.percentile(errors[validation], 95) <= 3),
             "validation_spatial_span": bool((span >= 50).all()),
             "positive_cloud_depth": minimum_depth > 0,
             "proper_rotation": bool(abs(np.linalg.det(matrix) - 1) < 1e-6)}
    record.update(status="TECHNICAL_CHECK_PASSED" if all(gates.values()) else "REJECT",
                  gates=gates, training_inliers=len(inliers), validation_span_px=span.tolist(),
                  training_p95_px=float(np.percentile(errors[training], 95)),
                  validation_p95_px=float(np.percentile(errors[validation], 95)),
                  minimum_cloud_depth_arbitrary_units=minimum_depth, errors_px=errors.tolist())
    return extrinsic, pixels_predicted, record


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first held-frame run")
    started = time.perf_counter()
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    parent = json.loads((SOURCE / "controls.json").read_text(encoding="utf-8"))
    if parent["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
        raise ValueError("Frozen model parent changed")
    intake = json.loads((PILOT / "report.json").read_text(encoding="utf-8"))
    case = next(c for c in intake["cases"] if c["id"] == "real-case-001")
    video = next(a for a in manifest["inputs"] if a["id"] == "real-case-001-video")
    model_paths = sorted((SOURCE / "sparse/0").glob("*.bin")) + [SOURCE / "model-0-cameras-points.npz"]
    frozen_hashes = {str(p.relative_to(SOURCE)): sha256_file(p) for p in model_paths}
    model = pycolmap.Reconstruction(SOURCE / "sparse/0")
    image = model.find_image_with_name("frame-000612.png")
    if image is None:
        raise ValueError("Last source frame is not reconstructed")
    point_ids, world, pixels = [], [], []
    for observed in image.points2D:
        if observed.has_point3D():
            point_ids.append(observed.point3D_id)
            world.append(model.points3D[observed.point3D_id].xyz)
            pixels.append(observed.xy)
    point_ids, world, points = np.array(point_ids, np.int64), np.array(world), np.array(pixels, np.float32) - .5
    cloud = np.array([point.xyz for point in model.points3D.values()])
    intrinsic = model.cameras[image.camera_id].calibration_matrix()
    OUT.mkdir()
    np.savez_compressed(OUT / "frozen-reference.npz", point_ids=point_ids, vertices=world,
                        reference_pixels_colmap=points + .5, intrinsic=intrinsic)
    controls = {"model_files_sha256": frozen_hashes, "manifest_sha256": sha256_file(PILOT / "manifest.json"),
                "tool_sha256": sha256_file(Path(__file__)), "tracking_helper_sha256": sha256_file(ROOT / "tools/temporal_video_sfm_0220.py"),
                "reference_points": len(point_ids), "partition": "even point3D IDs train pose; odd IDs validate",
                "intrinsic_fixed": intrinsic.tolist(), "held_frames": [624, 1040], "seed": 222}
    (OUT / "controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    paths = {612: PILOT / "video-sfm-0219/images/frame-000612.png"}
    for frame in (624, 1040):
        record = next(r for r in case["video"]["frames"] if r["frame"] == frame)
        path = PILOT / case["id"] / record["path"]
        if sha256_file(path) != record["sha256"]:
            raise ValueError("Reserved input image changed")
        paths[frame] = path
    expected = {f: hashlib.sha256(np.asarray(Image.open(p).convert("RGB")).tobytes()).hexdigest() for f, p in paths.items()}
    capture = cv2.VideoCapture(video["path"])
    decoded = []
    try:
        ordinal = 0
        while True:
            ok, bgr = capture.read()
            if not ok:
                break
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            decoded.append((ordinal, hashlib.sha256(rgb.tobytes()).hexdigest()))
            ordinal += 1
            if time.perf_counter() - started > 300:
                raise TimeoutError("Held-frame identity budget exhausted")
    finally:
        capture.release()
    resolved = resolve_keyframe_hashes(expected, decoded)
    (OUT / "decode-index-map.json").write_text(json.dumps(resolved, indent=2), encoding="utf-8")
    capture = cv2.VideoCapture(video["path"])
    cv2.setNumThreads(4)
    observations, steps, previous = {}, [], None
    target_by_ordinal = {resolved[f]: f for f in (624, 1040)}
    try:
        for ordinal in range(max(resolved.values()) + 1):
            ok, bgr = capture.read()
            if not ok:
                raise ValueError("Held transfer decode truncated")
            if ordinal < resolved[612] or (ordinal % 2 and ordinal not in target_by_ordinal and ordinal != resolved[612]):
                continue
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            if previous is not None:
                tracked, keep, fb, _ = track_step(previous, gray, points)
                steps.append({"ordinal": ordinal, "input": len(points), "kept": int(keep.sum()),
                              "fb_p95_px": float(np.percentile(fb[keep], 95)) if keep.any() else None})
                points, point_ids, world = tracked[keep], point_ids[keep], world[keep]
            if ordinal in target_by_ordinal:
                frame = target_by_ordinal[ordinal]
                if not np.array_equal(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), np.asarray(Image.open(paths[frame]))):
                    raise ValueError("Reserved image identity failed during tracking")
                observations[frame] = (point_ids.copy(), world.copy(), points.copy() + .5)
            previous = gray
            if time.perf_counter() - started > 300:
                raise TimeoutError("Held transfer budget exhausted")
    finally:
        capture.release()
    records, poses = [], []
    sheet = Image.new("RGB", (720, 690), (28, 28, 28))
    for column, frame in enumerate((624, 1040)):
        ids, xyz, uv = observations[frame]
        pose, prediction, record = estimate_reserved_pose(xyz, uv, ids, intrinsic, cloud)
        record.update(frame=frame, sequential_ordinal=resolved[frame], retained_reference_fraction=len(ids) / controls["reference_points"])
        records.append(record)
        np.savez_compressed(OUT / f"frame-{frame:06d}-observations.npz", point_ids=ids, vertices=xyz, pixels=uv)
        if pose is not None:
            poses.append((frame, pose))
        photo = Image.open(paths[frame]).convert("RGB")
        draw = ImageDraw.Draw(photo)
        for index, (x, y) in enumerate(uv):
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 190, 20) if ids[index] % 2 == 0 else (20, 255, 80))
            if prediction is not None:
                draw.line([(x, y), tuple(prediction[index])], fill=(255, 50, 50))
        photo.save(OUT / f"frame-{frame:06d}-validation.png")
        photo.thumbnail((360, 640))
        sheet.paste(photo, (column * 360, 35))
        ImageDraw.Draw(sheet).text((column * 360 + 5, 8), f"frame {frame}: {record['status']}", fill="white")
    sheet.save(OUT / "reserved-frame-review.png")
    unchanged = all(sha256_file(SOURCE / p) == digest for p, digest in frozen_hashes.items())
    if not unchanged:
        raise ValueError("Frozen model changed during held-frame validation")
    if poses:
        np.savez_compressed(OUT / "localized-poses.npz", frames=[f for f, _ in poses], extrinsics=np.array([p for _, p in poses]), intrinsic=intrinsic)
    report = {"execution_status": "TECHNICAL_CHECK_PASSED", "screen_status": "TECHNICAL_CHECK_PASSED" if all(
        r["status"] == "TECHNICAL_CHECK_PASSED" for r in records) else "REJECT", "model_unchanged": unchanged,
        "results": records, "tracking_steps": steps, "elapsed_seconds": time.perf_counter() - started,
        "limits": "Frozen-model temporal transfer with reserved point-ID partition; fitted nuisance poses use training IDs only. Shared video/tracking is not anatomical/scan truth, absolute camera calibration or head acceptance."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"screen_status": report["screen_status"], "results": records}))


if __name__ == "__main__":
    main()
