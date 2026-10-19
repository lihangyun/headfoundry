"""Locked local scan/video landmark screen; no camera or shape fit."""
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from detect_face_landmarks import extract
from headfoundry.manifest import sha256_file, validate_input_assets

PILOT = ROOT / "assets/private/real-capture-pilot-v1"
OUT = PILOT / "camera-baseline-0217"


def main():
    if OUT.exists():
        raise FileExistsError("Preserve first observation screen")
    manifest_path = PILOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata_path = PILOT / "provenance-confirmation.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    errors = validate_input_assets(manifest, PILOT)
    if errors:
        raise ValueError(errors)
    if metadata["manifest_sha256"] != sha256_file(manifest_path):
        raise ValueError("Metadata confirmation does not bind this intake")
    case_id = "real-case-001"
    confirmation = metadata["cases"][case_id]
    if confirmation["scan_units"] != "millimeter" or confirmation["scan_video_same_stage"] is not True:
        raise ValueError("Missing unit/stage evidence")
    intake = json.loads((PILOT / "report.json").read_text(encoding="utf-8"))
    renders = json.loads((PILOT / "scan-preview/report.json").read_text(encoding="utf-8"))
    if intake["manifest_sha256"] != sha256_file(manifest_path):
        raise ValueError("Intake changed")
    case = next(c for c in intake["cases"] if c["id"] == case_id)
    skin = next(a for a in manifest["inputs"] if a["id"] == case_id + "-skin")
    video = next(a for a in manifest["inputs"] if a["id"] == case_id + "-video")
    render = next(r for r in renders["renders"] if r["case"] == case_id and
                  r["kind"] == "skin" and r["view"] == "positive-Z")
    source_image = PILOT / "scan-preview" / render["image"]
    if render["source_sha256"] != skin["sha256"] or sha256_file(source_image) != render["image_sha256"]:
        raise ValueError("Scan preview provenance changed")
    OUT.mkdir()
    upright = OUT / "scan-frontal.png"
    Image.open(source_image).convert("RGB").rotate(180).save(upright)
    inputs = [dict(skin, id="scan-frontal", path=str(upright), sha256=sha256_file(upright),
                   source="180-degree display rotation of locked source scan render", yaw_degrees=0)]
    for frame in case["video"]["frames"]:
        path = PILOT / case_id / frame["path"]
        inputs.append(dict(video, id=f"frame-{frame['frame']:06d}", path=str(path), sha256=frame["sha256"],
                           source="Locked decoded frame of consented local video", nominal_frame=frame["frame"]))
    derived = {"schema_version": 1, "purpose": manifest["purpose"], "inputs": inputs,
               "parent_manifest_sha256": sha256_file(manifest_path), "upload_allowed": False,
               "training_allowed": False, "scan_display_rotation_degrees": 180}
    derived_path = OUT / "derived-manifest.json"
    derived_path.write_text(json.dumps(derived, indent=2), encoding="utf-8")
    if validate_input_assets(derived, OUT):
        raise ValueError("Derived image validation failed")
    model = ROOT / "assets/private/mediapipe/face_landmarker.task"
    report = extract(derived_path, model)
    selected = [4, 6, 168, 33, 133, 362, 263, 61, 291, 152, 98, 327, 10, 172, 397]
    for record, item in zip(report["records"], inputs):
        if record["id"] != item["id"]:
            raise ValueError("Observation order changed")
        if record["faces_detected"] != 1:
            continue
        image = Image.open(item["path"]).convert("RGB")
        draw = ImageDraw.Draw(image)
        for slot in selected:
            x, y = record["landmarks"][slot][:2]
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 45, 60))
            draw.text((x + 3, y - 4), str(slot), fill=(40, 255, 70))
        image.save(OUT / (item["id"] + "-landmarks.png"))
    report.update(tool_sha256=sha256_file(Path(__file__)),
                  extractor_sha256=sha256_file(ROOT / "tools/detect_face_landmarks.py"),
                  parent_manifest_sha256=sha256_file(manifest_path),
                  confirmation_sha256=sha256_file(metadata_path),
                  source_preview_record=render, model_lock_sha256=sha256_file(ROOT / "examples/mediapipe-face-asset-lock.json"),
                  derived_manifest_sha256=sha256_file(derived_path),
                  limits="Synthetic-clay landmarks and video predictions are provisional image-bound observations. Relative depth is not used. No camera/shape fit or anatomical correspondence acceptance.")
    (OUT / "observations.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"detected_faces": {r["id"]: r["faces_detected"] for r in report["records"]}}))


if __name__ == "__main__":
    main()
