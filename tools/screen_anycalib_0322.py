"""Bounded official source/metadata snapshot only;never imports downloaded code."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/anycalib-source-0322'
OUT.mkdir(exist_ok=False)
start=time.monotonic();total=0;responses=[]


def fetch(url,path):
    global total
    remaining=180-(time.monotonic()-start)
    if remaining<=0:raise TimeoutError('whole source snapshot budget')
    request=urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-public-source-screen','Accept':'application/vnd.github+json' if 'api.github.com' in url else 'text/plain'})
    with urllib.request.urlopen(request,timeout=min(20,remaining)) as response:
        content=response.read(min(512*1024,2*1024**2-total)+1)
        if len(content)>512*1024 or total+len(content)>2*1024**2:raise ValueError('source byte budget')
        content.decode('utf8')
        headers={key:response.headers.get(key) for key in ['Content-Type','ETag','Last-Modified']}
    total+=len(content);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    responses.append({'url':url,'path':str(path.relative_to(OUT)).replace('\\','/'),'bytes':len(content),
                      'sha256':hashlib.sha256(content).hexdigest(),'headers':headers})
    return content


try:
    commit=json.loads(fetch('https://api.github.com/repos/javrtg/AnyCalib/commits/main',OUT/'metadata/commit.json'))
    sha=commit['sha']
    tree=json.loads(fetch(f'https://api.github.com/repos/javrtg/AnyCalib/git/trees/{sha}?recursive=1',OUT/'metadata/tree.json'))
    if tree.get('truncated'):raise ValueError('truncated source tree')
    paths=[entry['path'] for entry in tree['tree'] if entry['type']=='blob' and
           (entry['path'] in ['LICENSE','README.md','pyproject.toml'] or
           (entry['path'].startswith('anycalib/') and (entry['path'].endswith('.py') or 'LICENSE' in entry['path'])))]
    for path in paths:
        if '..' in Path(path).parts:raise ValueError('unsafe source path')
        fetch(f'https://raw.githubusercontent.com/javrtg/AnyCalib/{sha}/{path}',OUT/'snapshot'/path)
    state={'status':'TECHNICAL_CHECK_PASSED','scope':'source acquisition only;not model/camera admission',
           'source_sha':sha,'bytes':total,'seconds':time.monotonic()-start,'responses':responses,
           'model_bytes':0,'executed_downloaded_code':False,'human_data_used':False}
except Exception as error:
    state={'status':'REJECT','scope':'source acquisition only','error':repr(error),'bytes':total,
           'seconds':time.monotonic()-start,'responses':responses,'model_bytes':0}
    raise
finally:
    (OUT/'result.json').write_text(json.dumps(state,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in state.items() if k!='responses'},indent=2))
