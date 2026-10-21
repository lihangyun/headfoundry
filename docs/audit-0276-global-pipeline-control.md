# Audit0276: complete global-geometry positive control

Registered2026-10-21T06:17:56Z,before a new solve. Whole20minutes including
implementation,one synthetic solve,verification and cleanup.0275 is rejected
and cleaned at a2f1f15. No patient reconstruction retry is authorized by this
audit,no head or medical quality claim,and no video/skin/bone/case002 reads.

## Evidence and question

The tagged global positioner already fixes its first residual scale. The later
"cannot fix gauge" message is downstream of zero remaining points,not evidence
that the initial scale was unconstrained. The mapper explicitly deletes and
retriangulates existing points before final refinement. A one-point projection
control did not test this complete chain. Upstream has a complete synthetic
global-mapping test,so test our own database/coordinate/unknown-focal chain on
independently generated exact3D observations before blaming patient data or
patching the solver. This is software isolation,not a new patient method.

Primary source commit be5e29168d4aff238409d60424812df66aac919f (tag4.2.0):
[global positioner](https://github.com/colmap/colmap/blob/be5e29168d4aff238409d60424812df66aac919f/src/colmap/estimators/global_positioning.cc),
[mapper](https://github.com/colmap/colmap/blob/be5e29168d4aff238409d60424812df66aac919f/src/colmap/sfm/global_mapper.cc),
[upstream test](https://github.com/colmap/colmap/blob/be5e29168d4aff238409d60424812df66aac919f/src/pycolmap/pipeline/sfm_test.py).
No claimed upstream bug is established by source reading alone.

## One fixed experiment

Main variable is exact known3D synthetic observations instead of unverified
patient observations. Independently generate270 asymmetric points withNumPy
seed276,uniform xyz in[-.35,.35]x[-.4,.4]x[-.3,.3]. Five camera centers:
(-.7,-.15,-3),(-.35,.2,-2.8),(0,-.1,-2.9),(.4,.25,-2.85),(.75,-.2,-3.05),
all look at origin with right=cross(worldY,forward),down=cross(forward,right).
True shared focal1200px,principal(360,640),720x1280,no distortion/no noise.
Three90-point groups visible only in012/123/234;no all-sequence identity.
IDs divisible by5 (54IDs/162observations) never enter the database/estimator.

Use the same index convention (storedOpenCVxy=COLMAPxy-.5),unknown-focal
SIMPLE_PINHOLE initial1500/360/640,all pairs sharing>=30training identities,
2px direct public geometric estimation,view-graph calibration and global mapper.
Same seed275,CPU4threads and otherwise identical effective4.2 defaults as0275.
No supplied relative poses,F/E,3D points,truef1200,calibration prior or patient
camera enters the estimator. Save every effective option before the one solve.
An isolated disposable environment uses the exact same24147180-byte official
wheel SHA6fac64ee716335d437637d798eaafb89c76cfa06dfd53ef8384e38d09008879d;
retain0275's versioned dependency-rights qualification,not a BSD-only product grant.

Require exactly one model,all5 cameras,>=200 training points,proper rotations,
positive observed depths and relative focal error<=.001. Establish only the7DOF
similarity gauge from fixed camera centers0/2/4 (no held points or pixel errors).
Independently project every known held3D point through recovered cameras;
require all finite/positive depths,p95<=.1px,all camera rotation errors<=.05deg
and center errors<=.001scene units. These strict synthetic engineering limits
do not replace patient3px/medical2mm gates. Negative control:rotate camera0 by
.1rad about itsX axis and require its held projectionp95>3px. Never count fitted
anchor pixels as independent held-view predictions.

Implementation<=480s,download/installation<=180s,complete worker<=180s,review/
closeout within1200s. No seed,focal,noise,visibility,geometry,solver or tolerance
sweep after an outcome. Ordinary pre-estimate API repairs may be recorded.
On failure keep minimal report/hash/source ref,remove exclusive code/runtime/
cache/database before another route. On success keep only a small optional
software regression and summary;remove disposable environment/generated data.
Success proves this synthetic software chain,not real identities/rigidity,
patient focal/cameras/surface accuracy,complete head,likeness or ACCEPT.

## Actual result:bounded software chain passes

Source31daf22,one complete worker0.187s. All5cameras/216training points survive
including the same final retriangulation/refinement that failed in0275. The
seven training edges have0rotation-filter rejections. Estimated shared focal
1199.999126px (relative error7.2814e-7). All162 genuinely withheld projections
are scored: p95=.001131176px,max=.001197709px. Maximum rotation error
5.0206e-5deg,maximum center error3.08745e-7 scene units. Proper rotations and
positive held/fitted depths pass. The deliberate wrong camera has heldp95
123.483215px,so the independent evaluator rejects it as required.

This isTECHNICAL_CHECK_PASSED for this exact synthetic software chain,not a
universal solver guarantee or patient result. Empty image-folder color-extraction
warnings are expected:the control has2D numeric observations,no raster images;
no appearance or texture is evaluated. No actual images/scans are rendered or
presented as reconstruction. No patient sequence is rerun or old failure changed.

The evidence rules out a universally broken database/pixel/unknown-focal/global-
mapping integration and a universal need for a permanent track. It does **not**
prove0267's identities,rigidity or focal.0275's failure remains specific to its
actual data/estimator combination;rotation inconsistencies and data/calibration
ambiguity require independent evidence rather than a solver threshold rescue.
No reason is established to patch an allegedly missing scale constraint.

Keep the small optional `tools/check_global_geometry_contract.py` as a successful
software regression;it uses NumPy and an explicitly installed pinnedPyCOLMAP
only when run,not as a shared runtime dependency. It is not a production head
pipeline. Generated database/model/truth and the disposable install are removed
after compact evidence verification;cleanup details follow below.

## Verified closeout

Private evidence:assets/private/closed-experiments/0276-global-software-control/
evidence.zip,10members,7331bytes,zeroimages,SHA256
1b15fe4687e25c5c603b56aeec7df9611e4201250c7c097e963bcd882de17786.
CRC/all member hashes pass. Source31daf22 is the scientific execution;5e6b424
adds only the successful NumPy/gauge regression and nonzero CLI status on a
rejected control,no scientific rerun. The unchanged dependency-rights evidence
is referenced by0275 archive hash,not copied into a BSD-only notice.

After authoritative terminal-worker/exact-path/reparse/archive checks,remove
153files/159950360logical bytes:isolated environment,public wheel/cache,synthetic
database/points/truth. This is not independently measured free-disk gain.
Reports and deterministic source remain;regenerating the binary test requires
installing the pinned official wheel again. No patient geometry/images are
read by the audit;protected authorization and unrelated0207 hashes are unchanged.
Main environment still has noPyCOLMAP;the retained math regression imports
without it. Production source/defaults unchanged.135shared tests pass in6.309s.
Focused local cleanup commit follows within the original1200s;goal stays active
and no head/camera/medical acceptance is claimed.
