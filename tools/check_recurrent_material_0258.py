"""Bounded TAPNext++ planar precision screen; not camera/head reconstruction."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/recurrent-material-0258"
LOCK = ROOT / "examples/tapnextpp-0258.asset-lock.json"
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


def to_model(points):
    """Integer-center xy to raster-corner yx,not a fitted offset."""
    return ((np.asarray(points) + .5) * [256 / 440, 256 / 500])[..., ::-1].copy()


def from_model(points):
    return np.asarray(points)[..., ::-1] * [440 / 256, 500 / 256] - .5


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


def infer():
    started = time.perf_counter()
    lock = json.loads(LOCK.read_text())
    assert lock["license"] == lock["checkpoint"]["license"] == "Apache-2.0"
    assert lock["rights"]["commercial_use_permitted_by_published_license"] is True
    assert lock["rights"]["fallback_checkpoint_allowed"] is False
    for name, expected in lock["source_sha256"].items():
        assert sha(OUT / "source" / name) == expected, name
    checkpoint = OUT / "tapnextpp_ckpt.pt"
    assert checkpoint.stat().st_size == lock["checkpoint"]["bytes"]
    assert sha(checkpoint) == lock["checkpoint"]["sha256"]
    assert sha(OUT / "input.npz") == json.loads((OUT / "preparation.json").read_text())["input_sha256"]
    import torch
    import torchvision
    import einops
    assert torch.__version__ == lock["runtime"]["torch"]
    assert torchvision.__version__ == lock["runtime"]["torchvision"]
    assert einops.__version__ == lock["runtime"]["einops"]
    assert np.__version__ == lock["runtime"]["numpy"]
    torch.set_num_threads(8)
    torch.set_num_interop_threads(1)
    sys.path.insert(0, str(OUT / "source"))
    from tapnet.tapnext.tapnext_torch import TAPNext
    model = TAPNext(image_size=(256, 256))
    checkpoint_data = torch.load(checkpoint, map_location="cpu", weights_only=True)
    state_dict = checkpoint_data.get("state_dict", checkpoint_data)
    state_dict = {k.removeprefix("tapnext."): v for k, v in state_dict.items()}
    loaded = model.load_state_dict(state_dict, strict=True)
    del state_dict, checkpoint_data
    model.eval()
    with np.load(OUT / "input.npz", allow_pickle=False) as data:
        video = data["video"].copy()
        queries = np.c_[np.zeros(64), data["queries_yx"]].astype(np.float32)
    tracks, visible, times = [], [], []
    state = None
    with torch.inference_mode():
        for frame in video:
            tick = time.perf_counter()
            tensor = torch.from_numpy(frame.copy()).float()[None, None] / 127.5 - 1
            pred, _, logits, state = model(tensor, query_points=torch.from_numpy(queries)[None]
                                          if state is None else None, state=state)
            tracks.append(from_model(pred[0, 0].cpu().numpy()))
            visible.append((logits[0, 0, :, 0] > 0).cpu().numpy())
            times.append(time.perf_counter() - tick)
            print(json.dumps(dict(completed_frames=len(tracks), seconds=times[-1])), flush=True)
    np.savez_compressed(OUT / "predictions.npz", tracks_xy=tracks, visible=visible)
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="execution_only", strict_load=True,
                  missing_keys=list(loaded.missing_keys), unexpected_keys=list(loaded.unexpected_keys),
                  model_parameters=sum(p.numel() for p in model.parameters()),
                  seconds=time.perf_counter() - started, frame_seconds=times,
                  versions=dict(torch=torch.__version__, torchvision=torchvision.__version__,
                                einops=einops.__version__, numpy=np.__version__),
                  device="cpu", dtype="float32", queries=64, frames=9,
                  input_sha256=sha(OUT / "input.npz"), prediction_sha256=sha(OUT / "predictions.npz"))
    (OUT / "inference.json").write_text(json.dumps(report, indent=2))


def evaluate():
    controls()
    with np.load(OUT / "predictions.npz", allow_pickle=False) as data:
        tracks, visible = data["tracks_xy"], data["visible"]
    with np.load(OUT / "truth.npz", allow_pickle=False) as data:
        target = data["target_xy"]
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
    parser.add_argument("action", choices=["prepare", "infer", "evaluate", "controls"])
    args = parser.parse_args()
    {"prepare": prepare, "infer": infer, "evaluate": evaluate, "controls": controls}[args.action]()
