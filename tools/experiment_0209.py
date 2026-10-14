"""Frozen synthetic normal screen. No photos, service, fitting or model fallback."""
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from headfoundry.manifest import sha256_file
from headfoundry.raster import render

RESEARCH = ROOT / "assets/private/research"
SOURCE = ROOT / "artifacts/experiment-0208"
OUT = ROOT / "artifacts/experiment-0209"
LOCK = ROOT / "examples/moge-2-normal-screen-lock.json"
MODEL = RESEARCH / "moge-2-vitb-normal/model.pt"


def source_digest(root):
    h = hashlib.sha256()
    files = sorted(p for p in root.rglob("*") if p.is_file()
                   and ".git" not in p.relative_to(root).parts
                   and (p.suffix == ".py" or p.name == "LICENSE"))
    for path in files:
        h.update(path.relative_to(root).as_posix().encode()+b"\0")
        h.update(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).digest())
    return h.hexdigest()


def vertex_normals(vertices, faces):
    normals = np.zeros_like(vertices)
    tri = vertices[faces]
    cross = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    for corner in range(3):
        np.add.at(normals, faces[:, corner], cross)
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(lengths < 1e-12):
        raise ValueError("undefined source vertex normal")
    return normals / lengths[:, None]


def material_samples(vertices, faces, extrinsic, intrinsic, face_ids):
    """Visible pixel-center samples with perspective-correct material weights."""
    y, x = np.nonzero(binary_erosion(face_ids >= 0, iterations=4))
    ids = face_ids[y, x]
    cam = vertices @ extrinsic[:, :3].T + extrinsic[:, 3]
    h = cam @ intrinsic.T
    uv = h[:, :2] / h[:, 2:]
    a, b, c = np.moveaxis(uv[faces[ids]], 1, 0)
    den = (b[:, 1]-c[:, 1])*(a[:, 0]-c[:, 0])+(c[:, 0]-b[:, 0])*(a[:, 1]-c[:, 1])
    if np.any(np.abs(den) < 1e-12):
        raise ValueError("degenerate projected support")
    w0 = ((b[:, 1]-c[:, 1])*(x+.5-c[:, 0])+(c[:, 0]-b[:, 0])*(y+.5-c[:, 1]))/den
    w1 = ((c[:, 1]-a[:, 1])*(x+.5-c[:, 0])+(a[:, 0]-c[:, 0])*(y+.5-c[:, 1]))/den
    weights = np.c_[w0, w1, 1-w0-w1] / cam[faces[ids], 2]
    weights /= weights.sum(1, keepdims=True)
    if np.any(weights < -1e-8):
        raise ValueError("sample lies outside its rendered first-hit triangle")
    return y, x, ids, weights


def normal_errors(prediction, truth, valid):
    """Invalid observations get180deg, not silently removed from statistics."""
    prediction, truth = np.asarray(prediction, float), np.asarray(truth, float)
    valid = np.asarray(valid, bool)
    if prediction.shape != truth.shape or prediction.ndim != 2 or prediction.shape[1] != 3 or valid.shape != prediction.shape[:1]:
        raise ValueError("matching normal vectors and validity required")
    if not np.isfinite(truth).all() or not np.allclose(np.linalg.norm(truth, axis=1), 1.):
        raise ValueError("finite unit ground-truth normals required")
    lengths = np.linalg.norm(prediction, axis=1)
    good = valid & np.isfinite(prediction).all(1) & (lengths > 1e-8)
    angles = np.full(len(prediction), 180.)
    angles[good] = np.degrees(np.arccos(np.clip(np.sum(prediction[good] * truth[good], axis=1)
                                                            / lengths[good], -1, 1)))
    return angles, good


def main():
    if OUT.exists():
        raise FileExistsError("preserve the first run; no automatic overwrite/rerun")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if lock["asset_id"] != "Ruicheng/moge-2-vitb-normal" or lock["license_id"] != "MIT":
        raise ValueError("only the reviewed exact model is allowed")
    if MODEL.stat().st_size != lock["model_size_bytes"] or sha256_file(MODEL) != lock["model_sha256"]:
        raise ValueError("checkpoint identity mismatch")
    for folder, record in lock["sources"].items():
        if source_digest(RESEARCH / folder) != record["python_license_tree_sha256_lf"]:
            raise ValueError("source/license changed: " + folder)
    for package, version in lock["runtime"].items():
        if metadata.version(package) != version:
            raise ValueError("unreviewed runtime: " + package)
    source_report = json.loads((SOURCE / "report.json").read_text(encoding="utf-8"))
    for relative, digest in source_report["source_locks"].items():
        if sha256_file(ROOT / relative) != digest:
            raise ValueError("synthetic source rights/hash changed")
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", XFORMERS_DISABLED="1")
    for folder in ("moge-source", "utils3d-moge-source"):
        sys.path.insert(0, str(RESEARCH / folder))
    import torch
    import utils3d_moge as utils3d
    from moge.model.v2 import MoGeModel
    torch.set_num_threads(8)
    torch.manual_seed(209)
    plane = utils3d.np.depth_map_to_normal_map(np.ones((16, 16), np.float32),
                                              intrinsics=np.array([[1., 0, .5], [0, 1., .5], [0, 0, 1.]]))
    np.testing.assert_allclose(plane[8, 8], [0, 0, -1], atol=1e-8)
    # Local filename and weights_only=True in the pinned upstream loader. Its
    # DINOv2 constructor uses pretrained=False; no Hub/backbone fallback.
    model = MoGeModel.from_pretrained(str(MODEL)).eval().to("cpu")
    cameras = np.load(SOURCE / "cameras.npz", allow_pickle=False)
    gnm = np.load(RESEARCH / "google-gnm/gnm/shape/data/versions/v3_0/gnm_head.npz", allow_pickle=False)
    donor = np.load(ROOT / "assets/private/subject-001/gnm-posterior-contact-v2/artifacts/donor.npz", allow_pickle=False)
    groups = dict(zip(gnm["vertex_group_names"].tolist(), gnm["vertex_groups"]))
    semantic = {n: groups[n][donor["original_vertex_ids"]] for n in
                ("nose_region", "upper_lip_region", "lower_lip_region", "chin_region")}
    semantic["combined_lips"] = np.maximum(semantic.pop("upper_lip_region"), semantic.pop("lower_lip_region"))
    OUT.mkdir(parents=True)
    records, started = [], time.perf_counter()
    for case in (0, 6, 11):
        folder = SOURCE / f"case-{case:02d}"
        data = np.load(folder / "replay.npz", allow_pickle=False)
        truth, prior, faces = data["truth"], data["prior"], data["faces"]
        tn, pn = vertex_normals(truth, faces), vertex_normals(prior, faces)
        for view, slot in (("front", 0), ("left30", 1), ("right30", 3)):
            if time.perf_counter()-started > 900:
                raise TimeoutError("single inference budget exhausted; do not retune")
            k, e = cameras["intrinsics"][slot], cameras["extrinsics"][slot]
            _, _, hit = render(truth, faces, e, k, (512, 512))
            y, x, ids, weights = material_samples(truth, faces, e, k, hit)
            def sampled(field):
                normal = np.einsum("ni,nij->nj", weights, field[faces[ids]]) @ e[:, :3].T
                return normal / np.linalg.norm(normal, axis=1)[:, None]
            true_normal, prior_normal = sampled(tn), sampled(pn)
            keep = true_normal[:, 2] < -.1
            y, x, ids, true_normal, prior_normal = (a[keep] for a in (y, x, ids, true_normal, prior_normal))
            image_path = folder / "clay" / f"truth-{view}.png"
            rgb = np.asarray(Image.open(image_path).convert("RGB"))
            image = torch.from_numpy(rgb.copy()).permute(2, 0, 1).float()/255
            fov = float(np.degrees(2*np.arctan(512/(2*k[0, 0]))))
            begin = time.perf_counter()
            with torch.inference_mode():
                prediction = model.infer(image, num_tokens=1200, fov_x=fov, apply_mask=False, use_fp16=False)
            array = {n: a.cpu().numpy() for n, a in prediction.items()}
            error, valid = normal_errors(array["normal"][y, x], true_normal, array["mask"][y, x])
            old_error, _ = normal_errors(prior_normal, true_normal, np.ones(len(x), bool))
            def stats(mask):
                if mask.sum() < 20:
                    raise ValueError("too few semantic samples")
                return {"count": int(mask.sum()), "coverage": float(valid[mask].mean()),
                        "median_deg": float(np.median(error[mask])),
                        "p90_deg": float(np.percentile(error[mask], 90)),
                        "oracle_prior_median_deg": float(np.median(old_error[mask]))}
            metrics = {"head": stats(np.ones(len(x), bool))}
            metrics.update({name: stats(values[faces[ids]].mean(1) > .25) for name, values in semantic.items()})
            passed = (all(m["coverage"] >= .95 for m in metrics.values())
                      and metrics["head"]["median_deg"] <= 12 and metrics["head"]["p90_deg"] <= 30
                      and all(metrics[n]["median_deg"] <= 15 for n in semantic))
            name = f"case-{case:02d}-{view}"
            np.savez_compressed(OUT / f"{name}.npz", **array, y=y, x=x, truth_normal=true_normal,
                                error_deg=error, valid=valid, source_faces=ids)
            normal_image = np.full_like(rgb, 30)
            normal_image[y, x] = np.clip((true_normal+1)*127.5, 0, 255).astype(np.uint8)
            estimated = np.nan_to_num(array["normal"], nan=0.)
            pred_image = np.clip((estimated+1)*127.5, 0, 255).astype(np.uint8)
            heat = np.full_like(rgb, 30)
            t = np.minimum(error/45, 1)
            heat[y, x] = np.c_[255*t, 160*(1-t), np.zeros(len(t))].astype(np.uint8)
            panel = Image.new("RGB", (4*512, 548), "#161616")
            for col, (title, pixels) in enumerate((("input white mesh", rgb), ("truth normal", normal_image),
                                                  ("MoGe-2 normal", pred_image), ("error: green0 to red45+ deg", heat))):
                ImageDraw.Draw(panel).text((col*512+6, 10), title+" | "+name, fill="white")
                panel.paste(Image.fromarray(pixels), (col*512, 36))
            panel.save(OUT / f"{name}-comparison.png")
            record = {"case": case, "view": view, "status": "PARTIAL_SUCCESS" if passed else "REJECT",
                      "metrics": metrics, "inference_seconds": time.perf_counter()-begin,
                      "input_sha256": sha256_file(image_path)}
            records.append(record)
            print(json.dumps(record), flush=True)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED",
              "synthetic_observation_screen": "PARTIAL_SUCCESS" if all(r["status"] == "PARTIAL_SUCCESS" for r in records) else "REJECT",
              "photo_likeness": "UNVERIFIED", "defaults_changed": False, "lock": lock,
              "plane_normal": plane[8, 8].tolist(), "precision": "FP32", "device": "CPU", "tokens": 1200,
              "elapsed_seconds": time.perf_counter()-started, "code_sha256": sha256_file(Path(__file__)),
              "results": records, "limits": "Known same-source synthetic heads and white-mesh domain; "
              "not a scan holdout, real-photo test, normal-to-shape reconstruction or visual acceptance."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("results", "lock")}), flush=True)


if __name__ == "__main__":
    main()
