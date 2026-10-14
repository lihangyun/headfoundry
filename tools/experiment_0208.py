"""Fixed dense-3D oracle capacity probe; local licensed assets only, no photos.

Run with the geometry extra installed. See the pre-registered experiment0208.
Outputs are ignored, never a production/default head replacement.
"""
import json
from pathlib import Path
import time

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu

from headfoundry.local_residual import geodesic_patches, fit_patch_residual
from headfoundry.manifest import sha256_file
from headfoundry.surface_diagnostic import write_obj


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "assets/private"
OUT = ROOT / "artifacts/experiment-0208"
MODEL = PRIVATE / "research/google-gnm/gnm/shape/data/versions/v3_0/gnm_head.npz"
DONOR = PRIVATE / "subject-001/gnm-posterior-contact-v2/artifacts/donor.npz"
LICENSE = DONOR.parent / "LICENSE-GNM.txt"
LOCKS = {MODEL: "785d62572590b1073d3f93c61d82346c1e33ffacd3f8245a1b6e0b33cf59e13d",
         DONOR: "fa4b14607fd4973d829e1b7e8cab51ce5e0746c70ca63acd30eabd68dacc2761",
         LICENSE: "40c4eb506541489bfa77cc4004acfb53cbc4973b9c55e42302ddff7f58e01f39"}
VIEWS = {"front": 0, "left30": -30, "left90": -90,
         "right30": 30, "right90": 90}
SIZE = 512
K = np.array([[700., 0, SIZE/2], [0, 700., SIZE/2], [0, 0, 1.]])


def closed_directions(model, donor):
    """Replay0202's fixed linear lip closure, identically for all directions.

    No new subject placement, image fitting, boundary rule or closure tuning.
    """
    template = donor["source_vertex_positions"]
    retained = donor["retained_original_vertex_ids"]
    faces = model["triangles"][np.sort(np.r_[donor["source_face_ids"],
                                                donor["collapsed_source_face_ids"]])]
    up, low = donor["source_rows_upper"][1:], donor["source_rows_lower"][1:]
    free = np.setdiff1d(retained[donor["support_mask"][retained]], np.r_[up.ravel(), low.ravel()])
    known = np.setdiff1d(retained, free)
    edges = np.unique(np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]],
                                               faces[:, [2, 0]]]), axis=1), axis=0)
    ii, jj = np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]]
    adj = coo_matrix((np.ones(len(ii)), (ii, jj)), shape=(len(template), len(template))).tocsr()
    lap = diags(np.asarray(adj.sum(1)).ravel()) - adj
    solver = splu(lap[free][:, free].tocsc())

    def closed(field):
        midpoint = (field[up[0]] + field[low[0]]) / 2
        delta = np.zeros_like(field)
        delta[up] = (midpoint - field[up[0]])[None]
        delta[low] = (midpoint - field[low[0]])[None]
        delta[up[1:], 0] = 0
        delta[low[1:], 0] = 0
        rhs = -(lap[free][:, known] @ delta[known].reshape(len(known), -1))
        delta[free] = solver.solve(rhs).reshape(delta[free].shape)
        result = field + delta
        result[up[0]], result[low[0]] = midpoint, midpoint
        return result[donor["original_vertex_ids"]]

    error = float(np.max(np.abs(closed(template) - donor["vertices"])))
    if error > 1e-14:
        raise ValueError("mean closure differs from the retained0202 source")
    return closed(model["vertex_identity_basis"].astype(float).transpose(1, 2, 0)), error


def safety(vertices, base, faces):
    normal = np.cross(vertices[faces[:, 1]]-vertices[faces[:, 0]],
                      vertices[faces[:, 2]]-vertices[faces[:, 0]])
    old = np.cross(base[faces[:, 1]]-base[faces[:, 0]], base[faces[:, 2]]-base[faces[:, 0]])
    record = {"finite": bool(np.isfinite(vertices).all()),
              "minimum_area_ratio": float(np.min(np.linalg.norm(normal, axis=1) /
                                                   np.linalg.norm(old, axis=1))),
              "normal_reversals": int(np.sum(np.einsum("ij,ij->i", normal, old) <= 0)),
              "maximum_displacement_radius": float(np.linalg.norm(vertices-base, axis=1).max())}
    record["passed"] = bool(record["finite"] and record["minimum_area_ratio"] >= .5
                            and record["normal_reversals"] == 0
                            and record["maximum_displacement_radius"] <= .12)
    return record


def rms(delta, mass):
    return float(np.sqrt(np.sum(mass * np.sum(delta*delta, axis=1)) / mass.sum()))


def project(vertices, extrinsic):
    cam = vertices @ extrinsic[:, :3].T + extrinsic[:, 3]
    if np.any(cam[:, 2] <= 0):
        raise ValueError("cheirality failure")
    h = cam @ K.T
    return h[:, :2] / h[:, 2:]


def main():
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("preserve the prior run; no implicit rerun/overwrite")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("missing or modified licensed asset: " + str(path.relative_to(ROOT)))
    model, donor = (np.load(path, allow_pickle=False) for path in (MODEL, DONOR))
    field, replay_error = closed_directions(model, donor)
    native, faces = donor["vertices"], donor["faces"]
    center = (native.max(0) + native.min(0)) / 2
    radius = np.linalg.norm(native-center, axis=1).max()
    conversion = np.diag([1., -1., -1.])
    base = (native-center) @ conversion / radius
    field = np.einsum("vck,cj->vjk", field, conversion) / radius
    basis = field[:, :, :30].reshape(-1, 30)
    mass = np.zeros(len(base))
    areas = np.linalg.norm(np.cross(base[faces[:, 1]]-base[faces[:, 0]],
                                   base[faces[:, 2]]-base[faces[:, 0]]), axis=1) / 6
    for corner in range(3):
        np.add.at(mass, faces[:, corner], areas)
    mass /= mass.sum()
    if np.any(mass <= 0):
        raise ValueError("surface mass must cover every retained vertex")
    patches = geodesic_patches(base, faces, (64, 192))
    camera = {}
    for name, yaw in VIEWS.items():
        theta = np.deg2rad(yaw)
        c, s = np.cos(theta), np.sin(theta)
        camera[name] = np.c_[[[c, 0, s], [0, 1, 0], [-s, 0, c]], [0., 0., 3.5]]
    original_ids = donor["original_vertex_ids"]
    groups = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    regions = {name: groups[name][original_ids] > .25 for name in
               ("nose_region", "upper_lip_region", "lower_lip_region", "chin_region",
                "left_orbital_region", "right_orbital_region", "ears")}
    regions["combined_lips"] = regions["upper_lip_region"] | regions["lower_lip_region"]
    if any(not m.any() for m in regions.values()):
        raise ValueError("empty semantic region")
    OUT.mkdir(parents=True)
    np.savez_compressed(OUT / "patches.npz", weights64=patches[0][0], nodes64=patches[0][1],
                        weights192=patches[1][0], nodes192=patches[1][1])
    np.savez_compressed(OUT / "cameras.npz", intrinsics=np.stack([K]*5),
                        extrinsics=np.array(list(camera.values())))
    weighted_basis = basis * np.repeat(np.sqrt(mass), 3)[:, None]
    rng = np.random.default_rng(20261014)
    records = []
    for index in range(12):
        if time.perf_counter()-started > 900:
            raise TimeoutError("preparation/fitting budget exhausted; stop without tuning")
        coefficients = rng.normal(size=253) * .7
        delta = np.einsum("vck,k->vc", field, coefficients)
        for halvings in range(11):
            truth = base + delta * 2.**(-halvings)
            if safety(truth, base, faces)["passed"]:
                break
        else:
            raise ValueError("fixed target generation safety limit exceeded")
        beta = np.linalg.lstsq(weighted_basis, ((truth-base) * np.sqrt(mass[:, None])).ravel(),
                               rcond=None)[0]
        prior = base + (basis @ beta).reshape(-1, 3)
        candidate, controls = fit_patch_residual(prior, truth, patches, mass)
        folder = OUT / f"case-{index:02d}"
        folder.mkdir()
        for name, vertices in (("truth", truth), ("prior", prior), ("candidate", candidate)):
            write_obj(folder / f"{name}.obj", vertices, faces)
        # Audit the serialized coordinates, not only the solver's in-memory arrays.
        def load_export(name):
            lines = (folder / f"{name}.obj").read_text(encoding="utf-8").splitlines()
            vertices = np.array([[float(x) for x in line.split()[1:4]]
                                 for line in lines if line.startswith("v ")])
            exported_faces = np.array([[int(x)-1 for x in line.split()[1:4]]
                                      for line in lines if line.startswith("f ")])
            if not np.array_equal(exported_faces, faces) or vertices.shape != base.shape:
                raise ValueError("exported topology changed")
            return vertices
        truth, prior, candidate = (load_export(n) for n in ("truth", "prior", "candidate"))
        metrics = {}
        for name, vertices in (("prior", prior), ("candidate", candidate)):
            metrics[name] = {"rms_radius": rms(vertices-truth, mass),
                             "regions_rms_radius": {n: rms((vertices-truth)[m], mass[m])
                                                    for n, m in regions.items()},
                             "projection_rms_px": {n: rms(project(vertices, e)-project(truth, e), mass)
                                                   for n, e in camera.items()},
                             "safety": safety(vertices, base, faces)}
        before, after = metrics["prior"], metrics["candidate"]
        protected = all(after["regions_rms_radius"][n] <= before["regions_rms_radius"][n]*1.05+1e-10
                        for n in regions)
        projected = all(after["projection_rms_px"][n] <= before["projection_rms_px"][n]*1.05+1e-8
                        for n in camera)
        gain = (after["rms_radius"] <= before["rms_radius"]*.6 and
                all(after["regions_rms_radius"][n] <= before["regions_rms_radius"][n]*.8
                    for n in ("nose_region", "combined_lips", "chin_region")))
        record = {"case": index, "target_halvings": halvings, "metrics": metrics,
                  "protected_regions_passed": protected, "five_projection_guard_passed": projected,
                  "required_gain_passed": gain, "mesh_safe": after["safety"]["passed"]}
        records.append(record)
        np.savez_compressed(folder / "replay.npz", base=base, truth=truth, prior=prior,
                            candidate=candidate, faces=faces, mass=mass, beta=beta,
                            controls64=controls[0], controls192=controls[1],
                            generator_coefficients=coefficients*2.**(-halvings))
        print(json.dumps(record), flush=True)
    guards = all(r["mesh_safe"] and r["protected_regions_passed"]
                 and r["five_projection_guard_passed"] for r in records)
    gain_count = sum(r["required_gain_passed"] for r in records)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED",
              "numeric_gate": "PARTIAL_SUCCESS" if guards and gain_count >= 10 else "REJECT",
              "visual_status": "UNVERIFIED", "real_reference_likeness": "UNVERIFIED",
              "defaults_changed": False, "gain_count": gain_count, "guards_all_passed": guards,
              "source_locks": {str(p.relative_to(ROOT)): h for p, h in LOCKS.items()},
              "license": "Apache-2.0; existing exact GNM graphical model lock",
              "source_radius_native_units": radius, "source_mean_replay_error": replay_error,
              "node_counts": [64, 192], "support_radii": [p[2] for p in patches], "ridge": 1e-6,
              "seed": 20261014, "samples": 12, "resolution": SIZE,
              "region_vertex_counts": {n: int(m.sum()) for n, m in regions.items()},
              "code_sha256": {"driver": sha256_file(Path(__file__)),
                              "local_residual": sha256_file(ROOT / "src/headfoundry/local_residual.py")},
              "elapsed_seconds": time.perf_counter()-started, "results": records,
              "limitations": "Full253 same-source synthetic GNM targets, exact dense3D material matches; "
              "not scanned identities, photo observations, arbitrary topology registration, self-intersection "
              "certification or likeness acceptance. First30 baseline is an optimistic dense oracle."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}), flush=True)


if __name__ == "__main__":
    main()
