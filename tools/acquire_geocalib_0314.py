"""One exact official weight acquisition;no Torch load,model,or human inputs."""
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

from headfoundry.manifest import sha256_file

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/private/geocalib-source-0313'
OUT=ROOT/'assets/private/geocalib-runtime-0314'
REF='1dedb29f94fc11b896c5f572005978aeebccd67f'
URL='https://github.com/cvg/GeoCalib/releases/download/v1.0/geocalib-pinhole.tar'

def validate_plan(plan):
    if plan.get('source_ref')!=REF:
        raise ValueError('wrong source ref')
    rights=plan.get('rights',{})
    if rights.get('code_license')!='Apache-2.0' or rights.get('weight_license')!='CC-BY-4.0':
        raise ValueError('missing/wrong explicit rights')
    for field,filename in [('code_notice','LICENSE'),('weight_notice','LICENSE-WEIGHTS')]:
        notice=rights.get(field,{})
        if not re.fullmatch('[0-9a-f]{64}',notice.get('sha256','')):
            raise ValueError('missing/invalid notice hash')
        if notice.get('url')!=f'https://raw.githubusercontent.com/cvg/GeoCalib/{REF}/{filename}':
            raise ValueError('wrong notice origin')
    asset=plan.get('checkpoint',{})
    if (asset.get('id'),asset.get('name'),asset.get('size'),asset.get('browser_download_url'))!=(191236355,'geocalib-pinhole.tar',116074121,URL):
        raise ValueError('wrong checkpoint;no fallback')

def write(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False))

def worker():
    start=time.monotonic()
    plan=json.loads((SOURCE/'asset-plan.json').read_text())
    validate_plan(plan)
    for row in json.loads((SOURCE/'fetched.json').read_text()):
        assert sha256_file(SOURCE/row['path'])==row['sha256'],row['path']
    for field in ['code_notice','weight_notice']:
        notice=plan['rights'][field]
        assert sha256_file(SOURCE/notice['path'])==notice['sha256']
    request=urllib.request.Request('https://api.github.com/repos/cvg/GeoCalib/releases/assets/191236355',
        headers={'User-Agent':'HeadFoundry-public-asset-audit'})
    with urllib.request.urlopen(request,timeout=30) as response:
        metadata=json.loads(response.read(1048576))
    old=plan['checkpoint']
    for key in ['id','name','size','created_at','updated_at','browser_download_url']:
        assert metadata[key]==old[key],('asset metadata changed',key)
    write('official-asset.json',metadata)
    path=OUT/'geocalib-pinhole.tar'
    download_start=time.monotonic()
    request=urllib.request.Request(URL,headers={'User-Agent':'HeadFoundry-public-asset-audit'})
    count=0
    with urllib.request.urlopen(request,timeout=30) as response,path.open('xb') as destination:
        final_url=response.geturl()
        assert urllib.parse.urlparse(final_url).scheme=='https'
        assert urllib.parse.urlparse(final_url).hostname in {'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'}
        headers=dict(response.headers.items())
        while True:
            data=response.read(1048576)
            if not data:break
            count+=len(data)
            assert count<=116074121 and time.monotonic()-download_start<=240,'transfer bound'
            destination.write(data)
    assert count==116074121
    digest=sha256_file(path)
    archive=[]
    is_zip=zipfile.is_zipfile(path)
    if is_zip:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            archive=[dict(name=m.filename,bytes=m.file_size,compressed=m.compress_size,crc32=m.CRC) for m in z.infolist()]
    write('archive-layout.json',dict(is_zip=is_zip,members=archive,unpickled=False))
    lock=dict(asset_id='cvg-geocalib-v1.0-pinhole-focal-prior',source_repository='https://github.com/cvg/GeoCalib',
        source_ref=REF,code_license='Apache-2.0',weight_license='CC-BY-4.0',rights=plan['rights'],
        checkpoint=dict(url=URL,release_asset_id=191236355,bytes=count,sha256=digest),
        hash_basis='first official HTTPS acquisition;publisher independent digest absent',
        serialized_tensors_verified=False,runtime_admitted=False,physical_accuracy='UNVERIFIED',
        automatic_download_or_fallback=False,role='focal prior only;not SE3or verified capture K')
    write('asset-lock.json',lock)
    write('transfer.json',dict(headers=headers,final_host=urllib.parse.urlparse(final_url).hostname,
        bytes=count,sha256=digest,transfer_seconds=time.monotonic()-download_start,total_seconds=time.monotonic()-start))
    print(json.dumps(dict(status='TECHNICAL_CHECK_PASSED',scope='official byte acquisition/local lock only',
        bytes=count,sha256=digest,is_zip=is_zip,archive_members=len(archive),seconds=time.monotonic()-start)))

if __name__=='__main__':
    if sys.argv[1:]==['worker']:
        worker()
    else:
        from bounded_process import run
        OUT.mkdir(exist_ok=False)
        result=run([sys.executable,str(Path(__file__)),'worker'],str(ROOT),os.environ.copy(),
            OUT/'worker.log',OUT/'worker.json',300,512*1024**2)
        print(json.dumps(result))
