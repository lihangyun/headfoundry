"""Multi-view capture checks over rights-validated manifest records."""

from __future__ import annotations

from typing import Any


def validate_multiview(inputs: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    def reject(code: str, message: str, asset_id: str | None = None) -> None:
        item: dict[str, Any] = {"code": code, "message": message}
        if asset_id is not None:
            item["asset_id"] = asset_id
        errors.append(item)

    if not 5 <= len(inputs) <= 10:
        reject("VIEW_COUNT", f"expected 5-10 views, got {len(inputs)}")

    digests: dict[str, str] = {}
    yaws: list[float] = []
    for index, record in enumerate(inputs):
        asset_id = str(record.get("id", index))
        width, height = record.get("width_px"), record.get("height_px")
        if not isinstance(width, int) or not isinstance(height, int) or min(width, height) < 1024:
            reject("RESOLUTION", "minimum image dimension must be at least 1024 px", asset_id)
        clarity = record.get("clarity_score")
        if isinstance(clarity, bool) or not isinstance(clarity, (int, float)) or not 0.0 <= clarity <= 1.0:
            reject("CLARITY_FORMAT", "clarity_score must be numeric in [0, 1]", asset_id)
        elif clarity < 0.5:
            reject("BLUR", f"clarity_score {clarity:.3f} is below 0.500", asset_id)
        digest = record.get("sha256")
        if isinstance(digest, str):
            if digest in digests:
                reject("DUPLICATE", f"same file content as {digests[digest]}", asset_id)
            else:
                digests[digest] = asset_id
        yaw = record.get("yaw_degrees")
        if isinstance(yaw, bool) or not isinstance(yaw, (int, float)) or not -90.0 <= yaw <= 90.0:
            reject("YAW_FORMAT", "yaw_degrees must be numeric in [-90, 90]", asset_id)
        else:
            yaws.append(float(yaw))

    coverage = {
        "left_profile": any(yaw <= -45 for yaw in yaws),
        "left_intermediate": any(-45 < yaw <= -15 for yaw in yaws),
        "frontal": any(abs(yaw) < 15 for yaw in yaws),
        "right_intermediate": any(15 <= yaw < 45 for yaw in yaws),
        "right_profile": any(yaw >= 45 for yaw in yaws),
    }
    missing = [name for name, covered in coverage.items() if not covered]
    if missing:
        reject("VIEW_COVERAGE", "missing yaw bands: " + ", ".join(missing))
    return {
        "status": "TECHNICAL_CHECK_PASSED" if not errors else "REJECT",
        "view_count": len(inputs),
        "coverage": coverage,
        "errors": errors,
    }
