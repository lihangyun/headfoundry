# Audit0281: frozen control-camera handedness,no solver rerun

Registered2026-10-21T07:58:00Z,budget300s.0280 closed atd8ccc39. Audit only,
not a new reconstruction or permission to restore the rejected initializer.

Verify0280 archive SHAa5255d4529a172fa9a344ed1a477222b11db18aa68f8103bba764ca877ec291a.
Read only its saved five synthetic control rotations. Recreate the prospectively
specified true rotations algebraically,no image/point observation or solver run.
Compare each camera's relative rotation R_i R_0^T to true relative motion and
to S R_true_relative S,where S=diag(1,1,-1). Report ALL five angular differences,
not selected views. S conjugation preserves proper rotations while reversing
depth handedness;it is not a global proper-rotation gauge. This tests a specific
ambiguity hypothesis on saved output,not physical patient error. Missing archive,
hash/shape/nonfinite/improper rotations stop. No inference,BA,reinitialization,
branch-selection replay,new environment,human file read or parameter sweep.

Interpretation must remain conditional. A closer reflected branch is evidence
of orientation ambiguity in this output,not proof of the sole failure cause or
successful repair. If neither branch fits,do not force that diagnosis. Keep a
small replayable arithmetic command/result in this document;no failed binary
or integration needs restoring. All actual3px/2mm/head/visual gates unchanged.

## Actual read-only result

Archive SHA/CRC and finite proper5x3x3rotation checks pass. Camera0 is the fixed
gauge identity,not an independent accuracy observation. For cameras1..4:

|Camera|True-relative rotation error,deg|Depth-reflected-relative error,deg|
|---|---:|---:|
|1|43.915129|0.511412|
|2|70.995916|0.585327|
|3|106.661715|1.022431|
|4|145.307639|1.393480|

This strongly supports a depth-reflected pose branch in the frozen0280 output.
It does not prove the affine initializer already had that branch(the archive
does not retain its pre-BA cameras),a sole cause,or convergence after correction.
The focal bound and positive depths did not expose this orientation failure.
Do not call it repaired or relabel0280. Next experimental justification should
address this discrete structural ambiguity before any actual-video fit,not
rescue by focal bounds/iterations/thresholds. No new patient error or head exists.

Replay from repository with its existing Python/NumPy/SciPy (standard imports
plus the following arithmetic;no deleted runner required):

```python
import io, zipfile, hashlib, numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
p = Path('assets/private/closed-experiments/0280-global-factorization/evidence.zip')
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'a5255d4529a172fa9a344ed1a477222b11db18aa68f8103bba764ca877ec291a'
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    est = np.load(io.BytesIO(z.read('control-evaluation.npz')), allow_pickle=False)['rotations']
assert est.shape == (5, 3, 3) and np.isfinite(est).all()
assert np.max(abs(np.linalg.det(est)-1)) < 1e-10
truth = Rotation.from_euler('yx', np.c_[[-35,-17,0,19,37],[-8,5,0,-4,7]], degrees=True).as_matrix()
er, tr = est @ est[0].T, truth @ truth[0].T
s = np.diag([1., 1., -1.])
for target in (tr, s @ tr @ s):
    print(np.rad2deg(Rotation.from_matrix(er @ target.transpose(0,2,1)).magnitude()))
```

Only this document/README changes;no source/runtime/default/input mutation,
solver/model execution,new generated file or cleanup is needed. Existing137
shared test result remains0280's historical result,not a newly executed test.
