"""Read-only residual attribution; no fit, candidate change or gate override."""
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from headfoundry.manifest import sha256_file

from experiment_0213 import OUT, SOURCE, MODEL, DONOR
from experiment_0210 import area_mass, surface_samples, matching
from experiment_0209 import vertex_normals


def main():
    source_report = json.loads((SOURCE / "report.json").read_text(encoding="utf-8"))
    data = np.load(OUT / "case-00/replay.npz", allow_pickle=False)
    base, prior, candidate, faces, truth, tf = (data[n] for n in
        ("base", "prior", "candidate", "faces", "truth", "target_faces"))
    cutoff = source_report["neck_y_cutoff_radius"]
    scope, mass = base[:, 1] < cutoff, area_mass(base, faces)
    cloud, normals = surface_samples(truth, tf, 200000, 21000)
    keep = cloud[:, 1] < cutoff
    cloud, normals = cloud[keep], normals[keep]
    fit_tree = cKDTree(cloud)
    _, weights, _ = matching(candidate, prior, faces, cloud, normals, fit_tree, scope, mass)
    supported = weights/mass < 2
    _, ids = fit_tree.query(candidate)
    compatible = np.einsum("ij,ij->i", vertex_normals(candidate, faces), normals[ids]) > .25
    evaluation, _ = surface_samples(truth, tf, 500000, 31000)
    tree = cKDTree(evaluation[evaluation[:, 1] < cutoff])
    error = tree.query(candidate)[0]**2*mass
    model, donor = np.load(MODEL, allow_pickle=False), np.load(DONOR, allow_pickle=False)
    region = {}
    named = np.zeros(len(candidate), bool)
    for name, mask in zip(model["vertex_group_names"].tolist(), model["vertex_groups"]):
        active = (mask[donor["original_vertex_ids"]] > .25) & scope
        if active.any() and name.endswith("_region"):
            named |= active
            region[name] = {"source_area_fraction": float(mass[active].sum()/mass[scope].sum()),
                            "source_squared_error_share": float(error[active].sum()/error[scope].sum()),
                            "supported_area_fraction": float(mass[active & supported].sum()/mass[active].sum())}
    def contribution(mask):
        active = scope & mask
        return {"source_area_fraction": float(mass[active].sum()/mass[scope].sum()),
                "source_squared_error_share": float(error[active].sum()/error[scope].sum())}

    result = {"scope_area_supported_fraction": float(mass[scope & supported].sum()/mass[scope].sum()),
              "unsupported_squared_error_share": float(error[scope & ~supported].sum()/error[scope].sum()),
              "rejection_partition": {"normal_incompatible": contribution(~compatible),
                                       "distance_trimmed": contribution(compatible & ~supported),
                                       "supported": contribution(supported)},
              "semantic_partition": {"named_facial_regions": contribution(named),
                                     "other_source_skin_not_anatomically_localized": contribution(~named)},
              "largest_regions": dict(sorted(region.items(), key=lambda item: -item[1]["source_squared_error_share"])[:12]),
              "input_sha256": {str(p): sha256_file(p) for p in
                  (SOURCE / "report.json", OUT / "report.json", OUT / "case-00/replay.npz", MODEL, DONOR)},
              "audit_code_sha256": sha256_file(Path(__file__)),
              "limits": "Area-weighted vertex quadrature of forward proximity only, not the sampled symmetric gate, "
                        "independent causal identification, anatomical truth or permission to alter masks/thresholds. "
                        "Overlapping source region labels must not be added together."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
