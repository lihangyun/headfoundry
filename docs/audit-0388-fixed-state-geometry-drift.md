# 0388: fixed-state geometry drift, not another solve

2026-10-29. Read-only calculation after0387closeoutd96cb6f; budget5minutes.
Only hashed0387archive, existing camera math and NumPy/OpenCV. No original
image/video/scan/case002 access, fitting, new output mesh or model restoration.

Question: does reanchoring each initial BA point to its exact source ray already
explain the training-coordinate drift, or did the photometric optimization add
substantial drift? Compute native training reprojection for exactly four saved
state combinations, all28points/no pruning: originalBA; original cameras with
ray-reanchored original depths (the actual direct objective's starting geometry);
final cameras with those starting world points; final cameras/final points.
Mixed state is sensitivity evidence only, never a proposed reconstruction or
selection between outputs. Do not compute a new held score or change0387REJECT.
Record per-view p95/RMS, point displacement in unit-baseline coordinates,
focal/pose deltas and allpositive depth. None is a millimeter truth measurement.
This can distinguish an initialization representation issue from later drift,
not uniquely identify illumination, nonrigidity or correspondence error.

## Measured fixed-state results

Archive verifiedSHA c4f2d312cff990a7ce930dc1a034f5fb1513885079230dad54d5603054d3655c.
No optimizer was called. All28training points retained, all depths positive.

| State | View0 p95 px | View1 p95 px | View2 p95 px |
| --- | ---: | ---: | ---: |
| Original point-coordinate BA | 0.504834 | 0.906537 | 0.889806 |
| Exact-source-ray start, original depths/cameras | 0 | 0.934304 | 0.966845 |
| Final cameras with starting world points | 0.786857 | 4.611138 | 4.423817 |
| Final cameras and final points | 0 | 61.960572 | 50.014823 |

These are discrepancies against frozen training observations, NOT physical
groundtruth. Final-point movement relative to ray-start p95=.112215014 unit
baseline; initial ray-reanchor movement p95=.000589287. No millimeter conversion.
Focal delta=-6.202544px; pose rotation deltas0/.169687/.381275degrees,
translation norms0/.002059/.022745 baselineunits. The mixed-state calculation
is not an additive decomposition or a valid candidate. It demonstrates that
camera change alone at fixed starting points does not account for the much
larger final training discrepancies; point-depth changes matter substantially.

## Confirmed implementation mechanism and limits

Read0332optimize/direct_patch_camera.residual: source point is constrained to
its source ray, but target observed coordinates are not residuals or constraints
in the direct objective. They initialize depth/cameras only. Per-pointlogdepth
box+/-0.3 does not bound target pixel motion. The eight-offset photometric loss
can decrease while the sample moves tens of pixels away from its measured
correspondence. The saved state confirms that this freedom was actually used;
it is not merely a hypothetical issue or an initial ray-conversion bug.

Combined with0387held degradation, this rejects treating that pure photometric
transfer as a safe refinement of the observation-based solution. It does not
prove every original match is correct, or establish which illumination/shape/
texture/nonrigidity term caused a lower-cost location. Do not label the drift
as independently measured3Derror. Current3px/2mmgates and0387REJECT unchanged.

Actionable next design question: retain observation consistency explicitly
while introducing image evidence, instead of discarding the former objective.
This requires a prospectively specified constrained formulation and a bias
control (wrong original observations must not become presumed truth), not a
weight sweep or shrinking0387depthbounds after seeing failure. Existing
photometric-only candidate is not rerun by this audit; no formalhead fit starts.

### Minimal read-only replay (from repository root)

```python
import io, zipfile, hashlib
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, 'tools')
from short_track_camera import project
p = Path('assets/private/closed-experiments/0387-real-photo/evidence.zip')
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'c4f2d312cff990a7ce930dc1a034f5fb1513885079230dad54d5603054d3655c'
with zipfile.ZipFile(p) as z:
    def load(n): return dict(np.load(io.BytesIO(z.read(n)), allow_pickle=False))
    a, b, o = load('initial.npz'), load('final.npz'), load('observations.npz')
xy = o['xy'][:, o['train']]
rows = np.array([[c,i,*xy[c,i]] for c in range(3) for i in range(xy.shape[1])])
x = np.c_[(xy[0]-a['K'][:2,2])/a['K'][0,0], np.ones(xy.shape[1])] * a['points'][:,2,None]
states = [(a['K'],a['poses'],a['points']), (a['K'],a['poses'],x),
          (b['K'],b['poses'],x), (b['K'],b['poses'],b['points'])]
for k, poses, points in states:
    uv, depth = project(k, poses, points, rows)
    print(np.percentile(np.linalg.norm(uv.reshape(xy.shape)-xy,axis=2),95,axis=1), bool((depth>0).all()))
```

No exclusive runner, loose output, weight or environment created. Original
archive remains the evidence and replay source; report is the only new file.
