"""Metadata/import audit of the pinned source snapshot;no model execution."""
import ast
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/private/anycalib-source-0322'
source=OUT/'snapshot'
original=json.loads((OUT/'result.json').read_text())
rows=[];imports=set();interesting=[];notices=[]
for row in original['responses']:
    path=OUT/row['path']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('source identity mismatch')
for path in sorted(source.rglob('*.py')):
    content=path.read_text(encoding='utf8');tree=ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):imports.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:imports.add(node.module.split('.')[0])
    for i,line in enumerate(content.splitlines()):
        if any(token in line for token in ['load_state_dict','torch.load','http','copyright','Copyright','license','License','xformers']):
            interesting.append({'path':str(path.relative_to(source)).replace('\\','/'),'line':i+1,'text':line})
        if any(token in line for token in ['Copyright','copyright','License','license']):
            notices.append({'path':str(path.relative_to(source)),'line':i+1,'text':line})
url='https://api.github.com/repos/javrtg/AnyCalib/releases/tags/v1.0.0'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-public-source-screen'}),timeout=20) as response:
    content=response.read(256*1024+1)
    if len(content)>256*1024:raise ValueError('release metadata budget')
(OUT/'metadata/release-v1.0.0.json').write_bytes(content)
release=json.loads(content)
selected=[asset for asset in release['assets'] if asset['name']=='anycalib_edit.pt']
if len(selected)!=1:raise ValueError('fixed edit asset not unique')
asset=selected[0]
record={'status':'TECHNICAL_CHECK_PASSED','scope':'source/asset metadata only','source_sha':original['source_sha'],
        'release_tag':release['tag_name'],'release_asset_id':asset['id'],'asset_name':asset['name'],
        'asset_size':asset['size'],'publisher_digest':asset.get('digest'),'asset_url':asset['browser_download_url'],
        'metadata_sha256':hashlib.sha256(content).hexdigest(),'all_source_import_roots':sorted(imports),
        'interesting_lines':interesting,'notices':notices,'model_bytes':0,'epoch':time.time()}
(OUT/'source-audit.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in record.items() if k not in ['notices']},indent=2))

notice_urls={
    'dinov2-Apache2.txt':'https://raw.githubusercontent.com/facebookresearch/dinov2/e1277af2ba9496fbadf7aec6eba56e8d882d1e35/LICENSE',
    'DPT-MIT.txt':'https://raw.githubusercontent.com/isl-org/DPT/f43ef9e08d70a752195028a51be5e1aff227b913/LICENSE',
    'RAFT-BSD3.txt':'https://raw.githubusercontent.com/princeton-vl/RAFT/3fa0bb0a9c633ea0a9bb8a79c576b6785d4e6a02/LICENSE',
    'OpenCap-Apache2.txt':'https://raw.githubusercontent.com/stanfordnmbl/opencap-core/main/LICENSE',
}
notice_rows=[]
for name,url in notice_urls.items():
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HeadFoundry-public-source-screen'}),timeout=20) as response:
        content=response.read(32*1024+1)
    if len(content)>32*1024:raise ValueError('notice byte budget')
    content.decode('utf8');path=OUT/'notices'/name;path.parent.mkdir(exist_ok=True);path.write_bytes(content)
    notice_rows.append({'url':url,'path':'notices/'+name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
(OUT/'notices.json').write_text(json.dumps(notice_rows,indent=2),encoding='utf8')
print('Retained upstream notices',len(notice_rows))
