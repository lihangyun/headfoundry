"""Render deterministic front/profile thumbnails from a synthetic identity set."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from headfoundry.raster import render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identities", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--count", type=int, default=12)
    args = parser.parse_args()
    data = np.load(args.identities)
    vertices, faces, base = data["vertices"], data["faces"], data["base_vertices"]
    count = min(args.count, len(vertices))
    chosen = np.linspace(0, len(vertices)-1, count, dtype=int)
    center = (base.max(0) + base.min(0)) / 2
    radius = np.linalg.norm(base-center, axis=1).max()
    size = 220
    sheet = Image.new("RGB", (size*8, size*((count+3)//4)), "#10161b")
    intrinsic = np.asarray([[285, 0, size/2], [0, 285, size/2], [0, 0, 1.]])
    for slot, index in enumerate(chosen):
        mesh = (vertices[index]-center)/radius
        row, column = divmod(slot, 4)
        for offset, angle in enumerate((0, 90)):
            theta = np.deg2rad(angle); c, s = np.cos(theta), np.sin(theta)
            rotation = np.asarray([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            extrinsic = np.column_stack([rotation, [0, 0, 3]])
            rgb = render(mesh, faces, extrinsic, intrinsic, (size, size), smooth_shading=True)[0]
            image = Image.fromarray(rgb)
            ImageDraw.Draw(image).text((6, 6), f"sample {index} / {angle}", fill="white")
            sheet.paste(image, ((column*2+offset)*size, row*size))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)


if __name__ == "__main__":
    main()
