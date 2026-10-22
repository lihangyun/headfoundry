"""Fetch public immutable metadata/source only;no model/runtime/human inputs."""
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/geocalib-source-0313'
REF='1dedb29f94fc11b896c5f572005978aeebccd67f'

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def worker():
    start=time.monotonic()
    fetched=[]
    def get(url,name):
        assert url.startswith(('https://api.github.com/repos/cvg/GeoCalib/',
                               f'https://raw.githubusercontent.com/cvg/GeoCalib/{REF}/'))
        request=urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-public-source-audit'})
        with urllib.request.urlopen(request,timeout=15) as response:
            data=response.read(524289)
            assert len(data)<=524288,'source/metadata byte cap'
        p=OUT/name
        assert p.resolve().is_relative_to(OUT.resolve())
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
        fetched.append(dict(url=url,path=str(p.relative_to(OUT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        assert sum(row['bytes'] for row in fetched)<=2*1024**2
        return data
    tree=json.loads(get(f'https://api.github.com/repos/cvg/GeoCalib/git/trees/{REF}?recursive=1','tree.json'))
    assert not tree.get('truncated',False)
    release=json.loads(get('https://api.github.com/repos/cvg/GeoCalib/releases/tags/v1.0','release.json'))
    candidates=[a for a in release['assets'] if a['name']=='geocalib-pinhole.tar']
    assert len(candidates)==1
    asset=candidates[0]
    assert asset['size']==116074121 and asset['browser_download_url']=='https://github.com/cvg/GeoCalib/releases/download/v1.0/geocalib-pinhole.tar'
    sources=[e['path'] for e in tree['tree'] if e['type']=='blob' and e['path'].startswith('geocalib/') and e['path'].endswith('.py')]
    names=['LICENSE','LICENSE-WEIGHTS','README.md','requirements.txt','pyproject.toml']+sorted(sources)
    imports=set()
    entrypoints=[]
    for name in names:
        parts=PurePosixPath(name).parts
        assert '..' not in parts and not PurePosixPath(name).is_absolute()
        text=get(f'https://raw.githubusercontent.com/cvg/GeoCalib/{REF}/{name}',f'snapshot/{name}').decode('utf-8')
        if name.endswith('.py'):
            parsed=ast.parse(text,filename=name)
            for node in ast.walk(parsed):
                if isinstance(node,ast.Import):imports.update(alias.name for alias in node.names)
                elif isinstance(node,ast.ImportFrom) and node.module:imports.add(node.module)
            for line_no,line in enumerate(text.splitlines(),1):
                if any(term in line for term in ['load_state_dict','torch.load','torch.hub','urlopen','requests.','pretrained=']):
                    entrypoints.append(dict(path=name,line=line_no,text=line.strip()))
    write('fetched.json',fetched)
    result=dict(status='TECHNICAL_CHECK_PASSED',scope='public source/metadata snapshot only;no software/model/physical accuracy admission',
        ref=REF,python_files=len(sources),imports=sorted(imports),entrypoints=entrypoints,
        model_asset={key:asset.get(key) for key in ['id','name','size','digest','created_at','updated_at','browser_download_url']},
        weight_bytes_downloaded=0,publisher_digest='AVAILABLE' if asset.get('digest') else 'UNVERIFIED',
        full_source_execution_review='UNVERIFIED',seconds=time.monotonic()-start)
    write('report.json',result)
    print(json.dumps(result))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        result=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),os.environ.copy(),
            OUT/'worker.log',OUT/'worker.json',120,512*1024**2)
        print(json.dumps(result))
