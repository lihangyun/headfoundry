"""One fixed fixture screen then authorized exact-video profile measurements."""
import json
import os
from pathlib import Path
import sys
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.manifest import sha256_file, validate_input_assets
from prepare_video_only_0241 import PILOT, video_document, forbid_patient_geometry
from gradient_profile_0243 import gradient_profile, known_boundary_fixture

OUT = ROOT / 'assets/private/gradient-profile-observations-0243'
FRAMES = (0, 69, 139, 208, 277, 347, 416, 485, 555, 624, 693, 763, 832, 901, 971, 1040)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first gradient profile observations')
    attempts = []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                forbid_patient_geometry(os.fsdecode(args[0]))
            except PermissionError:
                attempts.append(os.fsdecode(args[0]))
                raise

    sys.addaudithook(audit)
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0243-gradient-profile-observations.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    started, fixture = time.perf_counter(), []
    for direction in (1, -1):
        rgb, truth = known_boundary_fixture(direction)
        Image.fromarray(rgb).save(OUT / f'fixture-{direction:+d}.png')
        for sigma in (.75, 1., 1.25):
            curve, strength = gradient_profile(rgb, (0, 0, 190, 213), sigma)
            errors = abs(curve[:, 0]-truth[:, 0])
            item = {'direction': direction, 'sigma': sigma, 'count': len(errors),
                'p95_px': float(np.percentile(errors, 95)), 'maximum_px': float(errors.max())}
            fixture.append(item)
            np.savez_compressed(OUT / f'fixture-{direction:+d}-sigma{sigma}.npz', truth=truth,
                curve=curve, strength=strength, errors_px=errors)
    fixture_passed = all(r['p95_px'] <= 1 and r['maximum_px'] <= 2 for r in fixture)
    (OUT / 'fixture-report.json').write_text(json.dumps({'status': 'TECHNICAL_CHECK_PASSED' if fixture_passed else 'REJECT',
        'results': fixture, 'elapsed_seconds': time.perf_counter()-started}, indent=2), encoding='utf-8')
    if not fixture_passed or time.perf_counter()-started > 60:
        raise ValueError('Known-pixel fixture failed;video remains unopened')
    started = time.perf_counter()
    doc = video_document(json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8')))
    if validate_input_assets(doc, PILOT):
        raise ValueError('Authorized video-only source/hash required')
    (OUT / 'video-input-manifest.json').write_text(json.dumps(doc, indent=2), encoding='utf-8')
    video = doc['inputs'][0]
    cap, frames = cv2.VideoCapture(str(PILOT / video['path'])), []
    try:
        if not cap.isOpened() or cap.get(cv2.CAP_PROP_ORIENTATION_META) != 0:
            raise ValueError('Original unrotated video required')
        for ordinal in range(max(FRAMES)+1):
            ok, bgr = cap.read()
            if not ok:
                raise ValueError('Missing exact source-video ordinal')
            if ordinal in FRAMES:
                if bgr.shape != (1280, 720, 3):
                    raise ValueError('Original video image size changed')
                path = OUT / f'frame-{ordinal:06d}.png'
                Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(path)
                frames.append(dict(video, id=f'frame-{ordinal:06d}', path=path.name,
                    sha256=sha256_file(path), source='Exact sequential ordinal of authorized case001 video',
                    frame_ordinal=ordinal))
            if time.perf_counter()-started > 60:
                raise TimeoutError('Single video measurement budget exhausted')
    finally:
        cap.release()
    derived = dict(doc, inputs=frames, source_video_sha256=video['sha256'])
    (OUT / 'frame-manifest.json').write_text(json.dumps(derived, indent=2), encoding='utf-8')
    if validate_input_assets(derived, OUT):
        raise ValueError('Exact decoded frames lost original use restrictions')
    coverage = Image.new('RGB', (720, 1360), 'white')
    draw = ImageDraw.Draw(coverage)
    for index, item in enumerate(frames):
        x, y = (index % 4)*180, (index//4)*340
        draw.text((x+4, y+4), 'ordinal '+str(item['frame_ordinal']), fill='black')
        with Image.open(OUT / item['path']) as im:
            coverage.paste(im.resize((180, 320)), (x, y+20))
    coverage.save(OUT / 'video-coverage-review.png')
    measurements, panels = [], []
    for ordinal, box, direction in [(139, (400, 630, 590, 843), 1), (416, (120, 630, 320, 843), -1)]:
        image = Image.open(OUT / f'frame-{ordinal:06d}.png').convert('RGB')
        item = {'frame_ordinal': ordinal, 'roi_half_open': list(box), 'anterior_direction': direction,
            'image_sha256': sha256_file(OUT / f'frame-{ordinal:06d}.png'), 'scale_failures': []}
        curves = {}
        for sigma in (1., .75, 1.25):
            try:
                curve, strength = gradient_profile(np.asarray(image), box, sigma)
                curves[sigma] = curve
                np.savez_compressed(OUT / f'profile-{ordinal:06d}-sigma{sigma}.npz',
                    curve=curve, selected_strength=strength)
            except ValueError as error:
                item['scale_failures'].append({'sigma': sigma, 'reason': str(error)})
        if len(curves) == 3:
            uncertainty = np.max([abs(curves[s][:, 0]-curves[1.][:, 0]) for s in (.75, 1.25)], axis=0)
            item.update(count=len(uncertainty), uncertainty_p95_px=float(np.percentile(uncertainty, 95)),
                uncertainty_maximum_px=float(uncertainty.max()),
                precision_status='TECHNICAL_CHECK_PASSED' if np.percentile(uncertainty, 95) <= 2 and uncertainty.max() <= 4 else 'REJECT')
            np.savez_compressed(OUT / f'profile-{ordinal:06d}-uncertainty.npz', all_row_shift_px=uncertainty)
        else:
            item['precision_status'] = 'REJECT'
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        for sigma in (.75, 1.25, 1.):
            if sigma in curves:
                draw.line([tuple(p) for p in curves[sigma]], fill=(20, 255, 70) if sigma == 1 else (255, 200, 20), width=1)
        overlay.save(OUT / f'profile-{ordinal:06d}-overlay.png')
        panels.append(overlay.crop((box[0]-15, box[1]-30, box[2]+15, box[3]+30)).resize((440, 600)))
        measurements.append(item)
    sheet = Image.new('RGB', (900, 640), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    for column, (panel, item) in enumerate(zip(panels, measurements)):
        draw.text((column*450+5, 8), f'ordinal{item["frame_ordinal"]}: green=nominal,yellow=scale uncertainty', fill='white')
        sheet.paste(panel, (column*450, 30))
    sheet.save(OUT / 'gradient-profile-review.png')
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED', 'visual_review': 'UNVERIFIED', 'head_acceptance': 'UNVERIFIED',
        'observation_precision_status': 'TECHNICAL_CHECK_PASSED' if all(m['precision_status'] == 'TECHNICAL_CHECK_PASSED' for m in measurements) else 'REJECT',
        'measurements': measurements, 'source_video_sha256': video['sha256'], 'frame_manifest_sha256': sha256_file(OUT / 'frame-manifest.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'algorithm_sha256': sha256_file(ROOT / 'tools/gradient_profile_0243.py'),
        'preregistration_sha256': sha256_file(prereg), 'patient_geometry_read_attempts': attempts,
        'case002_used': False, 'elapsed_seconds': time.perf_counter()-started,
        'limits': 'View-dependent image ridge,not material coordinates,camera calibration or accepted head. A stable internal edge still fails visual review.'}
    if time.perf_counter()-started > 60:
        raise TimeoutError('Single video measurement budget exhausted')
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
