"""Bounded cross-model surface registration, not a photograph reconstruction."""
import json
from pathlib import Path
import time
import shutil
import sys

import numpy as np
from scipy.optimize import least_squares, lsq_linear
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from headfoundry.flame import FlameIdentityModel
from headfoundry.local_residual import geodesic_patches, fit_patch_residual
from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from headfoundry.surface_diagnostic import write_obj
from experiment_0208 import closed_directions, safety, MODEL, DONOR, LOCKS, VIEWS, K
from experiment_0209 import vertex_normals

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/experiment-0210"
FLAME_LOCK = ROOT / "assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json"


def surface_samples(vertices, faces, count, seed):
    """Area-uniform, deterministic surface points and smooth outward normals."""
    vertices, faces = np.asarray(vertices, float), np.asarray(faces)
    if (vertices.ndim != 2 or vertices.shape[1:] != (3,) or not np.isfinite(vertices).all()
            or faces.ndim != 2 or faces.shape[1:] != (3,) or not len(faces)
            or not np.issubdtype(faces.dtype, np.integer) or np.any(faces < 0)
            or np.any(faces >= len(vertices)) or count <= 0):
        raise ValueError("finite triangular surface and positive sample count required")
    tri = vertices[faces]
    area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)
    if np.any(area <= 0):
        raise ValueError("degenerate source surface")
    rng = np.random.default_rng(seed)
    ids = rng.choice(len(faces), size=count, p=area/area.sum())
    u, v = rng.random((2, count))
    u = np.sqrt(u)
    weights = np.c_[1-u, u*(1-v), u*v]
    points = np.einsum("ni,nij->nj", weights, tri[ids])
    normal = np.einsum("ni,nij->nj", weights, vertex_normals(vertices, faces)[faces[ids]])
    lengths = np.linalg.norm(normal, axis=1)
    if np.any(lengths <= 1e-12):
        raise ValueError("undefined interpolated normal")
    return points, normal/lengths[:, None]


def area_mass(vertices, faces):
    tri = vertices[faces]
    area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)/6
    mass = np.zeros(len(vertices))
    for corner in range(3):
        np.add.at(mass, faces[:, corner], area)
    if np.any(mass <= 0):
        raise ValueError("mass must cover every source vertex")
    return mass/mass.sum()


def transform(vertices, parameters):
    return np.exp(parameters[6])*(vertices @ Rotation.from_rotvec(parameters[:3]).as_matrix().T)+parameters[3:6]


def align(base, faces, cloud, cloud_normal, mass, facial):
    tree = cKDTree(cloud)
    x = np.zeros(7)
    lower, upper = -np.r_[[.14]*3, [.08]*3, .08], np.r_[[.14]*3, [.08]*3, .08]
    for _ in range(10):
        current = transform(base, x)
        distances, ids = tree.query(current)
        normal = vertex_normals(current, faces)
        mask = facial & (np.einsum("ij,ij->i", normal, cloud_normal[ids]) > .25)
        if mask.sum() < 100:
            raise ValueError("insufficient compatible facial alignment supports")
        mask &= distances <= np.quantile(distances[mask], .9)
        weights = np.sqrt(mass[mask]/mass[mask].sum())[:, None]
        matched = cloud[ids[mask]]
        result = least_squares(lambda p: np.r_[((transform(base[mask], p)-matched)*weights).ravel(),
                                               np.sqrt(1e-6)*p], x, bounds=(lower, upper), max_nfev=40)
        if not result.success:
            raise ValueError("bounded alignment solve did not converge")
        x = result.x
    return transform(base, x), x


def matching(current, rest, faces, cloud, normals, tree, scope, mass):
    distance, ids = tree.query(current)
    normal = vertex_normals(current, faces)
    usable = scope & (np.einsum("ij,ij->i", normal, normals[ids]) > .25)
    if usable.sum() < 100:
        raise ValueError("too few compatible head supports")
    usable &= distance <= np.quantile(distance[usable], .9)
    targets = rest.copy()
    targets[usable] = cloud[ids[usable]]
    weights = mass*np.where(usable, 1., 4.)
    return targets, weights, int(usable.sum())


def safe_update(current, desired, base, faces):
    for halvings in range(13):
        trial = current+(desired-current)*2.**(-halvings)
        if safety(trial, base, faces)["passed"]:
            return trial, halvings
    return current.copy(), None


def solve_prior(base, faces, basis, mass, cloud, normals, scope):
    tree, current, history = cKDTree(cloud), base.copy(), []
    beta = np.zeros(30)
    for iteration in range(10):
        target, weights, count = matching(current, base, faces, cloud, normals, tree, scope, mass)
        scale = np.repeat(np.sqrt(weights/weights.sum()), 3)
        matrix = np.vstack([basis.reshape(-1, 30)*scale[:, None], np.sqrt(1e-6)*np.eye(30)])
        rhs = np.r_[(target-base).ravel()*scale, np.zeros(30)]
        result = lsq_linear(matrix, rhs, bounds=(-3, 3), method="bvls", max_iter=100)
        if not result.success:
            raise ValueError("bounded first30 solve failed")
        desired = base+np.einsum("vck,k->vc", basis, result.x)
        next_mesh, halvings = safe_update(current, desired, base, faces)
        history.append({"iteration": iteration, "supports": count, "halvings": halvings})
        if halvings is None:
            break
        beta += (result.x-beta)*2.**(-halvings)
        current = next_mesh
    return current, beta, history


def solve_local(prior, base, faces, patches, mass, cloud, normals, scope):
    tree, current, history = cKDTree(cloud), prior.copy(), []
    controls = [np.zeros((len(p[1]), 3)) for p in patches]
    for iteration in range(10):
        target, weights, count = matching(current, prior, faces, cloud, normals, tree, scope, mass)
        desired, next_controls = fit_patch_residual(prior, target, patches, weights, ridge=1e-6)
        next_mesh, halvings = safe_update(current, desired, base, faces)
        history.append({"iteration": iteration, "supports": count, "halvings": halvings})
        if halvings is None:
            break
        controls = [a+(b-a)*2.**(-halvings) for a, b in zip(controls, next_controls)]
        current = next_mesh
    return current, controls, history


def evaluate(vertices, faces, target_points, regions, scope, cutoff, seed):
    tree = cKDTree(target_points)
    distance = tree.query(vertices)[0]
    points, _ = surface_samples(vertices, faces, 200000, seed)
    points = points[points[:, 1] < cutoff]
    forward = tree.query(points)[0]
    reverse = cKDTree(points).query(target_points)[0]
    return {"symmetric_rms_radius": float(np.sqrt((np.mean(forward**2)+np.mean(reverse**2))/2)),
            "forward_rms_radius": float(np.sqrt(np.mean(forward**2))),
            "reverse_rms_radius": float(np.sqrt(np.mean(reverse**2))),
            "forward_p95_radius": float(np.percentile(forward, 95)),
            "reverse_p95_radius": float(np.percentile(reverse, 95)),
            "regions_rms_radius": {n: float(np.sqrt(np.mean(distance[m & scope]**2))) for n, m in regions.items()},
            "source_evaluation_points": len(points), "target_evaluation_points": len(target_points)}


def depth_metrics(vertices, faces, truth_depth, truth_hit, target_faces, target_vertices, extrinsic, cutoff):
    _, depth, hit = render(vertices, faces, extrinsic, K, (512, 512))
    valid = truth_hit >= 0
    valid[valid] &= target_vertices[target_faces[truth_hit[valid]]].mean(1)[:, 1] < cutoff
    overlap = valid & (hit >= 0)
    error = np.full(valid.sum(), .12)
    error[(hit[valid] >= 0)] = np.abs(depth[overlap]-truth_depth[overlap])
    return {"rms_radius": float(np.sqrt(np.mean(error**2))),
            "p95_radius": float(np.percentile(error, 95)),
            "target_coverage": float(overlap.sum()/valid.sum())}


def main():
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("preserve the first run; no overwrite")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("licensed GNM source changed")
    record = json.loads(FLAME_LOCK.read_text(encoding="utf-8"))
    flame = FlameIdentityModel.from_asset_record(record, FLAME_LOCK.parent)
    model, donor = np.load(MODEL, allow_pickle=False), np.load(DONOR, allow_pickle=False)
    raw, closure_error = closed_directions(model, donor)
    native, faces = donor["vertices"], donor["faces"]
    low, high = flame.template.min(0), flame.template.max(0)
    center, radius = (low+high)/2, np.linalg.norm(flame.template-(low+high)/2, axis=1).max()
    conversion = np.diag([1., -1., -1.])
    scale = (high[1]-low[1]) / np.ptp(native[:, 1])
    offset = center-scale*(native.max(0)+native.min(0))/2
    initial = (native*scale+offset-center) @ conversion/radius
    fields = np.einsum("vck,cj->vjk", raw[:, :, :30], conversion)*scale/radius
    mean = (flame.template-center) @ conversion/radius
    cutoff = float(mean[:, 1].max()-.15*np.ptp(mean[:, 1]))
    groups = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    regions = {n: groups[n][donor["original_vertex_ids"]] > .25 for n in
               ("nose_region", "upper_lip_region", "lower_lip_region", "chin_region")}
    regions["combined_lips"] = regions["upper_lip_region"] | regions["lower_lip_region"]
    facial = np.logical_or.reduce([groups[n][donor["original_vertex_ids"]] > .25 for n in
                                  ("forehead_region", "nose_region", "upper_lip_region", "lower_lip_region",
                                   "chin_region", "left_cheek_region", "right_cheek_region",
                                   "left_orbital_region", "right_orbital_region")])
    mass = area_mass(initial, faces)
    cameras = []
    for yaw in VIEWS.values():
        angle = np.deg2rad(yaw)
        c, s = np.cos(angle), np.sin(angle)
        cameras.append(np.c_[[[c, 0, s], [0, 1, 0], [-s, 0, c]], [0., 0., 3.5]])
    OUT.mkdir(parents=True)
    np.savez_compressed(OUT / "cameras.npz", intrinsics=np.array([K]*5), extrinsics=np.array(cameras))
    rng, results = np.random.default_rng(20261015), []
    for index in range(4):
        if time.perf_counter()-started > 900:
            raise TimeoutError("preparation/fitting budget exhausted")
        coefficients = np.zeros(300) if index == 0 else np.clip(rng.normal(size=300)*.7, -3, 3)
        native_target = flame.neutral_vertices(coefficients)
        target = (native_target-center) @ conversion/radius
        for halvings in range(11):
            truth = mean+(target-mean)*2.**(-halvings)
            if safety(truth, mean, flame.faces)["passed"]:
                break
        else:
            raise ValueError("target generation safety limit")
        cloud, cloud_normal = surface_samples(truth, flame.faces, 200000, 21000+index)
        keep = cloud[:, 1] < cutoff
        cloud, cloud_normal = cloud[keep], cloud_normal[keep]
        target_eval, _ = surface_samples(truth, flame.faces, 500000, 31000+index)
        target_eval = target_eval[target_eval[:, 1] < cutoff]
        base, pose = align(initial, faces, cloud, cloud_normal, mass, facial)
        basis = np.einsum("vck,jc->vjk", fields, Rotation.from_rotvec(pose[:3]).as_matrix())*np.exp(pose[6])
        scope = base[:, 1] < cutoff
        prior, beta, prior_history = solve_prior(base, faces, basis, mass, cloud, cloud_normal, scope)
        patches = geodesic_patches(base, faces, (64, 192))
        candidate, controls, local_history = solve_local(prior, base, faces, patches, mass, cloud, cloud_normal, scope)
        folder = OUT / f"case-{index:02d}"
        folder.mkdir()
        for name, mesh, triangles in (("truth", truth, flame.faces), ("prior", prior, faces), ("candidate", candidate, faces)):
            write_obj(folder / f"{name}.obj", mesh, triangles, precision=17)
        # Re-read final OBJ coordinates and topology before any safety/quality claim.
        def exported(name, expected_faces):
            lines = (folder / f"{name}.obj").read_text(encoding="utf-8").splitlines()
            v = np.array([[float(x) for x in line.split()[1:4]] for line in lines if line.startswith("v ")])
            f = np.array([[int(x)-1 for x in line.split()[1:4]] for line in lines if line.startswith("f ")])
            if not np.array_equal(f, expected_faces):
                raise ValueError("export topology changed")
            return v
        truth, prior, candidate = exported("truth", flame.faces), exported("prior", faces), exported("candidate", faces)
        metrics = {n: evaluate(v, faces, target_eval, regions, scope, cutoff, 41000+index)
                   for n, v in (("prior", prior), ("candidate", candidate))}
        depth = {n: {} for n in ("prior", "candidate")}
        for view, e in zip(VIEWS, cameras):
            _, td, ti = render(truth, flame.faces, e, K, (512, 512))
            for name, mesh in (("prior", prior), ("candidate", candidate)):
                depth[name][view] = depth_metrics(mesh, faces, td, ti, flame.faces, truth, e, cutoff)
        guarded = (all(metrics["candidate"]["regions_rms_radius"][n] <= metrics["prior"]["regions_rms_radius"][n]*1.05+1e-8
                       for n in regions) and
                   all(depth["candidate"][n]["rms_radius"] <= depth["prior"][n]["rms_radius"]*1.05+1e-8 for n in VIEWS))
        mesh_safe = safety(candidate, base, faces)
        gain = metrics["candidate"]["symmetric_rms_radius"] <= metrics["prior"]["symmetric_rms_radius"]*.7
        result = {"case": index, "target_halvings": halvings, "alignment": pose.tolist(),
                  "metrics": metrics, "depth": depth, "guarded": bool(guarded), "gain": bool(gain),
                  "mesh_safe": mesh_safe["passed"], "safety": mesh_safe,
                  "prior_history": prior_history, "local_history": local_history}
        results.append(result)
        np.savez_compressed(folder / "replay.npz", base=base, truth=truth, target_faces=flame.faces,
                            prior=prior, candidate=candidate, faces=faces, beta=beta, basis=basis,
                            controls64=controls[0], controls192=controls[1],
                            patches64=patches[0][0], patches192=patches[1][0],
                            target_coefficients=coefficients*2.**(-halvings))
        print(json.dumps(result), flush=True)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
              "numeric_gate": "PARTIAL_SUCCESS" if all(r["mesh_safe"] and r["guarded"] for r in results)
                              and sum(r["gain"] for r in results) >= 3 else "REJECT",
              "photo_likeness": "UNVERIFIED", "defaults_changed": False,
              "display_label": "CROSS-SOURCE 3D | FLAME OPEN TARGET / GNM30 PRIOR / PATCH CANDIDATE",
              "source_locks": {str(p.relative_to(ROOT)): h for p, h in LOCKS.items()},
              "target_asset": record, "target_lock_sha256": sha256_file(FLAME_LOCK),
              "target_attribution": record["attribution"], "source_closure_replay_error": closure_error,
              "target_mean_radius_native_units": radius, "neck_y_cutoff_radius": cutoff,
              "initial_similarity": {"scale": scale, "offset": offset.tolist()},
              "iterations_per_fit": 10, "node_counts": [64, 192], "ridge": 1e-6,
              "code_sha256": sha256_file(Path(__file__)), "elapsed_seconds": time.perf_counter()-started,
              "results": results,
              "limits": "Cross-model synthetic3D surface registration; different topology and estimated "
              "nearest-compatible correspondences, sampled proximity not exact anatomical truth; "
              "no scan identity, photograph fitting, texture, hair, intersection certification or ACCEPT."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("results", "target_asset", "source_locks")}), flush=True)


def repair_export():
    """Recover the identical fitted field, not a refit or a post-fit shrink."""
    output = ROOT / "artifacts/experiment-0210-export-corrected"
    if output.exists():
        raise FileExistsError("preserve the one correction and the original run")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("licensed source changed")
    asset = json.loads(FLAME_LOCK.read_text(encoding="utf-8"))
    flame = FlameIdentityModel.from_asset_record(asset, FLAME_LOCK.parent)
    report = json.loads((OUT / "report.json").read_text(encoding="utf-8"))
    center = (flame.template.max(0)+flame.template.min(0))/2
    radius = report["target_mean_radius_native_units"]
    conversion = np.diag([1., -1., -1.])
    corrections = []
    output.mkdir()
    shutil.copy2(OUT / "cameras.npz", output / "cameras.npz")
    for result in report["results"]:
        old = OUT / f"case-{result['case']:02d}"
        new = output / old.name
        new.mkdir()
        with np.load(old / "replay.npz", allow_pickle=False) as archive:
            data = {n: archive[n] for n in archive.files}
        prior = data["base"]+np.einsum("vck,k->vc", data["basis"], data["beta"])
        candidate = prior+data["patches64"] @ data["controls64"]+data["patches192"] @ data["controls192"]
        truth = (flame.neutral_vertices(data["target_coefficients"])-center) @ conversion/radius
        original_safety = result["safety"]
        maximum_change = max(float(np.max(np.abs(v-data[n]))) for n, v in
                             (("truth", truth), ("prior", prior), ("candidate", candidate)))
        if maximum_change > 5.1e-9:
            raise ValueError("recovered geometry differs by more than eight-decimal rounding")
        for name, vertices, faces in (("truth", truth, data["target_faces"]),
                                      ("prior", prior, data["faces"]), ("candidate", candidate, data["faces"])):
            write_obj(new / f"{name}.obj", vertices, faces, precision=17)
            lines = (new / f"{name}.obj").read_text(encoding="utf-8").splitlines()
            actual = np.array([[float(x) for x in line.split()[1:4]] for line in lines if line.startswith("v ")])
            topology = np.array([[int(x)-1 for x in line.split()[1:4]] for line in lines if line.startswith("f ")])
            if not np.array_equal(topology, faces) or np.max(np.abs(actual-vertices)) > 1e-15:
                raise ValueError("corrected export changed fitted geometry/topology")
            data[name] = actual
        result["safety"] = safety(data["candidate"], data["base"], data["faces"])
        result["mesh_safe"] = result["safety"]["passed"]
        corrections.append({"case": result["case"], "maximum_rounding_change_radius": maximum_change,
                            "original_export_safety": original_safety, "corrected_export_safety": result["safety"]})
        np.savez_compressed(new / "replay.npz", **data)
    report.update(original_report_sha256=sha256_file(OUT / "report.json"),
                  export_correction_code_sha256=sha256_file(Path(__file__)),
                  export_correction="Identical original fit reconstructed from saved coefficients; precision8 to17; no refit/shrink/parameter change.",
                  quality_metrics_origin="Original eight-decimal exported meshes; not re-evaluated or advertised as improved by this precision repair. The original30% gain gate remains failed.",
                  numeric_gate="REJECT", export_corrections=corrections, defaults_changed=False)
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"corrections": corrections, "numeric_gate": "REJECT", "fit_reruns": 0}), flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["--repair-export"]:
        repair_export()
    elif len(sys.argv) == 1:
        main()
    else:
        raise ValueError("only the fixed run or --repair-export is supported")
