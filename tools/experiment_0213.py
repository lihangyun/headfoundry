"""One-case local-rigidity screen on the frozen0210 cross-source benchmark."""
import json
from pathlib import Path
import shutil
import time

import numpy as np
from scipy.spatial import cKDTree

from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from headfoundry.rigid_surface import fit_locally_rigid
from headfoundry.surface_diagnostic import write_obj
from experiment_0208 import LOCKS, MODEL, DONOR, VIEWS, K, safety
from experiment_0210 import (FLAME_LOCK, area_mass, surface_samples, matching,
                             safe_update, evaluate, depth_metrics)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/experiment-0210-export-corrected"
OUT = ROOT / "artifacts/experiment-0213"


def read_export(path, expected_faces):
    lines = path.read_text(encoding="utf-8").splitlines()
    vertices = np.array([[float(x) for x in line.split()[1:4]] for line in lines if line.startswith("v ")])
    faces = np.array([[int(x)-1 for x in line.split()[1:4]] for line in lines if line.startswith("f ")])
    if not np.array_equal(faces, expected_faces) or not np.isfinite(vertices).all():
        raise ValueError("actual export topology/coordinates invalid")
    return vertices


def main():
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("preserve the single first-case screen; no overwrite/sweep")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("licensed GNM source changed")
    old = json.loads((SOURCE / "report.json").read_text(encoding="utf-8"))
    original = ROOT / "artifacts/experiment-0210/report.json"
    if (sha256_file(original) != old["original_report_sha256"]
            or sha256_file(FLAME_LOCK) != old["target_lock_sha256"]):
        raise ValueError("frozen benchmark/target provenance changed")
    asset = json.loads(FLAME_LOCK.read_text(encoding="utf-8"))
    flame = FlameIdentityModel.from_asset_record(asset, FLAME_LOCK.parent)
    data = np.load(SOURCE / "case-00/replay.npz", allow_pickle=False)
    base, faces, prior, truth, target_faces = (data[n] for n in ("base", "faces", "prior", "truth", "target_faces"))
    recovered = base+np.einsum("vck,k->vc", data["basis"], data["beta"])
    center = (flame.template.max(0)+flame.template.min(0))/2
    expected_truth = (flame.neutral_vertices(data["target_coefficients"])-center) @ np.diag([1., -1., -1.])/old["target_mean_radius_native_units"]
    if (np.max(np.abs(recovered-prior)) > 1e-14 or np.max(np.abs(truth-expected_truth)) > 1e-14
            or not np.array_equal(target_faces, flame.faces)
            or not safety(prior, base, faces)["passed"]):
        raise ValueError("exact prior/target replay or starting safety failed")
    for name, vertices, triangles in (("truth", truth, target_faces), ("prior", prior, faces)):
        if np.max(np.abs(read_export(SOURCE / f"case-00/{name}.obj", triangles)-vertices)) > 1e-15:
            raise ValueError("baseline actual export does not replay")
    cameras = np.load(SOURCE / "cameras.npz", allow_pickle=False)
    if not np.array_equal(cameras["intrinsics"], np.array([K]*5)):
        raise ValueError("frozen camera intrinsics changed")
    for position, yaw in enumerate(VIEWS.values()):
        c, s = np.cos(np.deg2rad(yaw)), np.sin(np.deg2rad(yaw))
        if not np.array_equal(cameras["extrinsics"][position], np.c_[[[c, 0, s], [0, 1, 0], [-s, 0, c]], [0., 0., 3.5]]):
            raise ValueError("frozen camera extrinsics changed")
    cutoff = old["neck_y_cutoff_radius"]
    model, donor = np.load(MODEL, allow_pickle=False), np.load(DONOR, allow_pickle=False)
    groups = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    regions = {n: groups[n][donor["original_vertex_ids"]] > .25 for n in
               ("nose_region", "upper_lip_region", "lower_lip_region", "chin_region")}
    regions["combined_lips"] = regions["upper_lip_region"] | regions["lower_lip_region"]
    # Exact same source-area weights and sampled clouds as0210; no new observations.
    mass, scope = area_mass(base, faces), base[:, 1] < cutoff
    cloud, normals = surface_samples(truth, target_faces, 200000, 21000)
    keep = cloud[:, 1] < cutoff
    cloud, normals = cloud[keep], normals[keep]
    tree, current, history = cKDTree(cloud), prior.copy(), []
    folder = OUT / "case-00"
    folder.mkdir(parents=True)
    for outer in range(10):
        if time.perf_counter()-started > 900:
            raise TimeoutError("one-case fitting/evaluation budget exhausted")
        target, weight, count = matching(current, prior, faces, cloud, normals, tree, scope, mass)
        desired, diagnostics = fit_locally_rigid(prior, faces, target, weight, initial=current,
                                                 strength=.05, iterations=20)
        current, halvings = safe_update(current, desired, base, faces)
        step = {"iteration": outer, "supports": count, "halvings": halvings, **diagnostics}
        history.append(step)
        print(json.dumps({k: v for k, v in step.items() if k != "energy"}), flush=True)
        if halvings is None:
            break
    write_obj(folder / "candidate.obj", current, faces, precision=17)
    current = read_export(folder / "candidate.obj", faces)
    for name in ("truth", "prior"):
        shutil.copy2(SOURCE / f"case-00/{name}.obj", folder / f"{name}.obj")
    shutil.copy2(SOURCE / "cameras.npz", OUT / "cameras.npz")
    target_eval, _ = surface_samples(truth, target_faces, 500000, 31000)
    target_eval = target_eval[target_eval[:, 1] < cutoff]
    metrics = {n: evaluate(v, faces, target_eval, regions, scope, cutoff, 41000)
               for n, v in (("prior", prior), ("candidate", current))}
    depth = {n: {} for n in ("prior", "candidate")}
    for view, e in zip(VIEWS, cameras["extrinsics"]):
        _, td, ti = render(truth, target_faces, e, K, (512, 512))
        for name, mesh in (("prior", prior), ("candidate", current)):
            depth[name][view] = depth_metrics(mesh, faces, td, ti, target_faces, truth, e, cutoff)
    guarded = bool(all(metrics["candidate"]["regions_rms_radius"][n] <= metrics["prior"]["regions_rms_radius"][n]*1.05+1e-8 for n in regions)
                   and all(depth["candidate"][n]["rms_radius"] <= depth["prior"][n]["rms_radius"]*1.05+1e-8 for n in VIEWS))
    mesh = safety(current, base, faces)
    gain = bool(metrics["candidate"]["symmetric_rms_radius"] <= metrics["prior"]["symmetric_rms_radius"]*.7)
    result = {"case": 0, "metrics": metrics, "depth": depth, "guarded": guarded, "gain": gain,
              "mesh_safe": mesh["passed"], "safety": mesh, "history": history}
    np.savez_compressed(folder / "replay.npz", base=base, truth=truth, prior=prior, candidate=current,
                        faces=faces, target_faces=target_faces)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
              "numeric_gate": "PARTIAL_SUCCESS" if mesh["passed"] and gain and guarded else "REJECT",
              "photo_likeness": "UNVERIFIED", "defaults_changed": False,
              "display_label": "CROSS-SOURCE SCREEN | FLAME OPEN TARGET / FROZEN GNM30 / LOCAL RIGIDITY",
              "version_labels": {"truth": "FLAME Open target", "prior": "frozen GNM30", "candidate": "local rigidity"},
              "source_locks": {str(p.relative_to(ROOT)): h for p, h in LOCKS.items()},
              "baseline_input_locks": {str(p.relative_to(ROOT)): sha256_file(p) for p in
                  (SOURCE / "report.json", SOURCE / "case-00/replay.npz", SOURCE / "cameras.npz",
                   SOURCE / "case-00/truth.obj", SOURCE / "case-00/prior.obj", FLAME_LOCK)},
              "target_attribution": asset["attribution"], "results": [result],
              "algorithm": {"outer_iterations": 10, "inner_iterations": 20, "strength": .05,
                            "edges": "positive-clipped cotangents normalized by median", "prior": "frozen0210 GNM30"},
              "code_sha256": sha256_file(Path(__file__)),
              "helper_sha256": sha256_file(ROOT / "src/headfoundry/rigid_surface.py"),
              "elapsed_seconds": time.perf_counter()-started,
              "limits": "One cross-model synthetic3D screen, estimated nearest-compatible correspondences; "
                        "not anatomical/collision certification, native-source closure, photo fitting or ACCEPT. "
                        "Remaining cases forbidden until numeric and actual five-view visual screen pass."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"numeric_gate": report["numeric_gate"], "elapsed_seconds": report["elapsed_seconds"],
                      "result": {k: v for k, v in result.items() if k != "history"}}), flush=True)


if __name__ == "__main__":
    main()
