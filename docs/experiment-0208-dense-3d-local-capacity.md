# Experiment 0208: dense-3D representation upper bound

Pre-registered 2026-10-14, before generating targets or fitting candidates.
This is an oracle capacity experiment, **not photo reconstruction**. No subject
images, cameras, mesh defaults or learned predictors are changed.

## Frozen question and design

Can one continuous, topology-aware two-scale local residual recover shapes
that the current first30 GNM identity directions cannot express? Counter-evidence:
previous local fields folded lips, and sparse oracle fitting0192–0193 was fragile.
Here all retained surface vertices have exact material-matched3D supervision;
there is no camera/detector/2D correspondence ambiguity. This is not a renamed
39-point or silhouette experiment.

- Locked Apache-2.0 GNM v3 head and existing repaired closed exterior from0202;
  reuse its linear closure for mean and **all253** directions. No model download.
- Twelve synthetic targets, seed20261014; standard-normal253 coefficients times
  0.7. Deterministically halve a target's whole displacement up to ten times only
  to meet source safety (no reversed faces, area ratio>=0.5, displacement<=0.12
  fixed mean bounding-sphere radius). Record every scale; no aesthetic selection.
  These are same-source stress cases, not independent scanned identities.
- Baseline: optimistically unbounded, surface-area-weighted dense3D least squares
  using the first30 directions. Candidate: that exact baseline plus two fixed
  geodesic patch fields (64 then192 farthest-point nodes; compact Wendland weights,
  support twice the covering radius; partition-of-unity at each level).
  One ridge solve per level, fixed1e-6 after area weights sum to one. The candidate
  does not receive target coefficients or remaining223 basis directions.
- One main variable: representation. The target generator is a different basis
  from the patch field. There is no detector, camera fitting, texture or hair.
- No per-vertex free displacement. Shared mesh connectivity determines influence,
  rather than image-space proximity across lips. This is a locality safeguard,
  **not proof of anatomical validity or freedom from self-intersections**.

## Gates and stop rule

All twelve final serialized candidates must be finite with unchanged topology,
zero source-relative normal reversals, minimum area ratio>=0.5, and maximum
displacement<=0.12 radius. Safety failures are rejected, never silently scaled
after fitting. Nose, upper/lower lip, chin, orbital and ear3D errors may not exceed
baseline by>5% (numerical tolerance1e-10 radius). All five fixed-camera projected
material-point RMS errors must likewise avoid>5% regressions. These projections
are evaluations, not independent held-out observations.

Advancement additionally requires >=10/12 cases with >=40% reduction in global
area-weighted3D RMS and >=20% reduction in each nose/combined-lip/chin RMS. Actual
five-view white meshes plus nose/lip/chin crops must be inspected before calling
this a useful capacity gain. Statistical improvement without visible gain is
only `PARTIAL_SUCCESS`, never likeness `ACCEPT`.

Budget: <=15 minutes of fitting/preparation, <=15 minutes of rendering/review,
no sweep. One correction rerun is allowed **only for an identified implementation
bug**, documented separately; a missed quality gate is not such a bug. A timeout
or failed guard stops this fixed candidate. Do not change ridge, node count,
target amplitude or iterations after observing the outcome. Preserve results.

If this upper bound passes, the next separate gate is dense2D observations under
known cameras, declared noise and occlusion; passing here does not authorize
pretending that such observations already exist for the five independent AI refs.
If it fails, freeze this candidate, diagnose once, and do not return to0207 tuning.

## Results

Completed one frozen run, **zero correction reruns, no parameter sweep**.
Preparation/fitting8.603s, Blender5.2.1 LTS rendering56.541s. All115 public tests
pass. The existing untracked0207 record and subject/default head remain untouched.

| Mean of12 cases | First30 dense oracle | Oracle + local residual |
|---|---:|---:|
| Area-weighted3D RMS / fixed mean radius | 0.00256323 | 0.00119522 |
| Nose region RMS / radius | 0.00293036 | 0.00176000 |
| Combined-lip region RMS / radius | 0.00362660 | 0.00207506 |
| Chin region RMS / radius | 0.00330267 | 0.00155040 |
| Left/right90 material-point projection RMS,512px | 0.41401 /0.41463 | 0.19803 /0.19777 |

The reduction in mean3D RMS is53.37%. **12/12** meet the predeclared global and
nose/lip/chin gain criteria; all protected region/projection checks pass.
Final serialized meshes have zero source-relative normal reversals, minimum
area ratio0.51742 and maximum displacement0.081084 radius. Five cases needed
the predeclared target safety halving: cases00/01/02/09 at0.5, case11 at0.25;
the remaining seven at1. No candidate was post-fit scaled to hide a failure.

An independent saved-control replay of all12 exported candidates differs by at
most9.987e-9 radius (OBJ decimal serialization). Recomputing the repaired first30
directions and transforming them into the existing subject-frame basis agrees
to8.674e-19; this is the same prior subspace, not a weakened straw-man baseline.
The solver/driver hashes still match the recorded pre-render run.

All180 actual white-mesh renders (12 cases x3 surfaces x5 views) were generated.
Maximum Blender/analytic camera replay error0.000122px. The main review inspected
the all-case bilateral and front/oblique nose-lip-chin contact sheets, plus the
enlarged five-view case06 sheet. The same crops, cameras, geometry scale and
lighting are used for truth/prior/candidate; no shape exaggeration. The skin-only
oracle has empty eye apertures, not a completed head with eyes.

### Decision: retain a research helper, freeze this candidate

- Technical execution: `TECHNICAL_CHECK_PASSED`.
- Narrow same-source dense3D capacity: `PARTIAL_SUCCESS`.
- Meaningful visual remedy for the current generic-face failure: **not
  demonstrated**; real-reference likeness and KeenTools comparison `UNVERIFIED`.
- Production/default/subject promotion: `REJECT`; joint advancement gate not met.

The panels show small local changes toward the supplied truth, not a compelling
identity-level jump. Crucially, the old first30 representation already has
**<0.44px mean material-point RMS in every view** on these targets with perfect3D
supervision. Improving that already-small approximation does not explain or fix
the much larger existing photograph-fit failures. These targets are still from
GNM's own full253 basis, reduced for mesh safety; they do not establish an upper
bound on an independent scan or this user's reference head. This experiment
isolates capacity within one licensed source; it neither proves30 dimensions are
universally enough nor proves local patches are a universal solution.

**Stop:** do not enlarge node counts, retune ridge/target amplitude, add iterations,
or rerun0207 to manufacture a larger visible gain. Keep the opt-in helper off the
photo pipeline. Before another subject fit, require independently discriminating
evidence: an appropriately cleared, structurally distinct known3D target for
representation coverage, and reliable observations with separately measured
camera/correspondence error. A later oracle dense2D/noise diagnostic is a separate
observation experiment, not evidence that real-photo dense correspondences exist
or permission to promote this candidate. No training, unknown checkpoints or
uploads were performed.

### Reproduction and local evidence

Public code: `src/headfoundry/local_residual.py`, `tools/experiment_0208.py`,
`tools/render_capacity_0208.py`, `tools/review_capacity_0208.py`.

On a fresh output directory with the existing locked local assets installed:

```text
.venv/Scripts/python.exe -m unittest discover -s tests
.venv/Scripts/python.exe tools/experiment_0208.py
blender --background --python tools/render_capacity_0208.py
.venv/Scripts/python.exe tools/review_capacity_0208.py
```

The runner refuses to overwrite existing output; preserve the first run. Asset
paths are installation references, not a downloader or a consent bypass. No
subject image enters the solver; the earlier subject directory is used only for
its already-locked generic source closure asset, in source coordinates.

Ignored local evidence under `artifacts/experiment-0208/`:

- `report.json`: exact source/code hashes, all per-case metrics and safety scales.
- `render-report.json`:180 image/OBJ hashes, camera replay, Blender version.
- `visual-review.json`: explicit limited review and freeze decision.
- `all-profiles.png`, `all-front-obliques.png`: all12 cases, three repeated columns
  per view = **truth / first30 prior / local candidate**.
- `case-00`…`case-11`: actual OBJ exports, replay coefficients, full five-view
  comparisons and enlarged nose-lip-chin comparisons. No private assets in Git.
