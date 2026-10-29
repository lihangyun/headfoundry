# 0387: archived RoMa camera seed plus existing direct-image backend

2026-10-29 preregistration before image extraction or optimization. Budget20min
from14:28:20UTC, deadline14:48:20UTC; one direct worker<=300s/2GiB, four math threads.
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

## Actual outcome: photometric fit improves, held geometry worsens

Preregistration731a64d, implementatione14ff08. Exact1041frameRGB identities,
source/manifest/consent and archived observations verified. Intake6.891s,
201306112Bconservative peak. Before solve167shared tests passed8.354s.
One direct worker10.344s/148766720B, scientific gate rejection, not resource
failure. No retry, model call, camera reinitialization or geometricBA replay.

Original direct objective converged byxtol after132evaluations. PhotometricRMS
0.109468892 ->0.058548791 normalized gray (46.52% reduction); focal1199.776568
->1193.574024px. Bounds remained interior; minimum parameter-bound distance
0.034168 in heterogeneous parameter units, not a physical uncertainty estimate.
The omitted sparse derivative dependency check passed. All final poses proper,
allheld triangulated depths positive. Exact bilinear texels at held centers do
not overlap training sample texels in any view at initial/final states; this
does not establish statistical independence over optimization or image context.

| Held predictive p95 px | Original0385 | Final photometric |
| --- | ---: | ---: |
| view0 | 0.325038 | 2.001245 |
| view1 | 3.798079 | 3.380225 |
| view2 | 2.424998 | 5.192755 |

FinalREJECT: two target views exceed3px. Wrong-camera displacement controls
94.171/103.233px. Evaluation folder uses the historical evaluator's label
"initial" for final0387state; it does NOT mean baseline was overwritten.
Original baseline state/report and all9held observations remain preserved.

Confirmed mechanism at the objective level: reducing this sampled photometric
loss does not preserve/improve the fixed held geometry. This rules out blaming
this run on missing observations, nonconvergence, an active search bound or
insufficient iteration budget. It does NOT uniquely identify lighting,
nonrigidity, occlusion, patch-depth approximation or initial correspondence bias.
No patch deletion, alternate metric, extraiterations or changed weights.

Keep0332conditional owned-scene capability, not this failed real transfer as a
production component. A useful future design would need independently justified
constraints or observation uncertainty, not assume lower imageRMS means truth.
No new head, scan surface error, accepted camera or visual improvement exists.

Private archive closed-experiments/0387-real-photo/evidence.zip is389820bytes,
23members,SHA c4f2d312cff990a7ce930dc1a034f5fb1513885079230dad54d5603054d3655c.
Contains initial/finalstates, fixed observations, allheldscores, losses, bounds,
receipts, inputhashes, source and oneinputsheet; nativegraycopies excluded and
recoverable only by decodingoriginalvideo again. CRC/allmemberhashes verified;
all9protectedhashes unchanged. No new dependencies, frameworks or weights.

## Verified closure

Source recovery325bc7c. Worker terminal and no matching live Python job before
resolved-path/reparse/inventory checks. Removed25loosefiles1255591logicalbytes
and one exclusive runner. Shared0332and all9protected hashes unchanged; original
0383/0385archives intact.23archive members/CRC/SHA reverified after deletion;
no live caller remains.167retained tests passed8.131s. Original0207untouched.
Closed14:34UTC, within14:48:20deadline. Goal remains active and unfinished.
