"""Single local CPU SfM screen using only the authorized real development video."""
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time

import cv2
import numpy as np
from PIL import Image
import pycolmap

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
OUT = PILOT / "video-sfm-0219"


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first SfM run")
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    runtime = json.loads((ROOT / "examples/pycolmap-runtime-lock.json").read_text(encoding="utf-8"))
    if pycolmap.__version__ != runtime["version"]:
        raise ValueError("Unreviewed COLMAP runtime")
    distribution = importlib.metadata.distribution("pycolmap")
    for relative, digest in runtime["files"].items():
        if sha256_file(Path(distribution.locate_file(relative))) != digest:
            raise ValueError("COLMAP runtime/license hash changed")
    source = next(a for a in manifest["inputs"] if a["id"] == "real-case-001-video")
    OUT.mkdir()
    images, masks = OUT / "images", OUT / "masks"
    images.mkdir()
    masks.mkdir()
    started = time.perf_counter()
    capture = cv2.VideoCapture(source["path"])
    frames = list(range(0, 624, 12))
    records = []
    try:
        if not capture.isOpened():
            raise ValueError("Cannot open source video")
        for index in frames:
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, bgr = capture.read()
            if not ok or int(round(capture.get(cv2.CAP_PROP_POS_FRAMES))) - 1 != index:
                raise ValueError("Frame index/decode mismatch")
            if bgr.shape != (1280, 720, 3):
                raise ValueError("Unexpected video geometry")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            red_minus_blue = rgb[:, :, 0].astype(float) - rgb[:, :, 2]
            roi = np.zeros(bgr.shape[:2], np.uint8)
            roi[500:820, 100:620] = red_minus_blue[500:820, 100:620] > 12
            count, labels, stats, _ = cv2.connectedComponentsWithStats(roi, connectivity=4)
            if count <= 1:
                raise ValueError("No conservative face foreground")
            chosen = int(1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            mask = cv2.erode((labels == chosen).astype(np.uint8) * 255,
                             np.ones((3, 3), np.uint8), iterations=8)
            if np.count_nonzero(mask) < 1000:
                raise ValueError("Insufficient foreground interior")
            name = f"frame-{index:06d}.png"
            Image.fromarray(rgb).save(images / name)
            Image.fromarray(mask).save(masks / (name + ".png"))
            records.append({"frame": index, "name": name, "image_sha256": sha256_file(images / name),
                            "mask_sha256": sha256_file(masks / (name + ".png")),
                            "selected_mask_pixels": int(np.count_nonzero(mask))})
    finally:
        capture.release()
    reader = pycolmap.ImageReaderOptions(camera_model="SIMPLE_PINHOLE", mask_path=masks,
                                          camera_params="1500,360,640")
    extraction = pycolmap.FeatureExtractionOptions(num_threads=4, use_gpu=False)
    extraction.sift.max_num_features = 4096
    matching = pycolmap.FeatureMatchingOptions(num_threads=4, use_gpu=False)
    pairing = pycolmap.SequentialPairingOptions(overlap=8, num_threads=4, loop_detection=False)
    verification = pycolmap.TwoViewGeometryOptions()
    verification.ransac.max_error, verification.ransac.random_seed = 2., 219
    mapping = pycolmap.IncrementalPipelineOptions(multiple_models=False, max_num_models=1,
        num_threads=4, random_seed=219, ba_refine_principal_point=False,
        ba_refine_extra_params=False, max_runtime_seconds=300)
    mapping.mapper.init_min_num_inliers = 50
    mapping.mapper.init_max_error = 2.
    mapping.mapper.abs_pose_max_error = 3.
    mapping.mapper.filter_max_reproj_error = 3.
    mapping.mapper.random_seed, mapping.triangulation.random_seed = 219, 219
    mapping.mapper.num_threads = 4
    controls = {"source_video_sha256": source["sha256"], "manifest_sha256": sha256_file(PILOT / "manifest.json"),
                "tool_sha256": sha256_file(Path(__file__)), "frames": records, "scan_geometry_used": False,
                "runtime_lock_sha256": sha256_file(ROOT / "examples/pycolmap-runtime-lock.json"),
                "reader": reader.todict(), "extraction": extraction.todict(), "matching": matching.todict(),
                "pairing": pairing.todict(), "verification": verification.todict(), "mapping": mapping.todict()}
    (OUT / "controls.json").write_text(json.dumps(controls, indent=2, default=str), encoding="utf-8")
    token = pycolmap.CancellationToken()
    timer = threading.Timer(max(.1, 600 - (time.perf_counter() - started)), token.cancel)
    timer.daemon = True
    timer.start()
    stage, models = "extract", {}
    try:
        database = OUT / "database.db"
        pycolmap.extract_features(database, images, image_names=[r["name"] for r in records],
            camera_mode=pycolmap.CameraMode.SINGLE, reader_options=reader,
            extraction_options=extraction, device=pycolmap.Device.cpu, cancellation_token=token)
        stage = "match"
        pycolmap.match_sequential(database, matching_options=matching, pairing_options=pairing,
            verification_options=verification, device=pycolmap.Device.cpu, cancellation_token=token)
        stage = "map"
        models = pycolmap.incremental_mapping(database, images, OUT / "sparse", options=mapping,
                                               cancellation_token=token)
    except Exception as error:
        (OUT / "failure.json").write_text(json.dumps({"status": "REJECT", "stage": stage,
            "error": str(error), "elapsed_seconds": time.perf_counter() - started}, indent=2), encoding="utf-8")
        raise
    finally:
        timer.cancel()
    finish_report(models, frames, time.perf_counter() - started, token.is_cancelled)


def finish_report(models, frames, elapsed_seconds, cancelled, recovery=False, output=None):
    target = OUT if output is None else Path(output)
    if (target / "report.json").exists():
        raise FileExistsError("Preserve original summary")
    with sqlite3.connect((target / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as db:
        feature_rows = list(db.execute("SELECT image_id,rows FROM keypoints"))
        verified = list(db.execute("SELECT rows FROM two_view_geometries"))
    summaries = []
    for model_id, model in models.items():
        image_ids = sorted(model.reg_image_ids())
        registered = [int(Path(model.images[i].name).stem.split("-")[-1]) for i in image_ids]
        point_ids = sorted(model.points3D)
        points = np.array([model.points3D[i].xyz for i in point_ids])
        cameras, intrinsics, errors, depths = [], [], [], []
        for image_id in image_ids:
            image = model.images[image_id]
            camera = model.cameras[image.camera_id]
            extrinsic = image.cam_from_world().matrix()
            intrinsic = camera.calibration_matrix()
            cameras.append(extrinsic)
            intrinsics.append(intrinsic)
            for point in image.points2D:
                if not point.has_point3D():
                    continue
                xyz = model.points3D[point.point3D_id].xyz
                p = extrinsic[:, :3] @ xyz + extrinsic[:, 3]
                depths.append(float(p[2]))
                h = intrinsic @ p
                errors.append(float(np.linalg.norm(h[:2] / h[2] - point.xy)))
        path = target / f"model-{model_id}-cameras-points.npz"
        payload = dict(frame_indices=np.array(registered), intrinsics=np.array(intrinsics),
                       extrinsics=np.array(cameras), vertices=points,
                       rgb=np.array([model.points3D[i].color for i in point_ids]))
        if path.exists():
            saved = np.load(path, allow_pickle=False)
            if not recovery or any(not np.allclose(saved[key], value, atol=1e-12, rtol=1e-12)
                                   for key, value in payload.items()):
                raise ValueError("Saved source matrices differ; no overwrite")
        else:
            np.savez_compressed(path, **payload)
        focals = [camera.focal_length for camera in model.cameras.values()]
        gates = {"registered_80_percent": len(registered) >= .8 * len(frames),
                 "at_least_200_points": len(points) >= 200,
                 "both_profile_intervals": any(120 <= f <= 168 for f in registered) and any(396 <= f <= 444 for f in registered),
                 "positive_depth": bool(depths and min(depths) > 0),
                 "proper_rotations": all(abs(np.linalg.det(e[:, :3]) - 1) < 1e-6 for e in cameras),
                 "training_p95_below_3px": bool(errors and np.percentile(errors, 95) <= 3),
                 "interior_focal": all(400 < focal < 4000 for focal in focals)}
        summaries.append({"model": model_id, "registered_frames": registered, "points": len(points),
                          "focals_px": focals, "training_p95_px": float(np.percentile(errors, 95)) if errors else None,
                          "gates": gates, "summary": model.summary()})
    report = {"execution_status": "TECHNICAL_CHECK_PASSED", "screen_status": "UNVERIFIED" if any(
        all(m["gates"].values()) for m in summaries) else "REJECT", "models": summaries,
        "feature_counts": feature_rows, "verified_pair_inlier_counts": [r[0] for r in verified],
        "controls_sha256": sha256_file(target / "controls.json"), "elapsed_seconds": elapsed_seconds,
        "cancelled": cancelled, "heldout_frames": [624, 1040],
        "report_recovered_without_rerun": recovery, "report_writer_sha256": sha256_file(Path(__file__)),
        "limits": "Video-only sparse initialization. Training residuals are not held-out camera accuracy. No source-scan alignment, head mesh, scale truth or visual acceptance."}
    (target / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)


def review_features(output=None, image_root=None, mask_root=None):
    from PIL import ImageDraw
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    target = OUT if output is None else Path(output)
    image_root = target / "images" if image_root is None else Path(image_root)
    mask_root = target / "masks" if mask_root is None else Path(mask_root)
    controls = json.loads((target / "controls.json").read_text(encoding="utf-8"))
    destination = target / "feature-review.json"
    if destination.exists():
        raise FileExistsError("Preserve first feature review")
    sheet = Image.new("RGB", (900, 660), (28, 28, 28))
    rows = []
    with sqlite3.connect((target / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as db:
        for slot, frame in enumerate((0, 144, 408, 552)):
            record = next(r for r in controls["frames"] if r["frame"] == frame)
            image_path, mask_path = image_root / record["name"], mask_root / (record["name"] + ".png")
            if sha256_file(image_path) != record["image_sha256"] or sha256_file(mask_path) != record["mask_sha256"]:
                raise ValueError("Review source changed")
            count, columns, data = db.execute("SELECT k.rows,k.cols,k.data FROM keypoints k JOIN images i ON i.image_id=k.image_id WHERE i.name=?", (record["name"],)).fetchone()
            points = np.frombuffer(data, np.float32).reshape(count, columns)[:, :2]
            mask = np.asarray(Image.open(mask_path)) > 0
            pixels = np.asarray(Image.open(image_path).convert("RGB")).copy()
            pixels[mask] = (pixels[mask].astype(float) * .6 + [0, 90, 0]).clip(0, 255).astype(np.uint8)
            image = Image.fromarray(pixels)
            draw = ImageDraw.Draw(image)
            for x, y in points:
                draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 40, 40))
            x, y = (slot % 2) * 450, (slot // 2) * 330
            sheet.paste(image.crop((80, 470, 650, 860)).resize((440, 300)), (x, y + 25))
            ImageDraw.Draw(sheet).text((x + 5, y + 5), f"frame {frame}: {count} features, green=selected interior", fill="white")
            rows.append({"frame": frame, "features": count, "mask_pixels": int(mask.sum())})
    sheet.save(target / "feature-mask-review.png")
    destination.write_text(json.dumps({"status": "UNVERIFIED", "frames": rows,
        "tool_sha256": sha256_file(Path(__file__)), "limits": "Read-only extraction coverage diagnostic; no rematching or reconstruction."}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:] == ["--review-features"]:
        review_features()
    elif sys.argv[1:] == ["--recover-report"]:
        manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
        controls = json.loads((OUT / "controls.json").read_text(encoding="utf-8"))
        if validate_input_assets(manifest, PILOT) or controls["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
            raise ValueError("Original inputs changed")
        if sha256_file(OUT / "executed-runner-source.py") != controls["tool_sha256"]:
            raise ValueError("Missing exact original runner")
        for record in controls["frames"]:
            if (sha256_file(OUT / "images" / record["name"]) != record["image_sha256"] or
                    sha256_file(OUT / "masks" / (record["name"] + ".png")) != record["mask_sha256"]):
                raise ValueError("Saved frame/mask changed")
        models = {int(path.name): pycolmap.Reconstruction(path)
                  for path in (OUT / "sparse").iterdir() if path.is_dir()}
        finish_report(models, [r["frame"] for r in controls["frames"]], None, False, recovery=True)
    else:
        main()
