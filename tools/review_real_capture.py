"""Local source-only video/scan sheets; layouts are not fitted camera comparisons."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    output = args.directory.resolve()
    if not output.is_relative_to(ROOT / "assets/private"):
        raise ValueError("Private local intake required")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, output):
        raise ValueError("Input rights/hash validation failed")
    intake = json.loads((output / "report.json").read_text(encoding="utf-8"))
    renders = json.loads((output / "scan-preview/report.json").read_text(encoding="utf-8"))
    if sha256_file(output / "manifest.json") != intake["manifest_sha256"]:
        raise ValueError("Intake manifest changed")
    destination = output / "input-review"
    destination.mkdir()
    choices = {"real-case-001": (1040, 139, 416), "real-case-002": (0, 203, 324)}
    scan_views = (("positive-Z", 180), ("negative-X", 270), ("positive-X", 90))
    records = []
    for case in intake["cases"]:
        case_id = case["id"]
        sheet = Image.new("RGB", (960, 920), (28, 28, 28))
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 10), case_id + " INPUT REVIEW ONLY - no camera alignment", fill="white")
        for column, (frame, (view, rotation)) in enumerate(zip(choices[case_id], scan_views)):
            frame_record = next(r for r in case["video"]["frames"] if r["frame"] == frame)
            photo = output / case_id / frame_record["path"]
            render_record = next(r for r in renders["renders"]
                                 if r["case"] == case_id and r["kind"] == "skin" and r["view"] == view)
            scan = output / "scan-preview" / render_record["image"]
            for path, expected in ((photo, frame_record["sha256"]), (scan, render_record["image_sha256"])):
                if sha256_file(path) != expected:
                    raise ValueError("Preview source changed")
            image = Image.open(photo).convert("RGB")
            image.thumbnail((300, 520))
            sheet.paste(image, (column * 320 + (320 - image.width) // 2, 40))
            draw.text((column * 320 + 10, 568), f"Video frame {frame}", fill="white")
            image = Image.open(scan).convert("RGB").rotate(rotation).resize((300, 300))
            sheet.paste(image, (column * 320 + 10, 600))
            draw.text((column * 320 + 10, 902), f"Scan raw {view}; display roll {rotation}", fill="white")
            records.append({"case": case_id, "column": column, "frame": frame,
                            "video_frame_sha256": frame_record["sha256"],
                            "scan_image_sha256": render_record["image_sha256"],
                            "display_rotation_degrees": rotation})
        sheet.save(destination / (case_id + "-sources.png"))
    report = {"status": "TECHNICAL_CHECK_PASSED", "camera_alignment": "UNVERIFIED",
              "layout": records, "tool_sha256": sha256_file(Path(__file__)),
              "limits": "Photos and scans have different poses/projection/crops. Pixel errors and identity acceptance cannot be inferred from these intake sheets."}
    (destination / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
