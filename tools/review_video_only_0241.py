"""Independent numerical replay and unchanged-image contact sheets,no refitting."""
import json
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from prepare_video_only_0241 import OUT as INPUT, FLAME
from video_model_0241 import camera


def main():
    destination = INPUT / 'independent-replay.json'
    if destination.exists():
        raise FileExistsError('Preserve original independent replay')
    fit, evaluation = INPUT / 'fit', INPUT / 'scan-evaluation'
    record = json.loads((fit / 'optimization-report.json').read_text(encoding='utf-8'))
    numerical = np.load(fit / 'numerical-result.npz', allow_pickle=False)
    packet = np.load(fit / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.npz', allow_pickle=False)
    binding = np.load(INPUT / 'generic-bindings.npz', allow_pickle=False)
    observations = json.loads((INPUT / 'video-observations.json').read_text(encoding='utf-8'))['records']
    model = FlameIdentityModel.from_asset_record(json.loads(FLAME.read_text(encoding='utf-8')), FLAME.parent)
    reconstructed = model.template + np.tensordot(model.shape_directions, packet['coefficients'], axes=([2], [0]))
    eligible = numerical['eligible_semantic_ids']
    points = np.einsum('ni,nij->nj', binding['barycentric'][eligible],
        reconstructed[model.faces[binding['face_ids'][eligible]]])
    geometry_error = float(abs(reconstructed - packet['vertices']).max())
    all_errors, pose_errors = [], []
    for index, view in enumerate(record['final_views']):
        final = np.load(fit / f'final-{view["frame_ordinal"]:06d}.npz', allow_pickle=False)
        # OpenCV's projection is independent of the hand-written projection/Jac.
        rvec = cv2.Rodrigues(packet['extrinsics'][index, :, :3])[0]
        projected = cv2.projectPoints(points, rvec, packet['extrinsics'][index, :, 3], packet['intrinsic'], None)[0].reshape(-1, 2)
        observed = np.asarray(observations[index]['landmarks'])[eligible, :2]
        errors = np.linalg.norm(projected - observed, axis=1)
        all_errors.append(float(abs(errors - final['final_errors_px']).max()))
        rotation, translation, _ = camera(numerical['state'][300 + 6 * index:306 + 6 * index], numerical['initial_poses'][index])
        pose_errors.append(float(abs(np.c_[rotation, translation] - packet['extrinsics'][index]).max()))
    obj = np.array([[float(n) for n in line.split()[1:]] for line in
        (fit / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.obj').read_text(encoding='ascii').splitlines() if line.startswith('v ')])
    obj_error = float(abs(obj - reconstructed).max())
    maximum_error = max(all_errors)
    if geometry_error > 1e-12 or maximum_error > 1e-8 or obj_error > 1e-10 or max(pose_errors) > 1e-12:
        raise ValueError('Independent coefficient/camera/OBJ/observed-error replay failed')
    renders = json.loads((evaluation / 'renders.json').read_text(encoding='utf-8'))['images']
    for entry in renders:
        if sha256_file(evaluation / entry['image']) != entry['sha256']:
            raise ValueError('Actual frozen-source/candidate render changed')
    rows = [('supplied-source', 'SUPPLIED SKIN SCAN - LOCAL REFERENCE'),
        ('aligned-neutral-prior', 'GENERIC NEUTRAL - SAME EVALUATION TRANSFORM'),
        ('video-fit-NOT-ACCEPTED', 'VIDEO-ONLY FIT - NOT ACCEPTED')]
    for name, views in [('front-profiles', ['front', 'yaw-90', 'yaw+90']),
            ('obliques-back', ['yaw-45', 'yaw+45', 'back'])]:
        sheet = Image.new('RGB', (1080, 2016), 'white')
        draw = ImageDraw.Draw(sheet)
        for row, (variant, label) in enumerate(rows):
            draw.text((8, row * 672 + 8), label + ' | shared camera/light/scale', fill='black')
            for column, view in enumerate(views):
                item = next(r for r in renders if r['variant'] == variant and r['view'] == view)
                with Image.open(evaluation / item['image']) as original:
                    sheet.paste(original.resize((360, 640)), (column * 360, row * 672 + 32))
        sheet.save(evaluation / f'comparison-{name}.png')
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'geometry_max_error_native': geometry_error, 'obj_max_error_native': obj_error,
        'opencv_projection_error_replay_max_px': maximum_error,
        'pose_replay_max_error': max(pose_errors), 'fit_report_sha256': sha256_file(fit / 'optimization-report.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'render_count': len(renders),
        'limits': 'Numerical replay/contact sheet only,not physical correspondence,scan uncertainty or visual acceptance.'}
    destination.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
