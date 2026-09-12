"""Bounded local CPU SfM experiment; sparse registration is not camera acceptance.

Uses the separately installed, locked PyCOLMAP runtime. No weights are loaded.
All output, including masks/coordinates, inherits the input consent restrictions.
"""
import argparse
import importlib.metadata
import json
import shutil
import sqlite3
from pathlib import Path

import numpy as np

from headfoundry.inputs import validate_multiview
from headfoundry.manifest import sha256_file, validate_input_assets


def prepare(manifest, masks, output, lock):
    """Validate rights, capture, runtime and every mask before creating output."""
    manifest, masks, output = Path(manifest).resolve(), Path(masks).resolve(), Path(output).resolve()
    document = json.loads(manifest.read_text(encoding="utf-8"))
    errors = validate_input_assets(document, manifest.parent)
    if errors:
        raise ValueError("; ".join(errors))
    capture = validate_multiview(document["inputs"])
    if capture["status"] != "TECHNICAL_CHECK_PASSED":
        raise ValueError(f"Capture rejected: {capture['errors']}")
    if output.exists():
        raise ValueError("Output already exists; select a new experiment directory")
    runtime = json.loads(Path(lock).read_text(encoding="utf-8"))
    distribution = importlib.metadata.distribution(runtime["distribution"])
    if distribution.version != runtime["version"]:
        raise ValueError("PyCOLMAP runtime version drift")
    for name, expected in runtime["files"].items():
        if sha256_file(Path(distribution.locate_file(name))) != expected:
            raise ValueError(f"PyCOLMAP runtime hash drift: {name}")
    from PIL import Image

    records = []
    for asset in document["inputs"]:
        source = (manifest.parent / asset["path"]).resolve()
        if not source.is_relative_to(manifest.parent):
            raise ValueError("SfM inputs must be inside the manifest directory")
        name = source.relative_to(manifest.parent).as_posix()
        mask = masks / (name + ".png")
        if not mask.is_file():
            mask = (masks / name).with_suffix(".png")
        if not mask.resolve().is_relative_to(masks) or not mask.is_file():
            raise ValueError(f"Missing mask: {name}")
        with Image.open(source) as photo, Image.open(mask) as segmentation:
            pixels = np.asarray(segmentation.convert("L"))
            if photo.size != segmentation.size or photo.size != (asset["width_px"], asset["height_px"]):
                raise ValueError(f"Image/mask/manifest size mismatch: {name}")
            if not np.any(pixels == 0) or not np.any(pixels != 0):
                raise ValueError(f"Mask must contain included and excluded pixels: {name}")
        records.append({"name": name, "image_sha256": asset["sha256"], "mask_sha256": sha256_file(mask), "mask": mask})
    return manifest, output, runtime, records


def run(manifest, masks, output, lock, affine=False):
    manifest, output, runtime, records = prepare(manifest, masks, output, lock)
    import pycolmap
    from PIL import Image

    output.mkdir(parents=True)
    for record in records:
        destination = output / "masks" / (record["name"] + ".png")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(record.pop("mask"), destination)
    database = output / "database.db"
    reader = pycolmap.ImageReaderOptions(mask_path=output / "masks")
    extraction = pycolmap.FeatureExtractionOptions(num_threads=4, max_image_size=1254)
    extraction.sift.peak_threshold = .003
    extraction.sift.estimate_affine_shape = affine
    extraction.sift.domain_size_pooling = affine
    matching = pycolmap.FeatureMatchingOptions(num_threads=4)
    verification = pycolmap.TwoViewGeometryOptions()
    verification.ransac.random_seed = 17
    mapping = pycolmap.IncrementalPipelineOptions(num_threads=4, random_seed=17, max_runtime_seconds=120)
    report = {"status": "UNVERIFIED", "runtime": runtime, "manifest_sha256": sha256_file(manifest),
              "tool_sha256": sha256_file(Path(__file__)), "inputs": records,
              "affine_domain_size_pooling": affine, "camera_mode": "SINGLE",
              "options": {"reader": reader.todict(), "extraction": extraction.todict(),
                          "matching": matching.todict(), "verification": verification.todict(),
                          "mapping": mapping.todict()},
              "limitation": "All sparse observations are fitting inputs. No held-out camera or visual acceptance."}
    report_path = output / "report.json"
    def save():
        report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    save()
    pycolmap.extract_features(database, manifest.parent, image_names=[r["name"] for r in records],
                              camera_mode=pycolmap.CameraMode.SINGLE, reader_options=reader,
                              extraction_options=extraction, device=pycolmap.Device.cpu)
    with sqlite3.connect(database) as db:
        rows = db.execute("SELECT name,rows,cols,data FROM images JOIN keypoints USING(image_id)").fetchall()
    report["features"] = []
    for name, count, columns, data in rows:
        points = np.frombuffer(data, np.float32).reshape(count, columns)[:, :2]
        with Image.open(output / "masks" / (name + ".png")) as im:
            mask = np.asarray(im.convert("L"))
        xy = np.floor(points).astype(int)
        valid = (xy[:, 0] >= 0) & (xy[:, 0] < mask.shape[1]) & (xy[:, 1] >= 0) & (xy[:, 1] < mask.shape[0])
        inside = np.zeros(count, dtype=bool)
        inside[valid] = mask[xy[valid, 1], xy[valid, 0]] != 0
        report["features"].append({"name": name, "count": count, "outside_mask": int((~inside).sum())})
    if len(rows) != len(records) or any(r["outside_mask"] for r in report["features"]):
        report.update(status="REJECT", reason="Extraction omitted images or violated mask")
        save()
        raise ValueError(report["reason"])
    save()
    pycolmap.match_exhaustive(database, matching_options=matching, verification_options=verification, device=pycolmap.Device.cpu)
    with sqlite3.connect(database) as db:
        names = dict(db.execute("SELECT image_id,name FROM images"))
        report["pairs"] = [{"images": [names[i] for i in pycolmap.pair_id_to_image_pair(pid)], "inliers": count, "configuration": config}
                           for pid, count, config in db.execute("SELECT pair_id,rows,config FROM two_view_geometries")]
    save()
    (output / "sparse").mkdir()
    models = pycolmap.incremental_mapping(database, manifest.parent, output / "sparse", options=mapping)
    report["models"] = [{"id": index, "registered_images": model.num_reg_images(), "points3D": model.num_points3D(),
                          "training_mean_reprojection_error": model.compute_mean_reprojection_error(), "summary": model.summary()}
                         for index, model in models.items()]
    report["status"] = "UNVERIFIED" if any(m["registered_images"] == len(records) for m in report["models"]) else "REJECT"
    save()
    print(json.dumps({k: report[k] for k in ("status", "features", "pairs", "models")}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("masks", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--lock", type=Path, default=Path(__file__).resolve().parents[1] / "examples/pycolmap-runtime-lock.json")
    parser.add_argument("--affine", action="store_true")
    args = parser.parse_args()
    result = run(args.manifest, args.masks, args.output, args.lock, args.affine)
    raise SystemExit(1 if result["status"] == "REJECT" else 0)
