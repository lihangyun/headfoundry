"""Bounded side-profile contour fitting for the first geometry experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def fit_profile(
    baseline: np.ndarray,
    target: np.ndarray,
    editable: np.ndarray,
    smoothness: float = 0.15,
) -> np.ndarray:
    """Fit corresponding 2D contour points while freezing non-editable points."""
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)
    editable = np.asarray(editable, dtype=int)
    if baseline.shape != target.shape or baseline.ndim != 2 or baseline.shape[1] != 2:
        raise ValueError("baseline and target must have matching shape (N, 2)")
    if len(editable) == 0 or np.any(editable < 0) or np.any(editable >= len(baseline)):
        raise ValueError("editable indices must select at least one contour point")
    if smoothness < 0:
        raise ValueError("smoothness must be non-negative")

    column = {point_index: index for index, point_index in enumerate(editable)}
    regularizer = np.zeros((max(0, len(baseline) - 2), len(editable)))
    for row, center in enumerate(range(1, len(baseline) - 1)):
        for point_index, coefficient in ((center - 1, 1.0), (center, -2.0), (center + 1, 1.0)):
            if point_index in column:
                regularizer[row, column[point_index]] = coefficient

    system = np.vstack([np.eye(len(editable)), np.sqrt(smoothness) * regularizer])
    desired = target[editable] - baseline[editable]
    rhs = np.vstack([desired, np.zeros((len(regularizer), 2))])
    displacement, *_ = np.linalg.lstsq(system, rhs, rcond=None)
    candidate = baseline.copy()
    candidate[editable] += displacement
    return candidate


def evaluate_profile(
    baseline: np.ndarray,
    target: np.ndarray,
    candidate: np.ndarray,
    editable: np.ndarray,
) -> dict[str, Any]:
    baseline_errors = np.linalg.norm(baseline - target, axis=1)
    candidate_errors = np.linalg.norm(candidate - target, axis=1)
    editable = np.asarray(editable, dtype=int)
    protected = np.setdiff1d(np.arange(len(baseline)), editable)
    baseline_mean = float(baseline_errors[editable].mean())
    candidate_mean = float(candidate_errors[editable].mean())
    improvement = 1.0 - candidate_mean / baseline_mean if baseline_mean > 0 else 0.0
    protected_drift = float(np.linalg.norm(candidate[protected] - baseline[protected], axis=1).max()) if len(protected) else 0.0
    passed = improvement >= 0.5 and candidate_mean <= 0.03 and protected_drift <= 1e-12
    return {
        "status": "TECHNICAL_CHECK_PASSED" if passed else "REJECT",
        "profile": {
            "baseline_mean_error": baseline_mean,
            "candidate_mean_error": candidate_mean,
            "relative_improvement": improvement,
            "candidate_p95_error": float(np.percentile(candidate_errors[editable], 95)),
            "protected_max_drift": protected_drift,
        },
    }


def load_fixture(path: Path) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    document = json.loads(path.read_text(encoding="utf-8"))
    names = document["names"]
    editable = np.asarray([names.index(name) for name in document["editable"]], dtype=int)
    return names, np.asarray(document["baseline"], dtype=float), np.asarray(document["target"], dtype=float), editable


def write_svg(path: Path, names: list[str], baseline: np.ndarray, target: np.ndarray, candidate: np.ndarray, editable: np.ndarray) -> None:
    def points(values: np.ndarray) -> str:
        return " ".join(f"{40 + x * 620:.1f},{20 + y * 620:.1f}" for x, y in values)

    markers = "\n".join(
        f'<circle cx="{40 + candidate[index, 0] * 620:.1f}" cy="{20 + candidate[index, 1] * 620:.1f}" r="4" fill="#2563eb"><title>{names[index]}</title></circle>'
        for index in editable
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="700" viewBox="0 0 720 700">
<rect width="100%" height="100%" fill="white"/>
<text x="24" y="28" font-family="sans-serif" font-size="17">Experiment 0003 - side profile contour fit</text>
<polyline points="{points(target)}" fill="none" stroke="#111827" stroke-width="5"/>
<polyline points="{points(baseline)}" fill="none" stroke="#dc2626" stroke-width="3" stroke-dasharray="10 8"/>
<polyline points="{points(candidate)}" fill="none" stroke="#2563eb" stroke-width="3"/>
{markers}
<text x="24" y="662" font-family="sans-serif" font-size="15" fill="#111827">target</text>
<line x1="82" y1="657" x2="125" y2="657" stroke="#111827" stroke-width="5"/>
<text x="150" y="662" font-family="sans-serif" font-size="15" fill="#dc2626">baseline</text>
<line x1="215" y1="657" x2="258" y2="657" stroke="#dc2626" stroke-width="3" stroke-dasharray="10 8"/>
<text x="285" y="662" font-family="sans-serif" font-size="15" fill="#2563eb">candidate</text>
<line x1="360" y1="657" x2="403" y2="657" stroke="#2563eb" stroke-width="3"/>
</svg>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--svg", type=Path)
    args = parser.parse_args(argv)
    names, baseline, target, editable = load_fixture(args.fixture)
    candidate = fit_profile(baseline, target, editable)
    report = evaluate_profile(baseline, target, candidate, editable)
    if args.svg:
        write_svg(args.svg, names, baseline, target, candidate, editable)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "TECHNICAL_CHECK_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
