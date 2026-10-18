"""One bounded normal-line observation screen; original0213 solver unchanged."""
from pathlib import Path

import numpy as np

from headfoundry.normal_observation import normal_line_hits
from experiment_0209 import vertex_normals
from experiment_0213 import ROOT, main as run_case

OUT = ROOT / "artifacts/experiment-0214"


def normal_observations(truth, target_faces, cutoff):
    def observe(current, rest, faces, cloud, normals, tree, scope, mass):
        source_normals = vertex_normals(current, faces)
        ids = np.flatnonzero(scope)
        hit, count = normal_line_hits(current[ids], source_normals[ids], truth, target_faces,
                                      limit=.12, max_y=cutoff)
        usable = np.zeros(len(current), bool)
        usable[ids[count == 1]] = True
        if usable.sum() < 100:
            raise ValueError("too few unique compatible normal-line observations")
        targets = rest.copy()
        targets[usable] = hit[count == 1]
        print("Normal-line supports", int(usable.sum()), "ambiguous", int((count > 1).sum()), flush=True)
        return targets, mass*np.where(usable, 1., 4.), int(usable.sum())
    return observe


if __name__ == "__main__":
    run_case(OUT, observation_factory=normal_observations,
             observation_label="unique bidirectional source-normal triangle intersection within0.12 radius",
             extra_code_paths=(Path(__file__), ROOT / "src/headfoundry/normal_observation.py"))
