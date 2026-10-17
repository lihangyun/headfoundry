"""Frozen subject-identity source-construction ablation. No optimization."""
import json
from pathlib import Path
import shutil
import time

import numpy as np
from scipy.spatial.transform import Rotation

from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.subdivision import refine_triangle_attachments
from headfoundry.surface_diagnostic import write_obj
from experiment_0208 import LOCKS, MODEL, DONOR

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "assets/private/subject-001"
OUT = SUBJECT / "native-exterior-frozen-0212"
BASIS = SUBJECT / "whole-head-identity-v1/basis.npz"
FIT = SUBJECT / "whole-head-profile-fit-v2/fit.npz"
BASELINE = SUBJECT / "whole-head-profile-fit-v2"
CAMERAS = SUBJECT / "subject-central-depth-basis-v1/cameras.npz"


def shape_audit(mean, candidate, faces, pose_scale):
    original = np.cross(mean[faces[:, 1]]-mean[faces[:, 0]], mean[faces[:, 2]]-mean[faces[:, 0]])
    normal = np.cross(candidate[faces[:, 1]]-candidate[faces[:, 0]], candidate[faces[:, 2]]-candidate[faces[:, 0]])
    denominator = np.linalg.norm(original, axis=1)
    if np.any(denominator <= 1e-14):
        raise ValueError("degenerate source mean")
    result = {"minimum_area_ratio": float(np.min(np.linalg.norm(normal, axis=1)/denominator)),
              "normal_reversals": int(np.sum(np.einsum("ij,ij->i", normal, original) <= 0)),
              "maximum_shape_displacement_world": float(np.linalg.norm(candidate-mean, axis=1).max()*pose_scale)}
    result["passed"] = bool(result["minimum_area_ratio"] >= .5 and result["normal_reversals"] == 0
                            and result["maximum_shape_displacement_world"] <= .06)
    return result


def main():
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("preserve the one frozen ablation")
    manifest = json.loads((SUBJECT / "run-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("purpose") != "local_head_reconstruction_validation":
        raise ValueError("only the existing local validation purpose is allowed")
    errors = validate_input_assets(manifest, SUBJECT)
    if errors:
        raise ValueError(errors)
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("licensed source changed")
    basis_report = json.loads((BASIS.parent / "basis-report.json").read_text(encoding="utf-8"))
    if sha256_file(BASIS) != basis_report["basis_sha256"]:
        raise ValueError("source basis changed")
    for name, digest in basis_report["source_locks"].items():
        path = Path(name)
        if not path.is_relative_to(ROOT) or sha256_file(path) != digest:
            raise ValueError("source/placement lock changed")
    locks = {FIT: "e4238ad812e08417f39b70b06bc3b5890711f9a79cc3b07149d7df8a28df82dc",
             BASELINE / "after.obj": "a313862beeff06a0a9cd6ec8feb2c4e51b11bcf0503917c96e097fa03eea74a0",
             CAMERAS: "8598aa618e3223e562e72ebe0305286f3b51c002be1ffb13083d741abadf6abc"}
    for path, digest in locks.items():
        if sha256_file(path) != digest:
            raise ValueError("fixed experimental identity/camera changed")
    scene_record = json.loads((BASELINE / "fixed-scene/report.json").read_text(encoding="utf-8"))
    scene = SUBJECT / "head-only-relief-review-v2"
    scene_locks = {scene / "camera-diagnostic.blend": scene_record["baseline_scene_sha256"],
                   scene / "report.json": scene_record["baseline_report_sha256"],
                   SUBJECT / "render_in_fixed_clay_scene.py": scene_record["renderer_sha256"]}
    if scene_record["source_sha256"] != locks[BASELINE / "after.obj"] or scene_record["camera_sha256"] != locks[CAMERAS]:
        raise ValueError("baseline scene source/camera mismatch")
    for name, digest in scene_record["photo_sha256"].items():
        scene_locks[SUBJECT / f"{name}.png"] = digest
        scene_locks[BASELINE / "fixed-scene" / f"{name}-clay.png"] = scene_record["render_sha256"][name]
    for path, digest in scene_locks.items():
        if sha256_file(path) != digest:
            raise ValueError("reference image/scene/render changed")
    data, fitted, model, donor, cameras = (np.load(p, allow_pickle=False) for p in (BASIS, FIT, MODEL, DONOR, CAMERAS))
    parameters = fitted["parameters"]
    if parameters.shape != (37,) or not np.isfinite(parameters).all():
        raise ValueError("expected fixed seven pose and30 identity coefficients")
    beta, center = parameters[7:], data["marks"][:8].mean(0)
    def posed(points):
        return (points-center) @ Rotation.from_rotvec(parameters[1:4]).as_matrix().T*np.exp(parameters[0])+center+parameters[4:7]
    linear = np.diag([1., -1., -1.])*9.152741053300716 @ cameras["extrinsics"][0, :, :3]
    offsets = data["cage"]-donor["vertices"] @ linear
    if np.max(np.abs(offsets-offsets[0])) > 1e-12:
        raise ValueError("source-world placement is not the original fixed similarity")
    offset = offsets[0]
    native = model["template_vertex_positions"].astype(float)
    raw_identity = model["vertex_identity_basis"][:30].astype(float)
    shaped = native+np.einsum("kvc,k->vc", raw_identity, beta)
    groups = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    exterior = groups["skin_exterior"] > .5
    parent_ids = np.flatnonzero(np.all(exterior[model["triangles"]], axis=1))
    skin_ids, inverse = np.unique(model["triangles"][parent_ids], return_inverse=True)
    native_faces = inverse.reshape(-1, 3)
    if len(skin_ids) != 11460 or len(native_faces) != 22636:
        raise ValueError("unexpected native exterior contract")
    affected = donor["support_mask"].copy()
    edges = np.unique(np.sort(np.concatenate([model["triangles"][parent_ids][:, [0, 1]],
                                               model["triangles"][parent_ids][:, [1, 2]],
                                               model["triangles"][parent_ids][:, [2, 0]]]), axis=1), axis=0)
    for _ in range(5):
        affected[edges[np.any(affected[edges], axis=1)].ravel()] = True
    common = np.intersect1d(parent_ids, donor["source_face_ids"])
    safe = common[~np.any(affected[model["triangles"][common]], axis=1)]
    if len(safe) < 100:
        raise ValueError("insufficient unaffected material charts")
    protected = safe[np.linspace(0, len(safe)-1, min(1000, len(safe)), dtype=int)]
    old_lookup = {int(fid): i for i, fid in enumerate(donor["source_face_ids"])}
    old_faces = np.array([old_lookup[int(fid)] for fid in protected])
    native_lookup = {int(fid): i for i, fid in enumerate(parent_ids)}
    new_faces = np.array([native_lookup[int(fid)] for fid in protected])
    if not np.array_equal(donor["original_face_vertex_ids"][old_faces], model["triangles"][protected]):
        raise ValueError("unaffected source face orientation/order changed")
    weights = np.tile([.2, .3, .5], (len(protected), 1))
    old_cage = data["cage"]+np.einsum("vck,k->vc", data["cage_basis"], beta)
    old_body, old_tri, old_ids, old_w = refine_triangle_attachments(
        old_cage, data["cage_faces"], np.r_[data["source_faces"], old_faces], np.r_[data["source_weights"], weights])
    eyes = data["eyes"]+np.einsum("vck,k->vc", data["eye_basis"], beta)
    old_mesh, old_triangles = posed(np.vstack([old_body, eyes])), np.vstack([old_tri, data["eye_faces"]+len(old_body)])
    replay_error = float(np.max(np.abs(old_mesh-fitted["vertices"])))
    if replay_error > 1e-12 or not np.array_equal(old_triangles, fitted["faces"]):
        raise ValueError("original full exported baseline does not replay exactly")
    print("Original baseline full-surface replay passed", replay_error, flush=True)
    mean_cage = native[skin_ids] @ linear+offset
    shaped_cage = shaped[skin_ids] @ linear+offset
    mean_body, mean_tri, _, _ = refine_triangle_attachments(mean_cage, native_faces, new_faces, weights)
    new_body, new_tri, new_ids, new_w = refine_triangle_attachments(shaped_cage, native_faces, new_faces, weights)
    if not np.array_equal(mean_tri, new_tri):
        raise ValueError("native identity changed topology")
    old_points = posed(np.einsum("ni,nij->nj", old_w[32:], old_body[old_ids[32:]]))
    new_points = posed(np.einsum("ni,nij->nj", new_w, new_body[new_ids]))
    protected_error = float(np.linalg.norm(old_points-new_points, axis=1).max())
    candidate = posed(np.vstack([new_body, eyes]))
    candidate_faces = np.vstack([new_tri, data["eye_faces"]+len(new_body)])
    OUT.mkdir()
    write_obj(OUT / "candidate.obj", candidate, candidate_faces, precision=17)
    actual = np.array([[float(a) for a in line.split()[1:4]]
                       for line in (OUT / "candidate.obj").read_text().splitlines() if line.startswith("v ")])
    if np.max(np.abs(actual-candidate)) > 1e-14:
        raise ValueError("actual candidate export changed geometry")
    cage_audit = shape_audit(mean_cage, shaped_cage, native_faces, np.exp(parameters[0]))
    surface_audit = shape_audit(mean_body, new_body, new_tri, np.exp(parameters[0]))
    eye_error = float(np.max(np.abs(actual[-len(eyes):]-fitted["vertices"][-len(eyes):])))
    passed = bool(cage_audit["passed"] and surface_audit["passed"] and protected_error <= 1e-10 and eye_error <= 1e-12)
    shutil.copy2(BASELINE / "after.obj", OUT / "baseline.obj")
    np.savez_compressed(OUT / "replay.npz", parameters=parameters, vertices=actual, faces=candidate_faces,
                        native_cage=shaped_cage, native_mean_cage=mean_cage, native_faces=native_faces,
                        protected_source_parent_ids=protected, protected_old=old_points, protected_new=new_points)
    report = {"technical_status": "TECHNICAL_CHECK_PASSED" if passed else "REJECT", "candidate_safe": passed,
              "visual_status": "UNVERIFIED", "photo_likeness": "UNVERIFIED", "defaults_changed": False,
              "primary_variable": "native exterior source construction; identity/pose/cameras/eyes frozen; no optimization",
              "baseline_experiment": "0206, previously visually rejected; not production/default",
              "baseline_replay_max_error": replay_error, "protected_chart_count": len(protected),
              "protected_maximum_error_world": protected_error, "eye_replay_max_error": eye_error,
              "cage_audit": cage_audit, "surface_audit": surface_audit,
              "source_locks": {str(p.relative_to(ROOT)): h for p, h in {**LOCKS, **locks, **scene_locks}.items()},
              "basis_sha256": sha256_file(BASIS), "baseline_obj_sha256": sha256_file(OUT / "baseline.obj"),
              "candidate_obj_sha256": sha256_file(OUT / "candidate.obj"),
              "renderer": "existing subject render_in_fixed_clay_scene.py; original1254px cameras/lights/material/exposure",
              "code_sha256": sha256_file(Path(__file__)), "elapsed_seconds": time.perf_counter()-started,
              "limits": "Frozen-identity source-construction ablation on independent AI design references, "
              "not physical capture truth, a new fit, an expression solution, collision certification or acceptance."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "source_locks"}), flush=True)


if __name__ == "__main__":
    main()
