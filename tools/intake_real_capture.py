"""Inventory consented local videos/scans without fitting or modifying sources."""
import argparse
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import sparse
from scipy.sparse.csgraph import connected_components

from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.scan import read_binary_stl

ROOT = Path(__file__).resolve().parents[1]


def scan_stats(path):
    vertices, faces = read_binary_stl(path)
    triangle = vertices[faces]
    area = np.linalg.norm(np.cross(triangle[:, 1] - triangle[:, 0],
                                   triangle[:, 2] - triangle[:, 0]), axis=1) / 2
    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges, inverse, counts = np.unique(np.sort(directed, axis=1), axis=0,
                                       return_inverse=True, return_counts=True)
    direction = np.where(directed[:, 0] < directed[:, 1], 1, -1)
    balance = np.bincount(inverse, weights=direction, minlength=len(edges))
    graph = sparse.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])),
                              shape=(len(vertices), len(vertices))).tocsr()
    total, labels = connected_components(graph, directed=False)
    component_area = np.bincount(labels[faces[:, 0]], weights=area, minlength=total)
    component_faces = np.bincount(labels[faces[:, 0]], minlength=total)
    order = np.argsort(-component_area)[:8]
    return {"vertices_exact_weld": len(vertices), "triangles": len(faces),
            "coordinate_min": vertices.min(0).tolist(), "coordinate_max": vertices.max(0).tolist(),
            "coordinate_extent": np.ptp(vertices, axis=0).tolist(), "units": "UNVERIFIED",
            "degenerate_triangles": int(np.sum(area <= 1e-14)),
            "boundary_edges": int(np.sum(counts == 1)), "nonmanifold_edges": int(np.sum(counts > 2)),
            "inconsistent_two_face_edges": int(np.sum((counts == 2) & (balance != 0))),
            "connected_components": total,
            "largest_components": [{"faces": int(component_faces[i]),
                                     "area_share": float(component_area[i] / max(area.sum(), 1e-30))}
                                    for i in order],
            "mesh_acceptance": "UNVERIFIED", "source_modified": False}


def video_review(path, output):
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError("Video cannot be opened")
    try:
        fps, count = capture.get(cv2.CAP_PROP_FPS), int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if not np.isfinite(fps) or fps <= 0 or count < 16:
            raise ValueError("Invalid video metadata")
        ids = np.linspace(0, count - 1, 16).round().astype(int)
        sheet = Image.new("RGB", (720, 4 * 348), (25, 25, 25))
        records = []
        for slot, index in enumerate(ids):
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            ok, bgr = capture.read()
            if not ok:
                raise ValueError("Selected video frame failed to decode")
            decoded_index = int(round(capture.get(cv2.CAP_PROP_POS_FRAMES))) - 1
            if decoded_index != index:
                raise ValueError("Video frame seek did not return declared frame")
            image = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
            frame_path = output / f"frame-{index:06d}.png"
            image.save(frame_path)
            thumb = image.copy()
            thumb.thumbnail((180, 320))
            x, y = (slot % 4) * 180, (slot // 4) * 348
            sheet.paste(thumb, (x, y))
            ImageDraw.Draw(sheet).text((x + 3, y + 322), f"{index} / {index / fps:.2f}s", fill="white")
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            records.append({"frame": int(index), "nominal_time_seconds": float(index / fps),
                            "path": frame_path.name, "sha256": sha256_file(frame_path),
                            "whole_frame_laplacian_variance": float(cv2.Laplacian(gray, cv2.CV_64F).var())})
        sheet.save(output / "video-contact-sheet.png")
        return {"fps_reported": fps, "frame_count_reported": count,
                "duration_nominal_seconds": count / fps,
                "width_reported": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height_reported": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "orientation_metadata_degrees": capture.get(cv2.CAP_PROP_ORIENTATION_META),
                "frames": records, "coverage_and_expression_status": "UNVERIFIED",
                "timing_note": "Frame index/fps is nominal, not verified container presentation timestamps.",
                "clarity_note": "Whole-image sharpness is descriptive, not face-region acceptance."}
    finally:
        capture.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--consent-record", required=True)
    parser.add_argument("--consent-date", required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if not output.is_relative_to(ROOT / "assets/private") or output.exists():
        raise ValueError("Fresh output under assets/private required")
    started, assets, cases = time.perf_counter(), [], []
    for number, folder in enumerate(sorted(p for p in source.iterdir() if p.is_dir()), 1):
        case_id = f"real-case-{number:03d}"
        files = {"video": folder / (folder.name + ".mp4"),
                 "skin": folder / (folder.name + "_pi.stl"),
                 "bone": folder / (folder.name + "_gu.stl")}
        if not all(path.is_file() for path in files.values()):
            raise ValueError("Each case requires the declared video/pi/gu naming triplet")
        for kind, path in files.items():
            assets.append({"id": case_id + "-" + kind, "path": str(path), "sha256": sha256_file(path),
                           "source": "user-supplied local capture; file pairing and scan type declared by user",
                           "license_id": "private-user-authorized-local-validation-only",
                           "allowed_uses": ["local_head_reconstruction_validation"],
                           "retention_until": "local-validation-complete-or-user-revocation",
                           "deletion_process": "Delete project derivatives on request; original files remain user managed.",
                           "consent": {"subject_id": case_id, "record_id": args.consent_record,
                                       "granted_at": args.consent_date, "biometric_processing": True}})
        cases.append({"id": case_id, "files": {key: str(value) for key, value in files.items()},
                      "pairing": "user-declared same person", "scan_and_video_date_match": "UNVERIFIED"})
    if not cases:
        raise ValueError("No cases")
    manifest = {"schema_version": 1, "purpose": "local_head_reconstruction_validation", "inputs": assets,
                "training_allowed": False, "upload_allowed": False, "cases": cases}
    errors = validate_input_assets(manifest, output)
    if errors:
        raise ValueError(errors)
    output.mkdir(parents=True)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for case in cases:
        folder = output / case["id"]
        folder.mkdir()
        case["video"] = video_review(Path(case["files"]["video"]), folder)
        case["scans"] = {kind: scan_stats(Path(case["files"][kind])) for kind in ("skin", "bone")}
        print(case["id"], json.dumps({"video_seconds": case["video"]["duration_nominal_seconds"],
                                     "scans": case["scans"]}), flush=True)
    if validate_input_assets(manifest, output):
        raise ValueError("Source files changed during intake")
    result = {"technical_status": "TECHNICAL_CHECK_PASSED", "benchmark_readiness": "UNVERIFIED",
              "manifest_sha256": sha256_file(output / "manifest.json"), "cases": cases,
              "tool_sha256": sha256_file(Path(__file__)), "loader_sha256": sha256_file(ROOT / "src/headfoundry/scan.py"),
              "elapsed_seconds": time.perf_counter() - started,
              "limits": "Two development cases; no independent test set. Scan accuracy, units, timing, pose/expression and calibration await review. No geometry fitted or accepted."}
    (output / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
