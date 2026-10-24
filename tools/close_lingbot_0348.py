"""Read-only closeout audit and compact evidence preparation, no deletion."""
import hashlib
import json
from pathlib import Path
import zipfile
import csv
import io
import os
import shutil
import stat
import subprocess
import sys
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

def cleanup():
    audit = json.loads((OUT/'audit.json').read_text())
    assert sha(OUT/'evidence.zip') == audit['archive_sha256']
    with zipfile.ZipFile(OUT/'evidence.zip') as archive:
        assert archive.testzip() is None
    basis = PRIVATE/'closed-experiments/0344-aliked/plan.json'
    assert sha(basis) == '275fc10f129ae4b5300454edb3e29976ae3623c3c6d438a16c09d7d51ce6f7a4'
    protected = json.loads(basis.read_text())['protected']
    def verify_protected():
        for entry in protected:
            assert sha(Path(entry['path'])) == entry['sha256'], entry['path']
    verify_protected()
    targets = [PRIVATE/'lingbot-source-0346', PRIVATE/'lingbot-entry-0347',
               PRIVATE/'lingbot-physical-0348', ROOT/'.venv-lingbot-0347']
    paths = []
    for target in targets:
        assert target.resolve().is_relative_to(ROOT) and target != ROOT
        assert not target.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
        for folder, dirs, files in os.walk(target, followlinks=False):
            for name in dirs+files:
                path = Path(folder)/name
                assert not path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT, str(path)
                assert path.resolve().is_relative_to(target.resolve()), str(path)
            paths.extend(Path(folder)/name for name in files)
    tasks = subprocess.check_output(['tasklist','/FO','CSV','/NH']).decode('mbcs')
    live = {int(row[1]) for row in csv.reader(io.StringIO(tasks)) if len(row)>1}
    checked = []
    for receipt in paths:
        if receipt.name.endswith('worker.json') and '.venv-lingbot-0347' not in receipt.parts:
            record = json.loads(receipt.read_text())
            assert record['status'] != 'RUNNING'
            pids = {record['pid']} | {int(p) for p in record.get('observed_process_peaks', {})}
            assert not pids & live, (receipt, pids & live)
            checked.extend(sorted(pids))
    report = dict(status='PREPARED', targets=[str(p) for p in targets],
        file_count=len(paths), logical_bytes=sum(p.stat().st_size for p in paths),
        protected_count=len(protected), terminal_pids=checked,
        evidence_sha256=audit['archive_sha256'], source_recovery='692739f')
    (OUT/'cleanup.json').write_text(json.dumps(report, indent=2))
    for target in targets:
        shutil.rmtree(target)
    verify_protected()
    assert all(not p.exists() for p in targets)
    report['status'] = 'DELETED_AND_PROTECTED_HASHES_VERIFIED'
    (OUT/'cleanup.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report))

if __name__ == '__main__':
    if sys.argv[1:] == ['--cleanup']:
        cleanup()
    else:
        main()
