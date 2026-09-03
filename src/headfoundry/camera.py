"""Small, measurable camera-projection baseline.

This is not the production initializer. It is a normalized DLT reference used to
prove the coordinate conventions and camera quality gates before integrating a
learned multi-view initializer.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class CameraCheck:
    mean_reprojection_px: float
    p95_reprojection_px: float
    max_reprojection_px: float
    passed: bool


def _normalize_points(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dimension = points.shape[1]
    centroid = points.mean(axis=0)
    centered = points - centroid
    mean_distance = np.linalg.norm(centered, axis=1).mean()
    if mean_distance <= np.finfo(float).eps:
        raise ValueError("points do not span a usable coordinate system")
    scale = np.sqrt(dimension) / mean_distance
    transform = np.eye(dimension + 1)
    transform[:dimension, :dimension] *= scale
    transform[:dimension, dimension] = -scale * centroid
    homogeneous = np.column_stack([points, np.ones(len(points))])
    normalized = (transform @ homogeneous.T).T[:, :dimension]
    return normalized, transform


def estimate_projection_dlt(points_3d: np.ndarray, points_2d: np.ndarray) -> np.ndarray:
    """Estimate a 3x4 projective camera from at least six 3D/2D correspondences."""
    world = np.asarray(points_3d, dtype=float)
    image = np.asarray(points_2d, dtype=float)
    if world.ndim != 2 or world.shape[1] != 3:
        raise ValueError("points_3d must have shape (N, 3)")
    if image.shape != (len(world), 2):
        raise ValueError("points_2d must have shape (N, 2)")
    if len(world) < 6:
        raise ValueError("at least six correspondences are required")

    world_n, world_t = _normalize_points(world)
    image_n, image_t = _normalize_points(image)
    rows: list[list[float]] = []
    for (x, y, z), (u, v) in zip(world_n, image_n, strict=True):
        q = [x, y, z, 1.0]
        rows.append(q + [0.0] * 4 + [-u * value for value in q])
        rows.append([0.0] * 4 + q + [-v * value for value in q])
    _, _, vh = np.linalg.svd(np.asarray(rows))
    normalized_projection = vh[-1].reshape(3, 4)
    projection = np.linalg.inv(image_t) @ normalized_projection @ world_t
    scale = np.linalg.norm(projection[2, :3])
    if scale <= np.finfo(float).eps:
        raise ValueError("degenerate camera solution")
    return projection / scale


def project(projection: np.ndarray, points_3d: np.ndarray) -> np.ndarray:
    world_h = np.column_stack([points_3d, np.ones(len(points_3d))])
    image_h = (projection @ world_h.T).T
    if np.any(np.abs(image_h[:, 2]) <= np.finfo(float).eps):
        raise ValueError("a projected point lies on the camera plane")
    return image_h[:, :2] / image_h[:, 2, None]


def reprojection_errors(
    projection: np.ndarray, points_3d: np.ndarray, points_2d: np.ndarray
) -> np.ndarray:
    return np.linalg.norm(project(projection, points_3d) - points_2d, axis=1)


def synthetic_camera_check(threshold_px: float = 0.05) -> CameraCheck:
    rng = np.random.default_rng(20260903)
    world = rng.uniform([-1.0, -1.2, 0.0], [1.0, 1.2, 1.5], size=(32, 3))
    angle = np.deg2rad(17.0)
    rotation_y = np.array(
        [[np.cos(angle), 0.0, np.sin(angle)], [0.0, 1.0, 0.0], [-np.sin(angle), 0.0, np.cos(angle)]]
    )
    intrinsic = np.array([[1120.0, 0.0, 512.0], [0.0, 1090.0, 512.0], [0.0, 0.0, 1.0]])
    translation = np.array([[0.08], [-0.03], [4.5]])
    expected_projection = intrinsic @ np.column_stack([rotation_y, translation])
    observations = project(expected_projection, world)
    estimated = estimate_projection_dlt(world, observations)
    errors = reprojection_errors(estimated, world, observations)
    p95 = float(np.percentile(errors, 95))
    return CameraCheck(
        mean_reprojection_px=float(errors.mean()),
        p95_reprojection_px=p95,
        max_reprojection_px=float(errors.max()),
        passed=p95 <= threshold_px,
    )


def main() -> int:
    result = synthetic_camera_check()
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

