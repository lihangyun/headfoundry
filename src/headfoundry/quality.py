"""Fail-closed acceptance gates for reconstruction candidates."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Gate:
    metric: str
    operator: str
    threshold: float

    def passes(self, value: float) -> bool:
        return value <= self.threshold if self.operator == "max" else value >= self.threshold


GATES = (
    Gate("camera.landmark_reprojection_p95_px", "max", 3.0),
    Gate("geometry.scan_point_to_surface_p95_mm", "max", 2.0),
    Gate("geometry.profile_silhouette_iou", "min", 0.94),
    Gate("geometry.frontal_landmark_nme", "max", 0.025),
    Gate("texture.heldout_lpips", "max", 0.20),
    Gate("texture.seam_delta_e_p95", "max", 6.0),
    Gate("mesh.non_manifold_edges", "max", 0.0),
    Gate("mesh.degenerate_faces", "max", 0.0),
    Gate("mesh.flipped_faces", "max", 0.0),
)


def _lookup(document: dict[str, Any], dotted_key: str) -> float:
    value: Any = document
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_key)
        value = value[part]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{dotted_key} must be numeric")
    return float(value)


def evaluate(document: dict[str, Any]) -> dict[str, Any]:
    results = []
    for gate in GATES:
        try:
            value = _lookup(document, gate.metric)
            passed = gate.passes(value)
            reason = None
        except (KeyError, TypeError) as error:
            value = None
            passed = False
            reason = str(error)
        results.append(
            {
                "metric": gate.metric,
                "value": value,
                "operator": gate.operator,
                "threshold": gate.threshold,
                "passed": passed,
                "reason": reason,
            }
        )
    gates_passed = all(item["passed"] for item in results)
    evidence = document.get("evidence", {})
    complete_visual_evidence = (
        isinstance(evidence, dict)
        and evidence.get("licensed_benchmark") is True
        and evidence.get("heldout_visual_review") is True
        and evidence.get("complete_reconstruction") is True
    )
    status = "REJECT" if not gates_passed else "ACCEPT" if complete_visual_evidence else "PARTIAL_SUCCESS"
    return {"status": status, "gates": results, "complete_visual_evidence": complete_visual_evidence}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
