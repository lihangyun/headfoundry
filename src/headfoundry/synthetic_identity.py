"""Deterministic bounded synthetic identities from paired morph targets."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PairedControl:
    name: str
    negative: np.ndarray
    positive: np.ndarray


_PAIRS = (("-decr", "-incr"), ("-down", "-up"), ("-backward", "-forward"))
_EXPRESSION_TOKENS = ("jaw-drop", "mouth-angles", "mouth-open", "smile", "frown")


def paired_controls(names, deltas):
    """Return bilateral neutral controls; unpaired and expression targets are excluded."""
    names = [str(name) for name in names]
    deltas = np.asarray(deltas, float)
    if deltas.ndim != 3 or deltas.shape[0] != len(names) or deltas.shape[2] != 3:
        raise ValueError("target deltas must have shape (targets, vertices, 3)")
    entries = {}
    for index, name in enumerate(names):
        stem = name.removesuffix(".target")
        if any(token in stem for token in _EXPRESSION_TOKENS) or stem.startswith("asym/"):
            continue
        side = ""
        folder, leaf = stem.rsplit("/", 1)
        if leaf.startswith(("l-", "r-")):
            side, leaf = leaf[:1], leaf[2:]
        for negative, positive in _PAIRS:
            suffix = negative if leaf.endswith(negative) else positive if leaf.endswith(positive) else None
            if suffix is None:
                continue
            feature = leaf.removesuffix(suffix)
            key = f"{folder}/{feature}"
            entries.setdefault(key, {})[(side, suffix)] = deltas[index]
            break
    controls = []
    for key, variants in sorted(entries.items()):
        negative_suffix, positive_suffix = next(
            pair for pair in _PAIRS if any(suffix in pair for _, suffix in variants)
        )
        sides = {side for side, _ in variants}
        if "" in sides:
            required = [("", negative_suffix), ("", positive_suffix)]
        else:
            required = [(side, suffix) for side in ("l", "r") for suffix in (negative_suffix, positive_suffix)]
        if not all(item in variants for item in required):
            continue
        negative = sum((variants[(side, negative_suffix)] for side in ({""} if "" in sides else {"l", "r"})),
                       np.zeros_like(deltas[0]))
        positive = sum((variants[(side, positive_suffix)] for side in ({""} if "" in sides else {"l", "r"})),
                       np.zeros_like(deltas[0]))
        if np.any(negative) and np.any(positive):
            controls.append(PairedControl(key, negative, positive))
    return controls


def synthesize(vertices, faces, controls, *, count, seed, strength=.35, active_controls=12,
               maximum_displacement=.20, minimum_area_ratio=.35, attempts_per_sample=50):
    """Sample safe identities and return vertices, coefficients and safety records."""
    vertices, faces = np.asarray(vertices, float), np.asarray(faces, int)
    if (vertices.ndim != 2 or vertices.shape[1:] != (3,) or faces.ndim != 2 or faces.shape[1:] != (3,)
            or not controls or count <= 0 or active_controls <= 0 or not 0 < strength <= 1):
        raise ValueError("invalid synthetic identity inputs")
    base_normal = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]],
                           vertices[faces[:, 2]] - vertices[faces[:, 0]])
    base_area = np.linalg.norm(base_normal, axis=1)
    if np.any(base_area <= 0):
        raise ValueError("base mesh contains degenerate triangles")
    rng = np.random.default_rng(seed)
    samples, coefficients, records = [], [], []
    for _ in range(count):
        for attempt in range(attempts_per_sample):
            chosen = rng.choice(len(controls), min(active_controls, len(controls)), replace=False)
            values = np.zeros(len(controls))
            values[chosen] = rng.uniform(-strength, strength, len(chosen))
            candidate = vertices.copy()
            for value, control in zip(values, controls):
                candidate += abs(value) * (control.positive if value >= 0 else control.negative)
            normal = np.cross(candidate[faces[:, 1]] - candidate[faces[:, 0]],
                              candidate[faces[:, 2]] - candidate[faces[:, 0]])
            displacement = float(np.linalg.norm(candidate - vertices, axis=1).max())
            area_ratio = float(np.min(np.linalg.norm(normal, axis=1) / base_area))
            reversals = int(np.sum(np.einsum("ij,ij->i", normal, base_normal) <= 0))
            if displacement <= maximum_displacement and area_ratio >= minimum_area_ratio and reversals == 0:
                samples.append(candidate)
                coefficients.append(values)
                records.append({"attempt": attempt + 1, "maximum_displacement": displacement,
                                "minimum_area_ratio": area_ratio, "normal_reversals": reversals})
                break
        else:
            raise ValueError("could not sample a safe identity within attempt limit")
    return np.asarray(samples), np.asarray(coefficients), records
