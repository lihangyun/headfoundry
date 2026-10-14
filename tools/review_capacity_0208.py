"""Contact sheets from actual0208 white meshes, without geometry exaggeration."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from experiment_0208 import OUT, MODEL, DONOR, VIEWS, project


def main():
    report = json.loads((OUT / "report.json").read_text(encoding="utf-8"))
    rendered = json.loads((OUT / "render-report.json").read_text(encoding="utf-8"))
    if len(rendered["renders"]) != 180:
        raise ValueError("all12 cases x3 surfaces x5 views must be rendered")
    cameras = np.load(OUT / "cameras.npz", allow_pickle=False)["extrinsics"]
    model, donor = (np.load(p, allow_pickle=False) for p in (MODEL, DONOR))
    group = dict(zip(model["vertex_group_names"].tolist(), model["vertex_groups"]))
    roi = np.logical_or.reduce([group[n] > .25 for n in
                              ("nose_region", "upper_lip_region", "lower_lip_region", "chin_region")])
    roi = roi[donor["original_vertex_ids"]]
    versions = ("truth", "prior", "candidate")
    tile = 192
    side_overview = Image.new("RGB", (6*tile, 12*(tile+24)+48), "#161616")
    oblique_overview = Image.new("RGB", (9*tile, 12*(tile+24)+48), "#161616")
    for panel in (side_overview, oblique_overview):
        ImageDraw.Draw(panel).text((8, 8), "Synthetic oracle only | TRUTH / 30-D PRIOR / LOCAL CANDIDATE (repeated per view)", fill="white")
    for record in report["results"]:
        index = record["case"]
        folder = OUT / f"case-{index:02d}"
        base = np.load(folder / "replay.npz", allow_pickle=False)["base"]
        full = Image.new("RGB", (3*384, 5*(384+24)+48), "#161616")
        crop_panel = Image.new("RGB", (3*320, 5*(320+24)+48), "#161616")
        for panel in (full, crop_panel):
            ImageDraw.Draw(panel).text((8, 8), f"SYNTHETIC ORACLE case {index:02d} | TRUTH / PRIOR / CANDIDATE | fixed geometry scale", fill="white")
        for row, name in enumerate(VIEWS):
            points = project(base[roi], cameras[row])
            low, high = points.min(0), points.max(0)
            center = (low+high)/2
            extent = float(np.max(high-low))+24
            box = tuple(np.r_[center-extent/2, center+extent/2].round().astype(int))
            for column, version in enumerate(versions):
                image = Image.open(folder / "clay" / f"{version}-{name}.png").convert("RGB")
                for panel, size, patch in ((full, 384, image),
                                            (crop_panel, 320, image.crop(box))):
                    x, y = column*size, 48+row*(size+24)
                    ImageDraw.Draw(panel).text((x+6, y), f"{name} | {version}", fill="white")
                    panel.paste(patch.resize((size, size)), (x, y+24))
                crop = image.crop(box).resize((tile, tile))
                if name in ("left90", "right90"):
                    position = ((0 if name == "left90" else 1)*3+column)*tile
                    side_overview.paste(crop, (position, 48+index*(tile+24)+24))
                else:
                    position = (("front", "left30", "right30").index(name)*3+column)*tile
                    oblique_overview.paste(crop, (position, 48+index*(tile+24)+24))
        for panel in (side_overview, oblique_overview):
            ImageDraw.Draw(panel).text((6, 48+index*(tile+24)), f"case {index:02d}; no shape exaggeration", fill="white")
        full.save(folder / "five-view-comparison.png")
        crop_panel.save(folder / "nose-lip-chin-comparison.png")
        profiles = Image.new("RGB", (960, 48+2*344), "#161616")
        profiles.paste(crop_panel.crop((0, 0, 960, 48)))
        for row, source_row in enumerate((2, 4)):
            y = 48+source_row*344
            profiles.paste(crop_panel.crop((0, y, 960, y+344)), (0, 48+row*344))
        profiles.save(folder / "profiles-comparison.png")
    side_overview.save(OUT / "all-profiles.png")
    oblique_overview.save(OUT / "all-front-obliques.png")


if __name__ == "__main__":
    main()
