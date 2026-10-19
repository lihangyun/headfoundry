"""Single deterministic non-planar initial-pair screen on frozen temporal matches."""
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
import pycolmap

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from real_video_sfm_0219 import finish_report

PILOT = ROOT / "assets/private/real-capture-pilot-v1"
BASE = PILOT / "video-sfm-0219"
SOURCE = PILOT / "temporal-sfm-0220-index-corrected"
OUT = PILOT / "initialization-sfm-0221"


def homography_fraction(first, second):
    first, second = np.asarray(first, float), np.asarray(second, float)
    if first.ndim != 2 or first.shape[1:] != (2,) or second.shape != first.shape or len(first) < 4:
        raise ValueError("Matching2D points required")
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError("Finite point locations required")
    _, inliers = cv2.findHomography(first, second, cv2.USAC_MAGSAC, 2., maxIters=10000, confidence=.999)
    return float(inliers.mean()) if inliers is not None else 0.


def select_initial_pair(candidates):
    eligible = [dict(row, score=row["inliers"] * (1 - row["homography_fraction"]))
                for row in candidates if row["inliers"] >= 50 and row["homography_fraction"] < .8]
    if not eligible:
        raise ValueError("No non-planar-supported initialization pair")
    return min(eligible, key=lambda r: (-r["score"], *r["image_ids"]))


def verify_sources():
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Source rights/hash validation failed")
    controls = json.loads((SOURCE / "controls.json").read_text(encoding="utf-8"))
    if controls["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
        raise ValueError("Parent manifest changed")
    lock = json.loads((ROOT / "examples/pycolmap-runtime-lock.json").read_text(encoding="utf-8"))
    distribution = importlib.metadata.distribution("pycolmap")
    if pycolmap.__version__ != lock["version"] or any(
            sha256_file(Path(distribution.locate_file(p))) != digest for p, digest in lock["files"].items()):
        raise ValueError("Reconstruction runtime changed")
    for record in controls["frames"]:
        if (sha256_file(BASE / "images" / record["name"]) != record["image_sha256"] or
                sha256_file(BASE / "masks" / (record["name"] + ".png")) != record["mask_sha256"]):
            raise ValueError("Frozen source pixels/masks changed")
    return controls


def select():
    if OUT.exists():
        raise FileExistsError("Preserve first pair-selection run")
    controls = verify_sources()
    cv2.setRNGSeed(219)
    rows, supports = [], {}
    with sqlite3.connect((SOURCE / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as database:
        names = dict(database.execute("SELECT image_id,name FROM images"))
        keypoints = {i: np.frombuffer(data, np.float32).reshape(n, d)[:, :2]
                     for i, n, d, data in database.execute("SELECT image_id,rows,cols,data FROM keypoints")}
        for pair, count, data in database.execute("SELECT pair_id,rows,data FROM two_view_geometries WHERE rows>=50 ORDER BY pair_id"):
            a, b = pair // 2147483647, pair % 2147483647
            indices = np.frombuffer(data, np.uint32).reshape(count, 2)
            first, second = keypoints[a][indices[:, 0]], keypoints[b][indices[:, 1]]
            rows.append({"image_ids": [a, b], "names": [names[a], names[b]], "inliers": count,
                         "homography_fraction": homography_fraction(first, second)})
            supports[a, b] = (first, second)
        selected = select_initial_pair(rows)
        OUT.mkdir()
        with sqlite3.connect(OUT / "database.db") as destination:
            database.backup(destination)
    controls.update(source_database_sha256=sha256_file(SOURCE / "database.db"),
                    source_controls_sha256=sha256_file(SOURCE / "controls.json"),
                    selected_initial_pair=selected, tool_sha256=sha256_file(Path(__file__)))
    (OUT / "controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    (OUT / "selection.json").write_text(json.dumps({"selected": selected, "all_candidates": rows,
        "status": "UNVERIFIED", "rule": "one maximum verified non-homographic support, >=50 inliers, H<0.8"}, indent=2), encoding="utf-8")
    sheet = Image.new("RGB", (900, 650), (28, 28, 28))
    for column, (name, points) in enumerate(zip(selected["names"], supports[tuple(selected["image_ids"])])):
        image = Image.open(BASE / "images" / name).convert("RGB")
        draw = ImageDraw.Draw(image)
        for x, y in points:
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 50, 40))
        image.thumbnail((440, 620))
        sheet.paste(image, (column * 450, 25))
        ImageDraw.Draw(sheet).text((column * 450 + 5, 5), name, fill="white")
    sheet.save(OUT / "selected-pair-supports.png")
    print(json.dumps(selected))


def map_once():
    verify_sources()
    if (OUT / "report.json").exists() or (OUT / "sparse").exists():
        raise FileExistsError("Never retry a selected pair")
    controls = json.loads((OUT / "controls.json").read_text(encoding="utf-8"))
    if sha256_file(SOURCE / "database.db") != controls["source_database_sha256"]:
        raise ValueError("Original match database changed")
    selection = json.loads((OUT / "selection.json").read_text(encoding="utf-8"))["selected"]
    if selection != controls["selected_initial_pair"]:
        raise ValueError("Selected pair changed")
    expected = json.loads((BASE / "controls.json").read_text(encoding="utf-8"))["mapping"]
    mapping = pycolmap.IncrementalPipelineOptions(multiple_models=False, max_num_models=1,
        num_threads=4, random_seed=219, ba_refine_principal_point=False,
        ba_refine_extra_params=False, max_runtime_seconds=300)
    mapping.mapper.init_min_num_inliers, mapping.mapper.init_max_error = 50, 2.
    mapping.mapper.abs_pose_max_error, mapping.mapper.filter_max_reproj_error = 3., 3.
    mapping.mapper.random_seed, mapping.triangulation.random_seed, mapping.mapper.num_threads = 219, 219, 4
    if json.loads(json.dumps(mapping.todict(), default=str)) != expected:
        raise ValueError("Unexpected non-initializer parameter change")
    mapping.init_image_id1, mapping.init_image_id2 = selection["image_ids"]
    (OUT / "mapping-options.json").write_text(json.dumps(mapping.todict(), indent=2, default=str), encoding="utf-8")
    token = pycolmap.CancellationToken()
    timer = threading.Timer(300, token.cancel)
    timer.daemon = True
    timer.start()
    started = time.perf_counter()
    try:
        models = pycolmap.incremental_mapping(OUT / "database.db", BASE / "images", OUT / "sparse",
                                               options=mapping, cancellation_token=token)
    finally:
        timer.cancel()
    finish_report(models, [r["frame"] for r in controls["frames"]], time.perf_counter() - started,
                  token.is_cancelled, output=OUT)


if __name__ == "__main__":
    if sys.argv[1:] == ["select"]:
        select()
    elif sys.argv[1:] == ["map"]:
        map_once()
    else:
        raise ValueError("Use select then one map attempt")
