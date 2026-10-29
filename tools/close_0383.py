"""Compact failed experiment evidence without deleting originals."""
from pathlib import Path
import hashlib,json,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/private/roma-video-0383'
DEST=ROOT/'assets/private/closed-experiments/0383-roma-video'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
raw=np.load(OUT/'raw-observations.npz',allow_pickle=False)
summary={str(c):{'admitted':int(raw[f'admitted_{c}'].sum()),'fb_median_px':float(np.median(raw[f'fb_{c}'])),'fb_p95_px':float(np.percentile(raw[f'fb_{c}'],95))} for c in (1,2)}
q=raw['query'][raw['admitted_all']]
result=dict(status='REJECT',stage='observation_coverage',queries=len(raw['query']),complete=len(q),required=48,pairs=summary,complete_source_span_px=np.ptp(q,axis=0).tolist(),camera_solved=False,medical_accuracy='UNVERIFIED',head_produced=False,scope='entry failure, not measured physical correspondence/camera failure')
(OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json';document=json.loads(manifest.read_text())
source=Path(next(r['path'] for r in document['inputs'] if r['id']=='real-case-001-video'))
protected=[manifest,manifest.parent/'provenance-confirmation.json',ROOT/'assets/private/video-observability-0252/report.json',source,ROOT/'docs/experiment-0207-coupled-lip-and-jaw.md',ROOT/'tools/dense_photo_0332.py']
hashes={str(p):sha(p) for p in protected}
inputs=json.loads((OUT/'inputs.json').read_text())
assert hashes[str(source)]==inputs['source_sha256'] and hashes[str(manifest)]==inputs['manifest_sha256']
assert hashes[str(protected[1])]==inputs['consent_sha256'] and hashes[str(protected[2])]==inputs['ledger_sha256']
DEST.mkdir(exist_ok=False)
members=[p for p in OUT.rglob('*') if p.is_file() and (p.parent==OUT and (p.suffix in ('.json','.log') or p.name in ('raw-observations.npz','inputs.png','tracks.png')) or p.parent.name in ('notices','preimport-failure-1'))]
members += [ROOT/'tools'/n for n in ('install_roma_0383.py','roma_infer_0383.py','roma_video_0383.py','close_0383.py')]
index={}
with zipfile.ZipFile(DEST/'evidence.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in members:
        name=p.relative_to(OUT).as_posix() if p.is_relative_to(OUT) else 'source/'+p.name
        z.write(p,name);index[name]={'bytes':p.stat().st_size,'sha256':sha(p)}
with zipfile.ZipFile(DEST/'evidence.zip') as z:
    assert z.testzip() is None
    for name,record in index.items():assert hashlib.sha256(z.read(name)).hexdigest()==record['sha256']
receipt=dict(archive_sha256=sha(DEST/'evidence.zip'),archive_bytes=(DEST/'evidence.zip').stat().st_size,members=index,protected=hashes,result=result)
(DEST/'index.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k not in ('members','protected')},indent=2))
