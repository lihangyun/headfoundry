"""Local FaceMesh observation extraction for explicitly consented inputs.

Run with the existing MediaPipe environment. Model installation is explicit;
this command never downloads weights or uploads photographs.
"""
import argparse
import hashlib
import json
from pathlib import Path

import mediapipe as mp
import numpy as np
from PIL import Image

MODEL_SHA256 = '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'


def extract(manifest_path, model_path):
    document = json.loads(manifest_path.read_text(encoding='utf-8'))
    purpose = document.get('purpose')
    if purpose != 'local_head_reconstruction_validation':
        raise ValueError('this experimental command only supports local validation')
    if hashlib.sha256(model_path.read_bytes()).hexdigest() != MODEL_SHA256:
        raise ValueError('model hash does not match the reviewed asset')
    inputs = document.get('inputs', [])
    if not inputs:
        raise ValueError('no inputs')
    verified = []
    for item in inputs:
        consent = item.get('consent', {})
        if purpose not in item.get('allowed_uses', []) or consent.get('biometric_processing') is not True:
            raise ValueError('missing local reconstruction consent')
        if not all(item.get(field) for field in ('source', 'license_id', 'retention_until', 'deletion_process')):
            raise ValueError('missing rights provenance')
        if not all(consent.get(field) for field in ('subject_id', 'record_id', 'granted_at')):
            raise ValueError('missing consent provenance')
        path = manifest_path.parent / item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256'].lower():
            raise ValueError('input hash mismatch')
        verified.append((item, path))
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        output_facial_transformation_matrixes=False)
    records = []
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        for item, path in verified:
            with Image.open(path) as source:
                pixels = np.array(source.convert('RGB'))
            result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=pixels))
            record = {'id': item['id'], 'input_sha256': item['sha256'],
                      'status': 'UNVERIFIED', 'faces_detected': len(result.face_landmarks)}
            if len(result.face_landmarks) == 1:
                record['landmarks'] = [[p.x*pixels.shape[1], p.y*pixels.shape[0], p.z*pixels.shape[1]]
                                       for p in result.face_landmarks[0]]
            yaw = item.get('yaw_degrees')
            record['within_declared_yaw_domain'] = isinstance(yaw, (int, float)) and abs(yaw) <= 80
            records.append(record)
    return {'status': 'UNVERIFIED', 'model_url': MODEL_URL, 'model_sha256': MODEL_SHA256,
            'runtime_version': mp.__version__, 'records': records,
            'limitations': 'Predictions are not scan ground truth; depth is relative. '
            'Profile views beyond 80 degrees are outside documented use.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('model', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('choose a new output to preserve previous observations')
    report = extract(args.manifest, args.model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'images': len(report['records'])}))
