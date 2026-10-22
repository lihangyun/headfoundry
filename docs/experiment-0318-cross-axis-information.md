# Experiment0318:does a genuinely new motion axis add focal information?

Registered2026-10-22T16:07UTC after0316/0317closeout4fec116,before computation.
Whole900s to16:22UTC;worker120s/1GiB,CPU4math threads. No reconstruction output
or physical camera fit. Previous turn is progress:failed focal-prior candidate
was rejected/retired and fixed-band source census supplied bounded new evidence.

0311established local sigma(logf)=.0760183for141procedural tracks/.5pxnoise.
0316rules out treating one learned Kguess as precise;0317did not admit scene
orthogonality. A different information source remains possible:additional
cross-axis observations. Actual video has qualitative pitch,but no measured
20degree pose or certified correspondences is assumed. Do not request footage
or restore failed trackers/0308cached solve to test this hypothesis.

Single variable:geometry of ONE added view,with identical number/identity of
new observations. Compare repeat-anchor camera versus camera pitched+20deg
around the existing procedural cloud centroid. Both retain all five original
poses/K/141points/clean training rows/anchor2/baseline3 unchanged. New141rows
project those same points with fixedK;new camera extrinsics remain six FREE
nuisance variables in both information calculations. Pivot describes only
synthetic input generation,not a fixed-pivot human-motion assumption or prior
supplied to an estimator. No new point/seed/noise/focal/iteration sweep.

Read only the successful0311raw linearization capsule,check its SHA/CRC and
replay baseline sigma. Reuse unchanged shared linearize/focal_information.
Profile local logf against all free camera/point nuisance columns at exact truth,
same rcond1e-12 and declared .5pxindependent Gaussian coordinate noise. No random
noise draw,solver fit,estimated step or held observation is used. Preserve all
Jacobians/ranks/singular values. Require proper camera,positive depth and all
new points inside native image;outside data stops rather than pruning points.
Half-step/forward checks stay inherited. Verify that appended-view parameter
columns preserve every original residual/Jacobian block and that duplicating
an entire Jacobian gives the analytic1/sqrt(2)noise-information scaling.

Decision:only if pitch is locally identifiable,sigma(logf)<.02ANDlower than the
same-size repeat control does it justify a separately bounded noisy camera
capacity test. Otherwise no solver/new-model trial is justified by this cue.
This local regular-unbiased/Gaussian sensitivity is NOT achieved precision,
95%coverage,global identifiability or patient feasibility. Existing0255/0256
silhouette-only family remains frozen;this is not a silhouette loss variant.
Even a positive result admits no actual-video pose/3px/2mm/head/visual quality.

No private human pixel/scan/case002content,download,training,upload,new package,
source/default or gate change. Archive small read-only evidence/Git source and
retire one-off driver after tests/protected hashes. No model stack to keep.

## Actual fixed design contrast

Executed bedea11. Worker2.391s,conservative tree peak119664640bytes,payload
.937s. Both appended-view Jacobians have846rows/453unknowns,rank453and
nuisance rank452. Original Jacobian blocks differ by exactly0;all old rows
remain unchanged. Whole-Jacobian duplication obeys1/sqrt(2)scaling. Truth and
forward replay max4.55e-13px,half-step relative witnesses<=5.70e-11. All141new
points are positive and inside native image in both variants,no pruning.

| Fixed design | Local sigma(logf),pixel noise sigma=.5px/axis |
| --- | --- |
| Original five views | .0760182645 |
| +141observations from repeated anchor pose | .0504460003 |
| +141observations from one +20deg pitch pose | .0208726023 |

TECHNICAL_CHECK_PASSED mathematical information contrast. Decision remains
ADDITIONAL_INFORMATION_STILL_REQUIRED:the fixed pitch control improves local
information over same-size repeated observations,but .0208726 is NOT below.02.
No angle/count/point/seed change to cross this boundary,no noisy solver or real
camera/head/model trial follows this result. These are local theoretical
uncertainties at procedural truth,not achieved focal errors or actual-video
uncertainty. Actual3px/2mm/recognizable-head goals remainUNVERIFIED.

Derived engineering quantity only:under these exact regular/Gaussian/geometry
assumptions,local sigma(logf)=.02would require per-axis pixel sigma<=.47910for
the pitched design,versus<=.19823for equal-size repeated-view design. This is
not a calibrated95%target,a correspondence p95gate or proof actual pixels meet
that precision. It identifies needed observation quality,not a new acceptance.

## Verified compact closeout

Private closed-experiments/0318-cross-axis-information/evidence.zip161611bytes,
8members/no images/CRCverified,SHA256
bf996a89f2671af49410bb7150644a4dd86c31ebd8a6fd4fb514d8fd7a0ff8b5.
Both full raw Jacobians/truth rows/poses/points/ranks/source hashes/worker records
and executed protocol/driver retained.6loose files200993bytes compacted and
one-off runner retired;Git recovery bedea11. No model/package/environment was
installed.28protected original hashes plus4prior generic amendments verified;
shared camera/math/defaults and unrelated0207unchanged.146tests pass7.360s.
Closeout16:10UTCwithin16:22deadline. No actual-head acceptance or goal completion.
