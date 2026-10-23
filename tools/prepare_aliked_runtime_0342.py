"""Install one hash-bound isolated CPU runtime;no model import or inference."""
import hashlib
import html
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename
from bounded_process import run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/aliked-runtime-0342'
UV=Path('C:/Users/lihan/.local/bin/uv.exe')
PINS={'filelock':'3.32.3','fsspec':'2026.7.0','Jinja2':'3.1.6','MarkupSafe':'3.0.3',
    'mpmath':'1.3.0','networkx':'3.6.1','setuptools':'78.1.0','sympy':'1.14.0',
    'typing_extensions':'4.16.0','numpy':'2.5.2','pillow':'12.3.0','packaging':'26.3',
    'kornia':'0.8.3','kornia-rs':'0.1.10','opencv-contrib-python':'5.0.0.93'}

def fetch(url,path):
    request=urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-locked-CPU-runtime'})
    with urllib.request.urlopen(request,timeout=30) as response:data=response.read(5*1024**2+1)
    if len(data)>5*1024**2:raise ValueError('metadata bound exceeded')
    path.write_bytes(data);return data

def worker():
    if (OUT/'env').exists() or (OUT/'metadata').exists():raise FileExistsError('no setup repeat/overwrite')
    metadata=OUT/'metadata';metadata.mkdir()
    tags={t:i for i,t in enumerate(sys_tags())};wheels=[]
    for name,version in PINS.items():
        info=json.loads(fetch(f'https://pypi.org/pypi/{name}/{version}/json',metadata/(name+'.json')))
        candidates=[]
        for asset in info['urls']:
            if asset['packagetype']!='bdist_wheel' or asset.get('yanked'):continue
            _,_,_,wheel_tags=parse_wheel_filename(asset['filename'])
            rank=min((tags[t] for t in wheel_tags if t in tags),default=None)
            if rank is not None:candidates.append((rank,asset['filename'],asset))
        if not candidates:raise ValueError('no exact compatible wheel:'+name)
        asset=min(candidates,key=lambda x:x[:2])[2]
        wheels.append({'name':name,'version':version,'url':asset['url'],'filename':asset['filename'],
            'sha256':asset['digests']['sha256'],'size':asset['size'],'license':info['info'].get('license'),
            'license_expression':info['info'].get('license_expression')})
    for name,version in (('torch','2.10.0+cpu'),('torchvision','0.25.0+cpu')):
        index=f'https://download.pytorch.org/whl/cpu/{name}/'
        text=fetch(index,metadata/(name+'-index.html')).decode('utf8')
        expected=f'{name}-{version}-cp312-cp312-win_amd64.whl'
        links=[urllib.parse.urljoin(index,html.unescape(x)) for x in re.findall(r'href="([^"]+)"',text)]
        links=[x for x in links if urllib.parse.unquote(urllib.parse.urlsplit(x).path).split('/')[-1]==expected]
        if len(links)!=1:raise ValueError('ambiguous/missing official CPU wheel:'+name)
        parsed=urllib.parse.urlsplit(links[0]);digest=urllib.parse.parse_qs(parsed.fragment).get('sha256')
        if not digest or len(digest)!=1 or len(digest[0])!=64:raise ValueError('official wheel SHA256 absent')
        wheels.append({'name':name,'version':version,'url':links[0].split('#')[0],
            'filename':expected,'sha256':digest[0],'source_index':index})
    (OUT/'wheels.json').write_text(json.dumps(wheels,indent=2))
    (OUT/'requirements.txt').write_text('\n'.join(f"{w['name']} @ {w['url']} --hash=sha256:{w['sha256']}" for w in wheels)+'\n')
    env=dict(os.environ);env.update(UV_CACHE_DIR=str(OUT/'cache'),TEMP=str(OUT/'tmp'),TMP=str(OUT/'tmp'),UV_NO_CACHE='1')
    (OUT/'tmp').mkdir()
    subprocess.run([str(UV),'--no-cache','venv','--python',str(ROOT/'.venv/Scripts/python.exe'),str(OUT/'env')],
        env=env,check=True,cwd=ROOT)
    python=OUT/'env/Scripts/python.exe'
    subprocess.run([str(UV),'--no-cache','pip','install','--python',str(python),'--no-deps','--require-hashes',
        '-r',str(OUT/'requirements.txt')],env=env,check=True,cwd=ROOT)
    subprocess.run([str(UV),'--no-cache','pip','check','--python',str(python)],env=env,check=True,cwd=ROOT)
    source=ROOT/'assets/private/aliked-preflight-0339'
    expected=json.loads((source/'result.json').read_text())
    known={r['name']:r['sha256'] for r in expected['files']}
    for old,new in (('lg-lightglue_aliked.py','aliked.py'),('lg-lightglue_lightglue.py','lightglue.py'),('lg-lightglue_utils.py','utils.py')):
        path=source/'receipts'/old
        if hashlib.sha256(path.read_bytes()).hexdigest()!=known[old]:raise ValueError('source changed')
        shutil.copyfile(path,OUT/'source/lg0342'/new)
    for name in ('lg-LICENSE','ak-LICENSE'):
        shutil.copyfile(source/'receipts'/name,OUT/name)
    site=OUT/'env/Lib/site-packages';notices=OUT/'notices';notices.mkdir()
    distributions=[]
    for dist in importlib.metadata.distributions(path=[str(site)]):
        files=[]
        for relative in dist.files or []:
            lowered=str(relative).lower()
            if any(word in lowered for word in ('license','copying','notice')):
                path=Path(dist.locate_file(relative)).resolve()
                if not path.is_relative_to(site.resolve()) or not path.is_file():continue
                target=notices/dist.metadata['Name']/Path(relative)
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
                files.append({'path':relative.as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        distributions.append({'name':dist.metadata['Name'],'version':dist.version,'license':dist.metadata.get('License'),
            'license_expression':dist.metadata.get('License-Expression'),'notices':files})
    (OUT/'distributions.json').write_text(json.dumps(distributions,indent=2))
    (OUT/'setup-result.json').write_text(json.dumps({'status':'TECHNICAL_CHECK_PASSED','completed_utc':time.time(),
        'distributions':len(distributions),'source_numeric_edits':False,'model_imported':False},indent=2))
    print('TECHNICAL_CHECK_PASSED isolated pinned runtime,not model/physical accuracy')

if __name__=='__main__':
    if ROOT!=Path('C:/workspace/headfoundry').resolve():raise ValueError('wrong repository')
    for path in (ROOT,ROOT/'assets',ROOT/'assets/private',OUT):
        if getattr(path.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse path')
    if sys.argv[1:]==['worker']:worker()
    else:
        if (OUT/'setup-worker.json').exists():raise FileExistsError('existing setup receipt')
        result=run([sys.executable,str(Path(__file__).resolve()),'worker'],str(ROOT),dict(os.environ),
            OUT/'setup.log',OUT/'setup-worker.json',600,1024**3)
        print(json.dumps(result))
        if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)
