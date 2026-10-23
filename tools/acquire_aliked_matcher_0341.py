"""One exact public checkpoint acquisition;never execute checkpoint pickle."""
import collections
import hashlib
import io
import json
import os
from pathlib import Path,PurePosixPath
import pickletools
import sys
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/aliked-matcher-0341'
URL='https://github.com/cvg/LightGlue/releases/download/v0.1_arxiv/aliked_lightglue.pth'
SIZE=47632827
ALLOWED={'collections OrderedDict','torch._utils _rebuild_tensor_v2','torch FloatStorage','torch LongStorage'}

def inspect_zip(source):
    with zipfile.ZipFile(source) as z:
        infos=z.infolist();names=[i.filename for i in infos]
        if len(names)!=len(set(names)) or sum(i.file_size for i in infos)>64*1024**2:
            raise ValueError('duplicate/oversized container')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
                raise ValueError('unsafe member path')
        pickles=[i for i in infos if i.filename.endswith('/data.pkl')]
        if len(pickles)!=1 or pickles[0].file_size>1024**2 or z.testzip() is not None:
            raise ValueError('invalid pickle member or CRC')
        counts=collections.Counter();globals_=set()
        for op,arg,_ in pickletools.genops(z.read(pickles[0])):
            counts[op.name]+=1
            if sum(counts.values())>1000000:raise ValueError('opcode budget exceeded')
            if op.name=='GLOBAL':globals_.add(arg)
            if op.name in ('STACK_GLOBAL','EXT1','EXT2','EXT4','INST','OBJ','NEWOBJ','NEWOBJ_EX'):
                raise ValueError('unsupported executable pickle construct')
        if not globals_.issubset(ALLOWED):raise ValueError('unknown pickle globals:'+str(globals_-ALLOWED))
        return {'members':len(names),'uncompressed_bytes':sum(i.file_size for i in infos),
            'globals':sorted(globals_),'opcode_counts':dict(counts),'pickle_executed':False}

def controls():
    for payload in (b'\x80\x02}q\x00.',b'cos\nsystem\n.'):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:z.writestr('owned/data.pkl',payload)
        data.seek(0)
        if payload.startswith(b'\x80'):
            inspect_zip(data)
        else:
            try:inspect_zip(data)
            except ValueError:pass
            else:raise AssertionError('unsafe global negative control accepted')
    try:inspect_zip(io.BytesIO(b'not a ZIP'))
    except zipfile.BadZipFile:pass
    else:raise AssertionError('malformed container accepted')

def worker():
    controls()
    source=json.loads((ROOT/'assets/private/aliked-preflight-0339/result.json').read_text())
    expected=source['matcher_asset']
    metadata_url='https://api.github.com/repos/cvg/LightGlue/releases/assets/131252166'
    request=urllib.request.Request(metadata_url,headers={'User-Agent':'HeadFoundry-source-bound-acquisition'})
    with urllib.request.urlopen(request,timeout=30) as response:metadata=json.loads(response.read(1024**2))
    if any(metadata[k]!=expected[k] for k in ('id','name','size','browser_download_url')):
        raise ValueError('publisher asset identity changed')
    (OUT/'publisher.json').write_text(json.dumps(metadata,indent=2))
    part=OUT/'aliked_lightglue.part';target=OUT/'aliked_lightglue.pth'
    if part.exists() or target.exists():raise FileExistsError('no overwrite/retry')
    digest=hashlib.sha256();received=0;start=time.monotonic()
    request=urllib.request.Request(URL,headers={'User-Agent':'HeadFoundry-source-bound-acquisition'})
    with urllib.request.urlopen(request,timeout=30) as response,part.open('xb') as stream:
        while True:
            block=response.read(8*1024**2)
            if not block:break
            received+=len(block)
            if received>SIZE:raise ValueError('size limit exceeded')
            stream.write(block);digest.update(block)
    if received!=SIZE:raise ValueError('incomplete publisher bytes')
    actual=digest.hexdigest();publisher=metadata.get('digest')
    if publisher is not None and publisher!='sha256:'+actual:raise ValueError('publisher digest mismatch')
    inspection=inspect_zip(part)
    part.rename(target)
    extractor=ROOT/'assets/private/aliked-assets-0340/aliked-n16.pth'
    if hashlib.sha256(extractor.read_bytes()).hexdigest()!='5be8704840ed662d9d8c561bf7279c222092674e7eb05fd0feab94899e9d82f2':
        raise ValueError('original extractor changed')
    original=hashlib.sha256((ROOT/'docs/experiment-0207-coupled-lip-and-jaw.md').read_bytes()).hexdigest()
    if original!='eebdad1f8c22de9773927ae1e8961ed3159077f84ffff9b14298c0a3290ae8ef':raise ValueError('0207 changed')
    record={'status':'TECHNICAL_CHECK_PASSED','url':URL,'bytes':received,'sha256':actual,
        'publisher_digest':publisher,'trust_basis':'official HTTPS acquisition bound to recorded assetID/name/size;not an independent publisher SHA if null',
        'download_seconds':time.monotonic()-start,'inspection':inspection,'completed_utc':time.time(),
        'protected0207':original,'runtime_imported':False,'physical_precision':'UNVERIFIED'}
    (OUT/'result.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))

if __name__=='__main__':
    if ROOT!=Path('C:/workspace/headfoundry').resolve():raise ValueError('wrong repository')
    OUT.mkdir(exist_ok=True)
    for p in (ROOT,ROOT/'assets',ROOT/'assets/private',OUT):
        if getattr(p.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse target refused')
    if sys.argv[1:]==['worker']:worker()
    else:
        from bounded_process import run
        if (OUT/'worker.json').exists():raise FileExistsError('existing worker receipt')
        result=run([sys.executable,str(Path(__file__).resolve()),'worker'],str(ROOT),dict(os.environ),
            OUT/'worker.log',OUT/'worker.json',180,512*1024**2)
        print(json.dumps(result))
        if result['status']!='TECHNICAL_CHECK_PASSED':raise SystemExit(1)
