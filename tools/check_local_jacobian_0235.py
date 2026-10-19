"""One frozen local-Jacobian screen, with no real-data or truth-driven tuning."""
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file
from direct_video_matches_0224 import PILOT, verify_inputs
from check_nonplanar_images_0233 import stats
from check_native_observations_0234 import passes
from local_jacobian_0235 import refine_local_geometry

SOURCE = PILOT / 'scan-pattern-observations-0232'
PARENT = PILOT / 'nonplanar-image-precision-0233'
NATIVE = PILOT / 'native-observation-precision-0234'
OUT = PILOT / 'local-jacobian-precision-0235'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first local-Jacobian screen')
    started = time.perf_counter()
    verify_inputs()
    parent = json.loads((PARENT / 'controls.json').read_text(encoding='utf-8'))
    native = json.loads((NATIVE / 'controls.json').read_text(encoding='utf-8'))
    for path, digest in ((SOURCE / 'known-motion.npz', parent['known_geometry_sha256']),
            (SOURCE / 'generation-report.json', parent['source_generation_sha256']),
            (PARENT / 'simulated-coarse-noise.npz', parent['noise_sha256']),
            (ROOT / 'tools/nonplanar_context_0231.py', parent['context_helper_sha256']),
            (ROOT / 'tools/temporal_video_sfm_0220.py', native['local_refiner_sha256']),
            (PARENT / 'controls.json', native['parent_controls_sha256'])):
        if sha256_file(path) != digest:
            raise ValueError('Frozen input or component changed: ' + str(path))
    known = np.load(SOURCE / 'known-motion.npz', allow_pickle=False)
    noise = np.load(PARENT / 'simulated-coarse-noise.npz', allow_pickle=False)['target_noise']
    generation = json.loads((SOURCE / 'generation-report.json').read_text(encoding='utf-8'))
    images, gray = [], []
    for render in generation['renders']:
        path = SOURCE / render['image']
        if sha256_file(path) != render['image_sha256']:
            raise ValueError('Frozen rendered image changed')
        image = np.array(Image.open(path).convert('RGB'))
        images.append(image)
        gray.append(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))
    for name, digest in native['input_archives'].items():
        if sha256_file(PARENT / (name + '.npz')) != digest:
            raise ValueError('Original population or observations changed')
    cv2.setNumThreads(4)
    OUT.mkdir()
    controls = {'primary_variable': 'independent-context local image Jacobian; no fitted intercept',
        'preregistration_sha256': sha256_file(ROOT / 'docs/experiment-0235-context-local-jacobian.md'),
        'parent_controls_sha256': sha256_file(PARENT / 'controls.json'),
        'native_controls_sha256': sha256_file(NATIVE / 'controls.json'),
        'native_report_sha256': sha256_file(NATIVE / 'report.json'),
        'producer_sha256': sha256_file(Path(__file__)),
        'local_jacobian_sha256': sha256_file(ROOT / 'tools/local_jacobian_0235.py'),
        'failure_codes': {'0': 'eligible', '1': 'context rejected', '2': 'local slope rejected',
            '3': 'source crop outside image', '4': 'target samples outside image',
            '5': 'native image refinement rejected', '6': 'residual outside valid crop'},
        'native_archives': {str(name): sha256_file(NATIVE / (str(name) + '.npz'))
            for name in known['view_names'][1:]}}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    sheet = Image.new('RGB', (900, 1780), (28, 28, 28))
    ImageDraw.Draw(sheet).text((10, 5), 'PATTERNED SUPPLIED SCAN / OBSERVATION TEST ONLY / NOT RECONSTRUCTION', fill='white')
    records = []
    for view, name in enumerate(known['view_names'][1:], start=1):
        saved = np.load(PARENT / (str(name) + '.npz'), allow_pickle=False)
        old = np.load(NATIVE / (str(name) + '.npz'), allow_pickle=False)
        population = saved['context_population']
        result = refine_local_geometry(gray[0], gray[view], known['pixels'][0, population] - .5,
            known['pixels'][view, population] - .5 + noise[view, population],
            saved['source_points'], saved['coarse'])
        if not np.array_equal(result.get('fundamental'), saved['fundamental']):
            raise ValueError('Independent F context changed')
        errors = np.linalg.norm(result['pixels'] - saved['truth'], axis=1)
        keep = result['eligible']
        paired = keep & old['eligible']
        passed = passes(errors, keep)
        record = {'view': str(name), 'status': 'TECHNICAL_CHECK_PASSED' if passed else 'REJECT',
            'measurements': len(keep), 'retention': float(keep.mean()), 'endpoint_error': stats(errors[keep]),
            'native_F_same_ids': stats(old['F_errors'][paired]),
            'local_J_same_ids': stats(errors[paired]),
            'failure_counts': {str(i): int((result['failure_code'] == i).sum()) for i in range(7)},
            'context': result.get('context'), 'refinement_failure': result.get('refinement_failure')}
        records.append(record)
        np.savez_compressed(OUT / (str(name) + '.npz'),
            **{k: v for k, v in result.items() if k not in ('context', 'refinement_failure')},
            errors=errors, paired_native=paired, measurement_ids=saved['measurement_ids'],
            context_ids=known['point_ids'][population])
        for column, (pixels, valid, label) in enumerate(((old['pixels'], old['eligible'], 'F+NATIVE'),
                (result['pixels'], keep, 'LOCAL J+NATIVE'))):
            image = Image.fromarray(images[view])
            draw = ImageDraw.Draw(image)
            for xy, truth in zip(pixels[valid], saved['truth'][valid]):
                x, y = xy
                draw.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(20, 255, 80))
                draw.line([tuple(xy), tuple(truth)], fill=(255, 60, 50))
            x, y = column * 450, (view - 1) * 350 + 40
            sheet.paste(image.crop((100, 490, 620, 850)).resize((450, 315)), (x, y + 20))
            ImageDraw.Draw(sheet).text((x + 5, y), str(name) + ' / ' + label + ' / n=' + str(int(valid.sum())), fill='white')
        print(json.dumps(record), flush=True)
        if time.perf_counter() - started > 180:
            raise TimeoutError('One local-Jacobian screen budget exhausted')
    sheet.save(OUT / 'local-jacobian-review.png')
    all_pass = all(r['status'] == 'TECHNICAL_CHECK_PASSED' for r in records)
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'screen_status': 'TECHNICAL_CHECK_PASSED' if all_pass else 'REJECT',
        'results': records, 'elapsed_seconds': time.perf_counter() - started,
        'next_gate': 'one frozen real observation/camera check' if all_pass else 'patch family frozen; no real transfer',
        'limits': 'Synthetic source-scan observation precision only; no reconstructed head, scan or likeness acceptance.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'screen_status': report['screen_status'], 'next_gate': report['next_gate']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
