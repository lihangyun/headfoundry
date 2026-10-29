# 0387: archived RoMa camera seed plus existing direct-image backend

2026-10-29 preregistration before image extraction or optimization. Budget20min
from14:30UTC, deadline14:50UTC; one direct worker<=300s/2GiB, four math threads.
Previous0386closed0a4341b;0385source/results and REJECT remain frozen.

History review rules out simply reviving0220/0223chained/directLK or0227ECC;
0228passed16known2Dcases but0229never refined real measurements (context support
stopped it).0332direct unknown-camera backend passed its owned textured-plane
control, whereas0333actualvideo produced0complete points and NEVER ran it.
This trial is a different information objective, not a parameter/threshold or
model retry: use raw image intensities in addition to the now available0385seed.
No claim that successful planar controls automatically transfer to skin.

Single primary variable: existing0332direct photometric objective applied to
the frozen0385initial state, rather than stopping at point-coordinate BA.
No RoMa inference/download; no reinitialization or repeat geometricBA. Preserve
exact37observations,28training/9held split and seed matrices from0385archive
SHA7e5bc84d7e3cff0c5fab9078e8c61e6632b923bdc0d46d30c6a3b0f1822af1ec.
Source archive0383SHA75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266.
Sequentially decode originalcase001; verify all1041RGB hashes, consent/manifest,
source hash and exact240/300/630ordinals. Convert selected RGB to PillowL gray,
native720x1280 normalized/255. No crop/enhancement/scan/case002/otherframesfit.

Reuse exact0332camera_values,cameras,optimize,read_images,read_audit functions
and OFFSETS[(0,0),(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,1),(-1,1)].
Shared camera logf, poses (unitbaseline gauge), per-training-source inverse depth,
per-target gain/bias. Original TRF150,softL1scale.01, sparse numerical Jacobian,
1e-8tolerances, original pose/depth/exposure bounds and invalid-domain stops.
No new geometric prior; plane-patch brightness constancy is an explicit limited
model. Holding coordinates does NOT make image patches statistically independent:
record any source/target support overlap; this is necessary development evidence,
not a new subject test. No held coordinates used in optimization objective.

Before solve exact shared tests and0332source hash check. After terminal solve,
report initial/final photoRMS separately, convergence and bound distances;
evaluate original9held points by unchanged0385triangulate-two/predict-third
procedure, proper matrices, allpositive depths, interiorf640.640..5114.88,
allthreep95<=3px, wrong+.1radcamera displacement>3px. No held-point deletion.
Need optimizer convergence/finite domains too. At mostPARTIAL_SUCCESS; even
3pxpass does not prove true camera, physical identities, medical2mm or head.
No formal mesh/texture fit before these prerequisites, no accepted likeness.

One attempt only; failure/time/domain/nonconvergence stops. Keep complete
states/held errors/receipts/source recovery and hashes, clean exclusive runner,
gray frame copies and loose outputs; preserve shared0332backend, originals,
consent, prior archives and0207. Verify shared tests and cleanupcommit. No
threshold, frame, offset, bounds or iteration sweep and no other route this run.
