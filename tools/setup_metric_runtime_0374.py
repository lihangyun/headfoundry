"""Isolated official runtime installation with local evidence and temp files."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/metric-runtime-0374'
VENV=ROOT/'.venv-metric0374'


def worker():
    env=os.environ.copy()
    temp=OUT/'tmp';temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp),TMP=str(temp),PIP_NO_CACHE_DIR='1',PIP_DISABLE_PIP_VERSION_CHECK='1')
    python=VENV/'Scripts/python.exe'
    if not python.exists():
        subprocess.run([sys.executable,'-m','venv',str(VENV)],check=True,env=env,cwd=ROOT)
    base=[str(python),'-m','pip','install','--only-binary=:all:','--no-cache-dir','--retries','0','--timeout','30']
    subprocess.run(base+['torch==2.8.0','torchvision==0.23.0','numpy==2.2.6','pillow==11.3.0',
                        '--index-url','https://download.pytorch.org/whl/cu126',
                        '--report',str(OUT/'torch-install.json')],check=True,env=env,cwd=ROOT)
    subprocess.run(base+['opencv-python==4.12.0.88','--index-url','https://pypi.org/simple',
                        '--report',str(OUT/'opencv-install.json')],check=True,env=env,cwd=ROOT)
    subprocess.run([str(python),'-m','pip','check'],check=True,env=env,cwd=ROOT)
    result=subprocess.run([str(python),'-m','pip','freeze'],check=True,capture_output=True,text=True,env=env,cwd=ROOT)
    (OUT/'freeze.txt').write_text(result.stdout)
    subprocess.run([str(python),__file__,'inspect'],check=True,env=env,cwd=ROOT)


def inspect():
    import hashlib
    import importlib.metadata as metadata
    records={}
    for dist in metadata.distributions():
        licenses={}
        for entry in dist.files or []:
            if any(token in str(entry).lower() for token in ('license','copying','notice')):
                path=Path(dist.locate_file(entry))
                if path.is_file():
                    licenses[str(entry)]=hashlib.sha256(path.read_bytes()).hexdigest()
        records[dist.metadata['Name']]={'version':dist.version,'license':dist.metadata.get('License'),
                                      'license_expression':dist.metadata.get('License-Expression'),
                                      'license_files':licenses}
    (OUT/'licenses.json').write_text(json.dumps(records,indent=2))
    import torch,torchvision,cv2,numpy
    result={'status':'TECHNICAL_CHECK_PASSED','torch':torch.__version__,'torchvision':torchvision.__version__,
            'opencv':cv2.__version__,'numpy':numpy.__version__,'cuda_available':torch.cuda.is_available(),
            'cuda_runtime':torch.version.cuda,'license_review':'UNVERIFIED','scope':'imports only, no model inference'}
    (OUT/'runtime.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:]==['worker']:
        worker()
    elif sys.argv[1:]==['inspect']:
        inspect()
    else:
        from bounded_process import run
        print(run([sys.executable,__file__,'worker'],ROOT,os.environ.copy(),OUT/'worker.log',OUT/'worker.json',900,4*1024**3))
