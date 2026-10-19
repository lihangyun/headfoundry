# Active goal: improve head reconstruction using the real capture pilot

Started: 2026-10-19, explicitly requested by the user. Status: active.

## Outcome

Develop HeadFoundry until video-derived editable head meshes meet the established
head-geometry gates and actual visual review, especially bilateral nose/lip/chin
profiles. Use the two consented same-stage video/scan cases to diagnose errors,
improve algorithms and verify the result. A rendered supplied STL is a reference,
not a reconstructed output. Goal completion is presently unproven.

The user's current scope is head geometry; hair and texture remain deferred.
Passing this head-stage pilot does not by itself satisfy the complete original
product contract, the population benchmark or a claim of KeenTools parity.

## Resources and evidence boundaries

- Only modify this repository. Preserve unrelated changes and all original data.
- The private0216 manifest binds two videos, two skin STLs and two bone STLs.
  A separate confirmation binds millimeter units and matched acquisition stage.
  The user's consent permits local reconstruction/error validation; no upload or
  model training. Do not infer commercial dataset/redistribution permission.
- Develop on real-case-001. Keep real-case-002 out of parameter fitting/tuning
  until the reconstruction method, masks, thresholds and evaluation protocol are
  frozen. Intake previews of both cases have already been viewed.
- Scan-assisted camera calibration and dense oracle fits are diagnostic lanes.
  Final video-only reconstruction must generate the head without using the test
  subject's scan to produce or deform its geometry. Disclose scan-assisted
  evaluation alignment and any scale reference.
- Use free commercially permitted components with exact provenance or independent
  implementation. No paid/unavailable model fallback, Peek implementation reuse,
  or KeenTools private services/outputs.

## Head-stage completion evidence

Existing numeric targets are engineering acceptance targets, not medical accuracy
guarantees. Preserve them; do not lower targets to make a candidate pass.

| Requirement | Required evidence |
| --- | --- |
| Camera and observations | Reviewed anatomical support/visibility; valid intrinsics and proper rotations; cheirality, focal plausibility and cross-view consistency; withheld reprojection p95 <=3px on reliable independent observations |
| Facial surface | Scan point-to-surface p95 <=2mm as specified in `quality.py`, with separately reported reverse-direction error and coverage; regional nose/lip/chin/cheek errors must not be hidden by whole-head averages |
| Profiles and front | Both profile silhouette IoU >=0.94; frontal landmark NME <=0.025 with explicit normalization; common-camera white meshes and source-photo comparisons |
| Editable output | Actual complete OBJ/GLB or equivalent editable head, retained topology/provenance and export replay; no substituted reference scan |
| Mesh and neighboring anatomy | Zero nonmanifold edges, degenerate faces and flipped faces; no visible folds/cracks, lip ledges or ear/neck regressions; inspect source cuts/artifacts separately |
| Visual and reserved evidence | Actual front, both profiles, obliques and withheld-view review; case002 evaluation only after method freeze; user judges recognizable likeness and side-profile improvement |
| Reproduction | Immutable inputs/parameters, successful necessary tests, independent output checks, retained rejected runs and local Git commits |

Before evaluating candidates, fix the scan-valid region, defect exclusions,
sampling density/seeds and alignment convention. Any global similarity for
evaluation must be declared, applied once to the entire output and held fixed
across regional measurements. No regional alignment, anisotropic stretching,
target-driven deformation or post-score mask trimming may conceal errors.
Coverage and excluded-region images accompany the metrics. Quantify annotation
and scan uncertainty before using them to claim millimeter precision.

Two cases are a development pilot, not population coverage. Predicted detector
points and adjacent video frames are not independent ground truth. The complete
`quality.py` evaluator also requires texture evidence; do not fabricate those
fields or claim full-product `ACCEPT` while that work is deferred. Keep technical,
partial, unverified, rejected and accepted evidence distinct.

## Autonomous work and stop policy

Each experiment records one main hypothesis/variable, baseline, predictions,
protected regions, a finite runtime/evaluation budget and a failure exit before
execution. Use existing code and installed dependencies first. Ordinary
engineering fixes, local verification and commits are already authorized.

A negative screen stops that tested configuration. Do not continue amplitude,
focal, slot, mask, model-size or iteration sweeps under renamed experiments.
One implementation bug may be repaired with an independent replay; distinguish
that from changing a hypothesis after viewing its scores. A follow-up requires
new evidence supporting a materially different mechanism and keeps the failed
record. Do not deform geometry to compensate for unresolved camera/observation
errors. Escalate only an actual missing authorization, essential external input
or irrecoverable blocker; do not repeatedly ask about ordinary engineering.

## Current checkpoint and next action

At commit`ce0ba67`,135 tests pass.0216 supplies the real pilot and confirmed
metadata.0217's single scan-assisted detector-anchor camera screen is rejected:
withheld-slot p95 is7.07-22.38px and one outer-eye training anchor is occluded.
Seven actual source renders replay below0.000504px. Broad source/video placement
is plausible, but landmark correspondence is not accepted; no new head was fit.

Next inspect and independently define anatomical scan/image correspondences,
including which measurements are material points versus sliding contours.
Review and freeze this evidence before another calibration hypothesis. Then
validate cameras, fit one bounded video-derived head candidate, and compare the
actual output with the supplied skin scan and withheld images. Complete the
reserved-case evaluation and visual review before declaring the head-stage goal
achieved. The goal remains active until that evidence exists.

### 2026-10-19 observation screens after0217

0218 rejects exact color-crossing profile measurements at the predeclared
uncertainty gate; no camera is fit from them.0219 uses only real video texture
and the already pinned local COLMAP runtime. Its10/52 registered frames and92
points cover one side only, so the single configuration is rejected before
head fitting. A report-only API repair reuses existing saved geometry/matrices.
The next evidence target is reliable temporal tracks spanning bilateral motion,
with fixed observations and explicit tracking-error checks before another
camera/geometry candidate. No source-scanned output is substituted for video
reconstruction; case002 remains reserved.

0220's temporal observations connect all52 keyframes after exact source-frame
identity resolution; images/masks remain unchanged. The3-frame model still
fails focal/coverage checks. Its registered-pair homography support is99.45-100%,
so the next hypothesis concerns rejecting degenerate camera initialization,
with a deterministic predeclared selection rule and a single attempt. This is
not permission to manually sweep initial pairs or relax physical/visual gates.

0221 applies one predeclared deterministic degeneracy-aware initializer to the
same temporal observations. All52 frames register with2540 points and a plausible
focal under the implemented screen. Actual sparse views show incomplete facial
geometry with holes/scatter; physical/scan/head acceptance remains unverified.
Next freeze it, localize exact-identity withheld frames624/1040 with focal fixed,
and predeclare scan alignment/valid regions before the next head-fit hypothesis.
No reference scan may replace the video-derived output.

0222 rejects frozen-model localization on development sentinels624/1040. The
first reaches9.658699px odd-ID validation p95; the second has only17 pose inliers.
Independent pairwise pixel-rigidity also fails, so changing head geometry is not
justified.0223's single direct-versus-temporal endpoint closure retains only58/0
points, insufficient for the original>=30 points per pose/validation split.
Stop that LK observation family without tolerance or reference-frame sweeps.
The next distinct evidence target is direct learned feature/matcher associations
using the repository's already pinned Apache-2.0 XFeat/LighterGlue assets on the
real video, followed by a frozen observation coverage/loop check before mapping.
These inspected sentinels are now development evidence, not fresh held-out data;
case002 remains excluded from fitting/tuning. No final camera/head acceptance,
scan error or recognizable identity improvement has yet been established.

0224's already locked direct learned matcher also connects52 frames and yields
1639 points, but0225 rejects its frozen-model sentinel localization and exact-
index two-view pixel rigidity. No scan/head fitting follows. Duplicate matched
3D identities are excluded before scoring rather than counted as independent
points. Next isolate **pixel localization accuracy** with known image transforms
before proposing a subpixel correspondence method or another camera/shape solve.
No matcher confidence, reference-frame, focal or mask rescue sweep is authorized
by these negative results. The goal remains active and unmet.
