"""One fixed official checkpoint;no torch,pickle execution or human-data access."""
import hashlib
import json
import os
from pathlib import Path
import pickletools
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile

from bounded_process import run

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/private/anycalib-source-0322'
OUT=ROOT/'assets/private/anycalib-asset-0323'
NAME='anycalib_edit.pt'
SIZE=1281194246
URL='https://github.com/javrtg/AnyCalib/releases/download/v1.0.0/'+NAME


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf8')


def worker():
    start=time.monotonic()
    original=json.loads((SOURCE/'result.json').read_text())
    metadata=json.loads((SOURCE/'source-audit.json').read_text())
    if (original['source_sha']!='027a8497d893f4b2596f23d6324c05e4b81064ed' or
        metadata['release_asset_id']!=238336622 or metadata['asset_size']!=SIZE or metadata['asset_url']!=URL):
        raise ValueError('fixed source/asset identity mismatch')
    for row in original['responses']+json.loads((SOURCE/'notices.json').read_text()):
        if sha(SOURCE/row['path'])!=row['sha256']:raise ValueError('source/grant/notice bytes changed')
    readme=(SOURCE/'snapshot/README.md').read_text(encoding='utf8')
    if 'Code and weights are provided under the [Apache 2.0 license](LICENSE).' not in readme:
        raise ValueError('explicit code AND weight grant missing')
    if not (SOURCE/'snapshot/LICENSE').read_text().lstrip().startswith('Apache License'):
        raise ValueError('Apache grant missing')
    expected_sha=None;hf_record={'status':'UNVERIFIED','lfs_sha256':None}
    metadata_url='https://huggingface.co/api/models/javrtg/AnyCalib/tree/main'
    try:
        request=urllib.request.Request(metadata_url,headers={'User-Agent':'HeadFoundry-fixed-asset-entry'})
        with urllib.request.urlopen(request,timeout=20) as response:content=response.read(256*1024+1)
        if len(content)>256*1024:raise ValueError('HFmetadata budget')
        rows=json.loads(content);matches=[row for row in rows if row.get('path')==NAME]
        (OUT/'hf-metadata.json').write_bytes(content)
        if len(matches)==1:
            row=matches[0];lfs=row.get('lfs',{});value=lfs.get('oid')
            if row['size']!=SIZE:raise ValueError('official HF size conflicts with fixed GitHub asset')
            if value is not None:
                if len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise ValueError('invalid LFS SHA')
                expected_sha=value
            hf_record={'status':'TECHNICAL_CHECK_PASSED' if value else 'UNVERIFIED',
                'lfs_sha256':value,'file_metadata':row,'response_sha256':hashlib.sha256(content).hexdigest()}
    except (OSError,TimeoutError,json.JSONDecodeError) as error:
        hf_record['unavailable']=type(error).__name__+':'+str(error)
    save('entry.json',{'epoch':time.time(),'source_sha':original['source_sha'],'asset_id':238336622,
        'asset_name':NAME,'asset_size':SIZE,'github_digest':metadata['publisher_digest'],'hf':hf_record,
        'weight_bytes_before_download':0,'rights':'publisher Apache2code AND weight grant,not code-only inference'})
    request=urllib.request.Request(URL,headers={'User-Agent':'HeadFoundry-fixed-asset-entry'})
    total=0;digest=hashlib.sha256();first=b''
    with urllib.request.urlopen(request,timeout=30) as response,(OUT/(NAME+'.part')).open('xb') as stream:
        parsed=urllib.parse.urlsplit(response.url)
        if parsed.scheme!='https' or parsed.hostname not in ['github.com','release-assets.githubusercontent.com',
                'objects.githubusercontent.com','github-releases.githubusercontent.com']:
            raise ValueError('nonofficial checkpoint delivery redirect')
        length=response.headers.get('Content-Length')
        if length is not None and int(length)!=SIZE:raise ValueError('unexpected published download length')
        while True:
            block=response.read(1024*1024)
            if not block:break
            if not first:first=block[:4]
            total+=len(block)
            if total>SIZE or time.monotonic()-start>580:raise ValueError('download byte/time budget')
            stream.write(block);digest.update(block)
        stream.flush();os.fsync(stream.fileno())
    actual=digest.hexdigest()
    if total!=SIZE or first!=b'PK\x03\x04':raise ValueError('incomplete or nonZIP checkpoint')
    if expected_sha is not None and actual!=expected_sha:raise ValueError('official LFS/GitHub byte identities conflict')
    path=OUT/NAME;(OUT/(NAME+'.part')).rename(path)
    with zipfile.ZipFile(path) as archive:
        entries=archive.infolist();names=[entry.filename for entry in entries]
        if len(names)!=len(set(names)) or any('..' in Path(name).parts or name.startswith(('/', '\\')) or ':' in name for name in names):
            raise ValueError('unsafe/duplicate checkpoint members')
        if sum(entry.file_size for entry in entries)>SIZE*1.05:raise ValueError('unexpected inflated archive')
        if archive.testzip() is not None:raise ValueError('checkpoint CRC failure')
        pickle_names=[name for name in names if name.endswith('/data.pkl')]
        if len(pickle_names)!=1 or archive.getinfo(pickle_names[0]).file_size>2*1024**2:
            raise ValueError('unexpected checkpoint metadata')
        data=archive.read(pickle_names[0]);globals_=[];tensor_keys=[]
        allowed={'collections OrderedDict','torch._utils _rebuild_tensor_v2','torch FloatStorage','torch LongStorage',
                 'torch IntStorage','torch DoubleStorage','torch HalfStorage','torch BFloat16Storage','torch ByteStorage',
                 'torch BoolStorage','torch ShortStorage','torch CharStorage'}
        for opcode,arg,_ in pickletools.genops(data):
            if opcode.name=='GLOBAL':
                globals_.append(arg)
                if arg not in allowed:raise ValueError('unexpected pickle GLOBAL:'+str(arg))
            elif opcode.name in ['STACK_GLOBAL','EXT1','EXT2','EXT4','INST','OBJ','NEWOBJ','NEWOBJ_EX']:
                raise ValueError('unsupported executable pickle metadata:'+opcode.name)
            elif opcode.name in ['BINUNICODE','SHORT_BINUNICODE'] and isinstance(arg,str) and any(arg.startswith(prefix) for prefix in ('backbone.','decoder.','head.')):
                tensor_keys.append(arg)
        (OUT/'data.pkl-opcodes.txt').write_text('\n'.join(str(row) for row in pickletools.genops(data)),encoding='utf8')
    save('result.json',{'status':'TECHNICAL_CHECK_PASSED','scope':'acquired byte/ZIP/opcode metadata only',
        'asset_name':NAME,'asset_bytes':total,'asset_sha256':actual,'publisher_hf_lfs_sha256':expected_sha,
        'identity_basis':'official HF LFS/GitHub cross-check' if expected_sha else 'TOFU official HTTPS acquisition',
        'zip_members':len(entries),'pickle_globals':sorted(set(globals_)),'candidate_state_key_strings':len(tensor_keys),
        'pickle_metadata_sha256':hashlib.sha256(data).hexdigest(),'seconds':time.monotonic()-start,
        'state_compatible':'UNVERIFIED','tensor_finite':'UNVERIFIED','loaded_model':'UNVERIFIED',
        'physical_camera_head_medical':'UNVERIFIED','human_data_used':False})


if __name__=='__main__':
    if len(sys.argv)==1:
        OUT.mkdir(exist_ok=False)
        record=run([sys.executable,str(Path(__file__).resolve()),'worker'],str(ROOT),os.environ.copy(),
            OUT/'worker.log',OUT/'worker.json',600,128*1024**2)
        print(json.dumps(record,indent=2))
    else:
        try:worker()
        except Exception as error:
            save('failure.json',{'status':'REJECT','error':repr(error),'epoch':time.time()})
            raise
