"""Read-only closeout audit and compact evidence preparation, no deletion."""
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT/'assets/private'
OUT = PRIVATE/'closed-experiments/0348-lingbot'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    physical = PRIVATE/'lingbot-physical-0348'
    receipt = json.loads((physical/'prediction.json').read_text())
    assert sha(physical/'predictions.npz') == receipt['sha256']
    with np.load(physical/'scores.npz', allow_pickle=False) as data:
        rotations = data['poses'][:, :3, :3]
        audit = dict(prediction_sha256=receipt['sha256'],
            rotation_determinants=np.linalg.det(rotations).tolist(),
            rotation_orthogonality_max=float(np.max(np.abs(rotations@rotations.transpose(0,2,1)-np.eye(3)))),
            scored_positive_depth=bool((data['depths'][:,data['support']]>0).all()),
            supported_points=int(data['support'].sum()))
    assert np.allclose(np.linalg.det(rotations), 1, atol=1e-12)
    assert audit['rotation_orthogonality_max'] < 1e-12
    OUT.mkdir(exist_ok=False)
    candidates = list(physical.glob('*'))
    candidates += [p for p in (PRIVATE/'lingbot-entry-0347').glob('*')
                   if p.is_file() and p.suffix in ('.json','.log','.txt')]
    candidates += [p for p in (PRIVATE/'lingbot-source-0346').rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts]
    inventory = []
    with zipfile.ZipFile(OUT/'evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(candidates):
            assert path.stat().st_size < 32*1024**2
            name = path.relative_to(PRIVATE).as_posix()
            archive.write(path, name)
            inventory.append(dict(name=name, bytes=path.stat().st_size, sha256=sha(path)))
    with zipfile.ZipFile(OUT/'evidence.zip') as archive:
        assert archive.testzip() is None
        for entry in inventory:
            assert hashlib.sha256(archive.read(entry['name'])).hexdigest() == entry['sha256']
    audit.update(archive_sha256=sha(OUT/'evidence.zip'),
                 archive_bytes=(OUT/'evidence.zip').stat().st_size, inventory=inventory)
    (OUT/'audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps({k:v for k,v in audit.items() if k != 'inventory'}))
    plan = json.loads((PRIVATE/'closed-experiments/0344-aliked/plan.json').read_text())
    print('PROTECTION_KEYS', list(plan))
    for key,value in plan.items():
        if 'protect' in key:
            print(key, type(value).__name__, len(value), str(value)[:600])

if __name__ == '__main__':
    main()
