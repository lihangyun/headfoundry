"""Native expression-space source/contact screen; no photos or identity fit."""
import json
from pathlib import Path
import time

import numpy as np

from headfoundry.expression_contact import fit_contact_expression
from headfoundry.manifest import sha256_file
from headfoundry.mesh_section import section_segments
from headfoundry.surface_diagnostic import write_obj
from experiment_0208 import closed_directions, MODEL, DONOR, LOCKS, VIEWS, K
from experiment_0210 import safety

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/experiment-0211"


def proper_crossings(upper, lower, contact, tolerance=20e-6):
    """Proper2D strip crossings outside the declared contact neighborhood.

    Collinear overlaps/tangencies are not certified by this diagnostic.
    """
    def cross(a, b):
        return a[0]*b[1]-a[1]*b[0]
    count = 0
    for a, b in upper:
        for c, d in lower:
            ab, cd = b-a, d-c
            if (cross(ab, c-a)*cross(ab, d-a) >= -1e-24
                    or cross(cd, a-c)*cross(cd, b-c) >= -1e-24):
                continue
            point = a+cross(c-a, cd)/cross(ab, cd)*ab
            if np.linalg.norm(point-contact) > tolerance:
                count += 1
    return count


def section_audit(vertices, upper_faces, lower_faces, upper, lower):
    midpoint = (vertices[upper[0]]+vertices[lower[0]])/2
    order = np.argsort(midpoint[:, 0])
    records = []
    for x in np.linspace(-.015, .015, 21)+1.414e-8:
        a = section_segments(vertices, upper_faces, 0, float(x))[2][:, :, 1:]
        b = section_segments(vertices, lower_faces, 0, float(x))[2][:, :, 1:]
        if not len(a) or not len(b):
            raise ValueError("missing predeclared lip section")
        contact = np.array([np.interp(x, midpoint[order, 0], midpoint[order, axis]) for axis in (1, 2)])
        records.append({"x_native": float(x), "crossings_away_from_contact": proper_crossings(a, b, contact),
                        "upper_segments": len(a), "lower_segments": len(b)})
    return records


def relief(vertices, upper, lower, central):
    contact = (vertices[upper[0]]+vertices[lower[0]])/2
    return np.array([(vertices[rows[1:]].max(0)[:, 2]-contact[:, 2])[central]
                     for rows in (upper, lower)])


def main():
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("preserve the one frozen source/contact run")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("locked source/license changed")
    model, donor = np.load(MODEL, allow_pickle=False), np.load(DONOR, allow_pickle=False)
    template = model["template_vertex_positions"].astype(float)
    groups = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    original_faces = model["triangles"]
    skin_mask = groups["skin"] > .5
    selected_faces = original_faces[np.all(skin_mask[original_faces], axis=1)]
    skin_ids, inverse = np.unique(selected_faces, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    lookup = np.full(len(template), -1, int)
    lookup[skin_ids] = np.arange(len(skin_ids))
    upper = lookup[donor["source_rows_upper"][1:]]
    lower = lookup[donor["source_rows_lower"][1:]]
    if np.any(upper < 0) or np.any(lower < 0):
        raise ValueError("lip supports missing from original skin")
    upper_faces = lookup[original_faces[np.all(np.isin(original_faces, donor["source_rows_upper"][1:]), axis=1)]]
    lower_faces = lookup[original_faces[np.all(np.isin(original_faces, donor["source_rows_lower"][1:]), axis=1)]]
    expression_ids = np.flatnonzero(np.char.startswith(model["expression_names"], "lower_face_region_"))
    if len(expression_ids) != 150 or len(skin_ids) != 12466 or len(faces) != 24820:
        raise ValueError("unexpected native model topology/expression layout")
    expression = model["expression_basis"][expression_ids][:, skin_ids, :].transpose(1, 2, 0).astype(float)
    identity = model["vertex_identity_basis"][:30].astype(float)
    closed_identity, closure_error = closed_directions(model, donor)
    eye_faces_original = original_faces[np.all((groups["eyes"] > .5)[original_faces], axis=1)]
    eye_ids, eye_inverse = np.unique(eye_faces_original, return_inverse=True)
    eye_faces = eye_inverse.reshape(-1, 3)
    native_mean = template[skin_ids]
    center = (native_mean.max(0)+native_mean.min(0))/2
    radius = np.linalg.norm(native_mean-center, axis=1).max()
    conversion = np.diag([1., -1., -1.])
    cameras = []
    for angle in VIEWS.values():
        c, s = np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))
        cameras.append(np.c_[[[c, 0, s], [0, 1, 0], [-s, 0, c]], [0., 0., 3.5]])
    OUT.mkdir(parents=True)
    np.savez_compressed(OUT / "cameras.npz", intrinsics=np.array([K]*5), extrinsics=np.array(cameras))
    np.savez_compressed(OUT / "native-basis.npz", expression=expression, faces=faces, skin_ids=skin_ids,
                        upper=upper, lower=lower, upper_faces=upper_faces, lower_faces=lower_faces)
    rng, results = np.random.default_rng(20261017), []
    for case in range(3):
        if time.perf_counter()-started > 600:
            raise TimeoutError("source/contact budget exhausted; no retuning")
        beta = np.zeros(30) if case == 0 else np.clip(rng.normal(size=30)*.5, -1.5, 1.5)
        for halvings in range(11):
            full = template+np.einsum("kvc,k->vc", identity, beta*2.**(-halvings))
            source = full[skin_ids]
            check = safety((source-center)/radius, (native_mean-center)/radius, faces)
            if check["passed"]:
                break
        else:
            raise ValueError("identity source safety limit exceeded")
        beta *= 2.**(-halvings)
        candidate, alpha, solver = fit_contact_expression(source, faces, expression, upper[0], lower[0],
                                                          contact_sigma=20e-6, motion_sigma=1e-3,
                                                          coefficient_bound=3.)
        folder = OUT / f"case-{case:02d}"
        folder.mkdir()
        # Contact and mesh gates use actual17-decimal native-coordinate exports.
        write_obj(folder / "candidate-skin-native.obj", candidate, faces, precision=17)
        candidate = np.array([[float(a) for a in line.split()[1:4]]
                              for line in (folder / "candidate-skin-native.obj").read_text().splitlines()
                              if line.startswith("v ")])
        gap = np.linalg.norm(candidate[upper[0]]-candidate[lower[0]], axis=1)
        source_mid = (source[upper[0]]+source[lower[0]])/2
        midpoint_motion = float(np.linalg.norm((candidate[upper[0]]+candidate[lower[0]])/2-source_mid, axis=1).max())
        central = np.abs(source_mid[:, 0]) < .006
        if central.sum() < 3:
            raise ValueError("too few fixed central lip columns")
        before, after = relief(source, upper, lower, central), relief(candidate, upper, lower, central)
        ratio = after/np.maximum(before, 1e-15)
        sections = section_audit(candidate, upper_faces, lower_faces, upper, lower)
        skin_safety = safety((candidate-center)/radius, (source-center)/radius, faces)
        mesh_safe = bool(skin_safety["normal_reversals"] == 0 and skin_safety["minimum_area_ratio"] >= .5
                         and skin_safety["maximum_displacement_radius"] <= .02 and skin_safety["finite"])
        contact_passed = bool(gap.max() <= 20e-6 and np.median(gap) <= 10e-6 and midpoint_motion <= .75e-3)
        relief_passed = bool(np.all(before > 0) and np.all(after > 0) and np.all(ratio >= .5))
        section_passed = all(r["crossings_away_from_contact"] == 0 for r in sections)
        manual = donor["vertices"]+np.einsum("vck,k->vc", closed_identity[:, :, :30], beta)
        eyes = full[eye_ids]
        for name, mesh, triangles in (("truth", source, faces), ("prior", manual, donor["faces"]),
                                      ("candidate", candidate, faces)):
            joined = np.vstack([mesh, eyes])
            joined_faces = np.vstack([triangles, eye_faces+len(mesh)])
            write_obj(folder / f"{name}.obj", (joined-center) @ conversion/radius, joined_faces, precision=17)
        status = "PARTIAL_SUCCESS" if mesh_safe and contact_passed and relief_passed and section_passed else "REJECT"
        record = {"case": case, "status": status, "identity_halvings": halvings, "mesh_safe": mesh_safe,
                  "skin_safety": skin_safety, "solver": solver,
                  "maximum_gap_native": float(gap.max()), "median_gap_native": float(np.median(gap)),
                  "maximum_midpoint_motion_native": midpoint_motion, "minimum_relief_ratio": float(ratio.min()),
                  "contact_passed": contact_passed, "relief_passed": relief_passed,
                  "sections_passed": section_passed, "sections": sections}
        results.append(record)
        np.savez_compressed(folder / "replay.npz", source_skin=source, candidate_skin=candidate,
                            coefficients=alpha, identity=beta, faces=faces,
                            base=(full[donor["original_vertex_ids"]]-center) @ conversion/radius,
                            source_relief=before, candidate_relief=after)
        print(json.dumps(record), flush=True)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED",
              "source_contact_gate": "PARTIAL_SUCCESS" if all(r["status"] == "PARTIAL_SUCCESS" for r in results) else "REJECT",
              "photo_likeness": "UNVERIFIED", "defaults_changed": False,
              "display_label": "NATIVE OPEN SOURCE (NOT GT) / MANUAL CONTEXT / NATIVE EXPRESSION",
              "version_labels": {"truth": "native open source", "prior": "manual context", "candidate": "native expression"},
              "source_locks": {str(p.relative_to(ROOT)): h for p, h in LOCKS.items()},
              "closure_derivative_replay_error": closure_error, "native_radius": radius,
              "expression_names": model["expression_names"][expression_ids].tolist(),
              "contact_sigma_native": 20e-6, "motion_sigma_native": 1e-3, "coefficient_bound": 3.,
              "code_sha256": sha256_file(Path(__file__)), "basis_sha256": sha256_file(OUT / "native-basis.npz"),
              "elapsed_seconds": time.perf_counter()-started, "results": results,
              "limits": "Native-expression contact screen, known source support pairs; no anatomy ground truth, "
              "exact whole-head collision/solid-volume certification, photo fit, semantic sampler or default promotion. "
              "Primary open/candidate skin topology is identical; manually closed context has different topology."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("results", "expression_names", "source_locks")}), flush=True)


if __name__ == "__main__":
    main()
