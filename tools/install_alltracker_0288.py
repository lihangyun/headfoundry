"""Pinned public assets/private runtime only;no human inputs or default hub downloads."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/private/alltracker-0288'
REV = 'e7553135e7b361590dbccd10e2b274b024f41cd6'
MODEL_REV = 'c8ba31225828cab9ec512d0627f0f826e641a877'
HASHES = {
    'LICENSE':'ab740abe5c34e17963fe4d6a1f68a3dcd35bbc05dc520cf08d7a062c0ea13c79',
    'nets/alltracker.py':'42a203dfe1f4f6f035570c0c97a83172bd769591fa5930deda422ddac42f7807',
    'nets/blocks.py':'0c347f79b53367e0a99fb8d5bbe65346def904940f07dd361349af1da4eb0672',
    'utils/basic.py':'8a9057ef6ddecdc202ba49693dabede6c63dde204b15ec43b4bb81dfaed910a9',
    'utils/misc.py':'4ac64b714891789b21f1776292c7b9bd580031950f8df4398c9718922e7dbe90',
}
MODEL_HASH = 'ffd9ebcfb6d206d594b646999a150540f92c049cf9b2bf940facf7123f62aa1d'


def download(url,path,expected,limit):
    path.parent.mkdir(parents=True,exist_ok=True)
    part = path.with_suffix(path.suffix+'.part')
    h,count = hashlib.sha256(),0
    with urllib.request.urlopen(url,timeout=45) as response,part.open('xb') as out:
        while block := response.read(1024*1024):
            count += len(block)
            if count>limit:
                raise ValueError('asset exceeds locked size budget')
            out.write(block)
            h.update(block)
    if h.hexdigest()!=expected:
        raise ValueError('asset hash mismatch:'+str(path))
    part.replace(path)
    return {'path':str(path.relative_to(ROOT)),'bytes':count,'sha256':expected,'url':url}


def main():
    start = time.monotonic()
    DEST.mkdir(exist_ok=False)
    report = {'status':'REJECT','source_revision':REV,'model_revision':MODEL_REV,
              'license':'MIT','scope':'local-inference-only','assets':[]}
    try:
        for name,expected in HASHES.items():
            report['assets'].append(download('https://raw.githubusercontent.com/aharley/alltracker/'+REV+'/'+name,
                                             DEST/'source'/name,expected,100000))
        report['assets'].append(download('https://huggingface.co/aharley/alltracker/raw/'+MODEL_REV+'/README.md',
                                         DEST/'weight-license.md','f0ea38ffeb94f94c853029a28b9f59f05cc447a2a646f5c4ea0a4e90b1653d0f',10000))
        report['assets'].append(download('https://huggingface.co/aharley/alltracker/resolve/'+MODEL_REV+'/alltracker.pth',
                                         DEST/'alltracker.pth',MODEL_HASH,66005722))
        if report['assets'][-1]['bytes']!=66005722:
            raise ValueError('checkpoint size mismatch')
        uv = Path(os.environ['USERPROFILE'])/'.local/bin/uv.exe'
        env = dict(os.environ,UV_CACHE_DIR=str(DEST/'cache'),TORCH_HOME=str(DEST/'torch-cache'),
                   HF_HOME=str(DEST/'hf-cache'),TMP=str(DEST/'tmp'),TEMP=str(DEST/'tmp'))
        (DEST/'tmp').mkdir()
        def run(args):
            remaining = 600-(time.monotonic()-start)
            if remaining<=0:
                raise TimeoutError('installation600s cap')
            subprocess.run([str(uv),*args],cwd=ROOT,env=env,check=True,timeout=remaining,
                           creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        run(['venv',str(DEST/'env'),'--python',sys.executable])
        interpreter = str(DEST/'env/Scripts/python.exe')
        run(['pip','install','--python',interpreter,'--index-url','https://download.pytorch.org/whl/cu128',
             '--extra-index-url','https://pypi.org/simple','--index-strategy','unsafe-best-match',
             'torch==2.10.0+cu128','torchvision==0.25.0+cu128','einops==0.8.0','numpy==2.5.2'])
        report['status'] = 'TECHNICAL_CHECK_PASSED'
        report['runtime_status'] = 'UNVERIFIED'
    except Exception as error:
        report['failure'] = type(error).__name__+':'+str(error)
    finally:
        report['seconds'] = time.monotonic()-start
        (DEST/'installation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
