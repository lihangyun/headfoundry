"""Local source-only anatomical-candidate audit; no tracker, camera or head fit."""
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets

OUT = ROOT/'assets/private/manual-anatomical-0296'
FRAMES = [0, 60, 120, 240, 300, 360, 420, 600, 690]
IDS = ['R_inner_canthus', 'R_outer_canthus', 'L_inner_canthus', 'L_outer_canthus',
       'R_alar_groove', 'L_alar_groove', 'R_nostril_lateral', 'L_nostril_lateral',
       'R_commissure', 'L_commissure', 'subnasale', 'R_brow_medial', 'R_brow_lateral',
       'L_brow_medial', 'L_brow_lateral', 'R_tragal_root', 'L_tragal_root', 'forehead_spot']


def sha(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def refine(gray, seed):
    seed = np.asarray(seed, np.float32)
    if seed.shape != (2,) or not np.isfinite(seed).all():
        raise ValueError('finite native XY seed required')
    h, w = gray.shape
    if not (4 <= seed[0] < w-4 and 4 <= seed[1] < h-4):
        raise ValueError('seed outside native support')
    starts = seed + np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], np.float32)
    result = cv2.cornerSubPix(gray, starts[:, None].copy(), (3, 3), (-1, -1),
                              (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, .001))[:, 0]
    finite = bool(np.isfinite(result).all())
    diameter = float(np.linalg.norm(result[:, None]-result[None], axis=2).max())
    displacement = float(np.linalg.norm(result-seed, axis=1).max())
    in_bounds = bool(((result >= 0) & (result < np.array([w, h]))).all())
    stable = finite and in_bounds and diameter <= 1 and displacement <= 3
    return {'four_results': result.tolist(), 'diameter_px': diameter,
            'max_seed_displacement_px': displacement, 'local_attractor_stable': stable,
            'location': result.mean(axis=0).tolist() if stable else None}


def self_check():
    y, x = np.indices((33, 33))
    checker = (((x >= 16) == (y >= 16))*255).astype(np.uint8)
    result = refine(checker, [16, 16])
    if not result['local_attractor_stable'] or np.max(np.abs(np.array(result['location'])-15.5)) > .01:
        raise ValueError('known subpixel corner indexing failed')
    if refine(np.full((33, 33), 127, np.uint8), [16, 16])['local_attractor_stable']:
        raise ValueError('textureless input falsely stable')
    return {'known_corner': result, 'textureless_rejected': True}


def prepare():
    started = time.monotonic()
    OUT.mkdir(exist_ok=False)
    cv2.setNumThreads(4)
    checks = self_check()
    pilot = ROOT/'assets/private/real-capture-pilot-v1'
    manifest = json.loads((pilot/'manifest.json').read_text(encoding='utf-8'))
    selected = [a for a in manifest['inputs'] if a['id'] == 'real-case-001-video']
    if len(selected) != 1 or validate_input_assets({**manifest, 'inputs': selected}, pilot):
        raise ValueError('selected video rights/hash failed')
    source = Path(selected[0]['path'])
    index_path = ROOT/'assets/private/video-observability-0252/report.json'
    index = json.loads(index_path.read_text())
    if sha(source) != index['source_sha256']:
        raise ValueError('source video changed')
    lookup = {r['ordinal']: r['rgb_sha256'] for r in index['frame_records']}
    cap = cv2.VideoCapture(str(source))
    rows, panels = [], []
    ordinal = 0
    try:
        while ordinal <= max(FRAMES):
            if time.monotonic()-started > 60:
                raise TimeoutError('prepare60s')
            ok, bgr = cap.read()
            if not ok:
                raise ValueError('premature sequential video EOF')
            if ordinal in FRAMES:
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                digest = hashlib.sha256(rgb.tobytes()).hexdigest()
                if rgb.shape != (1280, 720, 3) or digest != lookup[ordinal]:
                    raise ValueError('native sequential RGB identity differs')
                path = OUT/f'frame-{ordinal:06d}.png'
                image = Image.fromarray(rgb)
                image.save(path)
                crop = image.crop((120, 240, 640, 960))
                crop.save(OUT/f'crop-{ordinal:06d}.png')
                panel = Image.new('RGB', (520, 752), 'white')
                panel.paste(crop, (0, 32))
                ImageDraw.Draw(panel).text((4, 6), f'Frame {ordinal}; native crop x120 y240; NOT A HEAD OUTPUT', fill='black')
                panels.append(panel)
                rows.append({'ordinal': ordinal, 'path': path.name, 'rgb_sha256': digest,
                             'png_sha256': sha(path), 'crop_origin': [120, 240]})
            ordinal += 1
    finally:
        cap.release()
    if len(rows) != 9 or sha(source) != index['source_sha256']:
        raise ValueError('incomplete preparation or source changed')
    sheet = Image.new('RGB', (1560, 2256), 'white')
    for i, panel in enumerate(panels):
        sheet.paste(panel, ((i % 3)*520, (i//3)*752))
    sheet.save(OUT/'source-review.png')
    save('input.json', {'source_sha256': index['source_sha256'], 'index_sha256': sha(index_path),
                        'frames': rows, 'candidates': IDS, 'cv2_version': cv2.__version__,
                        'self_check': checks, 'seconds': time.monotonic()-started})
    print(json.dumps({'status': 'TECHNICAL_CHECK_PASSED', 'frames': len(rows),
                      'seconds': time.monotonic()-started, 'cv2_version': cv2.__version__}), flush=True)


def audit():
    started = time.monotonic()
    cv2.setNumThreads(4)
    if (OUT/'audit.json').exists():
        raise ValueError('one numeric audit already exists;no replay')
    inputs = json.loads((OUT/'input.json').read_text())
    annotation_path = OUT/'annotations.json'
    document = json.loads(annotation_path.read_text())
    if document['candidates'] != IDS or [r['ordinal'] for r in document['frames']] != FRAMES:
        raise ValueError('candidate/frame population changed')
    results, sets = [], []
    for image_row, annotation in zip(inputs['frames'], document['frames']):
        path = OUT/image_row['path']
        if sha(path) != image_row['png_sha256'] or len(annotation['values']) != len(IDS):
            raise ValueError('source/annotation shape changed')
        rgb = np.array(Image.open(path).convert('RGB'))
        if hashlib.sha256(rgb.tobytes()).hexdigest() != image_row['rgb_sha256']:
            raise ValueError('decoded native RGB changed')
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        rows, stable = [], set()
        for name, value in zip(IDS, annotation['values']):
            row = {'id': name, 'manual': value}
            if isinstance(value, str):
                if value not in ('O', 'U', 'X'):
                    raise ValueError('unknown missing status')
            else:
                row.update(refine(gray, value))
                if row['local_attractor_stable']:
                    stable.add(name)
            rows.append(row)
        points = [r['location'] for r in rows if r.get('local_attractor_stable')]
        spread = np.ptp(points, axis=0).tolist() if points else None
        results.append({'ordinal': annotation['ordinal'], 'rows': rows,
                        'stable_count': len(stable), 'stable_spread_xy_px': spread})
        sets.append(stable)
    edges = [{'a': FRAMES[i], 'b': FRAMES[j], 'common': len(sets[i] & sets[j])}
             for i in range(9) for j in range(i+1, 9)]
    connected = {FRAMES[0]}
    for _ in FRAMES:
        for e in edges:
            if e['common'] >= 8 and (e['a'] in connected or e['b'] in connected):
                connected.update((e['a'], e['b']))
    ready = len(connected) == 9 and all(len(s) >= 8 for s in sets)
    result = {'status': 'TECHNICAL_CHECK_PASSED' if ready else 'REJECT',
              'scope': 'local-attractor/count only;not identity or anatomical accuracy',
              'physical_camera_head': 'UNVERIFIED', 'annotation_sha256': sha(annotation_path),
              'frames': results, 'edges': edges, 'connected_frames': sorted(connected),
              'seconds': time.monotonic()-started}
    save('audit.json', result)
    print(json.dumps({k: result[k] for k in ('status', 'scope', 'connected_frames', 'seconds')}))


if __name__ == '__main__':
    {'prepare': prepare, 'audit': audit}[sys.argv[-1]]()
