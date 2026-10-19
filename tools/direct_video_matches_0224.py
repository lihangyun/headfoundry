"""Existing pinned local learned matches, unchanged real video/masks/pair graph."""
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
import pycolmap
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extract_xfeat import verify, load_lighterglue
from parallax_initialization_0221 import homography_fraction, select_initial_pair
from real_video_sfm_0219 import finish_report

PILOT = ROOT / "assets/private/real-capture-pilot-v1"
BASE = PILOT / "video-sfm-0219"
UPSTREAM = ROOT / "assets/private/xfeat-upstream"
OUT = PILOT / "direct-matches-0224"


def component_gate(image_ids, pairs):
    image_ids = list(image_ids)
    lookup = {i: row for row, i in enumerate(image_ids)}
    endpoints = np.array([(lookup[a], lookup[b]) for a, b in pairs], int).reshape(-1, 2)
    graph = coo_matrix((np.ones(len(endpoints)), (endpoints[:, 0], endpoints[:, 1])), shape=(len(image_ids), len(image_ids)))
    _, labels = connected_components(graph, directed=False)
    chosen = int(np.argmax(np.bincount(labels)))
    return [i for i, label in zip(image_ids, labels) if label == chosen]


def chronological_adjacent_counts(names, counts):
    order = sorted(names, key=lambda i: int(Path(names[i]).stem.split('-')[-1]))
    return [counts.get(tuple(sorted((a,b))),0) for a,b in zip(order,order[1:])]


def verify_inputs():
    manifest_path = PILOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Input rights/hash failure")
    asset, _ = verify(manifest_path, UPSTREAM)
    base = json.loads((BASE / "controls.json").read_text(encoding="utf-8"))
    if base["manifest_sha256"] != sha256_file(manifest_path):
        raise ValueError("Parent input manifest changed")
    for item in base["frames"]:
        if (sha256_file(BASE / "images" / item["name"]) != item["image_sha256"] or
                sha256_file(BASE / "masks" / (item["name"] + ".png")) != item["mask_sha256"]):
            raise ValueError("Frozen image/mask changed")
    lock = json.loads((ROOT / "examples/pycolmap-runtime-lock.json").read_text(encoding="utf-8"))
    import importlib.metadata as metadata
    distribution = metadata.distribution("pycolmap")
    if pycolmap.__version__ != lock["version"] or any(sha256_file(Path(distribution.locate_file(p))) != h
            for p, h in lock["files"].items()):
        raise ValueError("COLMAP runtime changed")
    return base, asset


def observe():
    if OUT.exists():
        raise FileExistsError("Preserve first descriptor observation run")
    started = time.perf_counter()
    base, asset = verify_inputs()
    import torch
    if torch.__version__ != "2.8.0+cpu":
        raise ValueError("Unreviewed extractor runtime")
    torch.set_num_threads(4)
    torch.manual_seed(219)
    matcher, matcher_lock = load_lighterglue(UPSTREAM)
    sys.path.insert(0, str(UPSTREAM))
    from modules.xfeat import XFeat
    extractor = XFeat(weights=torch.load(UPSTREAM / "weights/xfeat.pt", map_location="cpu", weights_only=True), top_k=4096)
    OUT.mkdir()
    controls = dict(base, tool_sha256=sha256_file(Path(__file__)), observation_mechanism="independent XFeat/LighterGlue direct matches",
        source_database_sha256=sha256_file(BASE / "database.db"), source_controls_sha256=sha256_file(BASE / "controls.json"),
        feature_asset=asset, matcher_asset=matcher_lock, feature_loader_sha256=sha256_file(ROOT / "tools/extract_xfeat.py"),
        scan_geometry_used=False, feature_top_k=4096)
    (OUT / "controls.json").write_text(json.dumps(controls, indent=2), encoding="utf-8")
    with sqlite3.connect((BASE / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as source:
        names = dict(source.execute("SELECT image_id,name FROM images ORDER BY image_id"))
        pairs = [(p // 2147483647, p % 2147483647) for (p,) in source.execute("SELECT pair_id FROM two_view_geometries ORDER BY pair_id")]
        with sqlite3.connect(OUT / "database.db") as target:
            source.backup(target)
    features, rows = {}, []
    with torch.inference_mode():
        for image_id, name in names.items():
            pixels = np.array(Image.open(BASE / "images" / name).convert("RGB"))
            mask = np.asarray(Image.open(BASE / "masks" / (name + ".png"))) > 0
            detected = extractor.detectAndCompute(extractor.parse_input(pixels))[0]
            points = detected["keypoints"].cpu().numpy()
            locations = np.rint(points).astype(int)
            valid = ((locations >= 0) & (locations < [720,1280])).all(axis=1)
            keep = np.zeros(len(points), bool)
            keep[valid] = mask[locations[valid,1], locations[valid,0]]
            select = torch.from_numpy(keep)
            features[image_id] = {k: detected[k][select][None] for k in ("keypoints", "descriptors")}
            features[image_id]["image_size"] = torch.tensor([[720,1280]], dtype=torch.float32)
            saved = {k:v.cpu().numpy() for k,v in detected.items()}
            np.savez_compressed(OUT / f"image-{image_id:03d}-features.npz", **saved, mask_selected=keep)
            rows.append({"image_id":image_id,"name":name,"whole_image_features":len(points),"selected_features":int(keep.sum())})
            print(json.dumps({"stage":"extract","image":image_id,"selected":int(keep.sum())}), flush=True)
            if time.perf_counter() - started > 600:
                raise TimeoutError("Observation budget exhausted during extraction")
        matches, match_rows = {}, []
        for index, (a, b) in enumerate(pairs):
            if min(features[a]["keypoints"].shape[1], features[b]["keypoints"].shape[1]) == 0:
                indices = np.empty((0,2), np.uint32)
            else:
                result = matcher({"image0":features[a], "image1":features[b]})
                indices = result["matches"][0].cpu().numpy().astype(np.uint32)
            matches[a,b] = indices
            match_rows.append({"images":[a,b],"matches":len(indices)})
            if index % 25 == 0:
                print(json.dumps({"stage":"match","pairs_done":index+1,"total":len(pairs)}), flush=True)
            if time.perf_counter() - started > 600:
                raise TimeoutError("Observation budget exhausted during matching")
    with pycolmap.Database.open(OUT / "database.db") as database:
        database.clear_two_view_geometries()
        database.clear_matches()
        database.clear_descriptors()
        database.clear_keypoints()
        for image_id in names:
            database.write_keypoints(image_id, features[image_id]["keypoints"][0].cpu().numpy().astype(np.float32) + .5)
        for (a,b), indices in matches.items():
            database.write_matches(a,b,indices)
    pairs_path = OUT / "pairs.txt"
    pairs_path.write_text("".join(f"{names[a]} {names[b]}\n" for a,b in pairs), encoding="utf-8")
    verification = pycolmap.TwoViewGeometryOptions()
    verification.ransac.max_error, verification.ransac.random_seed = 2.,219
    if json.loads(json.dumps(verification.todict(), default=str)) != base["verification"]:
        raise ValueError("Geometric verification differs from baseline")
    token = pycolmap.CancellationToken()
    timer = threading.Timer(max(.1,600-(time.perf_counter()-started)),token.cancel)
    timer.daemon = True
    timer.start()
    try:
        pycolmap.verify_matches(OUT / "database.db", pairs_path, options=verification, cancellation_token=token)
    finally:
        timer.cancel()
    cv2.setRNGSeed(219)
    counts, candidates = {}, []
    with sqlite3.connect((OUT / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as database:
        for pair, count, data in database.execute("SELECT pair_id,rows,data FROM two_view_geometries ORDER BY pair_id"):
            a,b = pair // 2147483647,pair % 2147483647
            counts[a,b] = count
            if count >= 50:
                indices = np.frombuffer(data,np.uint32).reshape(count,2)
                first = features[a]["keypoints"][0].cpu().numpy()[indices[:,0]] + .5
                second = features[b]["keypoints"][0].cpu().numpy()[indices[:,1]] + .5
                candidates.append({"image_ids":[a,b],"names":[names[a],names[b]],"inliers":count,
                    "homography_fraction":homography_fraction(first,second)})
    covered = component_gate(names, [pair for pair,count in counts.items() if count >= 50])
    frames = [int(Path(names[i]).stem.split('-')[-1]) for i in covered]
    adjacent = chronological_adjacent_counts(names, counts)
    gates = {"adjacent_50_verified_80_percent": bool(np.mean(np.array(adjacent)>=50)>=.8),
        "component_80_percent": len(covered)>=.8*len(names),
        "bilateral_component": any(120<=f<=168 for f in frames) and any(396<=f<=444 for f in frames)}
    selected = None
    if all(gates.values()) and not token.is_cancelled:
        try:
            selected = select_initial_pair(candidates)
        except ValueError:
            gates["nonplanar_initial_pair"] = False
    report = {"status":"TECHNICAL_CHECK_PASSED" if selected is not None else "REJECT", "preflight":gates,
        "feature_counts":rows,"raw_match_counts":match_rows,"verified_pair_counts":[{"images":list(p),"inliers":n} for p,n in counts.items()],
        "largest_component_frames":frames,"adjacent_verified":adjacent,"selected":selected,"all_candidates":candidates,
        "database_sha256":sha256_file(OUT / "database.db"), "elapsed_seconds":time.perf_counter()-started,
        "cancelled":token.is_cancelled,"limits":"Observation connectivity and selected pair are not accepted cameras or anatomical correspondence truth."}
    (OUT / "observation-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if selected is not None:
        sheet = Image.new("RGB",(900,650),(28,28,28))
        a,b = selected["image_ids"]
        with sqlite3.connect((OUT / "database.db").resolve().as_uri() + "?mode=ro", uri=True) as database:
            count,data = database.execute("SELECT rows,data FROM two_view_geometries WHERE pair_id=?",(a*2147483647+b,)).fetchone()
            selected_indices = np.frombuffer(data,np.uint32).reshape(count,2)
        for column,(image_id,name) in enumerate(zip(selected["image_ids"],selected["names"])):
            image = Image.open(BASE / "images" / name).convert("RGB")
            draw = ImageDraw.Draw(image)
            for x,y in features[image_id]["keypoints"][0].cpu().numpy()[selected_indices[:,column]]:
                draw.ellipse((x-2,y-2,x+2,y+2),fill=(255,50,40))
            image.thumbnail((440,620))
            sheet.paste(image,(450*column,25))
            ImageDraw.Draw(sheet).text((450*column+5,5),name,fill="white")
        sheet.save(OUT / "selected-pair-supports.png")
    print(json.dumps({"status":report["status"],"preflight":gates,"selected":selected}),flush=True)


def map_once():
    base,_ = verify_inputs()
    report = json.loads((OUT / "observation-report.json").read_text(encoding="utf-8"))
    if report["status"] != "TECHNICAL_CHECK_PASSED" or sha256_file(OUT / "database.db") != report["database_sha256"]:
        raise ValueError("Unaccepted or changed observations")
    review = json.loads((OUT / "pre-fit-review.json").read_text(encoding="utf-8"))
    if review.get("status") != "TECHNICAL_CHECK_PASSED" or review.get("observation_report_sha256") != sha256_file(OUT / "observation-report.json"):
        raise ValueError("Explicit selected support review required")
    controls = json.loads((OUT / "controls.json").read_text(encoding="utf-8"))
    if controls["tool_sha256"] != sha256_file(Path(__file__)):
        capsule = OUT / "executed-observation-runner.py"
        audit = json.loads((OUT / "chronology-audit.json").read_text(encoding="utf-8"))
        if (sha256_file(capsule) != controls["tool_sha256"] or audit.get("chronological_gate_passed") is not True
                or audit["observation_report_sha256"] != sha256_file(OUT / "observation-report.json")):
            raise ValueError("Changed producer requires exact source and report-only chronological audit")
    if (OUT / "sparse").exists() or (OUT / "report.json").exists():
        raise FileExistsError("Never retry the single mapper")
    mapping = pycolmap.IncrementalPipelineOptions(multiple_models=False,max_num_models=1,num_threads=4,
        random_seed=219,ba_refine_principal_point=False,ba_refine_extra_params=False,max_runtime_seconds=300)
    mapping.mapper.init_min_num_inliers,mapping.mapper.init_max_error = 50,2.
    mapping.mapper.abs_pose_max_error,mapping.mapper.filter_max_reproj_error = 3.,3.
    mapping.mapper.random_seed,mapping.triangulation.random_seed,mapping.mapper.num_threads = 219,219,4
    if json.loads(json.dumps(mapping.todict(),default=str)) != base["mapping"]:
        raise ValueError("Mapping settings differ from established baseline")
    mapping.init_image_id1,mapping.init_image_id2 = report["selected"]["image_ids"]
    (OUT / "mapping-options.json").write_text(json.dumps(mapping.todict(),indent=2,default=str),encoding="utf-8")
    started = time.perf_counter()
    token = pycolmap.CancellationToken()
    timer = threading.Timer(300,token.cancel)
    timer.daemon=True
    timer.start()
    try:
        models = pycolmap.incremental_mapping(OUT / "database.db",BASE / "images",OUT / "sparse",options=mapping,cancellation_token=token)
    finally:
        timer.cancel()
    finish_report(models,[r["frame"] for r in base["frames"]],time.perf_counter()-started,token.is_cancelled,output=OUT)


def audit_chronology():
    destination = OUT / "chronology-audit.json"
    if destination.exists():
        raise FileExistsError("Preserve original chronological audit")
    report_path = OUT / "observation-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if sha256_file(OUT / "database.db") != report["database_sha256"]:
        raise ValueError("Original saved observations changed")
    names = {row["image_id"]:row["name"] for row in report["feature_counts"]}
    counts = {tuple(row["images"]):row["inliers"] for row in report["verified_pair_counts"]}
    adjacent = chronological_adjacent_counts(names,counts)
    audit = {"observation_report_sha256":sha256_file(report_path),"adjacent_verified_chronological":adjacent,
        "chronological_gate_passed":bool(np.mean(np.array(adjacent)>=50)>=.8),
        "original_pass_count":sum(n>=50 for n in report["adjacent_verified"]),
        "chronological_pass_count":sum(n>=50 for n in adjacent),"tool_sha256":sha256_file(Path(__file__)),
        "limits":"Report-only ordering repair; no extraction, association, geometric verification, initial-pair or camera rerun."}
    destination.write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print(json.dumps(audit))


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["observe"]:
            observe()
        elif sys.argv[1:] == ["map"]:
            map_once()
        elif sys.argv[1:] == ["audit-chronology"]:
            audit_chronology()
        else:
            raise ValueError("Explicit observe or map stage required")
    except Exception as error:
        if OUT.exists() and not (OUT / "failure.json").exists():
            (OUT / "failure.json").write_text(json.dumps({"status":"REJECT","error":str(error)},indent=2),encoding="utf-8")
        raise
