"""Acquire one public pinned artifact; never deserialize checkpoint objects."""
import hashlib
import json
from pathlib import Path
import shutil
import time
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SIZE = 4632303465
EXPECTED_SHA = 'ee665103348e07e6b826d529b8e61de8f413d5432a4f2e84970d6c8fd2e1cd72'
URL = 'https://huggingface.co/robbyant/lingbot-map/resolve/204754b72bb24f561f8d7e7e1e4e4cd9e809adf9/lingbot-map.pt'


def main():
    destination = ROOT / 'assets/private/lingbot-entry-0347'
    if destination.exists():
        raise FileExistsError(destination)
    if shutil.disk_usage(ROOT).free < EXPECTED_SIZE + 2 * 1024**3:
        raise OSError('insufficient disk reserve')
    destination.mkdir()
    partial = destination / 'lingbot-map.pt.part'
    start = time.monotonic()
    digest = hashlib.sha256()
    count = 0
    result = {'status': 'UNVERIFIED', 'url': URL}
    try:
        with urlopen(URL, timeout=30) as response, partial.open('xb') as output:
            while True:
                if time.monotonic()-start > 870:
                    raise TimeoutError('download deadline')
                chunk = response.read(4*1024*1024)
                if not chunk:
                    break
                count += len(chunk)
                if count > EXPECTED_SIZE:
                    raise ValueError('oversized artifact')
                digest.update(chunk)
                output.write(chunk)
        if count != EXPECTED_SIZE or digest.hexdigest() != EXPECTED_SHA:
            raise ValueError('artifact identity mismatch')
        with zipfile.ZipFile(partial) as archive:
            entries = [{'name': item.filename, 'bytes': item.file_size,
                        'compressed_bytes': item.compress_size} for item in archive.infolist()]
            if len({e['name'] for e in entries}) != len(entries):
                raise ValueError('duplicate ZIP entries')
            for entry in entries:
                path = Path(entry['name'])
                if path.is_absolute() or '..' in path.parts or '\\' in entry['name']:
                    raise ValueError('unsafe ZIP member')
            if len([e for e in entries if e['name'].endswith('/data.pkl')]) != 1:
                raise ValueError('unexpected checkpoint structure')
            if sum(e['bytes'] for e in entries) > EXPECTED_SIZE:
                raise ValueError('unexpected expansion')
        partial.rename(destination / 'lingbot-map.pt')
        result.update(status='TECHNICAL_CHECK_PASSED', archive=entries,
                      meaning='artifact bytes only; not loaded or inferred')
    except Exception as exc:
        result['error'] = repr(exc)
    result.update(bytes=count, sha256=digest.hexdigest(), elapsed_seconds=time.monotonic()-start)
    (destination / 'acquisition.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'archive'}), flush=True)
    if result['status'] == 'UNVERIFIED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
