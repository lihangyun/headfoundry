"""One residual-independent drift-closure screen; original model remains frozen."""
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
import pycolmap

from headfoundry.manifest import sha256_file
from localize_reserved_frames_0222 import PILOT, SOURCE, OUT as PARENT, estimate_reserved_pose
from temporal_video_sfm_0220 import track_step

OUT = PILOT / "anchor-cycle-0223"


def closed_observations(reference_ids, direct, direct_valid, sequential_ids, sequential):
    ids, reference_ids = np.asarray(sequential_ids), np.asarray(reference_ids)
    direct, sequential = np.asarray(direct), np.asarray(sequential)
    valid = np.asarray(direct_valid)
    if (reference_ids.ndim != 1 or ids.ndim != 1 or direct.shape != (len(reference_ids), 2)
            or valid.shape != reference_ids.shape or valid.dtype != bool
            or sequential.shape != (len(ids), 2) or len(np.unique(ids)) != len(ids)
            or len(np.unique(reference_ids)) != len(reference_ids)
            or not all(np.isfinite(x).all() for x in (direct[valid], sequential))):
        raise ValueError("Unique IDs and finite valid endpoints required")
    lookup = {int(pid): row for row, pid in enumerate(reference_ids)}
    rows = np.array([lookup[int(pid)] for pid in ids], dtype=int)
    disagreement = np.linalg.norm(direct[rows] - sequential, axis=1)
    keep = valid[rows] & np.isfinite(disagreement) & (disagreement <= .75)
    return rows[keep], disagreement, keep


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first anchor-cycle attempt")
    started = time.perf_counter()
    controls = json.loads((PARENT / "controls.json").read_text(encoding="utf-8"))
    if any(sha256_file(SOURCE / p) != h for p, h in controls["model_files_sha256"].items()):
        raise ValueError("Frozen model changed")
    reference = np.load(PARENT / "frozen-reference.npz", allow_pickle=False)
    ids, world, pixels, intrinsic = [reference[k] for k in ("point_ids", "vertices", "reference_pixels_colmap", "intrinsic")]
    model = pycolmap.Reconstruction(SOURCE / "sparse/0")
    cloud = np.array([p.xyz for p in model.points3D.values()])
    image_path = PILOT / "video-sfm-0219/images/frame-000612.png"
    gray = cv2.cvtColor(cv2.imread(str(image_path)), cv2.COLOR_BGR2GRAY)
    intake = json.loads((PILOT / "report.json").read_text(encoding="utf-8"))
    case = next(c for c in intake["cases"] if c["id"] == "real-case-001")
    OUT.mkdir()
    control = {"parent_controls_sha256": sha256_file(PARENT / "controls.json"), "model_files_sha256": controls["model_files_sha256"],
        "tool_sha256": sha256_file(Path(__file__)), "flow_helper_sha256": sha256_file(Path(__file__).with_name("temporal_video_sfm_0220.py")),
        "pose_helper_sha256": sha256_file(Path(__file__).with_name("localize_reserved_frames_0222.py")),
        "reference_image_sha256": sha256_file(image_path), "closure_limit_px": .75,
        "primary_variable": "residual-independent direct-versus-sequential endpoint closure"}
    (OUT / "controls.json").write_text(json.dumps(control, indent=2), encoding="utf-8")
    cv2.setNumThreads(4)
    results = []
    sheet = Image.new("RGB", (720, 690), (28, 28, 28))
    for column, frame in enumerate((624, 1040)):
        record = next(r for r in case["video"]["frames"] if r["frame"] == frame)
        path = PILOT / case["id"] / record["path"]
        if sha256_file(path) != record["sha256"]:
            raise ValueError("Held image changed")
        target = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2GRAY)
        direct, valid, fb, photometric = track_step(gray, target, pixels.astype(np.float32) - .5)
        direct += .5
        sequential_path = PARENT / f"frame-{frame:06d}-observations.npz"
        seq = np.load(sequential_path, allow_pickle=False)
        rows, disagreement, keep = closed_observations(ids, direct, valid, seq["point_ids"], seq["pixels"])
        pose, predicted, score = estimate_reserved_pose(world[rows], direct[rows], ids[rows], intrinsic, cloud)
        score.update(frame=frame, reference_points=len(ids), direct_valid=int(valid.sum()),
            sequential_survivors=len(keep), closure_accepted=int(keep.sum()),
            sequential_observations_sha256=sha256_file(sequential_path), image_sha256=record["sha256"],
            endpoint_disagreement_p50_px=float(np.median(disagreement)),
            endpoint_disagreement_p95_px=float(np.percentile(disagreement, 95)))
        results.append(score)
        np.savez_compressed(OUT / f"frame-{frame:06d}-cycle.npz", reference_ids=ids, direct_pixels=direct,
            direct_valid=valid, direct_fb_error=fb, direct_patch_error=photometric,
            sequential_ids=seq["point_ids"], endpoint_disagreement=disagreement,
            sequential_keep=keep, accepted_reference_rows=rows,
            **({"extrinsic": pose} if pose is not None else {}))
        photo = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(photo)
        for row_index, row in enumerate(rows):
            x, y = direct[row]
            draw.ellipse((x-2, y-2, x+2, y+2), fill=(255,190,20) if ids[row] % 2 == 0 else (20,255,80))
            if predicted is not None:
                draw.line([(x, y), tuple(predicted[row_index])], fill=(255,50,50))
        photo.save(OUT / f"frame-{frame:06d}-cycle-validation.png")
        photo.thumbnail((360,640))
        sheet.paste(photo, (360*column,35))
        ImageDraw.Draw(sheet).text((360*column+5,8), f"{frame}: {score['status']} ({len(rows)} points)", fill="white")
        if time.perf_counter() - started > 60:
            raise TimeoutError("One cycle-closure attempt exhausted budget")
    sheet.save(OUT / "cycle-review.png")
    unchanged = all(sha256_file(SOURCE / p) == h for p, h in controls["model_files_sha256"].items())
    if not unchanged:
        raise ValueError("Frozen model changed during cycle check")
    report = {"execution_status": "TECHNICAL_CHECK_PASSED", "screen_status": "TECHNICAL_CHECK_PASSED" if all(
        r["status"] == "TECHNICAL_CHECK_PASSED" for r in results) else "REJECT", "results": results,
        "source_model_unchanged": unchanged, "elapsed_seconds": time.perf_counter() - started,
        "limits": "Already inspected development frames; no new blind validation or head acceptance."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"screen_status": report["screen_status"], "results": [{k:v for k,v in r.items() if k != "errors_px"} for r in results]}))


if __name__ == "__main__":
    main()
