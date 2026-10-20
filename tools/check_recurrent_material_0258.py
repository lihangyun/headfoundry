"""Retained successful planar fixture/replay;model inference retired after0259."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

if not __debug__:
    raise RuntimeError("This diagnostic requires assertions;run without -O.")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/recurrent-material-0258"
ROWS = [(0, 1, 0, 0, 0, 0), (0, 1, 4, -3, 0, 0),
        (3, 1.01, 8, -6, 0, 0), (6, 1.02, 12, -9, .00005, -.00003),
        (3, 1.01, 8, -6, 0, 0), (0, 1, 0, 0, 0, 0),
        (-3, .99, -8, 6, 0, 0), (-6, .98, -12, 9, -.00005, .00003),
        (0, 1, 0, 0, 0, 0)]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def matrices():
    center = np.eye(3)
    center[:2, 2] = [219.5, 249.5]
    result = []
    for angle, scale, tx, ty, p, q in ROWS:
        a = np.deg2rad(angle)
        rot = np.eye(3)
        rot[:2, :2] = scale * np.array([[np.cos(a), -np.sin(a)],
                                       [np.sin(a), np.cos(a)]])
        perspective = np.eye(3)
        perspective[2, :2] = [p, q]
        translation = np.eye(3)
        translation[:2, 2] = [tx, ty]
        result.append(translation @ center @ perspective @ rot @ np.linalg.inv(center))
    return np.array(result)


def project(homographies, points):
    hp = np.c_[points, np.ones(len(points))] @ homographies.transpose(0, 2, 1)
    return hp[..., :2] / hp[..., 2:]


def to_model(points, extent=(440, 500)):
    """Integer-center xy to raster-corner yx,not a fitted offset."""
    return ((np.asarray(points) + .5) * (256 / np.asarray(extent)))[..., ::-1].copy()


def from_model(points, extent=(440, 500)):
    return np.asarray(points)[..., ::-1] * (np.asarray(extent) / 256) - .5


def controls():
    points = np.array([[80., 120.], [360., 400.], [173.25, 237.75]])
    assert np.max(np.abs(from_model(to_model(points)) - points)) < 1e-12
    assert np.allclose(to_model([[0, 0]])[0], [.256, 256 / 880])
    h = matrices()
    warped = project(h, points)
    replay = np.array([project(np.array([np.linalg.inv(m)]), p)[0]
                       for m, p in zip(h, warped)])
    assert np.max(np.abs(replay - points)) < 1e-10
    assert np.array_equal(h[0], h[5]) and np.array_equal(h[0], h[8])
    assert np.allclose(warped[1] - points, [4, -3])


def prepare():
    import cv2
    from PIL import Image
    sys.path.insert(0, str(ROOT / "src"))
    from headfoundry.manifest import validate_input_assets

    controls()
    base = ROOT / "assets/private/real-capture-pilot-v1"
    doc = json.loads((base / "manifest.json").read_text())
    selected = [x for x in doc["inputs"] if x["id"] == "real-case-001-video"]
    assert len(selected) == 1
    assert doc["training_allowed"] is False and doc["upload_allowed"] is False
    assert not validate_input_assets(dict(doc, inputs=selected), base)
    source_audit = json.loads((ROOT / "assets/private/video-observability-0252/report.json").read_text())
    assert sha(selected[0]["path"]) == selected[0]["sha256"] == source_audit["source_sha256"]
    cap = cv2.VideoCapture(selected[0]["path"])
    try:
        assert cap.isOpened()
        ok, bgr = cap.read()
        assert ok
    finally:
        cap.release()
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    assert hashlib.sha256(rgb.tobytes()).hexdigest() == source_audit["frame_records"][0]["rgb_sha256"]
    crop = rgb[400:900, 160:600]
    assert crop.shape == (500, 440, 3)
    queries = np.array([(80 + 40 * i, 120 + 40 * j)
                        for j in range(8) for i in range(8)], dtype=float)
    homographies = matrices()
    target = project(homographies, queries)
    assert np.all(target > 16) and np.all(target < [424, 484])
    warps = [cv2.warpPerspective(crop, h, (440, 500), flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REFLECT_101) for h in homographies]
    video = np.array([cv2.resize(x, (256, 256), interpolation=cv2.INTER_LINEAR) for x in warps])
    np.savez_compressed(OUT / "input.npz", video=video,
                        queries_yx=to_model(queries).astype(np.float32))
    np.savez_compressed(OUT / "truth.npz", target_xy=target, homographies=homographies,
                        queries_xy=queries)
    Image.fromarray(crop).save(OUT / "source-crop.png")
    report = dict(source_sha256=selected[0]["sha256"], ordinal=0,
                  full_rgb_sha256=source_audit["frame_records"][0]["rgb_sha256"],
                  crop_rgb_sha256=hashlib.sha256(crop.tobytes()).hexdigest(),
                  input_sha256=sha(OUT / "input.npz"), truth_sha256=sha(OUT / "truth.npz"),
                  query_count=64, evaluated_nonquery_pairs=512, scans_read=False,
                  case002_read=False, training=False, upload=False)
    (OUT / "preparation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def evaluate():
    controls()
    preparation = json.loads((OUT / "preparation.json").read_text())
    inference = json.loads((OUT / "inference.json").read_text())
    assert sha(OUT / "input.npz") == preparation["input_sha256"] == inference["input_sha256"]
    assert sha(OUT / "truth.npz") == preparation["truth_sha256"]
    assert sha(OUT / "predictions.npz") == inference["prediction_sha256"]
    with np.load(OUT / "predictions.npz", allow_pickle=False) as data:
        tracks, visible = data["tracks_xy"], data["visible"]
    with np.load(OUT / "truth.npz", allow_pickle=False) as data:
        target = data["target_xy"]
        assert np.array_equal(data["homographies"], matrices())
        queries = np.array([(80 + 40 * i, 120 + 40 * j) for j in range(8) for i in range(8)])
        assert np.array_equal(data["queries_xy"], queries)
        assert np.array_equal(target, project(matrices(), queries))
    assert tracks.shape == target.shape == (9, 64, 2) and visible.shape == (9, 64)
    errors = np.linalg.norm(tracks - target, axis=-1)
    rows = [dict(frame=i, count=64, p95=float(np.quantile(e, .95)),
                 maximum=float(e.max()), visible_fraction=float(visible[i].mean()),
                 finite=bool(np.isfinite(e).all())) for i, e in enumerate(errors)]
    for row in rows:
        row["passed"] = row["finite"] and row["p95"] <= 1 and row["maximum"] <= 3 and row["visible_fraction"] >= .95
    report = dict(status="TECHNICAL_CHECK_PASSED" if all(x["passed"] for x in rows[1:]) else "REJECT",
                  scope="planar_precision_only", rows=rows, camera_status="UNVERIFIED",
                  head_status="UNVERIFIED", independent_3d_truth=False, training=False, upload=False,
                  nonquery_population=512, no_visibility_error_pruning=True,
                  input_sha256=sha(OUT / "input.npz"), truth_sha256=sha(OUT / "truth.npz"),
                  predictions_sha256=sha(OUT / "predictions.npz"))
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "evaluate", "controls"])
    args = parser.parse_args()
    {"prepare": prepare, "evaluate": evaluate, "controls": controls}[args.action]()
