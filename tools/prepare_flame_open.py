"""Convert the exact official FLAME 2023 Open pickle to a safe neutral NumPy asset."""

from __future__ import annotations

import argparse
import io
import json
import os
import pickle
import pickletools
import zipfile
from pathlib import Path

import numpy as np
from scipy.sparse import csc_matrix

from headfoundry.flame import CONVERSION_ID, LICENSE_ID, MODEL_ID, SOURCE_URL
from headfoundry.manifest import sha256_file


MODEL_MEMBER = "flame2023_Open.pkl"
README_MEMBER = "FLAME2023_Open Readme.pdf"
ALLOWED_GLOBALS = {
    ("numpy.core.numeric", "_frombuffer"),
    ("numpy._core.numeric", "_frombuffer"),
    ("numpy", "dtype"),
    ("scipy.sparse._csc", "csc_matrix"),
}


class _RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if (module, name) not in ALLOWED_GLOBALS:
            raise pickle.UnpicklingError(f"forbidden global {module}.{name}")
        if name == "_frombuffer":
            return np._core.numeric._frombuffer
        if name == "dtype":
            return np.dtype
        return csc_matrix


def restricted_load(payload: bytes) -> dict:
    recent: list[str] = []
    globals_found: set[tuple[str, str]] = set()
    for operation, argument, _ in pickletools.genops(payload):
        if operation.name in {"BINUNICODE", "SHORT_BINUNICODE", "UNICODE"}:
            recent.append(str(argument)); recent = recent[-2:]
        elif operation.name == "GLOBAL":
            globals_found.add(tuple(str(argument).split(" ", 1)))
        elif operation.name == "STACK_GLOBAL" and len(recent) == 2:
            globals_found.add(tuple(recent))
    forbidden = globals_found - ALLOWED_GLOBALS
    if forbidden:
        raise ValueError(f"pickle contains forbidden globals: {sorted(forbidden)}")
    result = _RestrictedUnpickler(io.BytesIO(payload)).load()
    if not isinstance(result, dict):
        raise ValueError("official model must decode to a dictionary")
    return result


def convert(archive: Path, output: Path, reviewed_by: str, reviewed_at: str) -> Path:
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output directory must be empty: {output}")
    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        if not {MODEL_MEMBER, README_MEMBER} <= names:
            raise ValueError("archive is not the official FLAME 2023 Open layout")
        unexpected = [name for name in names if name not in {MODEL_MEMBER, README_MEMBER} and not name.startswith("__MACOSX/")]
        if unexpected:
            raise ValueError(f"unexpected archive members: {unexpected}")
        model_bytes = bundle.read(MODEL_MEMBER)
        readme_bytes = bundle.read(README_MEMBER)
    model = restricted_load(model_bytes)
    template = np.asarray(model.get("v_template"), dtype=np.float64)
    directions = np.asarray(model.get("shapedirs"), dtype=np.float64)
    faces_raw = np.asarray(model.get("f"))
    if template.shape != (5023, 3) or directions.shape != (5023, 3, 400):
        raise ValueError("unexpected FLAME 2023 Open template or shape basis")
    if faces_raw.shape != (9976, 3) or not np.issubdtype(faces_raw.dtype, np.integer):
        raise ValueError("unexpected FLAME 2023 Open topology")
    if not np.isfinite(template).all() or not np.isfinite(directions).all():
        raise ValueError("official model contains non-finite geometry")
    faces = faces_raw.astype(np.int64, copy=False)
    if faces.min() < 0 or faces.max() >= len(template) or np.any(np.diff(np.sort(faces, axis=1), axis=1) == 0):
        raise ValueError("official model contains invalid triangle indices")

    output.mkdir(parents=True, exist_ok=True)
    model_path = output / MODEL_MEMBER
    readme_path = output / README_MEMBER
    safe_path = output / "flame2023_Open.safe.npz"
    model_path.write_bytes(model_bytes)
    readme_path.write_bytes(readme_bytes)
    np.savez_compressed(safe_path, v_template=template, shapedirs=directions[:, :, :300], faces=faces)
    lock = {
        "id": MODEL_ID,
        "source_url": SOURCE_URL,
        "download_url": "https://download.is.tue.mpg.de/download.php?domain=flame&sfile=FLAME2023Open.zip",
        "license_id": LICENSE_ID,
        "source_path": Path(os.path.relpath(archive.resolve(), output.resolve())).as_posix(),
        "source_sha256": sha256_file(archive),
        "model_path": model_path.name,
        "model_sha256": sha256_file(model_path),
        "readme_path": readme_path.name,
        "readme_sha256": sha256_file(readme_path),
        "path": safe_path.name,
        "sha256": sha256_file(safe_path),
        "conversion_id": CONVERSION_ID,
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
        "attribution": "FLAME: Learning a model of facial shape and expression from 4D scans, Li et al., ACM TOG 2017; converted to a neutral identity-only NumPy archive.",
        "commercial_use": True,
        "changes_disclosed": True,
        "prohibited_uses_reviewed": True,
        "scope": "Exact official FLAME 2023 Open neutral template, topology and first 300 identity directions only. Expression directions, registered data, landmarks and texture assets are excluded.",
    }
    lock_path = output / "flame-2023-open-lock.json"
    lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
    return lock_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reviewed-by", required=True)
    parser.add_argument("--reviewed-at", required=True)
    args = parser.parse_args(argv)
    print(convert(args.archive, args.output, args.reviewed_by, args.reviewed_at))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
