"""Eight pinned ranges,full hashes,then offline private installation;no inference."""
import ast
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/private/sparse-runtime-0298'
LOCK = json.loads((ROOT/'examples/dedode-0298-lock.json').read_text())
REPORT = {'status':'REJECT','assets':[],'wheel_licenses':{}}
START = time.monotonic()
DEADLINE = START+600
DONE = threading.Event()


def save():
    (DEST/'provision.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')


def watchdog():
    while not DONE.wait(.5):
        if time.monotonic()>DEADLINE:
            REPORT.update(failure='phase deadline exceeded',seconds=time.monotonic()-START)
            save()
            os._exit(124)


def sha(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file,'sha256').hexdigest()


def stream(url,path,size,offset=None,total=None):
    headers = {} if offset is None else {'Range':f'bytes={offset}-{offset+size-1}'}
    request = urllib.request.Request(url,headers=headers)
    count = 0
    with urllib.request.urlopen(request,timeout=45) as response,path.open('xb') as out:
        if offset is not None and (response.status!=206 or response.headers.get('Content-Range')!=f'bytes {offset}-{offset+size-1}/{total}'):
            raise ValueError('range contract mismatch')
        while block := response.read(1024*1024):
            count += len(block)
            if count>size or time.monotonic()>DEADLINE:
                raise ValueError('transfer exceeds locked bytes/deadline')
            out.write(block)
    if count!=size:
        raise ValueError('short asset transfer')


def asset(spec,path,parallel=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    started = time.monotonic()
    if parallel:
        step = (spec['bytes']+7)//8
        ranges = [(i*step,min(step,spec['bytes']-i*step),path.with_suffix(f'.part{i}')) for i in range(8)]
        def get_range(row):
            offset,size,target = row
            stream(spec['url'],target,size,offset,spec['bytes'])
            print(json.dumps({'completed_range':offset,'bytes':size}),flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(get_range,ranges))
        with path.open('xb') as out:
            for _,_,part in ranges:
                with part.open('rb') as source:
                    shutil.copyfileobj(source,out,1024*1024)
        for _,_,part in ranges:
            part.unlink()
    else:
        stream(spec['url'],path,spec['bytes'])
    if sha(path)!=spec['sha256']:
        raise ValueError('full-byte hash mismatch:'+path.name)
    REPORT['assets'].append({'path':str(path.relative_to(ROOT)),'sha256':spec['sha256'],
                             'bytes':path.stat().st_size,'seconds':time.monotonic()-started})
    save()
    print(json.dumps({'verified':path.name,'seconds':time.monotonic()-started}),flush=True)


def publisher_record(spec):
    url = 'https://api.github.com/repos/Parskatt/DeDoDe/releases/'+str(spec['releaseId'])
    request = urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-local-asset-validation','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        payload = response.read(100001)
    if len(payload)>100000:
        raise ValueError('publisher metadata bound')
    release = json.loads(payload)
    matches = [a for a in release.get('assets',[]) if a['id']==spec['id']]
    if release['id']!=spec['releaseId'] or release['tag_name']!=spec['release'] or len(matches)!=1:
        raise ValueError('release/asset identity differs')
    item = matches[0]
    if item['name']!=spec['name'] or item['size']!=spec['bytes'] or item['browser_download_url']!=spec['url'] or item['updated_at']!=spec['updated'] or item['state']!='uploaded':
        raise ValueError('locked asset metadata differs')
    return {k:item.get(k) for k in ('id','name','size','browser_download_url','updated_at','state','digest')}


def main():
    global DEADLINE
    DEST.mkdir(exist_ok=False)
    save()
    threading.Thread(target=watchdog,daemon=True).start()
    try:
        if not LOCK.get('source_license') or not LOCK.get('model_license') or any(not w.get('license') for w in LOCK['wheels']):
            raise ValueError('missing rights information')
        for spec in LOCK['wheels']:
            target = DEST/'wheels'/spec['filename']
            asset(spec,target,parallel=spec['name']=='torch')
            with zipfile.ZipFile(target) as wheel:
                names = [n for n in wheel.namelist() if '.dist-info/' in n and ('license' in n.lower() or n.endswith('/NOTICE'))]
                if not names:
                    raise ValueError('wheel has no bundled license notice:'+spec['name'])
                REPORT['wheel_licenses'][spec['name']] = {n:hashlib.sha256(wheel.read(n)).hexdigest() for n in names if not n.endswith('/')}
        for name,expected in LOCK['source_files'].items():
            url = LOCK['source_base_url']+LOCK['source_revision']+'/'+name
            with urllib.request.urlopen(url,timeout=30) as response:
                data = response.read(100001)
            if len(data)>100000 or hashlib.sha256(data).hexdigest()!=expected:
                raise ValueError('source hash mismatch')
            target = DEST/'source'/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        spec = LOCK['reference_utils']
        with urllib.request.urlopen(spec['url'],timeout=30) as response:
            data = response.read(100001)
        if len(data)>100000 or hashlib.sha256(data).hexdigest()!=spec['sha256']:
            raise ValueError('reference utility source differs')
        text = data.decode('utf-8')
        selected = [node for node in ast.parse(text).body if isinstance(node,ast.FunctionDef) and node.name in spec['functions']]
        if {n.name for n in selected}!=set(spec['functions']):
            raise ValueError('reference inference function set differs')
        extracted = '# Reference-only MIT inference helpers;Copyright2023JohanEdstedt;see source/LICENSE.\nimport torch\nimport torch.nn.functional as F\n\n'
        extracted += '\n\n'.join(ast.get_source_segment(text,node) for node in selected)+'\n'
        reference = DEST/'source/inference-reference.py'
        reference.write_text(extracted,encoding='utf-8')
        REPORT['reference_extract'] = {'functions':spec['functions'],'sha256':sha(reference),'omitted_borrowed_pose_transforms':True}
        REPORT['checkpoints'] = []
        for model in LOCK['checkpoint_assets']:
            before = publisher_record(model)
            path = DEST/model['name']
            stream(model['url'],path,model['bytes'])
            actual_hash = sha(path)
            if model.get('sha256') and actual_hash != model['sha256']:
                raise ValueError('previously frozen acquired-byte identity differs')
            after = publisher_record(model)
            if before!=after:
                raise ValueError('publisher asset metadata changed during download')
            published = after.get('digest')
            if published and published!='sha256:'+actual_hash:
                raise ValueError('published model digest differs')
            REPORT['checkpoints'].append({**model,'sha256':actual_hash,'license':'MIT per pinned README',
                                          'published_digest':published,'publisher_record':after})
            save()
            print(json.dumps({'acquired_model':model['name'],'bytes':model['bytes'],'sha256':actual_hash}),flush=True)
        (DEST/'checkpoint-receipt.json').write_text(json.dumps(REPORT['checkpoints'],indent=2),encoding='utf-8')
        REPORT['transport_seconds'] = time.monotonic()-START
        DEADLINE = time.monotonic()+180
        REPORT['phase'] = 'offline-install'
        save()
        env = dict(os.environ,UV_CACHE_DIR=str(DEST/'cache'),UV_OFFLINE='true',
                   TMP=str(DEST/'tmp'),TEMP=str(DEST/'tmp'),TORCH_HOME=str(DEST/'torch-cache'))
        (DEST/'tmp').mkdir()
        uv = str(Path(os.environ['USERPROFILE'])/'.local/bin/uv.exe')
        def run(args):
            result = subprocess.run([uv,'--offline',*args],cwd=ROOT,env=env,check=True,
                                    timeout=max(1,DEADLINE-time.monotonic()),capture_output=True,text=True,
                                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            REPORT.setdefault('install_output',[]).append({'stdout':result.stdout,'stderr':result.stderr})
        run(['venv',str(DEST/'env'),'--python',sys.executable])
        interpreter = str(DEST/'env/Scripts/python.exe')
        run(['pip','install','--python',interpreter,'--no-deps','--no-index',
             *[str(DEST/'wheels'/w['filename']) for w in LOCK['wheels']]])
        run(['pip','check','--python',interpreter])
        REPORT.update(status='TECHNICAL_CHECK_PASSED',runtime_status='UNVERIFIED',
                      install_seconds=time.monotonic()-(DEADLINE-180))
    except Exception as error:
        REPORT['failure'] = type(error).__name__+':'+str(error)
        if isinstance(error,subprocess.CalledProcessError):
            REPORT['subprocess_output'] = {'stdout':error.stdout,'stderr':error.stderr}
    finally:
        DONE.set()
        REPORT['seconds'] = time.monotonic()-START
        save()
        print(json.dumps({k:v for k,v in REPORT.items() if k not in ('assets','wheel_licenses','install_output')}),flush=True)


if __name__=='__main__':
    main()
