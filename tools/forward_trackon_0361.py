"""One bounded full-forward control on a static owned image, not patient data."""
import hashlib
import json
import os
from pathlib import Path
import sys
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-forward-0361"


def prepare():
    import cv2
    import numpy as np
    import prepare_trackon_0359 as builder
    if (OUT / "inputs.npz").exists():
        raise RuntimeError("existing inputs: inspect, do not replace")
    builder.OUT = OUT / "runtime"
    builder.main()
    source = ROOT / "assets/private/dense-photo-0332/view-0.png"
    image = cv2.imread(str(source))[:, :, ::-1].copy()
    height, width = image.shape[:2]
    x, y = np.meshgrid(np.linspace(50, width-50, 8), np.linspace(50, height-50, 6))
    points = np.stack((x.ravel(), y.ravel()), -1).astype(np.float32)
    np.savez(OUT / "inputs.npz", image=image, points=points)
    (OUT / "input-identity.json").write_text(json.dumps(dict(source=str(source),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(), shape=list(image.shape), points=48), indent=2))


def worker():
    import check_trackon_load_0359 as loader
    sys.path.insert(0, str(OUT / "runtime"))
    import numpy as np
    import torch
    from torch.nn import functional as F
    model = loader.main(report_dir=OUT)
    model.memory_extension(72)
    model.eval()
    data = np.load(OUT / "inputs.npz")
    frame = torch.from_numpy(data["image"]).permute(2,0,1).unsqueeze(0).float()
    points = torch.from_numpy(data["points"])
    height, width = frame.shape[-2:]
    predictions, visible = [], []
    with torch.inference_mode():
        memory = torch.zeros(48,72,256)
        mask = torch.ones(48,72,dtype=torch.bool)
        for index in range(2):
            features = model.extract_frame_features(frame)
            if index == 0:
                field = features[-1].reshape(1,model.Hf,model.Wf,model.D).permute(0,3,1,2)
                grid = (points / torch.tensor([width,height]) * 2 - 1).reshape(1,48,1,2)
                query = F.grid_sample(field, grid, mode="bilinear", padding_mode="border", align_corners=False)
                query = query[0,:,:,0].transpose(0,1)
            p, logits, newest = model.track_frame(query, mask, memory, features, height, width)
            assert p.shape == (48,2) and torch.isfinite(p).all() and torch.isfinite(logits).all()
            predictions.append(p.numpy().copy())
            visible.append(logits.sigmoid().numpy().copy())
            memory = torch.roll(memory, -1, dims=1)
            memory[:, -1] = newest
            mask = torch.roll(mask, -1, dims=1)
            mask[:, -1] = False
    predicted = np.stack(predictions)
    errors = np.linalg.norm(predicted - data["points"][None], axis=-1)
    drift = np.linalg.norm(predicted[1] - predicted[0], axis=-1)
    p95 = np.quantile(errors, .95, axis=1)
    np.savez(OUT / "predictions.npz", predictions=predicted, points=data["points"], errors=errors,
             drift=drift, visibility=np.stack(visible))
    result = dict(status="TECHNICAL_CHECK_PASSED" if np.all(p95 <= 3) else "REJECT",
                  scope="static owned-image identity only", native_p95_px=p95.tolist(),
                  drift_p95_px=float(np.quantile(drift,.95)),
                  visible_counts=(np.stack(visible)>=.8).sum(axis=1).tolist(),
                  point_count=48, filtered_points=0, medical_accuracy="UNVERIFIED")
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


def main():
    stage = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    if stage == "prepare":
        prepare()
    elif stage == "worker":
        worker()
    elif stage == "run":
        receipt = OUT / "worker.json"
        if receipt.exists():
            raise RuntimeError("one-shot receipt already exists")
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="4")
        result = run([str(ROOT / ".venv-trackon0357/Scripts/python.exe"), __file__, "worker"],
                     ROOT, env, OUT / "worker.log", receipt, 600, 4*1024**3)
        print(json.dumps(result))
    else:
        raise ValueError("unknown stage")


if __name__ == "__main__":
    main()
