"""Actual safe video candidate/neutral clay and estimated-camera overlays."""
import json
from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from headfoundry.raster import render
from prepare_video_only_0241 import OUT as INPUT, FLAME, forbid_patient_geometry
from scan_motion_truth_0230 import look_at_origin

OUT = INPUT / 'render'


def main():
    import os
    sys.addaudithook(lambda event, args: forbid_patient_geometry(os.fsdecode(args[0]))
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)) else None)
    if OUT.exists():
        raise FileExistsError('Preserve first actual video candidate renders')
    started = time.perf_counter()
    fit = INPUT / 'fit'
    report = json.loads((fit / 'optimization-report.json').read_text(encoding='utf-8'))
    if report['mesh_feasibility_status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('Do not render unsafe geometry')
    model = FlameIdentityModel.from_asset_record(json.loads(FLAME.read_text(encoding='utf-8')), FLAME.parent)
    archive_path = fit / 'experimental-VIDEO-ONLY-NOT-ACCEPTED.npz'
    packet = np.load(archive_path, allow_pickle=False)
    if not np.array_equal(model.faces, packet['faces']) or abs(model.neutral_vertices(packet['coefficients']) - packet['vertices']).max() > 1e-12:
        raise ValueError('Video candidate replay failed')
    binding = np.load(INPUT / 'generic-bindings.npz', allow_pickle=False)
    OUT.mkdir()
    images, canonical = [], {}
    for variant, vertices in [('neutral', model.template), ('video-fit-NOT-ACCEPTED', packet['vertices'])]:
        display = (vertices - binding['generic_center']) / binding['generic_radius']
        for name, yaw in [('front', 0), ('yaw-90', -90), ('yaw+90', 90)]:
            angle = np.deg2rad(yaw)
            extrinsic = look_at_origin(4 * np.array([np.sin(angle), 0, np.cos(angle)]))
            pixels, depth, _ = render(display, model.faces, extrinsic, binding['source_intrinsic'],
                (512, 512), smooth_shading=True)
            pixels[~np.isfinite(depth)] = [235, 235, 235]
            path = OUT / f'{variant}-{name}.png'
            Image.fromarray(pixels).save(path)
            canonical[variant, name] = Image.fromarray(pixels)
            images.append({'image': path.name, 'sha256': sha256_file(path), 'variant': variant, 'view': name})
    sheet = Image.new('RGB', (1536, 1080), 'white')
    draw = ImageDraw.Draw(sheet)
    for row, variant in enumerate(('neutral', 'video-fit-NOT-ACCEPTED')):
        draw.text((10, row * 540 + 7), variant + ' | exact same cameras/light/scale | native open boundaries remain', fill='black')
        for column, name in enumerate(('front', 'yaw-90', 'yaw+90')):
            sheet.paste(canonical[variant, name], (column * 512, row * 540 + 28))
    sheet.save(OUT / 'neutral-versus-video-front-profiles.png')
    overlays = []
    for index, view in enumerate(report['final_views']):
        ordinal = view['frame_ordinal']
        pixels, depth, _ = render(packet['vertices'], model.faces, packet['extrinsics'][index],
            packet['intrinsic'], (720, 1280), smooth_shading=True)
        original = Image.open(INPUT / f'frame-{ordinal:06d}.png').convert('RGB')
        blend = np.asarray(original).copy()
        mask = np.isfinite(depth)
        blend[mask] = .5 * blend[mask] + .5 * pixels[mask]
        overlay = Image.fromarray(blend)
        draw = ImageDraw.Draw(overlay)
        draw.rectangle((0, 0, 720, 45), fill='white')
        draw.text((8, 8), f'VIDEO FIT - REJECTED camera gate | frame {ordinal} | validation p95 {view["validation"]["p95_px"]:.2f}px', fill='black')
        path = OUT / f'overlay-{ordinal:06d}.png'
        overlay.save(path)
        overlays.append(overlay)
        images.append({'image': path.name, 'sha256': sha256_file(path), 'frame': ordinal,
            'purpose': 'Actual mesh at estimated video camera,not silhouette or physical-camera acceptance'})
        if time.perf_counter() - started > 60:
            raise TimeoutError('Single actual rendering budget exhausted')
    sheet = Image.new('RGB', (360 * len(overlays), 640), 'white')
    for index, overlay in enumerate(overlays):
        sheet.paste(overlay.resize((360, 640)), (360 * index, 0))
    sheet.save(OUT / 'estimated-camera-overlays.png')
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'head_acceptance': 'UNVERIFIED',
        'camera_gate': 'REJECT', 'geometry_sha256': sha256_file(archive_path),
        'fit_report_sha256': sha256_file(fit / 'optimization-report.json'),
        'producer_sha256': sha256_file(Path(__file__)), 'images': images,
        'elapsed_seconds': time.perf_counter() - started,
        'limits': 'Actual safe mesh,not accepted camera/head; no scan input,geometry smoothing or post-fit shape correction.'}
    (OUT / 'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'images': len(images), 'elapsed_seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
