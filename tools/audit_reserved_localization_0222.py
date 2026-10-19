"""Read-only separation of frozen-3D prediction from transferred-pixel rigidity."""
import json
from pathlib import Path

import cv2
import numpy as np
import pycolmap

from headfoundry.manifest import sha256_file
from localize_reserved_frames_0222 import OUT, SOURCE, estimate_reserved_pose


def epipolar_validation(first, second, point_ids, intrinsic):
    first, second = np.asarray(first, float), np.asarray(second, float)
    ids, intrinsic = np.asarray(point_ids), np.asarray(intrinsic, float)
    if (first.ndim != 2 or first.shape[1:] != (2,) or second.shape != first.shape
            or ids.shape != (len(first),) or not np.issubdtype(ids.dtype, np.integer)
            or intrinsic.shape != (3, 3) or not all(np.isfinite(v).all() for v in (first, second, intrinsic))):
        raise ValueError("Finite paired pixels, integer IDs and camera required")
    train, validation = ids % 2 == 0, ids % 2 != 0
    if min(train.sum(), validation.sum()) < 30:
        return {"status": "UNVERIFIED", "reason": "insufficient_split_support"}
    cv2.setRNGSeed(222)
    essential, mask = cv2.findEssentialMat(first[train], second[train], intrinsic,
        method=cv2.RANSAC, prob=.999, threshold=1., maxIters=10000)
    if essential is None or essential.shape != (3, 3):
        return {"status": "UNVERIFIED", "reason": "ambiguous_or_missing_essential_matrix"}
    inverse = np.linalg.inv(intrinsic)
    fundamental = inverse.T @ essential @ inverse
    a, b = np.c_[first, np.ones(len(first))], np.c_[second, np.ones(len(second))]
    line_b, line_a = a @ fundamental.T, b @ fundamental
    numerator = abs(np.sum(b * line_b, axis=1))
    denominator = np.minimum(np.linalg.norm(line_a[:, :2], axis=1), np.linalg.norm(line_b[:, :2], axis=1))
    if (denominator <= 1e-12).any():
        return {"status": "UNVERIFIED", "reason": "singular_epipolar_line"}
    errors = numerator / denominator
    return {"status": "TECHNICAL_CHECK_PASSED" if np.percentile(errors[validation], 95) <= 3 else "REJECT",
            "essential_matrix": essential.tolist(), "training_inliers": int(mask.sum()),
            "validation_count": int(validation.sum()), "validation_p95_line_error_px": float(np.percentile(errors[validation], 95)),
            "all_symmetric_line_errors_px": errors.tolist(),
            "limits": "Epipolar lines constrain only one pixel direction; a pass cannot verify depths, anatomy or optical-flow identities."}


def main():
    destination = OUT / "rigidity-audit.json"
    if destination.exists():
        raise FileExistsError("Preserve first rigidity audit")
    controls = json.loads((OUT / "controls.json").read_text(encoding="utf-8"))
    if any(sha256_file(SOURCE / path) != digest for path, digest in controls["model_files_sha256"].items()):
        raise ValueError("Frozen source model changed")
    model = pycolmap.Reconstruction(SOURCE / "sparse/0")
    reference = np.load(OUT / "frozen-reference.npz", allow_pickle=False)
    ids, xyz = reference["point_ids"], reference["vertices"]
    pixels, intrinsic = reference["reference_pixels_colmap"], reference["intrinsic"]
    cloud = np.array([p.xyz for p in model.points3D.values()])
    _, _, baseline = estimate_reserved_pose(xyz, pixels, ids, intrinsic, cloud)
    baseline.pop("errors_px", None)
    lookup = {int(pid): row for row, pid in enumerate(ids)}
    results = []
    for frame in (624, 1040):
        path = OUT / f"frame-{frame:06d}-observations.npz"
        saved = np.load(path, allow_pickle=False)
        rows = [lookup[int(pid)] for pid in saved["point_ids"]]
        result = epipolar_validation(pixels[rows], saved["pixels"], saved["point_ids"], intrinsic)
        result.update(frame=frame, observation_sha256=sha256_file(path))
        results.append(result)
    report = {"reference_frame_612_pose_partition": baseline, "held_two_view_rigidity": results,
              "tool_sha256": sha256_file(Path(__file__)),
              "status": "UNVERIFIED", "limits": "Diagnostic only; do not promote the rejected0222 localization or optimize source geometry."}
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"reference": baseline, "held": [{k: v for k, v in r.items() if k not in
        ("all_symmetric_line_errors_px", "essential_matrix")} for r in results]}))


if __name__ == "__main__":
    main()
