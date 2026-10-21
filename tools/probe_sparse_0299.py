"""Bounded real-video sparse observation test. No scan input/camera/head fit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/private/real-sparse-0299'
BASE = ROOT/'assets/private/sparse-runtime-0298'
FRAMES = (0, 60, 120, 240, 300, 360, 420, 600, 690)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def prepare():
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
    from headfoundry.manifest import validate_input_assets
    started = time.monotonic()
    manifest_path = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if sha(manifest_path) != 'a537ed48ee7fd0d4027be4aa5ca90472e7f5c8edd0ec9b4270735747b9081809':
        raise ValueError('authorized manifest differs')
    # Validate only case001 video;case002/scan content is never opened here.
    source = next(row for row in manifest['inputs'] if row['id'] == 'real-case-001-video')
    minimal = {**manifest, 'inputs': [source]}
    errors = validate_input_assets(minimal, manifest_path.parent)
    if errors:
        raise ValueError(str(errors))
    audit = json.loads((ROOT/'assets/private/video-observability-0252/report.json').read_text())
    if sha(source['path']) != audit['source_sha256']:
        raise ValueError('original video identity differs')
    OUT.mkdir(exist_ok=False)
    capture = cv2.VideoCapture(source['path'])
    sheet = Image.new('RGB', (1080, 3*664), (25, 25, 25))
    rows = []
    try:
        for ordinal in range(max(FRAMES)+1):
            ok, bgr = capture.read()
            if not ok:
                raise ValueError('sequential decode failed')
            if ordinal not in FRAMES:
                continue
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            expected = audit['frame_records'][ordinal]['rgb_sha256']
            if rgb.shape != (1280, 720, 3) or hashlib.sha256(rgb.tobytes()).hexdigest() != expected:
                raise ValueError('native RGB/ordinal identity differs')
            image = Image.fromarray(rgb)
            image.save(OUT/f'frame-{ordinal:04}.png')
            slot = FRAMES.index(ordinal)
            x, y = slot%3*360, slot//3*664
            sheet.paste(image.resize((360, 640)), (x, y))
            ImageDraw.Draw(sheet).text((x+4, y+642), str(ordinal), fill='white')
            rows.append({'frame':ordinal, 'rgb_sha256':expected, 'file_sha256':sha(OUT/f'frame-{ordinal:04}.png')})
    finally:
        capture.release()
    sheet.save(OUT/'source-review.jpg', quality=90)
    save('preparation.json', {'status':'TECHNICAL_CHECK_PASSED', 'frames':rows,
         'seconds':time.monotonic()-started, 'video_sha256':audit['source_sha256'],
         'scan_content_read':False, 'case002_content_read':False, 'cv2':cv2.__version__})
    if time.monotonic()-started > 60:
        raise ValueError('source preparation deadline')


def freeze():
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
    regions = json.loads((OUT/'regions.json').read_text())['polygons']
    if set(regions) != {str(frame) for frame in FRAMES}:
        raise ValueError('fixed region population differs')
    matrix = cv2.getRotationMatrix2D((359.5, 639.5), 5, .97)
    matrix[:, 2] += (7.25, -5.5)
    source = np.array(Image.open(OUT/'frame-0240.png').convert('RGB'))
    warped = cv2.warpAffine(source, matrix, (720, 1280), flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    Image.fromarray(warped).save(OUT/'warp-0240.png')
    points = np.asarray(regions['240'], dtype=float)
    target_polygon = np.column_stack((points, np.ones(len(points))))@matrix.T
    save('control-geometry.json', {'matrix':matrix.tolist(), 'target_polygon':target_polygon.tolist(),
                                 'target_rgb_sha256':hashlib.sha256(warped.tobytes()).hexdigest()})
    sheet = Image.open(OUT/'source-review.jpg').copy()
    draw = ImageDraw.Draw(sheet)
    for slot, frame in enumerate(FRAMES):
        polygon = np.asarray(regions[str(frame)], dtype=float)
        if polygon.ndim != 2 or polygon.shape[1] != 2 or not np.isfinite(polygon).all():
            raise ValueError('invalid polygon')
        if (polygon < 0).any() or (polygon >= [720, 1280]).any():
            raise ValueError('source region outside native image')
        display = polygon/2+[slot%3*360, slot//3*664]
        draw.polygon([tuple(point) for point in display], outline=(255, 220, 0), width=2)
    sheet.save(OUT/'frozen-regions.jpg', quality=90)
    paths = ['regions.json', 'control-geometry.json', 'warp-0240.png']+[f'frame-{i:04}.png' for i in FRAMES]
    save('frozen-inputs.json', {p:sha(OUT/p) for p in paths})


def cells(points, polygon):
    import numpy as np
    if not len(points):
        return 0
    polygon = np.asarray(polygon)
    relative = (points-polygon.min(0))/np.maximum(np.ptp(polygon, axis=0), 1)
    indices = np.clip((relative*3).astype(int), 0, 2)
    return len(np.unique(indices[:, 0]+3*indices[:, 1]))


def infer():
    import importlib.metadata
    import socket
    import threading
    import urllib.request
    import numpy as np
    from PIL import Image, ImageDraw
    import dedode_runtime_0298 as runtime
    from check_sparse_runtime_0298 import state_check, blocked, peak_working_set
    torch = runtime.torch
    started = time.monotonic()
    deadline = [started+60]
    done = threading.Event()
    report = {'status':'REJECT', 'physical_identity':'UNVERIFIED', 'camera':'UNVERIFIED'}

    def write():
        save('inference.json', report)

    def phase(name, seconds):
        deadline[0] = time.monotonic()+seconds
        report['phase'] = name
        write()
        print(json.dumps({'phase':name}), flush=True)

    def watch():
        while not done.wait(.25):
            if time.monotonic() > deadline[0]:
                report['failure'] = 'phase deadline exceeded'
                write()
                os._exit(124)

    threading.Thread(target=watch, daemon=True).start()
    models, raw_states = [], []
    try:
        phase('strict-state', 60)
        frozen = json.loads((OUT/'frozen-inputs.json').read_text())
        if sha(OUT/'frozen-inputs.json') != sys.argv[-1] or any(sha(OUT/p) != value for p, value in frozen.items()):
            raise ValueError('pre-inference inputs/regions changed')
        regions = json.loads((OUT/'regions.json').read_text())['polygons']
        geometry = json.loads((OUT/'control-geometry.json').read_text())
        lock = runtime.LOCK
        if any(importlib.metadata.version(w['name']) != w['version'] for w in lock['wheels']):
            raise ValueError('runtime versions differ')
        if any(sha(BASE/'source'/p) != h for p, h in lock['source_files'].items()):
            raise ValueError('core/license source differs')
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        props = torch.cuda.get_device_properties(0)
        torch.cuda.set_per_process_memory_fraction(7*2**30/props.total_memory)
        socket.socket.connect = blocked
        urllib.request.urlopen = blocked
        torch.hub.load_state_dict_from_url = blocked
        factories, _ = runtime.core_modules()
        for asset, factory in zip(lock['checkpoint_assets'], (factories.dedode_detector_L, factories.dedode_descriptor_B)):
            path = BASE/asset['name']
            if sha(path) != asset['sha256'] or path.stat().st_size != asset['bytes']:
                raise ValueError('canonical checkpoint changed')
            raw = torch.load(path, map_location='cpu', weights_only=True)
            model = factory(device=torch.device('cuda:0'), weights=raw).eval().requires_grad_(False)
            for child in model.modules():
                if hasattr(child, 'amp'):
                    child.amp = False
            models.append(model)
            raw_states.append(raw)
        report['state'] = [state_check(m, r) for m, r in zip(models, raw_states)]

        def feature(name, polygon):
            rgb = np.asarray(Image.open(OUT/(name+'.png')).convert('RGB'))
            image = runtime.normalize_rgb(torch.from_numpy(rgb.copy()).permute(2, 0, 1)[None].to('cuda', dtype=torch.float32))
            with torch.inference_mode():
                detected = models[0].detect({'image':image}, num_keypoints=4096)
                desc = models[1].describe_keypoints({'image':image}, detected['keypoints'])['descriptions']
                pixels = runtime.cv_pixels(detected['keypoints'], 1280, 720)[0]
            if pixels.shape != (4096, 2) or desc.shape != (1, 4096, 256) or not torch.isfinite(desc).all():
                raise ValueError('native sparse output invalid')
            points = pixels.cpu().numpy()
            mask = Image.new('L', (720, 1280))
            ImageDraw.Draw(mask).polygon([tuple(p) for p in polygon], fill=255)
            integer = points.round().astype(int)
            if (integer < 0).any() or (integer >= [720, 1280]).any():
                raise ValueError('native key outside input')
            ids = np.flatnonzero(np.asarray(mask)[integer[:, 1], integer[:, 0]] > 0)
            record = dict(points=points[ids], descriptions=desc[0].cpu().numpy()[ids],
                          confidence=detected['confidence'][0].cpu().numpy()[ids], global_ids=ids,
                          all_native_points=points)
            np.savez_compressed(OUT/(name+'-features.npz'), **record)
            return record

        def match(a, b, name):
            if not len(a['points']) or not len(b['points']):
                raise ValueError('empty face feature population')
            with torch.inference_mode():
                probability = runtime.dual_softmax_matcher(torch.from_numpy(a['descriptions']).to('cuda'),
                              torch.from_numpy(b['descriptions']).to('cuda'), 20, True)
                pairs, ambiguous = runtime.match_indices(probability, .1)
                score = probability[tuple(pairs.T)].cpu().numpy()
                ids = pairs[:, 1:].cpu().numpy()
            unique = ((np.bincount(ids[:, 0], minlength=len(a['points']))[ids[:, 0]] == 1) &
                      (np.bincount(ids[:, 1], minlength=len(b['points']))[ids[:, 1]] == 1))
            record = dict(pairs=ids, scores=score, unique=unique)
            np.savez_compressed(OUT/(name+'.npz'), **record)
            return record, {'raw_pairs':len(ids), 'ambiguous_flag':ambiguous,
                            'unique_pairs':int(unique.sum()), 'ambiguous_pairs':int((~unique).sum())}

        phase('known-2d-control', 120)
        torch.cuda.reset_peak_memory_stats()
        source = feature('frame-0240', regions['240'])
        target = feature('warp-0240', geometry['target_polygon'])
        pair, count = match(source, target, 'control-pairs')
        ids = pair['pairs'][pair['unique']]
        a, b = source['points'][ids[:, 0]], target['points'][ids[:, 1]]
        expected = np.column_stack((a, np.ones(len(a))))@np.asarray(geometry['matrix']).T
        errors = np.linalg.norm(expected-b, axis=1)
        np.savez_compressed(OUT/'control-errors.npz', errors_px=errors, expected=expected, observed=b, source=a)
        control = {**count, 'source_face_features':len(source['points']), 'target_face_features':len(target['points']),
                   'source_cells':cells(a, regions['240']), 'target_cells':cells(b, geometry['target_polygon']),
                   'p95_px':float(np.percentile(errors, 95)) if len(errors) else None,
                   'max_px':float(errors.max()) if len(errors) else None,
                   'over_3px':int((errors > 3).sum())}
        report['control'] = control
        write()
        if len(ids) < 32 or min(control['source_cells'], control['target_cells']) < 4 or control['p95_px'] > 3:
            raise ValueError('fixed known-2D localization/support gate failed')
        phase('real-native-features', 120)
        features = {240:source}
        for frame in FRAMES:
            if frame != 240:
                features[frame] = feature(f'frame-{frame:04}', regions[str(frame)])
        report['face_feature_counts'] = {frame:len(features[frame]['points']) for frame in FRAMES}
        phase('real-pairs', 120)
        report['pairs'] = []
        for slot, frame in enumerate(FRAMES):
            for other in FRAMES[slot+1:]:
                _, count = match(features[frame], features[other], f'pair-{frame:04}-{other:04}')
                report['pairs'].append({'frames':[frame, other], **count})
        report['status'] = 'TECHNICAL_CHECK_PASSED'
    except Exception as error:
        report['failure'] = type(error).__name__+':'+str(error)
    finally:
        if len(models) == 2:
            report['state_after'] = [state_check(m, r) for m, r in zip(models, raw_states)]
            report['peak_reserved'] = torch.cuda.max_memory_reserved()
        report['peak_working_set'] = peak_working_set()
        if report.get('peak_reserved', 0) > 7*2**30 or report['peak_working_set'] > 8*2**30:
            report['status'] = 'REJECT'
            report['failure'] = 'fixed resource cap exceeded'
        report['seconds'] = time.monotonic()-started
        done.set()
        write()
        print(json.dumps(report), flush=True)
    return 0 if report['status'] == 'TECHNICAL_CHECK_PASSED' else 1


def analyze():
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
    started = time.monotonic()
    report = {'status':'REJECT', 'camera':'UNVERIFIED', 'physical_identity':'UNVERIFIED'}
    inference = json.loads((OUT/'inference.json').read_text())
    regions = json.loads((OUT/'regions.json').read_text())['polygons']

    def symmetric_error(matrix, a, b):
        a = np.column_stack((a, np.ones(len(a))))
        b = np.column_stack((b, np.ones(len(b))))
        line_b, line_a = a@matrix.T, b@matrix
        denominator_a = np.sum(line_a[:, :2]**2, axis=1)
        denominator_b = np.sum(line_b[:, :2]**2, axis=1)
        if min(denominator_a.min(), denominator_b.min()) <= 1e-20:
            raise ValueError('degenerate epipolar line')
        residual = np.sum(b*line_b, axis=1)
        return np.sqrt(.5*residual**2*(1/denominator_a+1/denominator_b))

    # Independent exact projection witness for distance convention and solver.
    rng = np.random.default_rng(299)
    points = rng.uniform([-1, -1, 4], [1, 1, 7], (80, 3))
    k = np.array([[900., 0, 359.5], [0, 900., 639.5], [0, 0, 1]])
    rotation, _ = cv2.Rodrigues(np.array([.02, .2, -.03]))
    def project(points):
        p = points@k.T
        return p[:, :2]/p[:, 2:]
    aa, bb = project(points), project(points@rotation.T+[.5, .1, .02])
    cv2.setRNGSeed(299)
    ff, _ = cv2.findFundamentalMat(aa[:56], bb[:56], cv2.USAC_MAGSAC, 1.5, .999, 10000)
    control_error = symmetric_error(ff, aa[56:], bb[56:])
    if control_error.max() > .001:
        raise ValueError('exact perspective distance/solver witness failed')
    report['exact_projection_control_max_px'] = float(control_error.max())

    def panel(left, right, a, b, title):
        # Fixed source-only review crop;never used for model or error selection.
        crop = (120, 240, 640, 960)
        sheet = Image.new('RGB', (1040, 748), (25, 25, 25))
        sheet.paste(Image.open(OUT/(left+'.png')).convert('RGB').crop(crop), (0, 28))
        sheet.paste(Image.open(OUT/(right+'.png')).convert('RGB').crop(crop), (520, 28))
        draw = ImageDraw.Draw(sheet)
        draw.text((5, 5), title+' | RAW SPATIAL SAMPLE,NOT A HEAD', fill='white')
        if len(a):
            normalized = (a-a.min(0))/np.maximum(np.ptp(a, axis=0), 1)
            chosen = [0]
            while len(chosen) < min(16, len(a)):
                distance = ((normalized[:, None]-normalized[chosen])**2).sum(2).min(1)
                distance[chosen] = -1
                chosen.append(int(distance.argmax()))
            for slot, index in enumerate(chosen):
                color = (40+slot*59%215, 40+slot*97%215, 40+slot*139%215)
                first = a[index]-[120, 240]+[0, 28]
                second = b[index]-[120, 240]+[520, 28]
                draw.line([tuple(first), tuple(second)], fill=color, width=1)
                for point in (first, second):
                    x, y = point
                    draw.ellipse((x-3, y-3, x+3, y+3), fill=color)
                    draw.text((x+4, y-10), str(slot), fill=color)
        return sheet

    if inference['status'] != 'TECHNICAL_CHECK_PASSED':
        if (OUT/'control-pairs.npz').exists():
            pair = np.load(OUT/'control-pairs.npz')
            ids = pair['pairs'][pair['unique']]
            a = np.load(OUT/'frame-0240-features.npz')['points'][ids[:, 0]]
            b = np.load(OUT/'warp-0240-features.npz')['points'][ids[:, 1]]
            panel('frame-0240', 'warp-0240', a, b, 'KNOWN 2D CONTROL').save(OUT/'control-review.jpg', quality=90)
        report['failure'] = 'inference/control not admitted;actual geometry not run'
        report['seconds'] = time.monotonic()-started
        save('geometry.json', report)
        return 1

    features = {frame:dict(np.load(OUT/f'frame-{frame:04}-features.npz')) for frame in FRAMES}
    rows, adjacency, parent = [], {frame:set() for frame in FRAMES}, {}
    def root(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(a, b):
        parent[root(a)] = root(b)
    for slot, frame in enumerate(FRAMES):
        for other in FRAMES[slot+1:]:
            if time.monotonic()-started > 180:
                raise ValueError('fixed geometry deadline')
            raw = np.load(OUT/f'pair-{frame:04}-{other:04}.npz')
            ids = raw['pairs'][raw['unique']]
            a, b = features[frame]['points'][ids[:, 0]], features[other]['points'][ids[:, 1]]
            global_a, global_b = features[frame]['global_ids'][ids[:, 0]], features[other]['global_ids'][ids[:, 1]]
            train = np.asarray([int.from_bytes(hashlib.sha256(f'{frame}/{x}/{other}/{y}'.encode()).digest()[:8], 'little')%10 < 7
                                for x, y in zip(global_a, global_b)], dtype=bool)
            row = {'frames':[frame, other], 'unique_matches':len(ids), 'train':int(train.sum()),
                   'held':int((~train).sum()), 'source_cells':cells(a, regions[str(frame)]),
                   'target_cells':cells(b, regions[str(other)]), 'eligible':False}
            for x, y in zip(global_a, global_b):
                union(FRAMES.index(frame)*4096+int(x), FRAMES.index(other)*4096+int(y))
            if train.sum() >= 16 and (~train).sum() >= 8:
                cv2.setRNGSeed(299)
                matrix, inliers = cv2.findFundamentalMat(a[train], b[train], cv2.USAC_MAGSAC, 1.5, .999, 10000)
                if matrix is not None and matrix.shape == (3, 3) and np.isfinite(matrix).all():
                    singular = np.linalg.svd(matrix, compute_uv=False)
                    if singular[1] > 0 and singular[2] <= 1e-6*singular[1]:
                        errors = symmetric_error(matrix, a[~train], b[~train])
                        row.update(held_p95_px=float(np.percentile(errors, 95)), held_max_px=float(errors.max()),
                                   train_inliers=int(inliers.sum()), held_over_3px=int((errors > 3).sum()))
                        np.savez_compressed(OUT/f'geometry-{frame:04}-{other:04}.npz', F=matrix,
                                            train=train, held_errors_px=errors, held_pairs=ids[~train], train_inliers=inliers)
                        row['eligible'] = bool(min(row['source_cells'], row['target_cells']) >= 4 and row['held_p95_px'] <= 3)
            if row['eligible']:
                adjacency[frame].add(other)
                adjacency[other].add(frame)
            rows.append(row)
    seen, queue = {FRAMES[0]}, [FRAMES[0]]
    while queue:
        for other in adjacency[queue.pop()]-seen:
            seen.add(other)
            queue.append(other)
    components = {}
    for node in parent:
        components.setdefault(root(node), []).append(node)
    consistent, conflicts = [], []
    for nodes in components.values():
        frames = [node//4096 for node in nodes]
        (consistent if len(set(frames)) == len(frames) else conflicts).append(nodes)
    report.update(pairs=rows, passing_edges=sum(row['eligible'] for row in rows), connected_frames=sorted(seen),
                  raw_components=len(components), conflicting_components=len(conflicts),
                  consistent_track_lengths={str(n):sum(len(c)==n for c in consistent) for n in range(2, 10)},
                  geometry_status='NECESSARY_ONLY_NOT_PHYSICAL_IDENTITY')
    np.savez_compressed(OUT/'track-components.npz', **{f'component_{i}':np.asarray(c) for i, c in enumerate(components.values())})
    reviews = [(0, 60), (240, 300), (300, 360), (600, 690)]
    for slot in range(2):
        sheet = Image.new('RGB', (1040, 1496))
        for position, (a, b) in enumerate(reviews[slot*2:slot*2+2]):
            raw = np.load(OUT/f'pair-{a:04}-{b:04}.npz')
            ids = raw['pairs'][raw['unique']]
            aa, bb = features[a]['points'][ids[:, 0]], features[b]['points'][ids[:, 1]]
            sheet.paste(panel(f'frame-{a:04}', f'frame-{b:04}', aa, bb, f'RAW PAIR {a}/{b}'), (0, position*748))
        sheet.save(OUT/f'raw-pair-review-{slot}.jpg', quality=90)
    report['status'] = 'TECHNICAL_CHECK_PASSED' if len(seen) == len(FRAMES) else 'REJECT'
    if len(seen) != len(FRAMES):
        report['failure'] = 'fixed nine-frame readiness graph disconnected'
    report['seconds'] = time.monotonic()-started
    save('geometry.json', report)
    return 0 if report['status'] == 'TECHNICAL_CHECK_PASSED' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare', 'freeze', 'infer', 'analyze'])
    parser.add_argument('frozen_sha256', nargs='?')
    args = parser.parse_args()
    if args.phase == 'infer':
        return infer()
    if args.phase == 'analyze':
        return analyze()
    if args.phase == 'freeze':
        freeze()
    else:
        prepare()


if __name__ == '__main__':
    raise SystemExit(main())
