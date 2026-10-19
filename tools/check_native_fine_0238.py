"""One frozen native learned-localization screen; no pose/head solve or training."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file
from measure_pixel_precision_0226 import evaluate_pixels
from direct_video_matches_0224 import PILOT, BASE, UPSTREAM, verify_inputs
from native_fine_0238 import refine_native

PARENT = PILOT / 'pixel-precision-0226'
OUT = PILOT / 'native-fine-precision-0238'


def within_mask(points, mask):
    finite = np.isfinite(points).all(axis=1)
    xy = np.rint(np.where(finite[:, None], points, 0)).astype(int)
    inside = finite & ((xy >= 0) & (xy < [mask.shape[1], mask.shape[0]])).all(axis=1)
    result = np.zeros(len(points), bool)
    result[inside] = mask[xy[inside, 1], xy[inside, 0]] > 0
    return result


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first native fine-localization experiment')
    started = time.perf_counter()
    base, asset = verify_inputs()
    parent = json.loads((PARENT / 'controls.json').read_text(encoding='utf-8'))
    if (parent['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or parent['source_controls_sha256'] != sha256_file(BASE / 'controls.json')
            or parent['feature_asset'] != asset or parent['frames'] != [0, 144, 408, 612]
            or list(parent['transforms']) != ['identity', 'translation', 'affine', 'projective']):
        raise ValueError('Frozen parent frames/warps/rights/model identity changed')
    import torch
    if torch.__version__ != '2.8.0+cpu':
        raise ValueError('Reviewed CPU runtime required')
    torch.set_num_threads(4)
    torch.manual_seed(219)
    cv2.setNumThreads(4)
    sys.path.insert(0, str(UPSTREAM))
    from modules.xfeat import XFeat
    extractor = XFeat(weights=torch.load(UPSTREAM / 'weights/xfeat.pt', map_location='cpu', weights_only=True), top_k=4096)
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0238-native-learned-fine-localization.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    controls = {'parent_controls_sha256': sha256_file(PARENT / 'controls.json'), 'feature_asset': asset,
        'producer_sha256': sha256_file(Path(__file__)), 'wrapper_sha256': sha256_file(ROOT / 'tools/native_fine_0238.py'),
        'evaluator_sha256': sha256_file(ROOT / 'tools/measure_pixel_precision_0226.py'),
        'preregistration_sha256': sha256_file(prereg), 'torch_version': torch.__version__,
        'opencv_version': cv2.__version__, 'numpy_version': np.__version__,
        'requested_top_k': 4096, 'native_multiscale_default': True, 'MNN_cosine_threshold': -1,
        'native_fine_confidence': .25, 'native_temperature': 3, 'threads': 4, 'seed': 219,
        'orientation': 'first=transformed target, second=unchanged reference-grid anchors',
        'baseline': 'same raw dense MNN identities', 'transform_truth_used_for_eligibility': False}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')

    def extract(pixels, mask):
        dense = extractor.detectAndComputeDense(extractor.parse_input(pixels))
        ids = np.flatnonzero(within_mask(dense['keypoints'][0].cpu().numpy(), mask))
        select = torch.from_numpy(ids)
        return {key: value[:, select].clone() for key, value in dense.items()}, ids

    def save_features(path, features, ids):
        np.savez_compressed(path, **{key: value.cpu().numpy() for key, value in features.items()}, native_dense_ids=ids)

    records = []
    sheet = Image.new('RGB', (1000, 1440), (28, 28, 28))
    with torch.inference_mode():
        for row, frame in enumerate(parent['frames']):
            entry = next(r for r in base['frames'] if r['frame'] == frame)
            pixels = np.array(Image.open(BASE / 'images' / entry['name']).convert('RGB'))
            mask = np.asarray(Image.open(BASE / 'masks' / (entry['name'] + '.png')))
            reference, reference_ids = extract(pixels, mask)
            save_features(OUT / f'frame-{frame:06d}-reference-features.npz', reference, reference_ids)
            for name, matrix in parent['transforms'].items():
                homography = np.asarray(matrix, float)
                prefix = f'frame-{frame:06d}-{name}'
                old = np.load(PARENT / (prefix + '.npz'), allow_pickle=False)
                if not np.array_equal(old['homography'], homography):
                    raise ValueError('Parent image transform changed')
                target_pixels = cv2.warpPerspective(pixels, homography, (720, 1280), flags=cv2.INTER_LINEAR)
                original_target = np.array(Image.open(PARENT / (prefix + '.png')).convert('RGB'))
                if not np.array_equal(target_pixels, original_target):
                    raise ValueError('Frozen transformed input pixel regeneration failed')
                target_mask = cv2.warpPerspective(mask, homography, (720, 1280), flags=cv2.INTER_NEAREST)
                target, target_ids = extract(target_pixels, target_mask)
                save_features(OUT / (prefix + '-target-features.npz'), target, target_ids)
                result = refine_native(extractor, target, reference)
                eligible = result['native_keep'] & result['identity_keep'] & within_mask(result['refined'], target_mask)
                # No transform is passed to the learned matcher or eligibility.
                score, truth, raw_errors, errors = evaluate_pixels(result['source'], result['raw'],
                    result['refined'], eligible, homography)
                score.update(frame=frame, transform=name, raw_dense_matches=len(eligible),
                    native_confidence_retained=int(result['native_keep'].sum()),
                    unique_coarse_retained=int(result['identity_keep'].sum()),
                    source_features=len(reference_ids), target_features=len(target_ids),
                    source_image_sha256=entry['image_sha256'], source_mask_sha256=entry['mask_sha256'],
                    target_regenerated_exact=True, native_reference_and_feature_arrays_unchanged=True)
                records.append(score)
                source_anchor_ids = reference_ids[result['matches'][:, 1]]
                target_coarse_ids = target_ids[result['matches'][:, 0]]
                np.savez_compressed(OUT / (prefix + '.npz'), **result, eligible=eligible, truth=truth,
                    raw_errors=raw_errors, errors=errors, homography=homography,
                    source_anchor_native_ids=source_anchor_ids, target_coarse_native_ids=target_coarse_ids)
                if name == 'projective':
                    for column, (endpoints, keep, label) in enumerate(((result['raw'], np.ones(len(eligible), bool), 'DENSE COARSE'),
                            (result['refined'], eligible, 'NATIVE LEARNED FINE'))):
                        photo = Image.fromarray(target_pixels)
                        draw = ImageDraw.Draw(photo)
                        for predicted, expected in zip(endpoints[keep], truth[keep]):
                            x, y = predicted
                            draw.line([tuple(predicted), tuple(expected)], fill=(255, 50, 50), width=2)
                            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(20, 255, 80))
                        sheet.paste(photo.crop((100, 490, 620, 850)).resize((500, 335)), (column * 500, row * 360 + 25))
                        stats = score['baseline_all' if column == 0 else 'candidate_eligible']
                        ImageDraw.Draw(sheet).text((column * 500 + 5, row * 360 + 5),
                            f'{frame} {label} n={stats["count"]}; p95={stats["p95_px"]}', fill='white')
                print(json.dumps(score), flush=True)
                if time.perf_counter() - started > 180:
                    raise TimeoutError('Single native-fine experiment budget exhausted')
    sheet.save(OUT / 'native-fine-projective-review.png')
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'screen_status': 'TECHNICAL_CHECK_PASSED' if all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in records) else 'REJECT',
        'results': records, 'elapsed_seconds': time.perf_counter() - started,
        'limits': 'Native learned localization on known2D image warps only. Not raw3D track, real-camera, full-head, scan or likeness acceptance.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'screen_status': report['screen_status'], 'cases': len(records)}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
