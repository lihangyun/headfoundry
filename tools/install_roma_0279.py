"""Bounded atomic installation of the two publisher RoMa components."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/roma-lifetime-0279'
SOURCE = '77f8d68803526dcddfd9b7a46bc76125bdc25f15'
MODELS = [
    ('roma_outdoor.pth', 'MIT', 445647516,
     'https://github.com/Parskatt/storage/releases/download/roma/roma_outdoor.pth'),
    ('dinov2_vitl14_pretrain.pth', 'Apache-2.0', 1217586395,
     'https://dl.fbaipublicfiles.com/dinov2/dinov2_vitl14/dinov2_vitl14_pretrain.pth'),
]


def download(name, url, size=None):
    target = OUT / name
    temporary = target.with_suffix(target.suffix+'.part')
    digest, count = hashlib.sha256(), 0
    request = urllib.request.Request(url, headers={'User-Agent': 'HeadFoundry-local-validation'})
    with urllib.request.urlopen(request, timeout=40) as response, temporary.open('xb') as f:
        if response.status != 200:
            raise ValueError('official download did not return200')
        while block := response.read(1024*1024):
            count += len(block)
            if count > (size if size else 50*1024*1024):
                raise ValueError('download exceeds registered size')
            f.write(block)
            digest.update(block)
        f.flush()
        os.fsync(f.fileno())
    if size is not None and count != size:
        raise ValueError('incomplete model download')
    expected_hashes = {'roma_outdoor.pth': 'c7a45c80d41ad788a63c641d1b686d7cb3f297f40097c6f4e75039889e5cc8ba',
                       'dinov2_vitl14_pretrain.pth': 'd5383ea8f4877b2472eb973e0fd72d557c7da5d3611bd527ceeb1d7162cbf428'}
    if name in expected_hashes and digest.hexdigest() != expected_hashes[name]:
        raise ValueError('official checkpoint differs from registered exact identity')
    temporary.replace(target)
    return {'path': name, 'source': url, 'bytes': count, 'sha256': digest.hexdigest()}


def runtime():
    env_dir = ROOT / '.venv-roma-0279'
    subprocess.run([sys.executable, '-m', 'venv', '--without-pip', str(env_dir)], check=True)
    python = env_dir / 'Scripts/python.exe'
    uv = Path.home() / '.local/bin/uv.EXE'
    base = [str(uv), 'pip', 'install', '--python', str(python), '--no-deps']
    with (OUT / 'runtime-install.log').open('x') as log:
        subprocess.run(base+['--index-url', 'https://download.pytorch.org/whl/cpu',
                       'torch==2.10.0+cpu', 'torchvision==0.25.0+cpu'],
                       stdout=log, stderr=log, check=True, timeout=180)
        packages = ['numpy==2.5.2', 'pillow==12.1.0', 'einops==0.8.1', 'loguru==0.7.3',
                    'filelock==3.32.3', 'fsspec==2026.7.0', 'networkx==3.6.1',
                    'Jinja2==3.1.6', 'MarkupSafe==3.0.3', 'sympy==1.14.0',
                    'mpmath==1.3.0', 'typing_extensions==4.16.0', 'setuptools==78.1.0',
                    'colorama==0.4.6', 'win32-setctime==1.2.0']
        subprocess.run(base+packages, stdout=log, stderr=log, check=True, timeout=90)
    return {'python': str(python), 'torch': '2.10.0+cpu', 'torchvision': '0.25.0+cpu'}


def main():
    started = time.monotonic()

    def stop():
        (OUT / 'install-timeout.json').write_text(json.dumps({'seconds': 300}))
        subprocess.run(['taskkill', '/PID', str(os.getpid()), '/T', '/F'])

    timer = threading.Timer(300, stop)
    timer.daemon = True
    timer.start()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        runtime_job = pool.submit(runtime)
        jobs = [pool.submit(download, name, url, size) for name, _, size, url in MODELS]
        source_job = pool.submit(download, 'publisher-source.zip',
                                f'https://codeload.github.com/Parskatt/RoMa/zip/{SOURCE}')
        models = [job.result() for job in jobs]
        source = source_job.result()
        installed = runtime_job.result()
    vendor = OUT / 'vendor'
    vendor.mkdir()
    with zipfile.ZipFile(OUT / 'publisher-source.zip') as z:
        for info in z.infolist():
            parts = Path(info.filename).parts[1:]
            if not parts or info.is_dir() or '..' in parts:
                continue
            if parts[0] != 'romatch' and '/'.join(parts) not in ['LICENSE', 'README.md', 'pyproject.toml']:
                continue
            target = vendor.joinpath(*parts)
            if not target.resolve().is_relative_to(vendor.resolve()):
                raise ValueError('source member escaped installation')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(info))
    preflight = ROOT / 'assets/private/dense-foundation-preflight-0277'
    review = json.loads((preflight / 'source-contract-review.json').read_text())
    for record in review['reviewed_files']:
        path = vendor / record['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('publisher source changed from audited commit')
    rights = json.loads((preflight / 'publisher-rights.json').read_text())
    notices = OUT / 'notices'
    notices.mkdir()
    for key in ['roma_license', 'storage_license', 'dinov2_license']:
        if not rights.get(key):
            raise ValueError('missing publisher license')
        (notices / (key+'.txt')).write_text(rights[key], encoding='utf8')
    for record, (name, license_id, size, url) in zip(models, MODELS):
        assert record['path'] == name and record['source'] == url and record['bytes'] == size
        record.update(id=name, license_id=license_id,
                      allowed_uses=['local_head_reconstruction_validation'],
                      rights_source='notices/storage_license.txt' if license_id == 'MIT'
                                   else 'notices/dinov2_license.txt')
    manifest = {'source_commit': SOURCE, 'models': models, 'source_archive': source,
                'runtime': installed, 'asset_source': 'official unauthenticated publisher endpoints',
                'publisher_signed_digest': False, 'seconds': time.monotonic()-started}
    (OUT / 'model-assets.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    timer.cancel()
    print(json.dumps({'installed': True, 'seconds': manifest['seconds'], 'models': models}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        (OUT / 'install-failure.json').write_text(json.dumps({'type': type(exc).__name__, 'error': str(exc)}))
        raise
