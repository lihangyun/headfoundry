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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare'])
    args = parser.parse_args()
    prepare()


if __name__ == '__main__':
    main()
