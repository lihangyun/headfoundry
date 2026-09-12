"""Local inference for the exact Apache MapAnything checkpoint."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import math
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.inputs import validate_multiview
from headfoundry.camera import invert_camera_poses

LOCK_PATH = PROJECT / "examples/mapanything-apache-lock.json"


def source_digest(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in Path(root).rglob("*") if p.suffix in (".py", ".yaml")):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).digest())
    return digest.hexdigest()


def verify(manifest, source, dino, assets):
    document = json.loads(manifest.read_text(encoding="utf-8"))
    if document.get("purpose") != "local_head_reconstruction_validation":
        raise ValueError("Only consented local validation is enabled")
    errors = validate_input_assets(document, manifest.parent)
    if errors:
        raise ValueError("input rights: " + "; ".join(errors))
    if validate_multiview(document["inputs"])["status"] != "TECHNICAL_CHECK_PASSED":
        raise ValueError("Capture gate failed")
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock["asset_id"] != "facebook/map-anything-apache" or lock["license_id"] != "Apache-2.0":
        raise ValueError("Only the reviewed Apache MapAnything variant is allowed")
    for name, expected in lock["model_sha256"].items():
        if sha256_file(assets / name) != expected:
            raise ValueError(f"Model asset hash mismatch: {name}")
    for label, root in (("mapanything", source), ("dinov2", dino)):
        if source_digest(root) != lock["sources"][label]["tree_sha256"]:
            raise ValueError(f"Source hash mismatch: {label}")
        if sha256_file(root / "LICENSE") != lock["sources"][label]["license_sha256"]:
            raise ValueError(f"License hash mismatch: {label}")
    for name, version in lock["runtime"].items():
        if metadata.version(name) != version:
            raise ValueError(f"Runtime version mismatch: {name}")
    uni_distribution = metadata.distribution("uniception")
    uni = Path(uni_distribution.locate_file("uniception"))
    if source_digest(uni) != lock["sources"]["uniception"]["tree_sha256"]:
        raise ValueError("UniCeption source hash mismatch")
    license_file = Path(uni_distribution.locate_file("uniception-0.1.7.dist-info/licenses/LICENSE"))
    if sha256_file(license_file) != lock["sources"]["uniception"]["license_sha256"]:
        raise ValueError("UniCeption license hash mismatch")
    return document, lock


def local_dino_loader(original, directory):
    def load(repository, model, **kwargs):
        if repository != "facebookresearch/dinov2" or model != "dinov2_vitg14" or kwargs.get("pretrained") is not False:
            raise ValueError("Unreviewed hub code or encoder weights requested")
        return original(str(directory), model, source="local", pretrained=False)
    return load


def assumed_intrinsics(focal_px, sizes_hw):
    """Uncalibrated centered pinhole hypothesis, resized to the fixed 518 grid."""
    import numpy as np
    if not math.isfinite(focal_px) or focal_px <= 0:
        raise ValueError("Assumed focal length must be finite and positive")
    sizes = np.asarray(sizes_hw, dtype=float)
    if sizes.ndim != 2 or sizes.shape[1] != 2 or len(sizes) == 0 or not np.isfinite(sizes).all() or np.any(sizes <= 0):
        raise ValueError("Positive finite image sizes required")
    result = np.repeat(np.eye(3, dtype=np.float32)[None], len(sizes), axis=0)
    result[:, 0, 0] = focal_px * 518 / sizes[:, 1]
    result[:, 1, 1] = focal_px * 518 / sizes[:, 0]
    result[:, :2, 2] = 259
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "source", "dino", "assets", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--focal-px", type=float, help="Uncalibrated original-pixel focal hypothesis; centered principal point, no pose conditioning")
    args = parser.parse_args()
    if args.focal_px is not None and (not math.isfinite(args.focal_px) or args.focal_px <= 0):
        parser.error("--focal-px must be finite and positive")
    args.manifest, args.source, args.dino, args.assets, args.output = [p.resolve() for p in (args.manifest, args.source, args.dino, args.assets, args.output)]
    if args.output.exists():
        raise ValueError("Output exists; choose a new experiment directory")
    document, lock = verify(args.manifest, args.source, args.dino, args.assets)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    # Explicit local DINO loading plus a process-level guard cover non-HF callers.
    def offline(event, _):
        if event in ("socket.connect", "socket.getaddrinfo"):
            raise RuntimeError("Network disabled during local reconstruction")
    sys.addaudithook(offline)
    sys.path.insert(0, str(args.source))
    import numpy as np
    import torch
    from PIL import Image
    from mapanything.models import MapAnything
    from mapanything.utils.image import load_images

    sizes = []
    paths = []
    for asset in document["inputs"]:
        path = args.manifest.parent / asset["path"]
        with Image.open(path) as im:
            if im.width != im.height or im.size != (asset["width_px"], asset["height_px"]) or im.getexif().get(274, 1) != 1:
                raise ValueError("Initial adapter supports matching square images without EXIF rotation only")
            sizes.append([im.height, im.width])
        paths.append(str(path))
    torch.set_num_threads(6)
    torch.manual_seed(17)
    print("Verified Apache weights and local source; loading CPU FP32 model", flush=True)
    start = time.perf_counter()
    with patch.object(torch.hub, "load", local_dino_loader(torch.hub.load, args.dino)):
        model = MapAnything.from_pretrained(str(args.assets), local_files_only=True, strict=True).eval()
    views = load_images(paths, resolution_set=518)
    if len(views) != len(paths) or any(tuple(v["img"].shape) != (1, 3, 518, 518) for v in views):
        raise ValueError("Input decoding/resize mismatch")
    conditioning = None
    if args.focal_px is not None:
        conditioning = assumed_intrinsics(args.focal_px, sizes)
        for view, intrinsic in zip(views, conditioning):
            view["intrinsics"] = torch.from_numpy(intrinsic[None])
    print(f"Loaded in {time.perf_counter()-start:.1f}s; beginning five-view inference", flush=True)
    started = time.perf_counter()
    predictions = model.infer(views, memory_efficient_inference=True, minibatch_size=1,
                              use_amp=False, apply_mask=False, mask_edges=False,
                              apply_confidence_mask=False, use_multiview_confidence=False)
    elapsed = time.perf_counter() - started
    keys = ("pts3d", "pts3d_cam", "depth_z", "ray_directions", "intrinsics", "camera_poses", "conf", "non_ambiguous_mask")
    arrays = {key: np.stack([p[key][0].cpu().numpy() for p in predictions]) for key in keys}
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("Nonfinite model output")
    arrays["extrinsics"] = invert_camera_poses(arrays["camera_poses"])
    transformed = np.einsum("vij,vhwj->vhwi", arrays["extrinsics"][:, :, :3], arrays["pts3d"]) + arrays["extrinsics"][:, None, None, :, 3]
    if not np.allclose(transformed, arrays["pts3d_cam"], rtol=1e-4, atol=1e-5):
        raise ValueError("Native camera/world point maps disagree after pose inversion")
    if conditioning is not None:
        arrays["conditioning_intrinsics"] = conditioning
    args.output.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(args.output / "predictions.npz", **arrays)
    report = {"status": "UNVERIFIED", "asset": lock, "input_ids": [a["id"] for a in document["inputs"]],
              "input_sha256": [a["sha256"] for a in document["inputs"]], "original_sizes_hw": sizes,
              "processed_size_hw": [518, 518], "preprocess": "upstream square pure resize; no crop or EXIF rotation",
              "camera_convention": "OpenCV camera-to-world 4x4; intrinsics at processed resolution",
              "runtime_seconds": elapsed, "device": "cpu", "precision": "float32", "network": "disabled",
              "runner_sha256": sha256_file(Path(__file__)),
              "conditioning": {"focal_original_px": args.focal_px, "status": "UNVERIFIED",
                               "kind": "image_only" if conditioning is None else "assumed_centered_pinhole_intrinsics",
                               "poses_supplied": False},
              "output_sha256": sha256_file(args.output / "predictions.npz"),
              "shapes": {key: list(value.shape) for key, value in arrays.items()},
              "limitations": "Model prediction; supplied intrinsics, if any, are an uncalibrated hypothesis. Validity mask is not head segmentation. No camera or visual acceptance."}
    (args.output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "UNVERIFIED", "runtime_seconds": elapsed, "shapes": report["shapes"]}), flush=True)


if __name__ == "__main__":
    main()
