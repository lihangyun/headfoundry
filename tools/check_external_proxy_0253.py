"""Bounded cap-only F / untouched-face consistency screen;not head inference."""
import argparse
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
from headfoundry.manifest import sha256_file, validate_input_assets


def line_errors(f, a, b):
    a, b = np.c_[a, np.ones(len(a))], np.c_[b, np.ones(len(b))]
    la, lb = b@f, a@f.T
    denominator = np.minimum(np.linalg.norm(la[:, :2], axis=1),
                             np.linalg.norm(lb[:, :2], axis=1))
    return np.abs(np.einsum('ij,ij->i', b, lb))/np.maximum(denominator, 1e-15)


def fit_proxy(a, b):
    if len(a) < 30:
        return None, 0
    cv2.setRNGSeed(253)
    f, mask = cv2.findFundamentalMat(a, b, cv2.FM_RANSAC, 1., .999, 10000)
    if f is None or f.shape != (3, 3) or not np.isfinite(f).all():
        return None, 0
    return f, int(mask.sum())


def self_check():
    rng = np.random.default_rng(253)
    x = rng.uniform([-1, -1, 4], [1, 1, 7], (160, 3))
    k = np.array([[900., 0, 360], [0, 900, 640], [0, 0, 1]])
    r = cv2.Rodrigues(np.array([.08, .23, -.03]))[0]
    t = np.array([.7, .1, .03])
    cross = np.array([[0, -t[2], t[1]], [t[2], 0, -t[0]], [-t[1], t[0], 0]])
    f = np.linalg.inv(k).T@cross@r@np.linalg.inv(k)
    a, b = x@k.T, (x@r.T+t)@k.T
    a, b = a[:, :2]/a[:, 2:], b[:, :2]/b[:, 2:]
    assert np.max(line_errors(f, a, b)) < 1e-9
    shifted = b+np.array([0., 40.])
    lines = cv2.computeCorrespondEpilines(a.reshape(-1, 1, 2), 1, f).reshape(-1, 3)
    d2 = np.abs(np.sum(lines*np.c_[shifted, np.ones(len(a))], axis=1))
    lines = cv2.computeCorrespondEpilines(shifted.reshape(-1, 1, 2), 2, f).reshape(-1, 3)
    d1 = np.abs(np.sum(lines*np.c_[a, np.ones(len(a))], axis=1))
    assert np.allclose(line_errors(f, a, shifted), np.maximum(d1, d2), atol=1e-9)
    fitted, count = fit_proxy(a[:80], b[:80])
    assert count == 80 and np.percentile(line_errors(fitted, a[80:], b[80:]), 95) < .01
    assert np.percentile(line_errors(fitted, a[80:], shifted[80:]), 95) > 3
    return dict(known3d=True, independent_line_replay=True, untouched_face_negative=True)


def features(gray, polygon):
    mask = np.zeros(gray.shape, np.uint8)
    cv2.fillPoly(mask, [np.asarray(polygon, np.int32)], 255)
    margin = cv2.distanceTransform(mask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    keypoints, desc = cv2.SIFT_create(nfeatures=4096).detectAndCompute(gray, mask)
    kept = []
    for i in sorted(range(len(keypoints)), key=lambda i: (-keypoints[i].response,
            keypoints[i].pt, keypoints[i].size, keypoints[i].angle)):
        p = np.array(keypoints[i].pt)
        if margin[int(round(p[1])), int(round(p[0]))] <= max(8., 4.5*keypoints[i].size):
            continue
        if any(np.linalg.norm(p-np.array(keypoints[j].pt)) < 5 for j in kept):
            continue
        kept.append(i)
    return (np.array([keypoints[i].pt for i in kept]).reshape(-1, 2),
            None if desc is None else desc[kept], dict(raw=len(keypoints), kept=len(kept)))


def matches(a, b):
    if a[1] is None or b[1] is None or min(len(a[1]), len(b[1])) < 2:
        return np.empty((0, 2)), np.empty((0, 2))
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    def good(x, y):
        return {m.queryIdx: m.trainIdx for pair in matcher.knnMatch(x, y, k=2)
                if len(pair) == 2 for m, n in [pair] if m.distance < .8*n.distance}
    ab, ba = good(a[1], b[1]), good(b[1], a[1])
    ids = sorted([(i, j) for i, j in ab.items() if ba.get(j) == i],
                 key=lambda ij: tuple(a[0][ij[0]]))
    return (np.array([a[0][i] for i, j in ids]).reshape(-1, 2),
            np.array([b[0][j] for i, j in ids]).reshape(-1, 2))


def run():
    started = time.perf_counter()
    out = ROOT/'assets/private/external-proxy-0253'
    if (out/'report.json').exists():
        raise ValueError('Refuse repeated scoring')
    manifest = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    document = json.loads(manifest.read_text())
    selected = [r for r in document['inputs'] if r['id'] == 'real-case-001-video']
    if (len(selected) != 1 or document['training_allowed'] is not False
            or document['upload_allowed'] is not False
            or validate_input_assets(dict(document, inputs=selected), manifest.parent)):
        raise ValueError('Original local case001 video authorization required')
    inputs = json.loads((out/'input.json').read_text())
    if (sha256_file(manifest) != inputs['manifest_sha256']
            or selected[0]['sha256'] != inputs['source_sha256']):
        raise ValueError('Frozen input changed')
    annotations = json.loads((out/'annotations.json').read_text())
    lock = json.loads((out/'pre-fit-review.json').read_text())
    if lock['annotations_sha256'] != sha256_file(out/'annotations.json') or not lock['reviewed_before_features']:
        raise ValueError('Pre-fit annotation review required')
    cv2.setNumThreads(4)
    checks = self_check()
    images, data, counts = {}, {}, {}
    for entry in inputs['frames']:
        i, p = entry['ordinal'], out/entry['path']
        if sha256_file(p) != entry['sha256']:
            raise ValueError('Frozen PNG changed')
        with Image.open(p) as image:
            rgb = np.array(image.convert('RGB'))
        if hashlib.sha256(rgb.tobytes()).hexdigest() != entry['rgb_sha256']:
            raise ValueError('Sequential RGB identity changed')
        images[i] = rgb
        for region in ('cap', 'face'):
            data[i, region] = features(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), annotations['frames'][str(i)][region])
        counts[str(i)] = {r: data[i, r][2] for r in ('cap', 'face')}
    archive, results = {}, []
    panel = Image.new('RGB', (720, len(annotations['pairs'])*444), (24, 24, 24))
    for slot, (i, j) in enumerate(annotations['pairs']):
        if time.perf_counter()-started > 120:
            raise TimeoutError('Fixed120s budget exceeded')
        ca, cb = matches(data[i, 'cap'], data[j, 'cap'])
        fa, fb = matches(data[i, 'face'], data[j, 'face'])
        train = np.arange(len(ca)) % 2 == 0
        held = ~train
        name = f'{i}-{j}'
        result = dict(pair=[i, j], cap_matches=len(ca), cap_fit=int(train.sum()),
            cap_held=int(held.sum()), face_held=len(fa), status='REJECT')
        for label, a, b in [('cap', ca, cb), ('face', fa, fb)]:
            archive[name+'_'+label+'_a'], archive[name+'_'+label+'_b'] = a, b
        f, inliers = fit_proxy(ca[train], cb[train])
        result['fit_inliers'] = inliers
        if f is not None:
            archive[name+'_F'] = f
            for label, a, b in [('cap', ca[held], cb[held]), ('face', fa, fb)]:
                errors = line_errors(f, a, b)
                archive[name+'_'+label+'_errors'] = errors
                result[label+'_p95'] = float(np.percentile(errors, 95)) if len(errors) else None
                result[label+'_span'] = [np.ptp(p, axis=0).tolist() if len(p) else [0, 0] for p in (a, b)]
            cv2.setRNGSeed(253)
            hom, hm = cv2.findHomography(ca[train], cb[train], cv2.RANSAC, 2., maxIters=10000, confidence=.999)
            result['homography_fraction'] = float(hm.mean()) if hom is not None else None
            enough = inliers >= 30 and held.sum() >= 30 and len(fa) >= 30
            spreads = all(min(s) >= 50 for r in ('cap', 'face') for s in result[r+'_span'])
            if enough and spreads and result['cap_p95'] <= 3 and result['face_p95'] <= 3:
                result['status'] = 'TECHNICAL_CHECK_PASSED'
        else:
            result['reason'] = 'Insufficient cap fit support or unavailable F'
        # Display all direct face matches and cap holdouts,not only F inliers.
        pair_image = Image.new('RGB', (720, 420))
        for column, index in enumerate((i, j)):
            pair_image.paste(Image.fromarray(images[index]).crop((0, 220, 720, 1060)).resize((360, 420)), (column*360, 0))
        draw = ImageDraw.Draw(pair_image)
        for a, b, color in [(ca[held], cb[held], 'cyan'), (fa, fb, 'orange')]:
            for p, q in zip(a, b):
                p, q = (p-np.array([0, 220]))*.5, (q-np.array([0, 220]))*.5+np.array([360, 0])
                draw.line([tuple(p), tuple(q)], fill=color, width=1)
        panel.paste(pair_image, (0, slot*444+24))
        ImageDraw.Draw(panel).text((4, slot*444+3), f'{name} cap held {held.sum()} / untouched face {len(fa)} / {result["status"]}', fill='white')
        results.append(result)
    nonplanar = all(any(r['pair'][0] >= low and r['pair'][1] <= high
        and r.get('homography_fraction', 1) is not None and r.get('homography_fraction', 1) < .8
        for r in results) for low, high in ((0, 120), (240, 420)))
    passed = all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in results) and nonplanar
    np.savez_compressed(out/'observations.npz', **archive)
    panel.save(out/'match-review.jpg', quality=90)
    (out/'executed-protocol.md').write_bytes((ROOT/'docs/experiment-0253-external-motion-proxy.md').read_bytes())
    result = dict(status='TECHNICAL_CHECK_PASSED' if passed else 'REJECT', self_checks=checks,
        elapsed_seconds=time.perf_counter()-started, pairs=results, bilateral_nonplanar_support=nonplanar,
        feature_counts=counts, source_sha256=inputs['source_sha256'],
        producer_sha256=sha256_file(Path(__file__)), annotations_sha256=sha256_file(out/'annotations.json'),
        protocol_sha256=sha256_file(out/'executed-protocol.md'), opencv_version=cv2.__version__,
        opencv_package_init_sha256=sha256_file(Path(cv2.__file__)), case002_read=False, scans_read=False,
        new_head=False, training=False, upload=False, camera_acceptance='UNVERIFIED',
        limits='Development observation prerequisite only;epipolar error is not reprojection/anatomical acceptance. No cap-rigidity proof or production segmentation.')
    (out/'report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    print(json.dumps(self_check())) if args.self_check else run()
