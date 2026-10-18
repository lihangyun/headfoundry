"""One missing-observation comparison; exact0214 ray rules and observed weights."""
from pathlib import Path

from experiment_0213 import ROOT, main as run_case
from experiment_0214 import normal_observations

OUT = ROOT / "artifacts/experiment-0215"


if __name__ == "__main__":
    run_case(OUT, observation_factory=normal_observations, unsupported_policy="missing",
             observation_label="same0214 unique normal-line intersections; unsupported positional data absent",
             extra_code_paths=(Path(__file__), ROOT / "tools/experiment_0214.py",
                               ROOT / "src/headfoundry/normal_observation.py"))
