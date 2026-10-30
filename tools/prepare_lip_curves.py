"""Prepare source-traceable local lip curves from frozen video observations."""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets
from headfoundry.curve_observations import point_to_polyline

CURVES={
    'outer_lower':[61,146,91,181,84,17,314,405,321,375,291],
    'outer_upper':[61,185,40,39,37,0,267,269,270,409,291],
    'inner_lower':[78,95,88,178,87,14,317,402,318,324,308],
    'inner_upper':[78,191,80,81,82,13,312,311,310,415,308],
}
FRAMES=[240,300,630]


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    archive=ROOT/'assets/private/closed-experiments/0303-semantic-video/evidence.zip'
    expected='0c1d4e82a60f6be70bf5d49edb0b0ed056eb085549a4a953e9b65be8df24ec26'
    if digest(archive)!=expected:raise ValueError('Frozen archive hash mismatch')
    manifest=ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    document=json.loads(manifest.read_text())
    records=[r for r in document['inputs'] if r['id']=='real-case-001-video']
    if len(records)!=1 or document['training_allowed'] is not False or document['upload_allowed'] is not False:
        raise ValueError('Local validation authorization required')
    errors=validate_input_assets(dict(document,inputs=records),manifest.parent)
    if errors:raise ValueError(str(errors))
    source_hash=digest(manifest.parent/records[0]['path'])
    if source_hash!='96fb14b83bc35be92bb9a92a90db38f524778c9a2fec930997c37105b8ade892':
        raise ValueError('Original video identity mismatch')
    # Verify chains against the installed public graph; no detector is created.
    from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections as C
    edges={(c.start,c.end) for c in C.FACE_LANDMARKS_LIPS}
    for ids in CURVES.values():
        if not all((a,b) in edges for a,b in zip(ids,ids[1:])):raise ValueError('Lip topology mismatch')
    with zipfile.ZipFile(archive) as z:
        xy=np.load(io.BytesIO(z.read('native-xy.npy')),allow_pickle=False)
        present=np.load(io.BytesIO(z.read('face-present.npy')),allow_pickle=False)
    ledger_path=ROOT/'assets/private/video-observability-0252/report.json'
    if digest(ledger_path)!='d42efcf9df29fd19df4cbe08976f66512bae87ab0ff57a3fe4a7d958472cba78':
        raise ValueError('Frame ledger mismatch')
    ledger=json.loads(ledger_path.read_text())
    values={};counts={}
    for name,ids in CURVES.items():
        curve=xy[np.array(FRAMES)[:,None],np.array(ids)[None,:]]
        if not present[FRAMES].all() or not np.isfinite(curve).all() or (curve<0).any() or (curve>[719,1279]).any():
            raise ValueError('Missing or invalid required curve')
        for frame in curve:
            point_to_polyline(frame,frame) # finite, nondegenerate segment contract
        values[name]=curve
        counts[name]=dict(vertices=len(ids),minimum_segment_px=float(np.linalg.norm(np.diff(curve,axis=1),axis=2).min()))
    out=ROOT/'assets/private/reconstruction-observations-v1'
    if out.exists():raise FileExistsError('Preserve existing observation bundle')
    out.mkdir()
    np.savez_compressed(out/'lip-curves.npz',frames=FRAMES,**values)
    report=dict(status='UNVERIFIED',purpose='local_head_reconstruction_validation',
        source_sha256=source_hash,archive_sha256=expected,manifest_sha256=digest(manifest),
        coordinate_convention='native 720x1280 integer center; archived adapter',
        frames=[dict(ordinal=f,rgb_sha256=ledger['frame_records'][f]['rgb_sha256']) for f in FRAMES],
        curve_ids=CURVES,curves=counts,array_sha256=digest(out/'lip-curves.npz'),
        anatomical_review='pending',visibility_review='pending',covariance='not calibrated',
        limitations='Detector contours are predictions; no rigid material identity or physical precision certified.',
        training_allowed=False,upload_allowed=False,scan_used=False)
    (out/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(status=report['status'],curves=counts,frames=FRAMES),indent=2))


if __name__=='__main__':main()
