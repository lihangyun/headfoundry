# Experiment0210: cross-source3D surface registration

Pre-registered2026-10-14 before target generation or fitting. This follows0208's
missing cross-source coverage gate, not a rerun of its easy same-GNM oracle.
It follows0209's rejection without increasing that model's size or tokens.
No subject images, camera estimation, training or default replacement.

## Question and frozen design

Can the existing first30 GNM directions plus the **unchanged**64/192 geodesic
patch residual fit a structurally different, already licensed3D head surface
without implausible shape/mesh or protected-view regressions? Target geometry
is FLAME2023 **Open**, not standard FLAME, its texture model, registered scans,
or external landmark assets. Use the existing fail-closed NumPy asset adapter
and pinned repaired GNM exterior/closure from0208. Disclose FLAME attribution
and identity-only conversion; keep target/derived geometry local and out of Git.

Four development cases: Open mean plus three300-D identity samples, seed20261015,
standard-normal coefficients times0.7, clipped to+/-3. Deterministically halve
whole identity displacement only for target safety: zero reversals, area>=0.5,
max displacement<=0.12 fixed target-mean radius; max ten halvings. These are
cross-model synthetic heads, **not independent human scans or photo truth**.

Initial isotropic similarity matches mean-template bounding-box height/center
in native common y-up/z-forward axes. Refine only seven nuisance pose/scale
parameters against target surface points: ten fixed closest-point updates,
rotation-vector components bounded+/-0.14rad, translations+/-0.08 radius,
log-scale+/-0.08. Use source facial semantic regions, compatible normals and
90% distance trimming. Freeze that same per-case alignment before both fits.
No camera or per-view normalization changes afterward.

Observe200000 deterministic area-uniform target surface points with normals.
The different vertex topology means there are **no true material correspondences**;
nearest compatible surface matches are explicitly an estimated part of this
registration diagnostic. Exclude lower15% of mean-height target/source neck from
matching; source neck gets a fourfold fixed-rest weight. Report this scope/cut.

Baseline: ten closest-surface updates with first30 identity directions, bounded
coefficients+/-3 and ridge1e-6. Candidate: baseline plus ten updates through the
existing64/192 patch fields, ridge1e-6. No new basis/node/regularization tuning.
Each update may take at most twelve deterministic half-steps for source-relative
area>=0.5, zero normal reversals, displacement<=0.12 radius; a zero safe update
stops that solve. This is predeclared constrained optimization, not post-fit
shrinking to conceal a failed export. Record every update/half-step.

## Independent evaluation and stop rule

Use500000 disjoint target surface samples and fresh200000 uniform samples of
each actual final exported source surface. Distances are **sampled surface
proximity**, not exact Hausdorff distance or known anatomical correspondence.
Report forward/reverse RMS and p95, plus fixed source nose/lip/chin-region errors.
Target/source facial region names are not assumed interchangeable.

Advancement requires all four candidates mesh-safe, no nose/lip/chin or any of
five fixed-view surface-depth errors worsening>5% (numeric tolerance1e-8 radius),
and at least three cases reducing symmetric surface RMS>=30% over the first30
baseline. Final-front/both-obliques/both-profiles white meshes and nose-lip-chin
crops must show meaningful target-shape recovery, with no obvious lip/eye/neck
defect. Numeric proximity alone never establishes anatomy, intersection freedom,
real-photo likeness or KeenTools parity. No default promotion in this experiment.

Budget: <=15 minutes preparation/fitting, <=15 minutes rendering/review. One
main run; at most one correction rerun **only** for an identified implementation
error, never a quality miss. If it fails, freeze this exact closest-point patch
scheme; do not retune node counts, masks, ridge, identity amplitude or iteration
limits, and do not feed it to the five independent AI reference images.

## Results

Completed one fitting run in270.230s. No fitting rerun, parameter sweep or
post-fit shape shrinking. Four target cases: mean at scale1; the three sampled
identities each needed the predeclared safety scale0.25. They are development
targets from one different model family, not four independent scans.

| Case | First30 symmetric sampled RMS / radius | Local candidate | Reduction |
|---|---:|---:|---:|
| 00 | 0.0419611 | 0.0362695 | 13.56% |
| 01 | 0.0401539 | 0.0344318 | 14.25% |
| 02 | 0.0437827 | 0.0378772 | 13.49% |
| 03 | 0.0410266 | 0.0354013 | 13.71% |

All four pass the relative regional/depth non-regression checks, but **0/4 meet
the30% symmetric-distance gain gate**. Mean RMS0.0417311→0.0359949. Nose/chin
proximity improves, especially chin, while lips change much less; these are
estimated nearest-surface matches, not proof that anatomical features correspond.

### One export correctness repair, not a new fit

The actual eight-decimal OBJ audit rejects case02 at minimum area ratio
0.499999637<0.5. Replaying the saved identity and patch coefficients reconstructs
the original fitted field; every coordinate differs from the eight-decimal export
by <=5.0000e-9 radius. The identical pre-export case02 has area ratio0.500000203.
This identifies decimal serialization, not a reason to relax the safety gate.

Add an optional17-decimal writer (legacy default precision remains8), a small
export regression test, and `--repair-export`. The repair recovers the same field
from original saved coefficients and writes a separate
`artifacts/experiment-0210-export-corrected/` capsule. **No optimization, coefficient
change, halving, pose update or topology edit occurs during this repair.** The
original failed files/report remain intact. All four corrected actual exports
pass the implemented guards: minimum area0.500000203, no reversed triangles,
maximum displacement0.087404 radius. This is not a collision/anatomy certificate.

The corrected capsule explicitly labels its numeric scores as the **original
eight-decimal mesh evaluation**, not recomputed or improved scores. It conservatively
retains `numeric_gate=REJECT`. The tiny precision repair is not counted as a
new gain or used to rescue the failed30% gate. Actual17-decimal white meshes are
rendered and inspected separately. Future fresh runs export17 decimals directly.

### Actual visual decision: REJECT and freeze

Reused fixed-camera Blender tooling generates60 actual renders (4 cases x3
surfaces x5 views) in19.811s. Maximum projection replay0.000118px. Review includes
case00's full five-view sheet and the all-four bilateral nose-lip-chin sheet.
Left column is the FLAME Open target, middle the GNM30 prior, right the local
candidate; all share camera, light, geometry scale and crops, with no shape
exaggeration or independent normalization.

The nose/chin changes do move toward the target, but the candidate develops
visible posterior-head/ear-to-neck kinks and neck folds; orbital/aperture and
mouth shape still differ. Thus natural whole-head form fails even though all
final triangle area/orientation guards pass. A continuous field and positive
triangles are insufficient protection against unnatural curvature. The different
aperture topology and estimated correspondences are additional confounds; the
experiment does **not** establish that every GNM representation, registration
method or use of local residuals is incapable of matching the target.

- Execution/export-repair checks: `TECHNICAL_CHECK_PASSED`;120 public tests pass.
- This fixed nearest-compatible-surface/patch registration scheme: `REJECT`.
- Photo likeness, real-scan identity and KeenTools parity: `UNVERIFIED`.
- Default promotion: `REJECT`; subject head/cameras remain unchanged.

**Stop:** freeze this scheme. No node/ridge/mask/iteration sweep, post-fit
smoothing or migration to the five independently generated AI reference images.
The current evidence does not justify a more expensive version of the same fit.

### Next distinct lead, not yet a geometry result

A read-only audit finds an untried anatomical alternative in the **same pinned
GNM asset**:150 `lower_face_region_*` expression directions, separate from its
identity basis. Previous0200–0207 fits explicitly excluded native expression
execution and manually adapted source closure. The native lower-face directions
are not named `mouthClose`, and there is no jaw joint in this model; do not
misdescribe them as an existing semantic closed-mouth button.

For the existing29 source lip-support pairs, their87 XYZ gap equations have
numerical rank87 in the150-dimensional lower-face field. Original mean pair gap
is0.00062583 native units, maximum0.00081142. This is only a linear controllability
preflight—**no expression fit, coefficient application, geometric acceptance or
semantic-sampler model execution occurred**. It says nothing yet about bounded
coefficients, lip volume, contact, collisions, likeness or expressions transferred
to an identity. The separate `.h5` semantic-sampler weights are not adopted.

A subsequent bounded native-expression source/contact experiment would change
the anatomical representation rather than retune this rejected generic patch
field. It must first pass actual closed-lip volume/contact and five-view source
checks before another subject fit; failure must stop it too.

## Reproduction and evidence

Exact target/source hashes and FLAME attribution are in each local report. No
new checkpoint, dataset, consent scope, image upload or training was introduced.
Public driver: `tools/experiment_0210.py`; focused checks:
`tests/test_surface_registration.py`. The shared OBJ writer only adds optional
precision; existing callers retain their eight-decimal default. Existing capacity
render/review tools now accept an explicit repository-artifacts directory; no
second renderer or external service was added.

```text
.venv/Scripts/python.exe tools/experiment_0210.py
# Only for reproducing the retained historical eight-decimal output's repair:
.venv/Scripts/python.exe tools/experiment_0210.py --repair-export
blender --background --python tools/render_capacity_0208.py -- artifacts/experiment-0210-export-corrected
.venv/Scripts/python.exe tools/review_capacity_0208.py artifacts/experiment-0210-export-corrected
.venv/Scripts/python.exe -m unittest discover -s tests
```

Runners refuse overwrites. The first command on a fresh output already uses17
decimals; it does not need the historical repair. Original output remains in
`artifacts/experiment-0210/`; corrected actual meshes, replay arrays, `.blend`,
render hashes, visual decision and full/cropped sheets are under the separate
`artifacts/experiment-0210-export-corrected/`. All are ignored local artifacts,
not production head assets or materials uploaded to Git/PCR.
