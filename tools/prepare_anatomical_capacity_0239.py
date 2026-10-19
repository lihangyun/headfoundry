"""Read-only licensed-prior axis/topology review before the real-scan oracle."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from scan_motion_truth_0230 import look_at_origin

LOCK = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
OUT = ROOT / 'assets/private/real-capture-pilot-v1/anatomical-prior-readiness-0239'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first prior readiness')
    asset = json.loads(LOCK.read_text(encoding='utf-8'))
    model = FlameIdentityModel.from_asset_record(asset, LOCK.parent)
    vertices, faces = model.template, model.faces
    edges, counts = np.unique(np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1), axis=0, return_counts=True)
    OUT.mkdir()
    np.savez_compressed(OUT / 'neutral-prior.npz', vertices=vertices, faces=faces)
    center = (vertices.max(0) + vertices.min(0)) / 2
    radius = np.ptp(vertices, axis=0).max() / 2
    displayed = (vertices - center) / radius
    k = np.array([[700., 0, 256], [0, 700, 256], [0, 0, 1.]])
    sheet = Image.new('RGB', (1536, 1070), (28, 28, 28))
    ImageDraw.Draw(sheet).text((10, 5), 'LICENSED NEUTRAL PRIOR ONLY / RAW +Y UP, +Z FRONT / NOT A SUBJECT RECONSTRUCTION', fill='white')
    records = []
    for index, (name, yaw) in enumerate([('front', 0), ('yaw-45', -45), ('yaw+45', 45), ('yaw-90', -90), ('yaw+90', 90), ('back', 180)]):
        angle = np.deg2rad(yaw)
        e = look_at_origin(4 * np.array([np.sin(angle), 0, np.cos(angle)]))
        rgb, _, _ = render(displayed, faces, e, k, (512, 512), smooth_shading=True)
        path = OUT / (name + '-native-neutral.png')
        Image.fromarray(rgb).save(path)
        x, y = index % 3 * 512, index // 3 * 530 + 20
        sheet.paste(Image.fromarray(rgb), (x, y + 18))
        ImageDraw.Draw(sheet).text((x + 8, y), name, fill='white')
        records.append({'view': name, 'image': path.name, 'sha256': sha256_file(path)})
    sheet.save(OUT / 'native-prior-axis-review.png')
    report = {'status': 'TECHNICAL_CHECK_PASSED', 'axis_review': 'UNVERIFIED',
        'role': 'UNCHANGED_LICENSED_PRIOR_NOT_RECONSTRUCTION', 'asset_lock_sha256': sha256_file(LOCK),
        'neutral_archive_sha256': sha256_file(OUT / 'neutral-prior.npz'), 'asset_attribution': asset['attribution'],
        'producer_sha256': sha256_file(Path(__file__)), 'vertices': len(vertices), 'faces': len(faces),
        'boundary_edges': int((counts == 1).sum()), 'nonmanifold_edges_over2': int((counts > 2).sum()),
        'renders': records, 'limits': 'Generic prior axes/topology only, not subject fit, scan/camera/head acceptance.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
