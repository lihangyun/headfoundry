"""Freeze skin/background profile evidence on the real development video."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label

from headfoundry.manifest import sha256_file, validate_input_assets

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "assets/private/real-capture-pilot-v1"
OUTPUT = PILOT / "profile-observations-0218"


def color_boundary(rgb, box, direction, threshold=0):
    """Subpixel R-B crossing on the largest connected foreground in a fixed ROI.

    This is a local blue-background diagnostic, not general skin segmentation.
    A missing/clipped row rejects the reading rather than inventing an edge.
    """
    rgb = np.asarray(rgb, float)
    if (rgb.ndim != 3 or rgb.shape[2] != 3 or not np.isfinite(rgb).all()
            or direction not in (-1, 1) or not np.isfinite(threshold)):
        raise ValueError("Finite RGB and signed direction required")
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= rgb.shape[1] and 0 <= y0 < y1 <= rgb.shape[0]):
        raise ValueError("ROI outside image")
    score = rgb[:, :, 0] - rgb[:, :, 2]
    regions, count = label(score[y0:y1, x0:x1] > threshold)
    if not count:
        raise ValueError("No foreground in ROI")
    sizes = np.bincount(regions.ravel())
    sizes[0] = 0
    component = regions == np.argmax(sizes)
    curve = []
    for row, y in enumerate(range(y0, y1)):
        choices = np.flatnonzero(component[row]) + x0
        if not len(choices):
            raise ValueError("Missing profile row")
        x = int(choices[-1] if direction == 1 else choices[0])
        outside = x + direction
        if not x0 <= outside < x1:
            raise ValueError("Profile clipped by search window")
        a, b = score[y, x] - threshold, score[y, outside] - threshold
        if a <= 0 or b > 0 or a == b:
            raise ValueError("No foreground/background crossing")
        curve.append([x + .5 + direction * a / (a - b), y + .5])
    return np.array(curve)


def main():
    if OUTPUT.exists():
        raise FileExistsError("Preserve first measurement")
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    if validate_input_assets(manifest, PILOT):
        raise ValueError("Input rights/hash validation failed")
    intake = json.loads((PILOT / "report.json").read_text(encoding="utf-8"))
    if intake["manifest_sha256"] != sha256_file(PILOT / "manifest.json"):
        raise ValueError("Intake manifest changed")
    case = next(c for c in intake["cases"] if c["id"] == "real-case-001")
    OUTPUT.mkdir()
    settings = ((139, (400, 630, 590, 843), 1), (416, (120, 630, 320, 843), -1))
    records, panels = [], []
    for frame, box, direction in settings:
        item = next(r for r in case["video"]["frames"] if r["frame"] == frame)
        path = PILOT / case["id"] / item["path"]
        if sha256_file(path) != item["sha256"]:
            raise ValueError("Decoded source frame changed")
        image = Image.open(path).convert("RGB")
        rgb = np.asarray(image, float)
        curve = color_boundary(rgb, box, direction)
        alternate = [color_boundary(rgb, box, direction, threshold=t) for t in (-4, 4)]
        sensitivity = np.max(np.abs(np.array(alternate)[:, :, 0] - curve[:, 0]), axis=0)
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        draw.line([tuple(point) for point in curve], fill=(20, 255, 70), width=2)
        for line in alternate:
            draw.line([tuple(point) for point in line], fill=(255, 200, 20), width=1)
        overlay.save(OUTPUT / f"frame-{frame:06d}-edge.png")
        crop = (box[0] - 15, box[1] - 30, box[2] + 15, box[3] + 30)
        panels.append(overlay.crop(crop).resize((440, 600)))
        records.append({"frame": frame, "image_sha256": item["sha256"], "roi_half_open": list(box),
                        "direction": direction, "all_rows": curve.tolist(),
                        "threshold_sensitivity_p95_px": float(np.percentile(sensitivity, 95)),
                        "threshold_sensitivity_max_px": float(sensitivity.max()),
                        "sensitivity_gate_passed": bool(np.percentile(sensitivity, 95) <= 2)})
    sheet = Image.new("RGB", (900, 635), (28, 28, 28))
    for column, (panel, record) in enumerate(zip(panels, records)):
        sheet.paste(panel, (column * 450, 30))
        ImageDraw.Draw(sheet).text((column * 450 + 5, 8), f"frame {record['frame']}: green=R-B0 yellow=+/-4", fill="white")
    sheet.save(OUTPUT / "profile-edge-review.png")
    report = {"technical_status": "TECHNICAL_CHECK_PASSED", "visual_status": "UNVERIFIED", "views": records,
              "manifest_sha256": sha256_file(PILOT / "manifest.json"), "tool_sha256": sha256_file(Path(__file__)),
              "limits": "View-dependent skin/background contours, not fixed3D landmarks. Threshold perturbation measures local color stability only. Review before camera fitting. Case002 unused."}
    (OUTPUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps([{key: r[key] for key in ("frame", "threshold_sensitivity_p95_px", "threshold_sensitivity_max_px", "sensitivity_gate_passed")} for r in records]))


if __name__ == "__main__":
    main()
