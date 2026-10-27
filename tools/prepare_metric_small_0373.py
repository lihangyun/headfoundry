"""Pinned official Small asset only; no inference or patient data."""
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/metric-small-0373'
MODEL='depth-anything/Depth-Anything-V2-Metric-Hypersim-Small'
NAME='depth_anything_v2_metric_hypersim_vits.pth'


def small(url):
    with urllib.request.urlopen(url,timeout=25) as response:
        data=response.read(2*1024**2+1)
    if len(data)>2*1024**2:
        raise ValueError('metadata size limit')
    return data


def worker():
    api=small(f'https://huggingface.co/api/models/{MODEL}?blobs=true')
    meta=json.loads(api)
    revision=meta['sha']
    card=small(f'https://huggingface.co/{MODEL}/raw/{revision}/README.md')
    if meta.get('cardData',{}).get('license')!='apache-2.0' or b'license: apache-2.0' not in card:
        raise ValueError('checkpoint rights missing or changed')
    entries=[s for s in meta['siblings'] if s['rfilename']==NAME]
    if len(entries)!=1:
        raise ValueError('exact checkpoint missing')
    identity=entries[0]['lfs'];expected=identity['sha256'];size=identity['size']
    if len(expected)!=64 or not 0<size<=150000000:
        raise ValueError('checkpoint identity or size rejected')
    (OUT/'api.json').write_bytes(api);(OUT/'README.md').write_bytes(card)
    url=f'https://huggingface.co/{MODEL}/resolve/{revision}/{NAME}'
    record={'model':MODEL,'revision':revision,'license':'Apache-2.0','url':url,
            'expected_sha256':expected,'bytes':size,'status':'UNVERIFIED','scope':'no inference'}
    (OUT/'manifest.json').write_text(json.dumps(record,indent=2))
    target=OUT/NAME
    if target.exists():
        with target.open('rb') as stream:
            actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=expected or target.stat().st_size!=size:
            raise ValueError('existing asset mismatch; refusing overwrite')
    else:
        partial=OUT/(NAME+'.partial');count=0;digest=hashlib.sha256()
        with urllib.request.urlopen(url,timeout=25) as response,partial.open('xb') as stream:
            while chunk:=response.read(1024**2):
                count+=len(chunk)
                if count>size:
                    raise ValueError('download exceeds declared size')
                digest.update(chunk);stream.write(chunk)
        if count!=size or digest.hexdigest()!=expected:
            raise ValueError('download checksum/size mismatch')
        partial.rename(target)
    record['status']='TECHNICAL_CHECK_PASSED'
    (OUT/'manifest.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        print(run([sys.executable,__file__,'worker'],ROOT,os.environ.copy(),OUT/'worker.log',OUT/'worker.json',180,1024**3))
