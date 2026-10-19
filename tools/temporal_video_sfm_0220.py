"""One bounded temporal-observation replacement for the real-video SfM screen."""
import importlib.metadata
import hashlib
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
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from real_video_sfm_0219 import finish_report, review_features

PILOT = ROOT / "assets/private/real-capture-pilot-v1"
BASE = PILOT / "video-sfm-0219"
OUT = PILOT / "temporal-sfm-0220-index-corrected"


def resolve_keyframe_hashes(expected, decoded):
    if len(set(expected.values())) != len(expected):
        raise ValueError("Frozen frames have ambiguous identical pixels")
    reverse = {digest: frame for frame, digest in expected.items()}
    hits = {frame: [] for frame in expected}
    for ordinal, digest in decoded:
        if digest in reverse:
            hits[reverse[digest]].append(ordinal)
    if any(len(values) != 1 for values in hits.values()):
        raise ValueError("Missing or ambiguous exact sequential-frame match")
    resolved = {frame: values[0] for frame, values in hits.items()}
    ordered = [resolved[f] for f in sorted(resolved)]
    if any(abs(resolved[f] - f) > 2 for f in resolved) or any(b <= a for a, b in zip(ordered, ordered[1:])):
        raise ValueError("Nonmonotonic or excessive source-frame offset")
    return resolved


def resolve_frames(video, records):
    expected = {r["frame"]: hashlib.sha256(np.asarray(Image.open(BASE / "images" / r["name"])).tobytes()).hexdigest()
                for r in records}
    capture = cv2.VideoCapture(video)
    try:
        decoded = []
        for ordinal in range(max(expected) + 5):
            ok, image = capture.read()
            if not ok:
                raise ValueError("Sequential hash audit truncated")
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            decoded.append((ordinal, hashlib.sha256(rgb.tobytes()).hexdigest()))
        return resolve_keyframe_hashes(expected, decoded)
    finally:
        capture.release()


def track_step(previous, current, points):
    points = np.asarray(points, np.float32)
    if (previous.ndim != 2 or previous.dtype != np.uint8 or current.shape != previous.shape
            or current.dtype != np.uint8 or points.ndim != 2 or points.shape[1:] != (2,)
            or not np.isfinite(points).all()):
        raise ValueError("Matching uint8 gray images and finite Nx2 points required")
    if not len(points):
        return points.copy(), np.zeros(0, bool), np.empty(0), np.empty(0)
    options = dict(winSize=(21, 21), maxLevel=3,
                   criteria=(cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 30, .01),
                   minEigThreshold=1e-4)
    forward, status, error = cv2.calcOpticalFlowPyrLK(previous, current, points[:, None], None, **options)
    forward = forward.reshape(-1, 2)
    valid = np.isfinite(forward).all(1)
    safe = np.where(valid[:, None], forward, points)
    backward, back_status, _ = cv2.calcOpticalFlowPyrLK(current, previous, safe[:, None], None, **options)
    fb = np.linalg.norm(backward.reshape(-1, 2) - points, axis=1)
    error = error.ravel()
    keep = (status.ravel() != 0) & (back_status.ravel() != 0) & valid & np.isfinite(fb) & np.isfinite(error)
    keep &= (forward[:, 0] >= 0) & (forward[:, 0] < current.shape[1])
    keep &= (forward[:, 1] >= 0) & (forward[:, 1] < current.shape[0])
    keep &= (fb <= .75) & (error <= 15)
    return forward, keep, fb, error


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first temporal run")
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    source = next(a for a in manifest["inputs"] if a["id"] == "real-case-001-video")
    base = json.loads((BASE / "controls.json").read_text(encoding="utf-8"))
    if base["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
        raise ValueError("Wrong baseline inputs")
    lock = json.loads((ROOT / "examples/pycolmap-runtime-lock.json").read_text(encoding="utf-8"))
    distribution = importlib.metadata.distribution("pycolmap")
    if pycolmap.__version__ != lock["version"] or any(
            sha256_file(Path(distribution.locate_file(p))) != digest for p, digest in lock["files"].items()):
        raise ValueError("Unreviewed reconstruction runtime")
    for record in base["frames"]:
        if (sha256_file(BASE / "images" / record["name"]) != record["image_sha256"] or
                sha256_file(BASE / "masks" / (record["name"] + ".png")) != record["mask_sha256"]):
            raise ValueError("Keyframe or mask changed")
    OUT.mkdir()
    started = time.perf_counter()
    resolved = resolve_frames(source["path"], base["frames"])
    resolution_path = OUT / "decode-index-map.json"
    resolution_path.write_text(json.dumps({"nominal_to_sequential_ordinal": resolved,
        "method": "Unique exact decoded RGB hash; original PNG bytes/masks unchanged"}, indent=2), encoding="utf-8")
    controls = dict(base, tool_sha256=sha256_file(Path(__file__)),
                    baseline_controls_sha256=sha256_file(BASE / "controls.json"),
                    baseline_database_sha256=sha256_file(BASE / "database.db"),
                    report_helper_sha256=sha256_file(ROOT / "tools/real_video_sfm_0219.py"),
                    observation_mechanism="forward/backward LK corner tracks", intermediate_stride=2,
                    decode_index_map_sha256=sha256_file(resolution_path))
    (OUT / "controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    cv2.setNumThreads(4)
    cv2.setRNGSeed(219)
    token = pycolmap.CancellationToken()
    timer = threading.Timer(600, token.cancel)
    timer.daemon = True
    timer.start()
    capture = cv2.VideoCapture(source["path"])
    records = {r["frame"]: r for r in base["frames"]}
    sequential_to_nominal = {ordinal: nominal for nominal, ordinal in resolved.items()}
    observations, steps, frame_hashes = {}, [], []
    points, ids, next_id, previous = np.empty((0, 2), np.float32), np.empty(0, int), 0, None
    try:
        if not capture.isOpened():
            raise ValueError("Cannot open original video")
        for frame in range(max(resolved.values()) + 1):
            ok, bgr = capture.read()
            if not ok or int(round(capture.get(cv2.CAP_PROP_POS_FRAMES))) - 1 != frame:
                raise ValueError("Sequential video frame mismatch")
            if frame % 2 and frame not in sequential_to_nominal:
                continue
            if time.perf_counter() - started > 180 or token.is_cancelled:
                raise TimeoutError("Tracking budget exhausted")
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            frame_hashes.append({"frame": frame, "gray_sha256": hashlib.sha256(gray.tobytes()).hexdigest()})
            if previous is not None:
                tracked, keep, fb, error = track_step(previous, gray, points)
                steps.append({"frame": frame, "input": len(points), "kept": int(keep.sum()),
                              "fb_p95_px": float(np.percentile(fb[keep], 95)) if keep.any() else None})
                points, ids = tracked[keep], ids[keep]
            if frame in sequential_to_nominal:
                nominal_frame = sequential_to_nominal[frame]
                record = records[nominal_frame]
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                if not np.array_equal(rgb, np.asarray(Image.open(BASE / "images" / record["name"]))):
                    raise ValueError("Sequential decode differs from the frozen keyframe")
                mask = np.asarray(Image.open(BASE / "masks" / (record["name"] + ".png"))).copy()
                if len(points):
                    xy = np.rint(points).astype(int)
                    in_bounds = (xy[:, 0] >= 0) & (xy[:, 0] < 720) & (xy[:, 1] >= 0) & (xy[:, 1] < 1280)
                    selected = np.zeros(len(points), bool)
                    selected[in_bounds] = mask[xy[in_bounds, 1], xy[in_bounds, 0]] > 0
                    points, ids = points[selected], ids[selected]
                for x, y in points:
                    cv2.circle(mask, (int(round(x)), int(round(y))), 5, 0, -1)
                capacity = 400 - len(points)
                new = cv2.goodFeaturesToTrack(gray, maxCorners=capacity, qualityLevel=.01,
                        minDistance=5, mask=mask, blockSize=7) if capacity > 0 else None
                if new is not None:
                    new = new.reshape(-1, 2)
                    points = np.r_[points, new]
                    ids = np.r_[ids, np.arange(next_id, next_id + len(new))]
                    next_id += len(new)
                observations[nominal_frame] = (ids.copy(), points.copy() + .5)
            previous = gray
    finally:
        capture.release()
        timer.cancel()
    frames = sorted(observations)
    offsets = np.r_[0, np.cumsum([len(observations[f][0]) for f in frames])]
    np.savez_compressed(OUT / "tracks.npz", frames=frames, offsets=offsets,
                        track_ids=np.concatenate([observations[f][0] for f in frames]),
                        pixels=np.concatenate([observations[f][1] for f in frames]))
    with sqlite3.connect((BASE / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as database:
        names = dict(database.execute("SELECT image_id,name FROM images"))
        pairs = [(pair // 2147483647, pair % 2147483647)
                 for (pair,) in database.execute("SELECT pair_id FROM two_view_geometries ORDER BY pair_id")]
        with sqlite3.connect(OUT / "database.db") as destination:
            database.backup(destination)
    index = {frame: i for i, frame in enumerate(frames)}
    name_frame = {r["name"]: r["frame"] for r in base["frames"]}
    associations, edges = {}, []
    for a, b in pairs:
        fa, fb = name_frame[names[a]], name_frame[names[b]]
        common, ia, ib = np.intersect1d(observations[fa][0], observations[fb][0], return_indices=True)
        associations[a, b] = np.c_[ia, ib].astype(np.uint32)
        if len(common) >= 50:
            edges.append((index[fa], index[fb]))
    adjacent = [len(np.intersect1d(observations[a][0], observations[b][0])) for a, b in zip(frames, frames[1:])]
    edge_array = np.array(edges, int).reshape(-1, 2)
    graph = coo_matrix((np.ones(len(edges)), (edge_array[:, 0], edge_array[:, 1])), shape=(len(frames), len(frames)))
    _, component = connected_components(graph, directed=False)
    largest = np.argmax(np.bincount(component))
    covered = [f for f, c in zip(frames, component) if c == largest]
    preflight = {"adjacent_50_tracks_80_percent": bool(np.mean(np.array(adjacent) >= 50) >= .8),
                 "component_80_percent": len(covered) >= .8 * len(frames),
                 "bilateral_component": any(120 <= f <= 168 for f in covered) and any(396 <= f <= 444 for f in covered)}
    report = {"status": "TECHNICAL_CHECK_PASSED" if all(preflight.values()) else "REJECT",
              "preflight": preflight, "adjacent_shared_tracks": adjacent, "steps": steps,
              "intermediate_frame_hashes": frame_hashes, "tracks_created": next_id,
              "keyframe_counts": {str(f): len(observations[f][0]) for f in frames},
              "largest_component_frames": covered, "tracks_sha256": sha256_file(OUT / "tracks.npz"),
              "limits": "Stepwise flow/track connectivity is not physical camera, long-term drift or rigid-anatomy acceptance."}
    (OUT / "tracking-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not all(preflight.values()):
        print(json.dumps({"preflight": preflight, "screen_status": "REJECT"}), flush=True)
        return
    with pycolmap.Database.open(OUT / "database.db") as database:
        database.clear_two_view_geometries()
        database.clear_matches()
        database.clear_descriptors()
        database.clear_keypoints()
        for image_id, name in names.items():
            database.write_keypoints(image_id, observations[name_frame[name]][1].astype(np.float32))
        for (a, b), matches in associations.items():
            database.write_matches(a, b, matches)
    pairs_path = OUT / "pairs.txt"
    pairs_path.write_text("".join(f"{names[a]} {names[b]}\n" for a, b in pairs), encoding="utf-8")
    verification = pycolmap.TwoViewGeometryOptions()
    verification.ransac.max_error, verification.ransac.random_seed = 2., 219
    mapping = pycolmap.IncrementalPipelineOptions(multiple_models=False, max_num_models=1,
        num_threads=4, random_seed=219, ba_refine_principal_point=False,
        ba_refine_extra_params=False, max_runtime_seconds=300)
    mapping.mapper.init_min_num_inliers, mapping.mapper.init_max_error = 50, 2.
    mapping.mapper.abs_pose_max_error, mapping.mapper.filter_max_reproj_error = 3., 3.
    mapping.mapper.random_seed, mapping.triangulation.random_seed, mapping.mapper.num_threads = 219, 219, 4
    if (json.loads(json.dumps(mapping.todict(), default=str)) != base["mapping"] or
            json.loads(json.dumps(verification.todict(), default=str)) != base["verification"]):
        raise ValueError("Mapping/verification settings differ from frozen baseline")
    timer = threading.Timer(max(.1, 600 - (time.perf_counter() - started)), token.cancel)
    timer.daemon = True
    timer.start()
    try:
        pycolmap.verify_matches(OUT / "database.db", pairs_path, options=verification, cancellation_token=token)
        models = pycolmap.incremental_mapping(OUT / "database.db", BASE / "images", OUT / "sparse",
                                               options=mapping, cancellation_token=token)
    finally:
        timer.cancel()
    finish_report(models, frames, time.perf_counter() - started, token.is_cancelled, output=OUT)
    review_features(output=OUT, image_root=BASE / "images", mask_root=BASE / "masks")


def audit_parallax():
    destination = OUT / "parallax-audit.json"
    if destination.exists():
        raise FileExistsError("Preserve first read-only parallax audit")
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    reconstruction = json.loads((OUT / "report.json").read_text(encoding="utf-8"))
    registered = set(reconstruction["models"][0]["registered_frames"]) if reconstruction["models"] else set()
    cv2.setRNGSeed(219)
    rows = []
    with sqlite3.connect((OUT / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as database:
        names = dict(database.execute("SELECT image_id,name FROM images"))
        points = {i: np.frombuffer(data, np.float32).reshape(n, d)[:, :2]
                  for i, n, d, data in database.execute("SELECT image_id,rows,cols,data FROM keypoints")}
        for pair, count, data in database.execute("SELECT pair_id,rows,data FROM matches WHERE rows>=50 ORDER BY pair_id"):
            a, b = pair // 2147483647, pair % 2147483647
            fa, fb = [int(Path(names[i]).stem.split("-")[-1]) for i in (a, b)]
            indices = np.frombuffer(data, np.uint32).reshape(count, 2)
            x, y = points[a][indices[:, 0]], points[b][indices[:, 1]]
            _, inlier = cv2.findHomography(x, y, cv2.USAC_MAGSAC, 2., maxIters=10000, confidence=.999)
            rows.append({"frames": [fa, fb], "matches": count,
                         "homography_inlier_fraction_2px": float(inlier.mean()) if inlier is not None else 0.,
                         "median_image_displacement_px": float(np.median(np.linalg.norm(y - x, axis=1))),
                         "both_registered": fa in registered and fb in registered})
    result = {"status": "TECHNICAL_CHECK_PASSED", "camera_acceptance": "REJECT", "pairs": rows,
              "pairs_homography_fraction_at_least_90_percent": sum(r["homography_inlier_fraction_2px"] >= .9 for r in rows),
              "database_sha256": sha256_file(OUT / "database.db"), "tool_sha256": sha256_file(Path(__file__)),
              "limits": "Read-only planar-motion consistency diagnostic. Homography support is not proof of true planarity or a single cause of focal failure. No pair selected or model refit."}
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"registered_pairs": [r for r in rows if r["both_registered"]],
                      "eligible_pairs": len(rows), "homography_dominated_pairs": result["pairs_homography_fraction_at_least_90_percent"]}))


if __name__ == "__main__":
    if sys.argv[1:] == ["--audit-parallax"]:
        audit_parallax()
    else:
        try:
            main()
        except Exception as error:
            if OUT.exists() and not (OUT / "failure.json").exists():
                (OUT / "failure.json").write_text(json.dumps({"status": "REJECT", "error": str(error)}, indent=2), encoding="utf-8")
            raise
