"""Offline integrity gate; does not import vendor code or execute a checkpoint."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/private/metric-runtime-0374'
WEIGHT = ROOT / 'assets/private/metric-small-0373/depth_anything_v2_metric_hypersim_vits.pth'
SHA = 'b782898d8a3e8be1f639de33837ed85e9b4b73e40f8f5e5cd99067588d722545'


def verify_bytes(data, size, digest):
    if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('asset size/hash mismatch')


def checked_path(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError('manifest path escapes asset directory')
    return path


def self_check():
    good = hashlib.sha256(b'ok').hexdigest()
    verify_bytes(b'ok', 2, good)
    for data, size in [(b'no', 2), (b'ok', 3)]:
        try:
            verify_bytes(data, size, good)
        except ValueError:
            continue
        raise AssertionError('corrupt asset admitted')
    try:
        checked_path(BASE, '../outside')
    except ValueError:
        return
    raise AssertionError('escaping path admitted')


def main():
    self_check()
    source = BASE / 'source'
    manifest = json.loads((source / 'manifest.json').read_text())
    if manifest['commit'] != 'a561b849ebae10a6f5ef49e26c83cbbcd36c71bf':
        raise ValueError('unexpected source revision')
    for name, entry in manifest['files'].items():
        verify_bytes(checked_path(source, name).read_bytes(), entry['bytes'], entry['sha256'])
    verify_bytes(WEIGHT.read_bytes(), 99222290, SHA)
    # Read archive CRCs only: no pickle evaluation or model construction.
    with zipfile.ZipFile(WEIGHT) as archive:
        if archive.testzip() is not None:
            raise ValueError('checkpoint archive CRC failure')
        members = len(archive.infolist())
    result = dict(status='TECHNICAL_CHECK_PASSED', source_files=len(manifest['files']),
                  checkpoint_sha256=SHA, archive_members=members,
                  scope='offline byte identity and archive integrity only',
                  license_review='UNVERIFIED', inference='NOT_RUN', accuracy='UNVERIFIED')
    (BASE / 'bundle-integrity.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-check']:
        self_check()
        print('integrity negative controls passed')
    else:
        main()
