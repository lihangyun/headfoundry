"""One frozen scan-assisted camera screen; no shape fitting or data uploads."""
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.raster import lift_pixels
from headfoundry.scan import read_binary_stl

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
SOURCE = PILOT / "camera-baseline-0217"
TRAIN = np.array([33, 263, 61, 291, 168, 4, 98, 327])
VALIDATION = np.array([133, 362, 6, 1, 2, 0, 17, 152])
FIT_FRAMES = (0, 208, 277, 555, 832)
CHECK_FRAMES = (624, 1040)


def lift_source(vertices, faces, upright_pixels, record):
    """First visible triangle in the exact original orthographic scan preview."""
    center, radius = np.array(record["display_center_source_units"]), record["display_radius_source_units"]
    matrix = np.array(record["camera_world_matrix"])
    camera = ((vertices - center) / radius - matrix[:3, 3]) @ matrix[:3, :3]
    # The source render is512 square at ortho_scale2.4, then rolled180 degrees.
    projected = np.c_[(camera[:, 0] / 2.4 + .5) * 512, (.5 - camera[:, 1] / 2.4) * 512]
    a, b, c = np.moveaxis(projected[faces], 1, 0)
    den = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    valid = np.abs(den) > 1e-12
    den = np.where(valid, den, 1)
    points, ids, barycentric = [], [], []
    for x, y in 512 - np.asarray(upright_pixels):
        w0 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / den
        w1 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / den
        weights = np.c_[w0, w1, 1 - w0 - w1]
        covered = np.flatnonzero(valid & (weights.min(1) >= -1e-9))
        if not len(covered):
            raise ValueError("Missing scan anchor surface hit")
        depths = -np.einsum("ni,ni->n", weights[covered], camera[faces[covered], 2])
        index = covered[np.argmin(depths)]
        points.append(weights[index] @ vertices[faces[index]])
        ids.append(index)
        barycentric.append(weights[index])
    points = np.array(points)
    replay_camera = ((points - center) / radius - matrix[:3, 3]) @ matrix[:3, :3]
    replay = 512 - np.c_[(replay_camera[:, 0] / 2.4 + .5) * 512,
                          (.5 - replay_camera[:, 1] / 2.4) * 512]
    error = float(np.abs(replay - upright_pixels).max())
    if error > 1e-6:
        raise ValueError("Orthographic anchor replay failed")
    return points, np.array(ids), np.array(barycentric), error


def project(points, pose, focal):
    camera = points @ Rotation.from_rotvec(pose[:3]).as_matrix().T + pose[3:]
    return focal * camera[:, :2] / np.maximum(camera[:, 2:3], 1e-6) + [360, 640]


def initial_pose(points, observations):
    intrinsic = np.array([[1000., 0, 360], [0, 1000, 640], [0, 0, 1]])
    ok, r, t = cv2.solvePnP(points, observations, intrinsic, None, flags=cv2.SOLVEPNP_EPNP)
    if not ok:
        raise ValueError("PnP initialization failed")
    ok, r, t = cv2.solvePnP(points, observations, intrinsic, None, r, t, True, flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:
        raise ValueError("PnP pose refinement failed")
    return np.r_[r.ravel(), t.ravel()]


def main():
    output = SOURCE / "calibration"
    if output.exists():
        raise FileExistsError("Preserve first calibration screen")
    manifest_path = PILOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    observations_path = SOURCE / "observations.json"
    observations = json.loads(observations_path.read_text(encoding="utf-8"))
    derived = json.loads((SOURCE / "derived-manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT) or validate_input_assets(derived, SOURCE):
        raise ValueError("Input rights or bytes changed")
    if observations["parent_manifest_sha256"] != sha256_file(manifest_path):
        raise ValueError("Wrong parent observations")
    if observations["derived_manifest_sha256"] != sha256_file(SOURCE / "derived-manifest.json"):
        raise ValueError("Observation image manifest changed")
    confirmation_path = PILOT / "provenance-confirmation.json"
    if observations["confirmation_sha256"] != sha256_file(confirmation_path):
        raise ValueError("Units/stage confirmation changed")
    source = Path(next(a for a in manifest["inputs"] if a["id"] == "real-case-001-skin")["path"])
    vertices, faces = read_binary_stl(source)
    records = {record["id"]: record for record in observations["records"]}
    slots = np.r_[TRAIN, VALIDATION]
    scan_pixels = np.array(records["scan-frontal"]["landmarks"])[slots, :2]
    points, hit_ids, weights, replay = lift_source(vertices, faces, scan_pixels, observations["source_preview_record"])
    # Center/scale are numerical conditioning; exported poses remain original STL mm.
    center = points.mean(0)
    conditioned = (points - center) / 100
    frames = FIT_FRAMES + CHECK_FRAMES
    targets = []
    for frame in frames:
        record = records[f"frame-{frame:06d}"]
        if record["faces_detected"] != 1:
            raise ValueError("Declared frame has no single face")
        targets.append(np.array(record["landmarks"])[slots, :2])
    targets = np.array(targets)
    started = time.perf_counter()
    initial = np.array([initial_pose(conditioned[:len(TRAIN)], t[:len(TRAIN)]) for t in targets])
    def residual(parameters):
        focal = np.exp(parameters[0])
        poses = parameters[1:].reshape(-1, 6)
        return np.concatenate([(project(conditioned[:len(TRAIN)], p, focal) - t[:len(TRAIN)]).ravel()
                               for p, t in zip(poses, targets[:len(FIT_FRAMES)])])
    start = np.r_[np.log(1000), initial[:len(FIT_FRAMES)].ravel()]
    lower, upper = np.full(len(start), -np.inf), np.full(len(start), np.inf)
    lower[0], upper[0] = np.log(400), np.log(3000)
    fit = least_squares(residual, start, bounds=(lower, upper), loss="soft_l1", f_scale=2,
                        max_nfev=200, ftol=1e-9, xtol=1e-9, gtol=1e-9)
    focal = float(np.exp(fit.x[0]))
    poses = list(fit.x[1:].reshape(-1, 6))
    for index in range(len(FIT_FRAMES), len(frames)):
        result = least_squares(lambda p: (project(conditioned[:len(TRAIN)], p, focal) -
                                         targets[index, :len(TRAIN)]).ravel(), initial[index],
                               loss="soft_l1", f_scale=2, max_nfev=200, ftol=1e-9, xtol=1e-9, gtol=1e-9)
        if not result.success:
            raise ValueError("Reserved-frame nuisance pose did not converge")
        poses.append(result.x)
    intrinsic = np.array([[focal, 0, 360], [0, focal, 640], [0, 0, 1]])
    output.mkdir()
    rows, extrinsics = [], []
    for index, (frame, pose, target) in enumerate(zip(frames, poses, targets)):
        rotation = Rotation.from_rotvec(pose[:3]).as_matrix()
        extrinsic = np.c_[rotation, pose[3:] * 100 - rotation @ center]
        extrinsics.append(extrinsic)
        pixel = project(conditioned, pose, focal)
        error = np.linalg.norm(pixel - target, axis=1)
        depth = (vertices @ rotation.T + extrinsic[:, 3])[:, 2]
        if depth.min() <= 0:
            raise ValueError("Source scan behind fitted camera")
        hit, bary = lift_pixels(vertices, faces, extrinsic, intrinsic, pixel)
        if np.any(hit < 0):
            raise ValueError("Fitted source anchor lost its mesh support")
        nearest = np.einsum("ni,nij->nj", bary, vertices[faces[hit]])
        gaps = ((points - nearest) @ rotation.T)[:, 2]
        hidden_train = TRAIN[gaps[:len(TRAIN)] > .05]
        row = {"frame": frame, "focal_training_frame": index < len(FIT_FRAMES),
               "training_mean_px": float(error[:len(TRAIN)].mean()),
               "validation_p95_px": float(np.percentile(error[len(TRAIN):], 95)),
               "errors_px": error.tolist(), "minimum_scan_depth_mm": float(depth.min()),
               "rotation_determinant": float(np.linalg.det(rotation)),
               "hidden_training_slots": hidden_train.tolist(), "anchor_visibility_gap_mm": gaps.tolist()}
        rows.append(row)
        image_path = next(a["path"] for a in derived["inputs"] if a["id"] == f"frame-{frame:06d}")
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        for slot, observed, predicted in zip(slots, target, pixel):
            x, y = observed
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(20, 255, 80))
            x, y = predicted
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), outline=(255, 40, 40), width=2)
            draw.line([tuple(observed), tuple(predicted)], fill=(255, 200, 20))
        draw.text((10, 10), "GREEN video observation / RED fixed scan projection", fill="white")
        image.save(output / f"frame-{frame:06d}-points.png")
    np.savez_compressed(output / "cameras.npz", intrinsics=np.repeat(intrinsic[None], len(frames), axis=0),
                        extrinsics=np.array(extrinsics), frame_indices=np.array(frames),
                        scan_anchor_slots=slots, scan_anchor_points_mm=points, source_triangle_ids=hit_ids,
                        source_barycentric_weights=weights)
    gates = {"converged": bool(fit.success), "interior_focal": bool(400.01 < focal < 2999.99),
             "all_validation_p95_below_3px": all(r["validation_p95_px"] < 3 for r in rows),
             "all_training_supports_visible": all(not r["hidden_training_slots"] for r in rows)}
    report = {"technical_status": "TECHNICAL_CHECK_PASSED", "screen_status": "UNVERIFIED" if all(gates.values()) else "REJECT",
              "visual_status": "UNVERIFIED", "scan_assisted": True, "focal_px": focal, "gates": gates,
              "solver_message": fit.message, "evaluations": fit.nfev, "orthographic_replay_max_px": replay,
              "camera_convention": "OpenCV world-to-camera; original STL coordinates in millimeters",
              "training_slots": TRAIN.tolist(), "validation_slots": VALIDATION.tolist(), "results": rows,
              "observations_sha256": sha256_file(observations_path), "source_sha256": sha256_file(source),
              "tool_sha256": sha256_file(Path(__file__)), "cameras_sha256": sha256_file(output / "cameras.npz"),
              "elapsed_seconds": time.perf_counter() - started,
              "limits": "Scan anchors come from learned detection on synthetic clay. Reserved frames fit nuisance poses on training slots. Detector validation slots are not independent anatomical annotations. No scan deformation or photo-only camera/geometry acceptance."}
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"screen_status": report["screen_status"], "focal_px": focal, "gates": gates, "results": rows}, indent=2))


if __name__ == "__main__":
    main()
