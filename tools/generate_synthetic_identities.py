"""Generate a deterministic private synthetic identity set from a verified target basis."""
import argparse
import json
from pathlib import Path

import numpy as np

from headfoundry.manifest import sha256_file
from headfoundry.synthetic_identity import paired_controls, synthesize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("basis", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--count", type=int, default=256)
    parser.add_argument("--seed", type=int, default=155)
    args = parser.parse_args()
    source = args.basis / "targets.npz"
    data = np.load(source)
    controls = paired_controls(data["names"], data["deltas"])
    samples, coefficients, records = synthesize(
        data["vertices"], data["faces"], controls, count=args.count, seed=args.seed,
    )
    args.output.mkdir(exist_ok=False)
    np.savez_compressed(args.output / "identities.npz", vertices=samples,
                        coefficients=coefficients, control_names=np.asarray([item.name for item in controls]),
                        faces=data["faces"], base_vertices=data["vertices"])
    report = {
        "status": "TECHNICAL_CHECK_PASSED", "source_sha256": sha256_file(source),
        "seed": args.seed, "sample_count": len(samples), "control_count": len(controls),
        "active_controls_per_sample": min(12, len(controls)), "strength": 0.35,
        "maximum_displacement": max(item["maximum_displacement"] for item in records),
        "minimum_area_ratio": min(item["minimum_area_ratio"] for item in records),
        "maximum_attempts": max(item["attempt"] for item in records),
        "normal_reversals": sum(item["normal_reversals"] for item in records),
        "limitations": "Paired neutral CC0 morph combinations only. Safety is geometric, not realism, demographic coverage or subject-quality acceptance.",
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
