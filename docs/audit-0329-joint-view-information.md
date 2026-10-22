# Audit0329:does common-three-view structure break the two-view ambiguity?

Registered 2026-10-22T19:43:57Z;whole900s,deadline 2026-10-22T19:58:57.000Z.
Prior0328closeoutdb91d50is complete. No failed solver/model/runtime restored.
This is a read-only information audit,not another camera fit or easier head goal.

0328proved a continuous two-view focal family.0318already measured improved
but insufficient noisy information on a DIFFERENTfive-view fixture;do not tune
its angles/counts to cross.02or reuse that result as this context's truth.
New question:does a shared3Dpoint across three cameras supply a focal constraint
that independent pairwise essential constraints lack? Single structural contrast:
original0328two-view commonXYZversus those same views/points plus ONE different
axis view,R3=Ry(-18deg)@Rx(15deg),same pivot(0,0,3). No selected angle/seed/count/
noise/focal/geometry/solver sweep. A third copy of view2is a redundancy witness.

Read only0328compact owned-coordinate capsule after SHA/CRCverification:
b36d23d6279c073793e74048fa86caaf3359587ef7f407e50d2e0a648598971a.
Its XYZ/trueK/poses are diagnostic inputs only,never camera initialization or
human inference. Normalize scene and all translations by original baseline
length to preserve the existing unit-baseline parameter gauge. Three contexts
keep original120points and both original poses,all observations included,no
held noise draw/optimization step. No actual video,scan,case002,model,download,
new package,training/upload or default change.

Reuse shared focal_information/linearize;add the minimum analytic native
Jacobian using OpenCVprojectPointsrotation/translation derivatives,closed-form
point and common logf derivatives,and the exact baseline-direction chain rule.
Verify all columns against existing two-step central differences(relative<=1e-7)
and forward replay<=1e-9pxbefore interpreting rank. Proper matrices,finite
inside-native positive-depth support required. Existing rankrcond1e-12unchanged.
Analytic columns prevent finite-difference error from inventing rank in the
proven critical case. Profile logf against ALLfree camera/point nuisances;
anchorSE3and baseline norm fix similarity gauges only,no known pose/point prior.

Required controls:analytic-vs-numerical match,original two-view focal contrast
relative norm<=1e-10and no added focal rank;copied-third-camera same null result;
all original data/gauge preserve exactly in extended contexts. Report actual
third-view rank/profile whether useful or not,no tuning if it remains confounded.
If identifiable,report local sigma(logf)for declared.5pxindependent Gaussian
coordinate noise as a diagnostic only,not achieved accuracy/confidence/global
uniqueness/3pxor2mmacceptance. Copied view's independent-noise precision is not
claimed. Nonzero information does not authorize a patient fit or new stack.

Worker<=120s/1GiB,four math threads,existing descendant-tree monitor;full retained
suite<=120s. Save raw Jacobians/states/ranks/input/source hashes and compact
private archive,no pictures. Retire one-off driver/bulk after read-only audit,
keep only verified generic analytic derivative/regression if correct. Protect
38prior identities and unrelated0207. Stop on domain/control/resource failure,
no tolerance/finite-difference step/angle/point rescue or restored SDK trial.

Derivative API source:https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
(projectPoints);installed implementation is separately checked numerically.

## Before next solver:check the actual query-excluding holdout structure

Initial read-only result:two/repeated views have no analytic focal rank;common
three-view rows do. Before promoting that into a capacity protocol,one additional
<=120s/1GiBstatic matrix audit applies unchanged split_observations to EXACTLY
those same three-view rows/point IDs,host0queries ineligible for holdout. Remove
only the corresponding already-computed Jacobian rows;no new camera,point,
noise,derivative,solver or optimized state. Preserve resulting rank/contrast and
all row IDs. This checks whether the project's real split retains the constraint
just demonstrated,not a tuning of the earlier0318scene or physical threshold.
Compact this independent supplemental evidence without rewriting first capsule.

## Actual joint-information result,not recovered precision

Executed166283a. Worker2.375s/118894592peak bytes,payload.922s.156shared
tests pass8.425s. Forward replay<=1e-9px,all points positive/inside native,
analytic-vs-central Jacobian relative differences1.11..1.26e-10. Every original
residual/column block remains EXACTLYunchanged in both extended contexts.

| Frozen observations | Analytic rank / nuisance rank | Relative focal contrast |
| --- | --- | --- |
| Original two views | 365 /365 | 4.43626e-15 |
| +copy of second view | 371 /371 | 6.59129e-15 |
| +independent third view,commonXYZ | 372 /371 | .01846157 |

Only the last has locally independent focal information after profiling ALL
free cameras/XYZ. Under declared independent.5pxGaussian coordinate noise,
local sigma(logf)=.0069986015in this ONE exact three-view geometry. This is
NOT achieved.7%focal precision,global uniqueness,confidence coverage or evidence
the patient's video supplies those observations. No camera/point fit ran.

The original finite-difference Jacobians spuriously report an extra focal rank
in both exact critical controls at unchanged1e-12relative rank tolerance.
Close derivatives alone(relative1e-10)are not enough to infer tiny-rank geometry.
The analytic null witness resolves this without tuning rcond or actual3px/2mm.
Older0311/0318contexts are not thereby automatically invalidated or recomputed;
future critical-motion decisions must use an independent analytic/null check.

## Actual holdout interaction and next gate

Supplemental worker1.532s/118280192peak bytes,no derivative or solver rerun.
Unchanged source-query-excluding split leaves240training observations for120
points,exactly TWOviews/point. Target1/target2have ZEROcommon training points.
Subselected analytic matrix rank370/nuisance370,relativefocalcontrast1.28792e-14:
the training fold loses the newly shown focal constraint. Do not proceed with a
three-view capacity recipe that assumes the full-row result survives this split.
Do NOT cancel/relabel holdout or use hidden rows in initialization. A later
joint-camera design must retain sufficient independent training structure AND
genuinely independent held evidence;justify it before one bounded solver test.
This is a fold/constraint structural requirement,not another frame-count sweep.

TECHNICAL_CHECK_PASSED read-only controls and information contrast. All actual
video cameras/head/medicalmm/visual acceptance remainUNVERIFIED. No production
default,source asset,neural model,patient pixel/geometry or case002was used.

## Compact closeout

Original capsule299400bytes/6members/no images,CRCverified,SHA256
acbc02d82e373025b48eb3a57a825da5d12782b1fe25552588e98f5c8a34388d.
Supplement45497bytes/5members/no images,CRCverified,SHA256
662ca3d3edffe662981c270226ed994b131602caeebd4d0ea82e1622ce062664.
Both under assets/private/closed-experiments/0329-joint-information;keep ALL
raw arrays/rows/poses/ranks/source/worker reports within these capsules. Original
5loose files415752bytes compacted;the supplemental4raw files are verified
byte-identical to their capsule before compaction. This is complete recovery
of these small diagnostic arrays,not a new runtime/model/head backup. Retire
one-off audit entry;keep correct native_camera_jacobian/regression only.
38prior protected identities verify;unrelated0207and production defaults unchanged.

Supplemental4raw files58655bytes compacted,all recoverable exactly from their
unchanged capsule. Post-retirement156tests pass8.619s;protected38verify again,
no dangling one-off import or production src/examples/dependency-lock diff.
Final verification19:51:12UTCis within19:58:57UTCwhole deadline. Correct generic
derivative/regression retained;full head objective stays active and unmet.
