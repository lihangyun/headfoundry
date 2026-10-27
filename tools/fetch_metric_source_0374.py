"""Fetch only pinned inference source and license, never run vendor installers."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/metric-runtime-0374/source'
COMMIT='a561b849ebae10a6f5ef49e26c83cbbcd36c71bf'
PREFIX='metric_depth/depth_anything_v2/'


def fetch(url):
    with urllib.request.urlopen(url,timeout=20) as response:
        data=response.read(2*1024**2+1)
    if len(data)>2*1024**2:
        raise ValueError('source response too large')
    return data


def main():
    tree=json.loads(fetch(f'https://api.github.com/repos/DepthAnything/Depth-Anything-V2/git/trees/{COMMIT}?recursive=1'))
    if tree.get('truncated'):
        raise ValueError('incomplete tree')
    names=[entry['path'] for entry in tree['tree'] if entry['type']=='blob' and
           entry['path'].startswith(PREFIX) and entry['path'].endswith('.py')]
    if not 1<=len(names)<=40:
        raise ValueError('unexpected source inventory')
    names+=['LICENSE','README.md','metric_depth/README.md','metric_depth/requirements.txt']
    records={}
    for name in names:
        path=OUT/name
        if OUT.resolve() not in path.resolve().parents:
            raise ValueError('source path escaped')
        url=f'https://raw.githubusercontent.com/DepthAnything/Depth-Anything-V2/{COMMIT}/{name}'
        data=fetch(url)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=data:
            raise ValueError('refuse changed existing source')
        path.write_bytes(data)
        records[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'url':url}
    (OUT/'manifest.json').write_text(json.dumps({'commit':COMMIT,'files':records},indent=2))
    print(json.dumps({'files':len(records),'bytes':sum(x['bytes'] for x in records.values()),'commit':COMMIT}))


if __name__=='__main__':
    main()
