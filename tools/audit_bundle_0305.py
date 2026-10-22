"""Single frozen endpoint diagnostic;no optimizer/inference/medical input."""
from pathlib import Path
import hashlib
import io
import json
import os
import time
import zipfile

for name in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS']:
    os.environ[name] = '4'

import numpy as np
from bundle_stationarity import audit

root = Path(__file__).resolve().parents[1]
assert Path.cwd().resolve() == root
archive = root/'assets/private/closed-experiments/0304-anatomical-camera/evidence.zip'
expected = 'b4098c99c478dc223c3d489dddb662dce61f4003712585fbf111355d07385a52'
with archive.open('rb') as handle:
    assert hashlib.file_digest(handle, 'sha256').hexdigest() == expected
out = root/'assets/private/bundle-stationarity-0305'
out.mkdir(exist_ok=False)
started = time.monotonic()
result = {'status':'TECHNICAL_CHECK_PASSED', 'archive_sha256':expected}
with zipfile.ZipFile(archive) as source:
    assert source.testzip() is None
    for name, folder in [('procedural', 'control/camera'), ('real_frozen', 'camera')]:
        metadata = json.loads(source.read(folder+'/result.json'))
        with np.load(io.BytesIO(source.read(folder+'/solution.npz')), allow_pickle=False) as arrays:
            frames = [row['frame'] for row in metadata['frames']]
            result[name] = audit(arrays['K'], arrays['poses'], arrays['points'], arrays['train'],
                                 frames.index(metadata['anchor_frame']), frames.index(metadata['baseline_frame']))
        assert result[name]['array_bytes'] <= 128*1024**2
result.update(seconds=time.monotonic()-started, head=False, patient_refit=False, held_fields_read=False)
assert result['seconds'] <= 60
with archive.open('rb') as handle:
    assert hashlib.file_digest(handle, 'sha256').hexdigest() == expected
(out/'report.json').write_text(json.dumps(result, indent=2))
print(json.dumps({key:({k:v for k,v in value.items() if 'singular_values' not in k} if isinstance(value, dict) else value) for key,value in result.items()}))
