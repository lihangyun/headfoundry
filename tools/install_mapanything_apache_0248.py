"""Public immutable downloads only;does NOT clear or execute the model runtime."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file
from mapanything_assets_0248 import (REPOSITORY, REVISION, WEIGHT_SHA, WEIGHT_SIZE, CONFIG_SHA,
    SOURCE_REVISION, DINO_REVISION, DPT_REVISION, validate_identity)

OUT = ROOT/'assets/private/mapanything-apache-0248'


def safe_zip_members(archive):
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if (path.is_absolute() or '..' in path.parts or any(':' in part or '\\' in part for part in path.parts)
                or ((info.external_attr >> 16) & 0o170000) == 0o120000 or info.file_size > 100*1024*1024):
            raise ValueError('Unsafe public source archive path/type/size')
    if sum(i.file_size for i in archive.infolist()) > 512*1024*1024:
        raise ValueError('Unexpected public source archive expansion')


def main():
    if not OUT.resolve().is_relative_to((ROOT/'assets/private').resolve()):
        raise ValueError('Only private repository asset root may be written')
    OUT.mkdir(exist_ok=True)
    receipt_path = OUT/'download-receipts.json'
    receipts = json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {}
    started = time.perf_counter()

    def download(relative, url, expected=None, size=None):
        destination = OUT/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            known = expected or receipts.get(relative, {}).get('sha256')
            if known and sha256_file(destination) == known:
                return destination
            raise ValueError('Existing asset does not match a reviewed identity/receipt')
        partial = destination.with_name(destination.name+'.part')
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {'User-Agent': 'HeadFoundry-Public-Asset-Installer'}
        if offset:
            headers['Range'] = f'bytes={offset}-'
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            if offset and response.status != 206:
                raise ValueError('Server did not honor partial resume;preserve original partial')
            count, previous = offset, -1
            digest = hashlib.sha256()
            if offset:
                with partial.open('rb') as prior:
                    for chunk in iter(lambda: prior.read(1024*1024), b''):
                        digest.update(chunk)
            with partial.open('ab' if offset else 'xb') as output:
                for chunk in iter(lambda: response.read(1024*1024), b''):
                    output.write(chunk)
                    digest.update(chunk)
                    count += len(chunk)
                    if size:
                        progress = int(20*count/size)
                        if progress != previous:
                            print(json.dumps({'asset': relative, 'bytes': count, 'total_bytes': size}), flush=True)
                            previous = progress
                    if time.perf_counter()-started > 1200:
                        raise TimeoutError('Public asset download budget exhausted;partial retained')
        actual = digest.hexdigest()
        if (expected and actual != expected) or (size and count != size):
            raise ValueError('Public asset bytes/hash differ from pinned publisher identity;partial retained')
        partial.rename(destination)
        receipts[relative] = {'url': url, 'sha256': actual, 'bytes': count}
        receipt_path.write_text(json.dumps(receipts, indent=2), encoding='utf-8')
        return destination

    base = f'https://huggingface.co/{REPOSITORY}/resolve/{REVISION}'
    download('weights/config.json', base+'/config.json', CONFIG_SHA)
    download('weights/README.md', base+'/README.md', '1481978d474172ee1acac213eddaf3572e54dba369190d898c8578f26097f1d2')
    for name, repository, revision in [('mapanything', 'facebookresearch/map-anything', SOURCE_REVISION),
            ('dinov2', 'facebookresearch/dinov2', DINO_REVISION)]:
        archive = download(f'{name}.zip', f'https://codeload.github.com/{repository}/zip/{revision}')
        destination = OUT/'source'/name
        if not destination.exists():
            with zipfile.ZipFile(archive) as package:
                safe_zip_members(package)
                parents = {PurePosixPath(i.filename).parts[0] for i in package.infolist()}
                if len(parents) != 1:
                    raise ValueError('Expected one immutable source root')
                prefix = next(iter(parents))
                destination.mkdir(parents=True)
                for item in package.infolist():
                    parts = PurePosixPath(item.filename).parts[1:]
                    if not parts or item.is_dir():
                        continue
                    target = (destination/Path(*parts)).resolve()
                    if not target.is_relative_to(destination.resolve()):
                        raise ValueError('Public extraction target escaped asset root')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with package.open(item) as source, target.open('xb') as output:
                        output.write(source.read())
    download('source/dpt/blocks.py', f'https://raw.githubusercontent.com/isl-org/DPT/{DPT_REVISION}/dpt/blocks.py',
        '16ce2f53322a7d912ced6057c90bbaf8f2fa12ac1304d4fd6f4c358ff710be6a')
    download('source/dpt/LICENSE', f'https://raw.githubusercontent.com/isl-org/DPT/{DPT_REVISION}/LICENSE',
        '248e59d88b238917f1167dd118fbace3e8136e37e9c91ee952fef80c191e3e32')
    if '--metadata-only' not in sys.argv:
        download('weights/model.safetensors', base+'/model.safetensors', WEIGHT_SHA, WEIGHT_SIZE)
    tree = {str(p.relative_to(OUT)).replace('\\', '/'): sha256_file(p) for p in sorted((OUT/'source').rglob('*')) if p.is_file()}
    (OUT/'source-tree-hashes.json').write_text(json.dumps(tree, indent=2), encoding='utf-8')
    record = {'schema_version': 1, 'id': 'MapAnything-Apache', 'repository': REPOSITORY, 'revision': REVISION,
        'license_id': 'Apache-2.0', 'commercial_use': True, 'inference_upload_allowed': False,
        'rights_reviewed_by': 'Codex public publisher/license evidence review', 'rights_reviewed_at': '2026-10-19',
        'path': 'weights/model.safetensors', 'sha256': WEIGHT_SHA, 'size_bytes': WEIGHT_SIZE,
        'config_path': 'weights/config.json', 'config_sha256': CONFIG_SHA,
        'model_card_path': 'weights/README.md', 'model_card_sha256': sha256_file(OUT/'weights/README.md'),
        'source_revision': SOURCE_REVISION, 'dino_revision': DINO_REVISION, 'dpt_revision': DPT_REVISION,
        'license_evidence': ['weights/README.md', 'source/mapanything/LICENSE', 'source/dinov2/LICENSE', 'source/dpt/LICENSE'],
        'source_tree_hashes_path': 'source-tree-hashes.json', 'source_tree_hashes_sha256': sha256_file(OUT/'source-tree-hashes.json'),
        'runtime_clearance': 'UNVERIFIED', 'runtime_warning': 'Original UniCeption DPT/CroCo path contains NC code;do not execute without reviewed permissive replacement.',
        'asset_download_status': 'TECHNICAL_CHECK_PASSED' if (OUT/'weights/model.safetensors').exists() else 'UNVERIFIED',
        'elapsed_seconds': time.perf_counter()-started, 'installer_sha256': sha256_file(Path(__file__))}
    if validate_identity(record, require_runtime=False):
        raise ValueError('Internal exact Apache record/rights validation failed')
    (OUT/'asset-lock.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({'asset_download_status': record['asset_download_status'], 'runtime_clearance': record['runtime_clearance'],
        'elapsed_seconds': record['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
