"""Small official source/license snapshot, no checkpoint or inference."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/public/depthpro-source-audit-0372'
COMMIT='9e65e4dbe9568d23c546fcec53302b10445e109e'
FILES=['LICENSE','README.md','ACKNOWLEDGEMENTS.md','pyproject.toml',
       'src/depth_pro/depth_pro.py','src/depth_pro/utils.py','get_pretrained_models.sh']


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if __import__('sys').argv[1:]==['model-license']:
        url='https://huggingface.co/apple/DepthPro/raw/main/LICENSE'
        with urllib.request.urlopen(url,timeout=20) as response:
            data=response.read(1024*1024+1)
        if len(data)>1024*1024:
            raise ValueError('license budget exceeded')
        (OUT/'HF-LICENSE.txt').write_bytes(data)
        evidence={'url':url,'sha256':hashlib.sha256(data).hexdigest(),
                  'bytes':len(data),'decision':'REJECT HF checkpoint; conflicting GitHub grant remains UNVERIFIED'}
        (OUT/'model-license.json').write_text(json.dumps(evidence,indent=2))
        print(json.dumps(evidence,indent=2))
        return
    record={'commit':COMMIT,'scope':'public source audit only; no weights or human inputs','files':{}}
    for name in FILES:
        url=f'https://raw.githubusercontent.com/apple/ml-depth-pro/{COMMIT}/{name}'
        with urllib.request.urlopen(url,timeout=20) as response:
            data=response.read(1024*1024+1)
        if len(data)>1024*1024:
            raise ValueError('source budget exceeded')
        path=OUT/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        record['files'][name]={'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    request=urllib.request.Request('https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt',method='HEAD')
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            record['checkpoint_head']={'status':response.status,'content_length':response.headers.get('Content-Length'),
                                       'etag':response.headers.get('ETag'),'url':response.url}
    except Exception as error:
        record['checkpoint_head']={'status':'UNVERIFIED','error':str(error)}
    (OUT/'manifest.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
