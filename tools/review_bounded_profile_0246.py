"""Independent projection/OBJ replay,actual clay overlays and fixed-crop sheets."""
import json
from pathlib import Path
import sys
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from headfoundry.raster import render

INPUT = ROOT/'assets/private/bounded-profile-geometry-0246'
BASE = ROOT/'assets/private/video-only-model-0241'
OBS = ROOT/'assets/private/gradient-profile-observations-0243'
OUT = INPUT/'render-review'
LOCK = ROOT/'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first actual replay/render review')
    started = time.perf_counter()
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    current_path = INPUT/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'
    current = np.load(current_path, allow_pickle=False)
    baseline = np.load(BASE/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    prepared = np.load(INPUT/'prepared.npz', allow_pickle=False)
    report = json.loads((INPUT/'fit/optimization-report.json').read_text(encoding='utf-8'))
    if report['mesh_status'] != 'TECHNICAL_CHECK_PASSED' or report['required_view347_status'] != 'REJECT':
        raise ValueError('Safe experimental output and explicit failed gate required')
    replay_vertices = model.template+np.tensordot(model.shape_directions, current['coefficients'], axes=([2], [0]))
    geometry_error = float(abs(replay_vertices-current['vertices']).max())
    obj = np.array([[float(n) for n in line.split()[1:]] for line in
        (INPUT/'fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.obj').read_text(encoding='ascii').splitlines() if line.startswith('v ')])
    obj_error = float(abs(obj-replay_vertices).max())
    replays = []
    for index, ordinal in enumerate((139, 416, 69)):
        packet = np.load(INPUT/f'fit/final-{ordinal:06d}.npz', allow_pickle=False)
        points = np.einsum('ni,nij->nj', packet['edge_weights'], current['vertices'][packet['edge_vertex_ids']])
        e = packet['extrinsic']
        uv = cv2.projectPoints(points, cv2.Rodrigues(e[:, :3])[0], e[:, 3], current['intrinsic'], None)[0].reshape(-1, 2)
        replays.append(float(abs(uv-np.c_[packet['predicted_x'], prepared['curves'][index, :, 1]]).max()))
    if geometry_error > 1e-12 or obj_error > 1e-10 or max(replays) > 1e-8:
        raise ValueError('Independent coefficient,OBJ or OpenCV perspective envelope replay failed')
    renders = json.loads((INPUT/'scan-evaluation/renders.json').read_text(encoding='utf-8'))['images']
    images, bounds = {}, []
    for item in renders:
        path = INPUT/'scan-evaluation'/item['image']
        if sha256_file(path) != item['sha256']:
            raise ValueError('Frozen actual clay image hash changed')
        image = Image.open(path).convert('RGB')
        y, x = np.where(np.asarray(image).max(2) > 105)
        bounds.append([int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)])
        images[item['variant'], item['view']] = image
    bound = np.array(bounds)
    crop = (max(0, int(bound[:, 0].min())-12), max(0, int(bound[:, 1].min())-12),
        min(720, int(bound[:, 2].max())+12), min(1280, int(bound[:, 3].max())+12))
    OUT.mkdir()
    rows = [('supplied-source', 'SUPPLIED SKIN SCAN'), ('video-baseline-0241', 'VIDEO BASELINE 0241 - NOT ACCEPTED'),
        ('profile-candidate-0246', 'PROFILE CANDIDATE 0246 - NOT ACCEPTED')]
    for label, views in [('front-profiles', ['front', 'yaw-90', 'yaw+90']), ('obliques-back', ['yaw-45', 'yaw+45', 'back'])]:
        sheet = Image.new('RGB', (1440, 1530), 'white')
        draw = ImageDraw.Draw(sheet)
        for row, (variant, title) in enumerate(rows):
            draw.text((8, row*510+8), title+' | same transform/camera/light/scale/crop', fill='black')
            for column, view in enumerate(views):
                image = images[variant, view].crop(crop)
                image.thumbnail((480, 480))
                sheet.paste(image, (column*480+(480-image.width)//2, row*510+30+(480-image.height)//2))
        sheet.save(OUT/f'comparison-{label}.png')
    overlays = Image.new('RGB', (1080, 1320), 'white')
    draw = ImageDraw.Draw(overlays)
    for column, ordinal in enumerate((139, 416, 69)):
        original = np.asarray(Image.open(OBS/f'frame-{ordinal:06d}.png').convert('RGB'))
        for row, (name, vertices) in enumerate([('BASELINE at SAME candidate camera', baseline['vertices']),
                ('CANDIDATE - IMAGE GATE REJECT', current['vertices'])]):
            pixels, depth, _ = render(vertices, model.faces, current['extrinsics'][column], current['intrinsic'],
                (720, 1280), smooth_shading=True)
            blended = original.copy()
            visible = np.isfinite(depth)
            blended[visible] = .5*blended[visible]+.5*pixels[visible]
            image = Image.fromarray(blended)
            image.save(OUT/f'video-{ordinal:06d}-{row}.png')
            draw.text((column*360+3, row*660+5), f'{ordinal}: '+name, fill='black')
            overlays.paste(image.resize((360, 640)), (column*360, row*660+20))
            if time.perf_counter()-started > 60:
                raise TimeoutError('Single actual replay/render budget exhausted')
    overlays.save(OUT/'same-camera-video-overlays.png')
    edges = np.sort(np.concatenate([model.faces[:, [0, 1]], model.faces[:, [1, 2]], model.faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'geometry_replay_max_native': geometry_error, 'obj_replay_max_native': obj_error,
        'independent_opencv_envelope_replay_max_px': max(replays), 'all18_images_common_pixel_crop': crop,
        'boundary_edges': int((counts == 1).sum()), 'over_two_face_edges': int((counts > 2).sum()),
        'candidate_geometry_sha256': sha256_file(current_path), 'producer_sha256': sha256_file(Path(__file__)),
        'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Numerical/render replay only;required347,held69/visibility and complete-head gates remain failed/unverified.'}
    (OUT/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
