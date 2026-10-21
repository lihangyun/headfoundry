# Experiment0278: pinned RoMa dense physical-capacity check

Registered2026-10-21T06:37:14Z,before installation/loading/forward. Whole2400s
including implementation,downloads,one neural pair,physical scoring and cleanup.
0276/0277 are closed at5df5a6f/dd1f3e2. No accepted patient head exists.

## One variable and immutable evidence

Replace the observation component by original RoMa outdoor/DINOv2. Its frozen
semantic backbone plus dense local refinement is different from retired DIS/LK,
XFeat/LighterGlue and EfficientLoFTR. Keep camera solver/quality thresholds and
production defaults unchanged. This is a source-only capacity diagnostic,not
real-video reconstruction or a controlled improvement percentage over0274.

Use exactly two already archived SUPPLIED-SCAN-NOT-RECONSTRUCTION images:0274
pos(yaw+30) andneg(yaw-30),720x1280,procedural fixed material,not natural skin.
SHA256pos=d511845b67f90afc9b5b3fc8018000d04e413057e6946d04c398e0982c137516,
neg=8fc3538eb50923ae53855615caf4f8871b1bf4914a3ee38d3f4aa0456f355258;
0274 archive SHA256
4a401e543f4133ef9a45287eca7e7bdcf2c24b7e7a83068e09be8c5126993437
is verified directly before extraction. No rerender,texture/crop/checkpoint/
precision sweep.
Successful0230 truth SHAeea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942
has5000immutable material IDs,trueK/poses/visibility. Common+30/-30=1343points.
Truth is evaluator-only;inference gets the two PNGs,not scan geometry/poses/points.
No original video,skin/boneSTL orcase002 is read,no data training/upload.

## Asset and runtime gates

Original source77f8d68803526dcddfd9b7a46bc76125bdc25f15;author weight source
and Meta original descriptor/licensing exactly0277. Two official downloads:
RoMa445647516bytes andDINOv21217586395bytes. Verify complete atomic downloads,
record source/rights/actual SHA256 locks before loading;missing rights/hash/size
fail closed. Publisher currently supplies no release digest;do not invent one.
No account form,alternate model,RoMaV2,DINOv3,TinyRoMa or paid fallback.

Isolated Python3.12 environment,Torch2.10.0+cpu/TorchVision0.25.0+cpu,CPU4threads,
FP32,highest float32 matmul precision,default560coarse/864upsample,symmetric,
no compilation,Windows ordinary local correlation. No trained layers changed.
Both RoMa wrapper AND unregistered descriptor-list component must strictly match
complete local checkpoint keys/shapes/dtypes/finite values/loaded state. Network
denied during model loading/inference;all caches/TEMP inside route directory.
Preserve MIT/Apache/dependency notices. No production manifest/default changed.

Before neural scoring:independent edge/center and bidirectional-grid controls,
NumPy roundtrip<=1e-10px,TorchFP32 bilinear replay<=.001px,wrong halfpixel must
exceed.1px. These are software arithmetic bounds,not a universal1px physical
prerequisite. One full forward must return finite864x1728x4warp/864x1728certainty
with correct symmetric source grids. Maximum8GiB peak process working set.

## Physical scorer,not an oracle reconstructor

After the one forward,independently bilinear-sample each output direction at
all source-visible0230 material projections (no truth queries to neural model).
Score all1343 true-common IDs per direction,including low confidence and wrong
outputs;report occluded/unavailable cases,do not residual-filter held points.
KnownK is explicitly an oracle calibration. For pose fitting use only source-
visible even IDs with native in-bounds finite target predictions and the
publisher default confidence>=.05;never use target truth visibility/residuals.
Require>=24training/24held and50px spans each axis. Existingrobust_refine_pose:
2px,.6support,1deg medianparallax,512samples,seed278,unchanged500nonlinear budget.
One fit per direction;no alternate initializer or scientific rerun after failure.

Fix unit-baseline scale by the single true baseline magnitude only (explicit
metric gauge,not estimated metric scale). Score the estimated camera on all
untouched odd common-visible truth3D points:p95<=3px,proper rotation/positive
depth. Triangulate those held points from source pixels and raw predicted target
pixels,require all finite positive depths andp95<=2mm. No truth3D goes to fitting.
Both directions must pass;composed poses must replay held source points<=3px.
This remains point/camera capacity,not2mm **surface**,actual video,complete head,
likeness orACCEPT. Procedural texture failure cannot prove universal inability.

Implementation<=600s;parallel asset/runtime install<=300s;strict load/control<=180s;
single full forward<=180s;physical scoring<=120s;no more than two necessary
source/diagnostic views and whole-phase budget includes closeout. Any failed
stage stops progression to patient head fitting. Preserve compact numeric/rights/
source evidence,remove exclusive runners/weights/framework/cache/env/outputs,
verify protected inputs/shared tests and commit local cleanup before a new route.
