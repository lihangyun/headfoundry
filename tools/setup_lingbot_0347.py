"""Isolated, bounded fixed-version runtime setup; no model execution."""
import json
import os
from pathlib import Path
import subprocess
import sys

from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/lingbot-entry-0347'
ENV = ROOT / '.venv-lingbot-0347'
UV = Path('C:/Users/lihan/.local/bin/uv.exe')


def install():
    if ENV.exists():
        raise FileExistsError(ENV)
    env = dict(os.environ, UV_CACHE_DIR=str(OUT / 'uv-cache'),
               TEMP=str(OUT / 'temp'), TMP=str(OUT / 'temp'))
    (OUT / 'temp').mkdir(exist_ok=True)
    subprocess.run([str(UV), 'venv', str(ENV), '--python', str(ROOT / '.venv/Scripts/python.exe')],
                   cwd=ROOT, env=env, check=True)
    python = str(ENV / 'Scripts/python.exe')
    subprocess.run([str(UV), 'pip', 'install', '--python', python,
                   'torch==2.8.0', 'torchvision==0.23.0',
                   '--index-url', 'https://download.pytorch.org/whl/cu128'],
                  cwd=ROOT, env=env, check=True)
    subprocess.run([str(UV), 'pip', 'install', '--python', python,
                   'numpy==2.5.2', 'scipy==1.18.1', 'Pillow==12.3.0',
                   'einops==0.8.1', 'huggingface_hub==0.34.4', 'tqdm==4.67.1'],
                  cwd=ROOT, env=env, check=True)
    subprocess.run([str(UV), 'pip', 'freeze', '--python', python],
                   cwd=ROOT, env=env, check=True)
    subprocess.run([str(UV), 'pip', 'check', '--python', python],
                   cwd=ROOT, env=env, check=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        install()
    elif not sys.argv[1:]:
        record = run([sys.executable, str(Path(__file__).resolve()), '--worker'],
                     ROOT, dict(os.environ), OUT / 'setup.log', OUT / 'setup-worker.json',
                     seconds=600, working_bytes=8*1024**3)
        print(json.dumps(record))
    else:
        raise SystemExit('unsupported arguments')
