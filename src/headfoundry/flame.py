"""Fail-closed neutral identity adapter for the CC-BY FLAME 2023 Open model."""

from __future__ import annotations

import argparse
import json
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .manifest import sha256_file


MODEL_ID = "FLAME-2023-Open"
SOURCE_URL = "https://flame.is.tue.mpg.de/"
LICENSE_ID = "CC-BY-4.0"
CONVERSION_ID = "numpy-safe-neutral-identity-v1"
IDENTITY_DIMENSIONS = 300


def validate_flame_open_asset(record: dict[str, Any], root: Path) -> list[str]:
    """Validate the exact open model and a hash-locked safe NumPy conversion."""
    required = (
        "id", "source_url", "license_id", "path", "sha256", "source_sha256",
        "reviewed_by", "reviewed_at", "attribution",
    )
    errors = [f"model.{field}: missing" for field in required if not record.get(field)]
    if record.get("id") != MODEL_ID:
        errors.append(f"model.id: only {MODEL_ID} is allowed")
    if record.get("source_url") != SOURCE_URL:
        errors.append(f"model.source_url: expected {SOURCE_URL}")
    if record.get("license_id") != LICENSE_ID:
        errors.append(f"model.license_id: expected {LICENSE_ID}")
    if record.get("conversion_id") != CONVERSION_ID:
        errors.append(f"model.conversion_id: expected {CONVERSION_ID}")
    if record.get("commercial_use") is not True:
        errors.append("model.commercial_use: explicit true is required")
    if record.get("changes_disclosed") is not True:
        errors.append("model.changes_disclosed: explicit true is required")
    if record.get("prohibited_uses_reviewed") is not True:
        errors.append("model.prohibited_uses_reviewed: explicit true is required")
    source_digest = str(record.get("source_sha256", "")).lower()
    if len(source_digest) != 64 or any(character not in string.hexdigits for character in source_digest):
        errors.append("model.source_sha256: expected 64 hexadecimal characters")
    path = root / str(record.get("path", ""))
    if not record.get("path") or not path.is_file():
        errors.append(f"model.path: file not found: {path}")
    elif record.get("sha256") and sha256_file(path) != str(record["sha256"]).lower():
        errors.append("model.sha256: converted asset digest mismatch")
    return errors


@dataclass(frozen=True)
class FlameIdentityModel:
    template: np.ndarray
    shape_directions: np.ndarray
    faces: np.ndarray

    @classmethod
    def from_asset_record(cls, record: dict[str, Any], root: Path) -> "FlameIdentityModel":
        errors = validate_flame_open_asset(record, root)
        if errors:
            raise ValueError("FLAME 2023 Open asset rejected: " + "; ".join(errors))
        with np.load(root / record["path"], allow_pickle=False) as archive:
            missing = [name for name in ("v_template", "shapedirs", "faces") if name not in archive]
            if missing:
                raise ValueError("FLAME conversion missing arrays: " + ", ".join(missing))
            faces = np.asarray(archive["faces"])
            if not np.issubdtype(faces.dtype, np.integer):
                raise ValueError("faces must contain integer indices")
            model = cls(
                np.asarray(archive["v_template"], dtype=float),
                np.asarray(archive["shapedirs"], dtype=float),
                faces.astype(np.int64, copy=False),
            )
        model.validate()
        return model

    def validate(self) -> None:
        vertex_count = len(self.template)
        if self.template.ndim != 2 or self.template.shape[1:] != (3,):
            raise ValueError("v_template must have shape (vertices, 3)")
        if self.shape_directions.shape != (vertex_count, 3, IDENTITY_DIMENSIONS):
            raise ValueError(f"shapedirs must have shape (vertices, 3, {IDENTITY_DIMENSIONS})")
        if self.faces.ndim != 2 or self.faces.shape[1:] != (3,) or not len(self.faces):
            raise ValueError("faces must be a non-empty (triangles, 3) array")
        if not all(np.isfinite(array).all() for array in (self.template, self.shape_directions)):
            raise ValueError("FLAME geometry contains non-finite values")
        if self.faces.min() < 0 or self.faces.max() >= vertex_count:
            raise ValueError("face index outside template")
        if np.any(np.diff(np.sort(self.faces, axis=1), axis=1) == 0):
            raise ValueError("degenerate face index")

    def neutral_vertices(self, identity: np.ndarray, max_absolute: float = 3.0) -> np.ndarray:
        coefficients = np.asarray(identity, dtype=float)
        if coefficients.shape != (IDENTITY_DIMENSIONS,) or not np.isfinite(coefficients).all():
            raise ValueError(f"identity must contain {IDENTITY_DIMENSIONS} finite coefficients")
        if not np.isfinite(max_absolute) or max_absolute <= 0:
            raise ValueError("max_absolute must be positive and finite")
        if np.any(np.abs(coefficients) > max_absolute):
            raise ValueError("identity coefficient outside configured bound")
        return self.template + np.einsum("vck,k->vc", self.shape_directions, coefficients)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_record", type=Path)
    args = parser.parse_args(argv)
    record = json.loads(args.asset_record.read_text(encoding="utf-8"))
    try:
        model = FlameIdentityModel.from_asset_record(record, args.asset_record.parent)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "REJECT", "error": str(error)}, indent=2))
        return 1
    print(json.dumps({
        "status": "TECHNICAL_CHECK_PASSED",
        "model_id": MODEL_ID,
        "vertices": len(model.template),
        "triangles": len(model.faces),
        "identity_dimensions": IDENTITY_DIMENSIONS,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
