"""Isolated video observations and generic-prior bindings; no patient geometry."""
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from headfoundry.raster import render, lift_pixels
from scan_motion_truth_0230 import look_at_origin

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
OUT = ROOT / 'assets/private/video-only-model-0241'
FLAME = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
TASK = ROOT / 'assets/private/mediapipe/face_landmarker.task'
TASK_LOCK = ROOT / 'examples/mediapipe-face-asset-lock.json'
FRAMES = (0, 208, 277, 555, 832, 624, 1040)


def forbid_patient_geometry(path, pilot=PILOT):
    path = Path(path).resolve()
    if path.suffix.lower() == '.stl' or (path.is_relative_to(pilot.resolve()) and path != (pilot / 'manifest.json').resolve()):
        raise PermissionError('Video inference must not read patient scan/oracle files')


def video_document(parent):
    if parent.get('purpose') != 'local_head_reconstruction_validation':
        raise ValueError('Only local video validation is authorized')
    videos = [dict(a) for a in parent.get('inputs', []) if a.get('id') == 'real-case-001-video']
    if len(videos) != 1:
        raise ValueError('One explicit case001 video authorization required')
    return {'schema_version': 1, 'purpose': parent['purpose'], 'inputs': videos,
        'upload_allowed': False, 'training_allowed': False, 'patient_geometry_inputs': False}


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first isolated video preparation')
    started = time.perf_counter()
    blocked = []

    def audit(event, args):
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                forbid_patient_geometry(os.fsdecode(args[0]))
            except PermissionError:
                blocked.append(os.fsdecode(args[0]))
                raise

    sys.addaudithook(audit)
    original = json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8'))
    doc = video_document(original)
    if validate_input_assets(doc, PILOT):
        raise ValueError('Video-only consent/source bytes rejected')
    asset = json.loads(FLAME.read_text(encoding='utf-8'))
    model = FlameIdentityModel.from_asset_record(asset, FLAME.parent)
    task = json.loads(TASK_LOCK.read_text(encoding='utf-8'))
    if task['license_id'] != 'Apache-2.0' or sha256_file(TASK) != task['face_landmarker']['sha256']:
        raise ValueError('Exact reviewed offline landmark task required')
    OUT.mkdir()
    os.environ['MPLCONFIGDIR'] = str(OUT / 'cache')
    (OUT / 'video-input-manifest.json').write_text(json.dumps(doc, indent=2), encoding='utf-8')
    (OUT / 'executed-preregistration.md').write_bytes((ROOT / 'docs/experiment-0241-video-only-model-fit.md').read_bytes())
    video = doc['inputs'][0]
    cap = cv2.VideoCapture(str(PILOT / video['path']))
    selected = {}
    try:
        if not cap.isOpened() or cap.get(cv2.CAP_PROP_ORIENTATION_META) != 0:
            raise ValueError('Declared unrotated video decode failed')
        for ordinal in range(max(FRAMES) + 1):
            ok, bgr = cap.read()
            if not ok:
                raise ValueError('Missing exact sequential frame')
            if ordinal in FRAMES:
                if bgr.shape != (1280, 720, 3):
                    raise ValueError('Fixed original video image dimensions changed')
                path = OUT / f'frame-{ordinal:06d}.png'
                Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).save(path)
                selected[ordinal] = dict(video, id=f'frame-{ordinal:06d}', path=path.name,
                    sha256=sha256_file(path), source='Exact sequential RGB decode from consented case001 video',
                    frame_ordinal=ordinal, width_px=720, height_px=1280)
            if time.perf_counter() - started > 60:
                raise TimeoutError('Single preparation budget exhausted')
    finally:
        cap.release()
    derived = dict(doc, inputs=[selected[f] for f in FRAMES], source_video_sha256=video['sha256'])
    derived_path = OUT / 'frame-manifest.json'
    derived_path.write_text(json.dumps(derived, indent=2), encoding='utf-8')
    if validate_input_assets(derived, OUT):
        raise ValueError('Derived video frame provenance failed')
    center = (model.template.max(0) + model.template.min(0)) / 2
    radius = np.ptp(model.template, axis=0).max() / 2
    display = (model.template - center) / radius
    intrinsic = np.array([[700., 0, 256], [0, 700., 256], [0, 0, 1.]])
    extrinsic = look_at_origin([0, 0, 4])
    pixels, _, _ = render(display, model.faces, extrinsic, intrinsic, (512, 512), smooth_shading=True)
    prior_image = OUT / 'generic-neutral-only.png'
    Image.fromarray(pixels).save(prior_image)
    # Generic licensed model image has no real subject. No fabricated consent.
    import mediapipe as mp
    from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections
    from detect_face_landmarks import extract
    if mp.__version__ != '1.0.1':
        raise ValueError('Recorded MediaPipe1.0.1 runtime required')
    options = mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(TASK)),
        output_facial_transformation_matrixes=False)
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        detected = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=pixels))
    if len(detected.face_landmarks) != 1:
        raise ValueError('Generic prior has no unambiguous landmark detection')
    generic = np.array([[p.x * 512, p.y * 512] for p in detected.face_landmarks[0][:468]])
    edges = np.concatenate([model.faces[:, [0, 1]], model.faces[:, [1, 2]]])
    graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(len(model.template), len(model.template)))
    _, components = connected_components(graph, directed=False)
    skin = components[model.faces[:, 0]] == np.bincount(components).argmax()
    face_ids, bary = lift_pixels(display, model.faces, extrinsic, intrinsic, generic, allowed_faces=skin)
    oval = np.unique([[e.start, e.end] for e in FaceLandmarksConnections.FACE_LANDMARKS_FACE_OVAL])
    eligible = (face_ids >= 0) & ~np.isin(np.arange(468), oval)
    if eligible.sum() < 100 or not eligible[[4, 168, 0, 17]].all():
        raise ValueError('Generic nasal/central-mouth or skin-binding coverage failed')
    points = np.full((468, 3), np.nan)
    points[eligible] = np.einsum('ni,nij->nj', bary[eligible], model.template[model.faces[face_ids[eligible]]])
    np.savez_compressed(OUT / 'generic-bindings.npz', semantic_ids=np.arange(468), face_ids=face_ids,
        barycentric=bary, eligible=eligible, points_native=points, source_pixels=generic,
        skin_faces=skin, oval_indices=oval, generic_center=center, generic_radius=radius,
        source_intrinsic=intrinsic, source_extrinsic_normalized=extrinsic)
    marked = Image.fromarray(pixels)
    draw = ImageDraw.Draw(marked)
    for i in np.flatnonzero(eligible):
        x, y = generic[i]
        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(20, 255, 80) if i % 5 else (255, 70, 40))
    for i in (4, 168, 0, 17, 33, 133, 263, 362):
        draw.text(tuple(generic[i] + [3, -5]), str(i), fill=(255, 220, 40))
    marked.save(OUT / 'generic-bindings-review.png')
    observed = extract(derived_path, TASK)
    if any(r['faces_detected'] != 1 for r in observed['records']):
        raise ValueError('A declared video frame has no single face')
    (OUT / 'video-observations.json').write_text(json.dumps(observed, indent=2), encoding='utf-8')
    for record, item in zip(observed['records'], derived['inputs']):
        if record['id'] != item['id']:
            raise ValueError('Video observation ordering changed')
        photo = Image.open(OUT / item['path']).convert('RGB')
        draw = ImageDraw.Draw(photo)
        for i in np.flatnonzero(eligible):
            x, y = record['landmarks'][i][:2]
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(20, 255, 80) if i % 5 else (255, 70, 40))
        photo.save(OUT / (item['id'] + '-observations.png'))
    if time.perf_counter() - started > 60:
        raise TimeoutError('Single preparation/binding budget exhausted')
    controls = {'status': 'TECHNICAL_CHECK_PASSED', 'binding_review': 'UNVERIFIED',
        'role': 'VIDEO_ONLY_OBSERVATIONS_AND_GENERIC_PRIOR_NOT_RECONSTRUCTION',
        'source_video_sha256': video['sha256'], 'frame_manifest_sha256': sha256_file(derived_path),
        'asset_lock_sha256': sha256_file(FLAME), 'task_lock_sha256': sha256_file(TASK_LOCK),
        'task_sha256': sha256_file(TASK), 'runtime_mediapipe': mp.__version__,
        'runtime_opencv': cv2.__version__, 'runtime_numpy': np.__version__,
        'bindings_sha256': sha256_file(OUT / 'generic-bindings.npz'),
        'observations_sha256': sha256_file(OUT / 'video-observations.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'detector_sha256': sha256_file(ROOT / 'tools/detect_face_landmarks.py'),
        'generic_skin_bindings': int(eligible.sum()), 'frames_exact_order': list(FRAMES),
        'fit_frames': list(FRAMES[:5]), 'development_sentinels': list(FRAMES[5:]),
        'patient_geometry_or_oracle_read_attempts': blocked, 'isolation': 'Python open audit guard,not an OS sandbox',
        'initial_identity': 'exact zero', 'elapsed_seconds': time.perf_counter() - started,
        'limits': 'Provisional model-projected semantic observations; no scan input,pose/shape fit or physical camera acceptance.'}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    print(json.dumps(controls), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
