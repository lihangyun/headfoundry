"""Bounded public-text acquisition only; never import upstream or fetch weights."""
import hashlib
import json
from pathlib import Path
import time
import sys
import ast
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REV = 'b9dd1b1de535e6d36e777fb42b8433c781bfd783'


def complete_source():
    """Inspect inert Python text, never load or execute the collected package."""
    destination = ROOT / 'assets/private/lingbot-source-0346'
    receipt_path = destination / 'receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    start = time.monotonic()
    tree_url = f'https://api.github.com/repos/Robbyant/lingbot-map/git/trees/{REV}?recursive=1'
    with urlopen(tree_url, timeout=15) as response:
        tree_bytes = response.read(500001)
    if len(tree_bytes) > 500000:
        raise ValueError('tree metadata cap')
    tree = json.loads(tree_bytes)
    if tree.get('truncated') or tree.get('sha') != REV:
        raise ValueError('incomplete or wrong source tree')
    entries = [e for e in tree['tree'] if e['type'] == 'blob' and
               (e['path'].startswith('lingbot_map/') and e['path'].endswith('.py') or
                'license' in e['path'].lower() or 'notice' in e['path'].lower())]
    known = {e['path']: e for e in receipt['files']}
    imports = {}
    try:
        for entry in entries:
            name = entry['path']
            target = destination / name
            if not target.resolve().is_relative_to(destination.resolve()) or target.is_symlink():
                raise ValueError('unsafe source path')
            if name in known:
                data = target.read_bytes()
                if hashlib.sha256(data).hexdigest() != known[name]['sha256']:
                    raise ValueError('changed source snapshot')
            else:
                remaining = 100 - (time.monotonic()-start)
                if remaining <= 0:
                    raise TimeoutError('remaining collection budget')
                url = f'https://raw.githubusercontent.com/Robbyant/lingbot-map/{REV}/{name}'
                with urlopen(url, timeout=min(15, remaining)) as response:
                    data = response.read(2*1024*1024 - receipt['bytes'] + 1)
                if receipt['bytes'] + len(data) > 2*1024*1024:
                    raise ValueError('total text cap')
                data.decode('utf-8')
            if hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest() != entry['sha']:
                raise ValueError('Git blob mismatch')
            if name not in known:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                receipt['files'].append({'path': name, 'url': url, 'bytes': len(data),
                                         'sha256': hashlib.sha256(data).hexdigest()})
                receipt['bytes'] += len(data)
            if name.endswith('.py'):
                imports[name] = sorted({n.module or '.' for n in ast.walk(ast.parse(data))
                                       if isinstance(n, ast.ImportFrom)} |
                                      {a.name for n in ast.walk(ast.parse(data))
                                       if isinstance(n, ast.Import) for a in n.names})
        receipt['source_tree_verified'] = True
        receipt['imports'] = imports
    finally:
        receipt['closure_elapsed_seconds'] = time.monotonic()-start
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'files': len(receipt['files']), 'bytes': receipt['bytes'],
                      'elapsed': receipt['closure_elapsed_seconds'], 'imports': imports}))


def verify_and_pin_card():
    destination = ROOT / 'assets/private/lingbot-source-0346'
    receipt_path = destination / 'receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    for entry in receipt['files']:
        data = (destination / entry['path']).read_bytes()
        assert len(data) == entry['bytes']
        assert hashlib.sha256(data).hexdigest() == entry['sha256']
    metadata = json.loads((destination / 'hf-metadata.json').read_text(encoding='utf-8'))
    weight = next(s for s in metadata['siblings'] if s['rfilename'] == 'lingbot-map.pt')
    assert weight['lfs']['sha256'] == 'ee665103348e07e6b826d529b8e61de8f413d5432a4f2e84970d6c8fd2e1cd72'
    assert weight['size'] == 4632303465
    card = next(s for s in metadata['siblings'] if s['rfilename'] == 'README.md')
    target = destination / 'model-card.md'
    if not target.exists():
        url = f"https://huggingface.co/robbyant/lingbot-map/resolve/{metadata['sha']}/README.md"
        with urlopen(url, timeout=15) as response:
            data = response.read(card['size'] + 1)
        assert len(data) == card['size']
        assert hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() == card['blobId']
        assert receipt['bytes'] + len(data) <= 2 * 1024 * 1024
        target.write_bytes(data)
        receipt['files'].append({'path': 'model-card.md', 'url': url, 'bytes': len(data),
                                 'sha256': hashlib.sha256(data).hexdigest()})
        receipt['bytes'] += len(data)
        receipt['model_revision'] = metadata['sha']
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'SNAPSHOT_IDENTITIES_VERIFIED',
                      'files': len(receipt['files']), 'bytes': receipt['bytes'],
                      'model_revision': metadata['sha'], 'weight_bytes_verified': False}))


def main():
    start = time.monotonic()
    destination = ROOT / 'assets/private/lingbot-source-0346'
    if destination.exists():
        raise FileExistsError(destination)
    destination.mkdir()
    records, total = [], 0
    base = f'https://raw.githubusercontent.com/Robbyant/lingbot-map/{REV}/'
    urls = [(name, base + name) for name in (
        'LICENSE.txt', 'pyproject.toml', 'demo.py',
        'lingbot_map/models/gct_stream.py', 'lingbot_map/models/gct_base.py',
        'lingbot_map/aggregator/stream.py', 'lingbot_map/aggregator/base.py',
        'lingbot_map/utils/load_fn.py', 'lingbot_map/utils/pose_enc.py',
        'lingbot_map/utils/rotation.py', 'lingbot_map/utils/geometry.py')]
    urls.append(('hf-metadata.json',
                 'https://huggingface.co/api/models/robbyant/lingbot-map?blobs=true'))
    try:
        for name, url in urls:
            remaining = 115 - (time.monotonic() - start)
            if remaining <= 0:
                raise TimeoutError('115s collection budget')
            with urlopen(Request(url, headers={'User-Agent': 'HeadFoundry-source-audit'}),
                         timeout=min(15, remaining)) as response:
                data = response.read(2 * 1024 * 1024 - total + 1)
            total += len(data)
            if total > 2 * 1024 * 1024:
                raise ValueError('2MiB text budget')
            data.decode('utf-8')
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            records.append({'path': name, 'url': url, 'bytes': len(data),
                            'sha256': hashlib.sha256(data).hexdigest()})
        result = {'status': 'COLLECTED_NOT_EXECUTED'}
    except Exception as exc:
        result = {'status': 'UNVERIFIED', 'error': repr(exc)}
    result.update(source_revision=REV, files=records, bytes=total,
                  elapsed_seconds=time.monotonic()-start)
    (destination / 'receipt.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
    if result['status'] == 'UNVERIFIED':
        raise SystemExit(1)


if __name__ == '__main__':
    if sys.argv[1:] == ['--verify-and-pin-card']:
        verify_and_pin_card()
    elif sys.argv[1:] == ['--complete-source']:
        complete_source()
    elif not sys.argv[1:]:
        main()
    else:
        raise SystemExit('unsupported arguments')
