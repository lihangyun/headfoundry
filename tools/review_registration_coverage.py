"""Locate discarded observations on unchanged benchmark inputs. No fitting."""
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from experiment_0208 import LOCKS, VIEWS
from experiment_0209 import vertex_normals
from experiment_0210 import area_mass, surface_samples
from experiment_0213 import OUT, SOURCE, read_export


def categories(points, faces, scope, cloud, normals):
    distance, ids = cKDTree(cloud).query(points)
    compatible = scope & (np.einsum("ij,ij->i", vertex_normals(points, faces), normals[ids]) > .25)
    labels = np.full(len(points), 3, int)  # excluded neck scope
    labels[scope] = 1  # incompatible normal
    labels[compatible] = 0  # supported
    labels[compatible & (distance > np.quantile(distance[compatible], .9))] = 2
    return labels, ids


def weighted_quantiles(values, weights):
    order = np.argsort(values)
    return np.interp([.1, .5, .9], np.cumsum(weights[order])/weights.sum(), values[order]).tolist()


def main():
    started = time.perf_counter()
    output = OUT / "coverage-review"
    if output.exists():
        raise FileExistsError("preserve the one coverage audit")
    for path, digest in LOCKS.items():
        if sha256_file(path) != digest:
            raise ValueError("source provenance changed")
    old = json.loads((SOURCE / "report.json").read_text(encoding="utf-8"))
    rendered = json.loads((SOURCE / "render-report.json").read_text(encoding="utf-8"))
    audit = json.loads((OUT / "residual-audit.json").read_text(encoding="utf-8"))
    for name, digest in audit["input_sha256"].items():
        if sha256_file(Path(name)) != digest:
            raise ValueError("frozen diagnostic inputs changed")
    data = np.load(OUT / "case-00/replay.npz", allow_pickle=False)
    base, prior, final, faces, truth, tf = (data[n] for n in ("base", "prior", "candidate", "faces", "truth", "target_faces"))
    for name, mesh, triangles in (("prior", prior, faces), ("truth", truth, tf)):
        if np.max(np.abs(read_export(SOURCE / f"case-00/{name}.obj", triangles)-mesh)) > 1e-15:
            raise ValueError("unchanged input geometry mismatch")
    scope, mass = base[:, 1] < old["neck_y_cutoff_radius"], area_mass(base, faces)
    cloud, normals = surface_samples(truth, tf, 200000, 21000)
    keep = cloud[:, 1] < old["neck_y_cutoff_radius"]
    cloud, normals = cloud[keep], normals[keep]
    labels, _ = categories(prior, faces, scope, cloud, normals)
    final_labels, nearest = categories(final, faces, scope, cloud, normals)
    evaluation, _ = surface_samples(truth, tf, 500000, 31000)
    evaluation = evaluation[evaluation[:, 1] < old["neck_y_cutoff_radius"]]
    squared_error = cKDTree(evaluation).query(final)[0]**2*mass
    target_edges, counts = np.unique(np.sort(np.concatenate([tf[:, [0, 1]], tf[:, [1, 2]], tf[:, [2, 0]]]), axis=1), axis=0, return_counts=True)
    boundary = truth[np.unique(target_edges[counts == 1])]
    if not len(boundary):
        raise ValueError("expected original FLAME Open boundary")
    matched = cloud[nearest]
    boundary_distance = np.minimum(cKDTree(boundary).query(matched)[0], old["neck_y_cutoff_radius"]-matched[:, 1])
    trimmed = final_labels == 2
    active = np.flatnonzero(trimmed)
    edges = np.unique(np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1), axis=0)
    edges = edges[np.all(trimmed[edges], axis=1)]
    remap = np.full(len(prior), -1, int)
    remap[active] = np.arange(len(active))
    graph = sparse.coo_matrix((np.ones(len(edges)), (remap[edges[:, 0]], remap[edges[:, 1]])), shape=(len(active), len(active))).tocsr()
    count, component = connected_components(graph, directed=False)
    components = []
    for index in range(count):
        ids = active[component == index]
        components.append({"vertices": len(ids), "area_share": float(mass[ids].sum()/mass[scope].sum()),
                           "forward_squared_error_share": float(squared_error[ids].sum()/squared_error[scope].sum()),
                           "bounds_xyz_radius": [final[ids].min(0).tolist(), final[ids].max(0).tolist()],
                           "target_boundary_distance_error_weighted_p10_p50_p90": weighted_quantiles(boundary_distance[ids], squared_error[ids])})
    components.sort(key=lambda r: -r["forward_squared_error_share"])
    result = {"technical_status": "TECHNICAL_CHECK_PASSED", "geometry_changed": False, "fit_runs": 0,
              "initial_trimmed_area_share": float(mass[labels == 2].sum()/mass[scope].sum()),
              "final_trimmed_area_share": float(mass[trimmed].sum()/mass[scope].sum()),
              "trimmed_initial_and_final_area_share": float(mass[(labels == 2) & trimmed].sum()/mass[scope].sum()),
              "final_trimmed_error_weighted_target_boundary_distance_p10_p50_p90": weighted_quantiles(boundary_distance[trimmed], squared_error[trimmed]),
              "final_trimmed_components": components,
              "input_sha256": {str(p): sha256_file(p) for p in (OUT / "residual-audit.json", SOURCE / "render-report.json", SOURCE / "cameras.npz")},
              "code_sha256": sha256_file(Path(__file__)),
              "limits": "Input-only coverage diagnostic, never new head quality evidence. Labels are recomputed on the frozen prior; "
                        "flat majority-vertex labels per visible face. Final error attribution is forward vertex quadrature only. "
                        "Boundary distance is Euclidean to original open-boundary vertices or the artificial target cutoff plane; "
                        "it is not a geodesic/anatomical correspondence or collision guarantee."}
    output.mkdir()
    cameras = np.load(SOURCE / "cameras.npz", allow_pickle=False)
    sheet = Image.new("RGB", (1152, 80+5*408), "#181818")
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 6), "UNCHANGED INPUTS ONLY | FLAME Open target / frozen GNM30 / prior observation coverage", fill="white")
    draw.text((8, 25), "Green: target support | Red: distance trimmed | Amber: normal incompatible | Blue: excluded scope", fill="white")
    draw.text((8, 44), "No new head fit. Same geometry/cameras/crops. Labels are not quality or anatomical truth.", fill="white")
    palette = np.array([[35, 180, 85], [240, 165, 35], [235, 45, 55], [45, 105, 220]], float)
    face_labels = np.argmax(np.stack([(labels[faces] == i).sum(1) for i in range(4)], axis=1), axis=1)
    for position, view in enumerate(VIEWS):
        if time.perf_counter()-started > 180:
            raise TimeoutError("input coverage review budget exhausted")
        images = []
        for version in ("truth", "prior"):
            record = next(r for r in rendered["renders"] if r["case"] == 0 and r["version"] == version and r["view"] == view)
            path = SOURCE / f"case-00/clay/{version}-{view}.png"
            if (sha256_file(path) != record["image_sha256"] or sha256_file(SOURCE / f"case-00/{version}.obj") != record["source_sha256"]):
                raise ValueError("source/reference image changed")
            images.append(Image.open(path).convert("RGB"))
        _, _, hit = render(prior, faces, cameras["extrinsics"][position], cameras["intrinsics"][position], (512, 512))
        pixels = np.array(images[1]).astype(float)
        visible = hit >= 0
        pixels[visible] = .25*pixels[visible]+.75*palette[face_labels[hit[visible]]]
        images.append(Image.fromarray(pixels.astype(np.uint8)))
        for column, image in enumerate(images):
            x, y = column*384, 80+position*408
            draw.text((x+6, y), view+" | "+("target", "frozen prior", "prior support labels")[column], fill="white")
            sheet.paste(image.resize((384, 384)), (x, y+24))
    sheet.save(output / "five-view-coverage.png")
    profiles = Image.new("RGB", (1152, 80+2*408), "#181818")
    profiles.paste(sheet.crop((0, 0, 1152, 80)))
    for row, old_row in enumerate((2, 4)):
        profiles.paste(sheet.crop((0, 80+old_row*408, 1152, 80+(old_row+1)*408)), (0, 80+row*408))
    profiles.save(output / "profiles-coverage.png")
    result["elapsed_seconds"] = time.perf_counter()-started
    (output / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
