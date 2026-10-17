"""Read-only geometry diagnosis of0211 supports; no expression/identity refit."""
import json
from pathlib import Path
import shutil

import numpy as np

from headfoundry.manifest import sha256_file
from headfoundry.raster import lift_pixels
from experiment_0208 import LOCKS, MODEL

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/experiment-0211"
REVIEW = ROOT / "artifacts/experiment-0211-source-only-review"
MACRO = ROOT / "artifacts/experiment-0211-source-mouth-macro"


def main():
    if REVIEW.exists() or MACRO.exists() or (SOURCE / "source-visibility.json").exists():
        raise FileExistsError("preserve the first visibility/source-reference audit")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("locked asset/license changed")
    report = json.loads((SOURCE / "report.json").read_text(encoding="utf-8"))
    if sha256_file(SOURCE / "native-basis.npz") != report["basis_sha256"]:
        raise ValueError("support/basis archive changed")
    basis = np.load(SOURCE / "native-basis.npz", allow_pickle=False)
    data = np.load(SOURCE / "case-00/replay.npz", allow_pickle=False)
    model = np.load(MODEL, allow_pickle=False)
    native = model["template_vertex_positions"][basis["skin_ids"]].astype(float)
    if np.any(data["identity"] != 0) or not np.array_equal(native, data["source_skin"]):
        raise ValueError("this audit only observes the unchanged native mean")
    center, radius = (native.max(0)+native.min(0))/2, report["native_radius"]
    world = (native-center) @ np.diag([1., -1., -1.])/radius
    cameras = np.load(SOURCE / "cameras.npz", allow_pickle=False)
    views = ("front", "left30", "left90", "right30", "right90")
    records = []
    for index, name in enumerate(views):
        e, k = cameras["extrinsics"][index], cameras["intrinsics"][index]
        projection = k @ e
        for row in range(4):
            points = np.vstack([world[basis["upper"][row]], world[basis["lower"][row]]])
            h = points @ projection[:, :3].T+projection[:, 3]
            pixels = h[:, :2]/h[:, 2:]
            ids, weights = lift_pixels(world, basis["faces"], e, k, pixels)
            found = ids >= 0
            error = np.full(len(points), np.inf)
            hits = np.einsum("ni,nij->nj", weights[found], world[basis["faces"][ids[found]]])
            error[found] = np.linalg.norm(hits-points[found], axis=1)*radius
            records.append({"view": name, "original_source_row": row+1, "samples": len(points),
                            "visible_within_5e_minus6_native": int(np.sum(error <= 5e-6)),
                            "median_first_hit_offset_native": float(np.median(error))})
    result = {"technical_status": "TECHNICAL_CHECK_PASSED", "case": "unchanged native mean only",
              "visibility_tolerance_native": 5e-6,
              "model_sha256": sha256_file(MODEL), "basis_sha256": report["basis_sha256"],
              "camera_sha256": sha256_file(SOURCE / "cameras.npz"),
              "code_sha256": sha256_file(Path(__file__)), "records": records,
              "limits": "First-hit visibility, not anatomical contact truth, native-mouth closure, "
              "whole-head collision or likeness acceptance. No alternative row fit performed."}
    (SOURCE / "source-visibility.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Only unchanged source/context files are copied. Unsafe expression results
    # are deliberately absent; no candidate geometry or coefficients are moved.
    REVIEW.mkdir()
    (REVIEW / "case-00").mkdir()
    hashes = {}
    for name in ("truth", "prior"):
        original = SOURCE / "case-00" / f"{name}.obj"
        target = REVIEW / "case-00" / original.name
        shutil.copy2(original, target)
        hashes[name] = sha256_file(original)
        if sha256_file(target) != hashes[name]:
            raise ValueError("source/context copy changed")
    shutil.copy2(SOURCE / "cameras.npz", REVIEW / "cameras.npz")
    np.savez_compressed(REVIEW / "case-00/replay.npz", base=data["base"])
    reference_report = {
        "technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
        "unaltered_source_references_only": True, "variants": ["truth", "prior"],
        "display_label": "UNCHANGED NATIVE SOURCE / MANUALLY CLOSED CONTEXT (NOT GROUND TRUTH)",
        "version_labels": {"truth": "unchanged native source", "prior": "manual closed context"},
        "results": [{"case": 0}], "source_hashes": hashes,
        "limits": "Unaltered source/context inspection only; different topologies. No unsafe expression "
        "candidate, new fit, alternative row closure, actual photo or production acceptance."}
    (REVIEW / "report.json").write_text(json.dumps(reference_report, indent=2), encoding="utf-8")
    # Optical inspection only: same extrinsics/lighting/geometry for both
    # references. Never change or refit the subject's camera archive.
    MACRO.mkdir()
    (MACRO / "case-00").mkdir()
    for name in ("truth", "prior"):
        shutil.copy2(REVIEW / "case-00" / f"{name}.obj", MACRO / "case-00" / f"{name}.obj")
    intrinsic = cameras["intrinsics"].copy()
    mouth = ((world[basis["upper"][0]]+world[basis["lower"][0]])/2).mean(0)
    for i, e in enumerate(cameras["extrinsics"]):
        cam = e[:, :3] @ mouth+e[:, 3]
        intrinsic[i, 0, 0] *= 4
        intrinsic[i, 1, 1] *= 4
        intrinsic[i, 0, 2] = 256-intrinsic[i, 0, 0]*cam[0]/cam[2]
        intrinsic[i, 1, 2] = 256-intrinsic[i, 1, 1]*cam[1]/cam[2]
    np.savez_compressed(MACRO / "cameras.npz", intrinsics=intrinsic, extrinsics=cameras["extrinsics"])
    np.savez_compressed(MACRO / "case-00/replay.npz", base=data["base"])
    reference_report["display_label"] = "4X INSPECTION ZOOM | NATIVE ORIGINAL / MANUAL CONTEXT | NO GEOMETRY CHANGE"
    reference_report["inspection_camera"] = "Fourfold focal length, common native-mouth center; same extrinsics and geometry. Not reconstructed cameras."
    (MACRO / "report.json").write_text(json.dumps(reference_report, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
