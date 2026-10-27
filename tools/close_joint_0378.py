"""Archive only; deletion separately uses exact validated paths."""
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/private/joint-local-0378'
OUT = ROOT / 'assets/private/closed-experiments/0378-joint-local'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

OUT.mkdir(exist_ok=False)
files = sorted(SOURCE.iterdir())
assert all(p.is_file() and not p.is_symlink() for p in files)
partition = ROOT / 'assets/private/archived-geometry-0352/partition.npz'
original = dict(np.load(partition, allow_pickle=False))
changed = dict(np.load(SOURCE/'refined.npz', allow_pickle=False))
assert np.array_equal(changed['original_xy'], original['xy'])
assert np.array_equal(changed['xy'][:, original['held']], original['xy'][:, original['held']])
assert np.array_equal(changed['xy'][0], original['xy'][0])
assert json.loads((SOURCE/'result.json').read_text())['status'] == 'REJECT'
protected = [partition, ROOT/'assets/private/closed-experiments/0344-aliked/evidence.zip',
    ROOT/'assets/private/real-capture-pilot-v1/manifest.json',
    ROOT/'assets/private/real-capture-pilot-v1/provenance-confirmation.json',
    ROOT/'assets/private/video-observability-0252/report.json',
    ROOT/'docs/experiment-0207-coupled-lip-and-jaw.md']
members = {p.name:p for p in files}
members['recovery-source/joint_local_0378.py'] = ROOT/'tools/joint_local_0378.py'
members['recovery-source/close_joint_0378.py'] = Path(__file__)
digests = {name:sha(p) for name,p in members.items()}
archive = OUT/'evidence.zip'
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
    for name,p in members.items():
        z.write(p, name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in digests.items())
record = dict(archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
    members_sha256=digests, original_outputs={str(p):sha(p) for p in files},
    output_bytes=sum(p.stat().st_size for p in files),
    protected={str(p):sha(p) for p in protected},
    held_and_root_unchanged=True, scientific_status='REJECT', source_recovery='e23b911')
with (OUT/'verification.json').open('x') as stream:
    json.dump(record, stream, indent=2)
print(json.dumps({k:v for k,v in record.items() if k not in ('members_sha256','protected','original_outputs')},indent=2))
