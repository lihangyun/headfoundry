"""Fail-closed input and model asset manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .inputs import validate_multiview


COMMERCIAL_MODEL_ID = "VGGT-1B-Commercial"
COMMERCIAL_REPOSITORY = "facebook/VGGT-1B-Commercial"
COMMERCIAL_LICENSE = "vggt-aup-license"
ALLOWED_PURPOSES = {"commercial_head_reconstruction", "local_head_reconstruction_validation"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _present(record: dict[str, Any], fields: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix}.{field}: missing" for field in fields if not record.get(field)]


def _validate_file(record: dict[str, Any], root: Path, prefix: str) -> list[str]:
    errors = _present(record, ("path", "sha256"), prefix)
    if errors:
        return errors
    path = root / record["path"]
    if not path.is_file():
        return [f"{prefix}.path: file not found: {path}"]
    expected = str(record["sha256"]).lower()
    actual = sha256_file(path)
    return [] if expected == actual else [f"{prefix}.sha256: expected {expected}, got {actual}"]


def validate_commercial_model(record: dict[str, Any], root: Path, prefix: str = "model") -> list[str]:
    errors = _present(record, ("id", "repository", "license_id", "accepted_by", "accepted_at"), prefix)
    if record.get("id") != COMMERCIAL_MODEL_ID:
        errors.append(f"{prefix}.id: only {COMMERCIAL_MODEL_ID} is allowed")
    if record.get("repository") != COMMERCIAL_REPOSITORY:
        errors.append(f"{prefix}.repository: only {COMMERCIAL_REPOSITORY} is allowed")
    if record.get("license_id") != COMMERCIAL_LICENSE:
        errors.append(f"{prefix}.license_id: expected {COMMERCIAL_LICENSE}")
    if record.get("acceptable_use_reviewed") is not True:
        errors.append(f"{prefix}.acceptable_use_reviewed: explicit true is required")
    if record.get("military_use") is not False:
        errors.append(f"{prefix}.military_use: explicit false is required")
    errors.extend(_validate_file(record, root, prefix))
    return errors


def validate_input_assets(document: dict[str, Any], root: Path) -> list[str]:
    """Shared rights boundary; independent adapters must still validate their models."""
    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    purpose = document.get("purpose")
    if purpose not in ALLOWED_PURPOSES:
        errors.append("purpose: unsupported")

    inputs = document.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        errors.append("inputs: at least one input asset is required")
    else:
        for index, record in enumerate(inputs):
            prefix = f"inputs[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix}: must be an object")
                continue
            errors.extend(_present(record, ("id", "source", "license_id", "retention_until", "deletion_process"), prefix))
            allowed = record.get("allowed_uses")
            if not isinstance(allowed, list) or purpose not in allowed:
                errors.append(f"{prefix}.allowed_uses: manifest purpose is required")
            consent = record.get("consent")
            if not isinstance(consent, dict):
                errors.append(f"{prefix}.consent: missing")
            else:
                errors.extend(_present(consent, ("subject_id", "record_id", "granted_at"), f"{prefix}.consent"))
                if consent.get("biometric_processing") is not True:
                    errors.append(f"{prefix}.consent.biometric_processing: explicit true is required")
            errors.extend(_validate_file(record, root, prefix))

    return errors


def validate_manifest(document: dict[str, Any], root: Path) -> list[str]:
    errors = validate_input_assets(document, root)
    models = document.get("models")
    if not isinstance(models, list) or not models:
        errors.append("models: at least one model asset is required")
    else:
        for index, record in enumerate(models):
            prefix = f"models[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix}: must be an object")
                continue
            errors.extend(validate_commercial_model(record, root, prefix))
    return errors


def load_and_validate(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_manifest(document, path.parent)
    capture = validate_multiview(document.get("inputs", []))
    passed = not errors and capture["status"] == "TECHNICAL_CHECK_PASSED"
    return {
        "status": "TECHNICAL_CHECK_PASSED" if passed else "REJECT",
        "rights_and_assets": {"passed": not errors, "errors": errors},
        "capture": capture,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    report = load_and_validate(args.manifest)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "TECHNICAL_CHECK_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
