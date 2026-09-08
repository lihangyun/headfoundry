"""Commercial VGGT camera/point-map adapter and camera-only quality gate."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .manifest import validate_commercial_model


COORDINATE_CONVENTION = "opencv_camera_from_world_x_right_y_down_z_forward"


@dataclass(frozen=True)
class CameraInitialization:
    extrinsics: np.ndarray
    intrinsics: np.ndarray
    world_points: np.ndarray
    track_points_world: np.ndarray
    tracks_2d: np.ndarray
    coordinate_convention: str = COORDINATE_CONVENTION


@dataclass(frozen=True)
class CommercialVGGTAdapter:
    checkpoint: Path

    @classmethod
    def from_asset_record(cls, record: dict[str, Any], root: Path) -> "CommercialVGGTAdapter":
        errors = validate_commercial_model(record, root)
        if errors:
            raise ValueError("commercial checkpoint rejected: " + "; ".join(errors))
        return cls(root / record["path"])

    def adapt(self, predictions: dict[str, Any]) -> CameraInitialization:
        return adapt_predictions(predictions)


def adapt_predictions(predictions: dict[str, Any]) -> CameraInitialization:
    """Normalize already-decoded commercial VGGT predictions to NumPy arrays."""
    required = ("extrinsic", "intrinsic", "world_points", "track_points_world", "tracks_2d")
    missing = [name for name in required if name not in predictions]
    if missing:
        raise ValueError("missing VGGT outputs: " + ", ".join(missing))
    return CameraInitialization(
        extrinsics=np.asarray(predictions["extrinsic"], dtype=float),
        intrinsics=np.asarray(predictions["intrinsic"], dtype=float),
        world_points=np.asarray(predictions["world_points"], dtype=float),
        track_points_world=np.asarray(predictions["track_points_world"], dtype=float),
        tracks_2d=np.asarray(predictions["tracks_2d"], dtype=float),
    )


def _project(extrinsic: np.ndarray, intrinsic: np.ndarray, points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    camera = (extrinsic[:, :3] @ points.T + extrinsic[:, 3:4]).T
    pixels_h = (intrinsic @ camera.T).T
    return pixels_h[:, :2] / pixels_h[:, 2, None], camera[:, 2]


def evaluate_camera_initialization(
    result: CameraInitialization,
    image_sizes: list[tuple[int, int]],
    max_reprojection_p95_px: float = 3.0,
) -> dict[str, Any]:
    view_count = len(image_sizes)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, value: Any = None, reason: str | None = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "value": value, "reason": reason})

    shapes_ok = (
        result.extrinsics.shape == (view_count, 3, 4)
        and result.intrinsics.shape == (view_count, 3, 3)
        and result.world_points.ndim == 4
        and result.world_points.shape[0] == view_count
        and result.world_points.shape[-1] == 3
        and result.track_points_world.ndim == 2
        and result.track_points_world.shape[1:] == (3,)
        and result.tracks_2d.shape == (view_count, len(result.track_points_world), 2)
    )
    check("matrix_and_point_formats", shapes_ok)
    check("coordinate_convention", result.coordinate_convention == COORDINATE_CONVENTION, result.coordinate_convention)
    finite = all(np.isfinite(array).all() for array in (result.extrinsics, result.intrinsics, result.world_points, result.track_points_world, result.tracks_2d))
    check("finite_values", finite)
    if not (shapes_ok and finite):
        return {"status": "REJECT", "checks": checks}

    rotations = result.extrinsics[:, :, :3]
    rotation_errors = np.linalg.norm(rotations @ rotations.transpose(0, 2, 1) - np.eye(3), axis=(1, 2))
    determinants = np.linalg.det(rotations)
    rotation_ok = bool(np.all(rotation_errors <= 1e-4) and np.all(np.abs(determinants - 1.0) <= 1e-4))
    check("rigid_world_to_camera", rotation_ok, {"max_orthonormal_error": float(rotation_errors.max()), "min_determinant": float(determinants.min())})

    intrinsic_errors: list[str] = []
    focals: list[float] = []
    for index, ((height, width), intrinsic) in enumerate(zip(image_sizes, result.intrinsics, strict=True)):
        fx, fy, cx, cy = intrinsic[0, 0], intrinsic[1, 1], intrinsic[0, 2], intrinsic[1, 2]
        scale = max(height, width)
        if (not np.allclose(intrinsic[2], [0.0, 0.0, 1.0], atol=1e-6)
                or max(abs(intrinsic[0, 1]), abs(intrinsic[1, 0])) > 1e-6):
            intrinsic_errors.append(f"view {index}: non-canonical K")
        if not (0.25 * scale <= fx <= 4.0 * scale and 0.25 * scale <= fy <= 4.0 * scale):
            intrinsic_errors.append(f"view {index}: implausible focal length")
        if not (0 <= cx <= width and 0 <= cy <= height):
            intrinsic_errors.append(f"view {index}: principal point outside image")
        focals.append(float((fx + fy) / (2 * scale)))
    check("intrinsic_and_focal_plausibility", not intrinsic_errors, {"normalized_focal_range": [min(focals), max(focals)]}, "; ".join(intrinsic_errors) or None)
    focal_spread = max(focals) - min(focals)
    check("cross_view_focal_consistency", focal_spread <= 0.25, focal_spread)

    positive = 0
    total = 0
    track_positive = 0
    errors: list[float] = []
    for index in range(view_count):
        points = result.world_points[index].reshape(-1, 3)
        _, depths = _project(result.extrinsics[index], result.intrinsics[index], points)
        positive += int(np.count_nonzero(depths > 0))
        total += len(depths)
        projected, track_depths = _project(result.extrinsics[index], result.intrinsics[index], result.track_points_world)
        visible = track_depths > 0
        track_positive += int(visible.sum())
        errors.extend(np.linalg.norm(projected[visible] - result.tracks_2d[index, visible], axis=1))
    cheirality = positive / total if total else 0.0
    check("cheirality", cheirality >= 0.95, cheirality)
    track_total = view_count * len(result.track_points_world)
    track_cheirality = track_positive / track_total if track_total else 0.0
    check("track_cheirality", track_cheirality >= 0.95, track_cheirality,
          "Reported common-view tracks cannot silently disappear behind cameras.")
    p95 = float(np.percentile(errors, 95)) if errors else float("inf")
    check("cross_view_reprojection_p95_px", p95 <= max_reprojection_p95_px, p95)
    return {
        "status": "TECHNICAL_CHECK_PASSED" if all(item["passed"] for item in checks) else "REJECT",
        "coordinate_convention": COORDINATE_CONVENTION,
        "camera": {"landmark_reprojection_p95_px": p95, "cheirality_fraction": cheirality, "normalized_focal_spread": focal_spread},
        "checks": checks,
    }


def load_fixture(path: Path) -> tuple[CameraInitialization, list[tuple[int, int]]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return adapt_predictions(document["predictions"]), [tuple(size) for size in document["image_sizes"]]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args(argv)
    result, sizes = load_fixture(args.fixture)
    report = evaluate_camera_initialization(result, sizes)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "TECHNICAL_CHECK_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
