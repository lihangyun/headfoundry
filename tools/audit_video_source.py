"""Local authorized-video audit,not a camera estimator or reconstruction model."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import time

import cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import sha256_file, validate_input_assets


def box_metadata(stream, length):
    """Bounded ISO-BMFF structural walk;never read media payload or infer K."""
    containers = {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'udta', b'edts', b'dinf', b'meta', b'ilst'}
    inventory, texts, keys, total = [], [], [], 0

    def walk(start, end, prefix, depth):
        nonlocal total
        if depth > 12:
            raise ValueError('Metadata nesting limit exceeded')
        position = start
        while position < end:
            if end-position < 8:
                raise ValueError('Truncated atom header')
            stream.seek(position)
            size, kind = struct.unpack('>I4s', stream.read(8))
            header = 8
            if size == 1:
                if end-position < 16:
                    raise ValueError('Truncated extended atom header')
                size = struct.unpack('>Q', stream.read(8))[0]
                header = 16
            elif size == 0:
                size = end-position
            if size < header or position+size > end:
                raise ValueError('Atom extends outside its declared parent')
            total += 1
            if total > 10000:
                raise ValueError('Metadata atom count limit exceeded')
            label = kind.decode('latin1') if all(c >= 32 for c in kind) else 'index-'+str(int.from_bytes(kind, 'big'))
            name = prefix+'/'+label
            inventory.append(dict(path=name, offset=position, bytes=size))
            payload, stop = position+header, position+size
            if kind in containers or (prefix.endswith('/ilst') and int.from_bytes(kind, 'big') < 10000):
                if kind == b'meta':
                    stream.seek(payload)
                    # ISO full-box flags precede children;old QuickTime may omit them.
                    if stop-payload >= 4 and stream.read(4) == b'\0\0\0\0':
                        payload += 4
                walk(payload, stop, name, depth+1)
            elif kind == b'keys':
                if stop-payload > 65536 or stop-payload < 8:
                    raise ValueError('Unsupported key table size')
                stream.seek(payload)
                data = stream.read(stop-payload)
                count = int.from_bytes(data[4:8], 'big')
                cursor = 8
                if count > 1024:
                    raise ValueError('Key count limit exceeded')
                for _ in range(count):
                    if cursor+8 > len(data):
                        raise ValueError('Truncated key record')
                    size_key = int.from_bytes(data[cursor:cursor+4], 'big')
                    if size_key < 8 or cursor+size_key > len(data):
                        raise ValueError('Invalid key record')
                    keys.append(data[cursor+8:cursor+size_key].decode('utf-8', errors='replace'))
                    cursor += size_key
                if cursor != len(data):
                    raise ValueError('Unexpected key table tail')
            elif kind == b'data' or kind[:1] == b'\xa9' or kind in (b'cprt', b'loci'):
                if stop-payload <= 65536:
                    stream.seek(payload)
                    data = stream.read(stop-payload)
                    if kind == b'data':
                        data = data[8:]  # type/locale,not a camera matrix
                    texts.append(dict(path=name, text=data[:4096].decode('utf-8', errors='replace'),
                        truncated=len(data) > 4096))
            position = stop
    walk(0, length, '', 0)
    candidates = [v for v in keys if any(w in v.lower() for w in
        ('focal', 'lens', 'intrinsic', 'distort', 'camera', 'make', 'model', 'zoom', 'stabili', 'crop'))]
    return dict(atoms=inventory, keys=keys, text_records=texts, camera_key_candidates=candidates,
        calibration_status='UNVERIFIED',
        limits='Only recognized structural/text metadata inspected. Opaque codec/uuid payloads are not decoded. No focal,distortion or physical pose is inferred;tkhd display transforms are not extrinsics.')


def self_check():
    def box(kind, payload):
        return struct.pack('>I4s', 8+len(payload), kind)+payload
    good = box(b'moov', box(b'udta', box(b'\xa9too', b'test encoder')))+box(b'mdat', b'not metadata')
    result = box_metadata(io.BytesIO(good), len(good))
    assert len(result['atoms']) == 4 and result['text_records'][0]['text'] == 'test encoder'
    assert result['calibration_status'] == 'UNVERIFIED'
    for bad in (b'123', struct.pack('>I4s', 7, b'free'), struct.pack('>I4s', 99, b'moov')):
        try:
            box_metadata(io.BytesIO(bad), len(bad))
        except ValueError:
            continue
        raise AssertionError('Malformed atom accepted')
    return dict(structural_fixture=True, malformed_bounds_rejected=True, camera_not_invented=True)


def audit(manifest_path, output, budget=120.):
    started = time.perf_counter()
    if (output.exists() or not output.resolve().is_relative_to((ROOT/'assets/private').resolve())
            or budget <= 0):
        raise ValueError('Fresh private output and positive budget required')
    document = json.loads(manifest_path.read_text(encoding='utf-8'))
    records = [x for x in document['inputs'] if x['id'] == 'real-case-001-video']
    if (len(records) != 1 or document.get('training_allowed') is not False or document.get('upload_allowed') is not False
            or document.get('purpose') != 'local_head_reconstruction_validation'
            or validate_input_assets(dict(document, inputs=records), manifest_path.parent)):
        raise ValueError('Exact case001 local-validation video authorization required')
    source = Path(records[0]['path'])
    with source.open('rb') as stream:
        metadata = box_metadata(stream, source.stat().st_size)
    intake = json.loads((manifest_path.parent/'report.json').read_text(encoding='utf-8'))
    old = next(c['video']['frames'] for c in intake['cases'] if c['id'] == 'real-case-001')
    expected = {}
    for entry in old:
        p = manifest_path.parent/'real-case-001'/entry['path']
        if sha256_file(p) != entry['sha256']:
            raise ValueError('Original intake PNG changed')
        with Image.open(p) as image:
            h = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
        expected.setdefault(h, []).append(dict(labelled_frame=entry['frame'], actual_matches=[]))
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError('Video cannot open')
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    backend = capture.getBackendName()
    if fps <= 0 or count <= 0:
        raise ValueError('Invalid reported frame count/rate')
    output.mkdir(parents=True)
    prereg = ROOT/'docs/audit-0252-video-observability.md'
    (output/'executed-protocol.md').write_bytes(prereg.read_bytes())
    frames, pages, overview = [], [], []
    sheet = None
    try:
        while True:
            if time.perf_counter()-started > budget:
                raise TimeoutError('Sequential input audit budget exceeded')
            ok, bgr = capture.read()
            if not ok:
                break
            ordinal = len(frames)
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            if (w, h) != (720, 1280):
                raise ValueError('Declared case001720x1280 input required')
            digest = hashlib.sha256(rgb.tobytes()).hexdigest()
            if digest in expected:
                for e in expected[digest]:
                    e['actual_matches'].append(ordinal)
            frames.append(dict(ordinal=ordinal, rgb_sha256=digest,
                reported_position_msec=float(capture.get(cv2.CAP_PROP_POS_MSEC))))
            slot = ordinal%128
            if slot == 0:
                sheet = Image.new('RGB', (960, 16*192), (24, 24, 24))
            # Fixed display crop only,no segmentation,pose fit or residual selection.
            thumb = Image.fromarray(rgb).crop((60, 120, 660, 960)).resize((120, 168))
            x, y = slot%8*120, slot//8*192
            sheet.paste(thumb, (x, y))
            ImageDraw.Draw(sheet).text((x+2, y+169), str(ordinal), fill='white')
            if ordinal%30 == 0:
                overview.append((ordinal, thumb.copy()))
            if slot == 127:
                name = f'all-frames-{len(pages):02d}.jpg'
                sheet.save(output/name, quality=88)
                pages.append(dict(path=name, first_ordinal=ordinal-127, last_ordinal=ordinal, sha256=sha256_file(output/name)))
                print(json.dumps(dict(decoded=ordinal+1)), flush=True)
        if sheet is not None and len(frames)%128:
            name = f'all-frames-{len(pages):02d}.jpg'
            sheet.save(output/name, quality=88)
            pages.append(dict(path=name, first_ordinal=len(frames)//128*128, last_ordinal=len(frames)-1, sha256=sha256_file(output/name)))
    finally:
        capture.release()
    if len(frames) < count:
        raise ValueError('Decode terminated before reported frame count')
    panel = Image.new('RGB', (720, ((len(overview)+5)//6)*192+28), (24, 24, 24))
    ImageDraw.Draw(panel).text((4, 5), 'CASE001 VIDEO INPUT AUDIT / EVERY30TH DECODED FRAME / NOT A RECONSTRUCTION', fill='white')
    for index, (ordinal, thumb) in enumerate(overview):
        x, y = index%6*120, index//6*192+28
        panel.paste(thumb, (x, y))
        ImageDraw.Draw(panel).text((x+2, y+169), str(ordinal), fill='white')
    panel.save(output/'overview.jpg', quality=90)
    if sha256_file(source) != records[0]['sha256']:
        raise ValueError('Source video changed during audit')
    result = dict(technical_status='TECHNICAL_CHECK_PASSED', camera_calibration='UNVERIFIED',
        physical_coverage='UNVERIFIED', source_sha256=records[0]['sha256'], manifest_sha256=sha256_file(manifest_path),
        producer_sha256=sha256_file(Path(__file__)), protocol_sha256=sha256_file(prereg), self_checks=self_check(),
        backend=backend, fps_reported=fps, frame_count_reported=count, frame_count_decoded=len(frames),
        width=720, height=1280, source_modified=False, case002_content_read=False,
        scans_read=False, training=False, upload=False, box_metadata=metadata,
        frame_records=frames, all_frame_pages=pages, old_intake_frame_matches=[e for es in expected.values() for e in es],
        display_crop_xyxy=[60, 120, 660, 960], elapsed_seconds=time.perf_counter()-started,
        limits='Sequential decoding audit and human review substrate only. Backend position is not independently verified container PTS. Thumbnails do not calibrate angles,metric scale,focal,distortion or declare head quality.')
    (output/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('frame_records', 'box_metadata', 'all_frame_pages')}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        print(json.dumps(self_check()))
    else:
        audit(args.manifest, args.output)
