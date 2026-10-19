# Experiment0241: scan-free global anatomical-model video fitting

Date:2026-10-19. Pre-registered before new observations/bindings or model fitting.
Status:`UNVERIFIED`. Case001 development,not a new population benchmark.

0240 establishes bounded prior capacity and generic unit-invariant mesh guards.
Now test the actual video-input path. Primary change is global shared anatomical
model projection instead of local image-match triangulation. No scan-derived
identity,pose,similarity,quadratic,geometry,landmarks or evaluation masks enter
inference. Start exact licensed native FLAME2023 Open identity zero. Keep300
identity dimensions,bounds[-3,3],original topology and the generic mesh guards.

Prepare an isolated private video-only input manifest. Read the original consent
manifest **metadata** to copy only case001 video authorization; verify that video
and derived frame hashes,without opening skin/bone or oracle files. Decode exact
sequential ordinals0,208,277,555,832 for fitting and624,1040 as development
sentinels. These views have been inspected previously; do not call them fresh
unseen data. Record hashes and ordinal identity; do not reuse seek-based old PNGs.

Generate a generic neutral-prior frontal512px image with native +Y-up,+Z-front
cameras and known normalization. Run only the already locked local Apache
MediaPipe Face Landmarker task on that **generic asset** and the authorized frames.
The generic model has no real person's consent record; its CC-BY asset license,
not a fabricated biometric consent,is its use basis. Video consent remains local
validation only. Pin actual MediaPipe1.0.1/runtime/task identities.

Lift the first468 generic detector pixels onto the exact nearest neutral skin
triangle using existing perspective-correct ray lifting. The largest connected
native component is skin; eye-ball first hits reject a binding rather than
seeing through them. Exclude the official runtime face-oval connection vertices
as sliding contours,not material anchors; iris indices are not used. Preserve all
IDs,rejections,barycentric attachments and source-render overlays. Require>=100
skin bindings and nose/central-mouth support; visually inspect them before fitting.
These remain provisional semantic estimates,not anatomical or physical truth.

Split original semantic IDs mod5==0 as validation,others training across all
frames. Initial poses use training-only generic points,OpenCV PnP at focal1000
and center(360,640). Freeze exact initial first-hit skin visibility,independent of
residual error; require>=100 training and>=20 validation points per fit view.
At every final candidate recheck all used bindings on the complete actual mesh.
No residual-based deletion or mask/slot/focal sweep; changed/occluded final support
must be disclosed and cannot be promoted as accepted observation evidence.

After binding review,fit one shared identity and per-frame proper pose to the
training observations,with shared focal in400..3000px. Detector residuals use
fixed4px engineering scale and unit Gaussian identity regularization,not a claim
of calibrated detector uncertainty. Exact pose/identity Jacobians must be checked
before the single fitting run. Use the generic hard-mesh inequalities before any
reviewable output; do not import0240's case-specific active faces or coefficients.
Preserve complete validation errors,cheirality,focal,visibility and full topology.
The unchanged3px p95 criterion is detector consistency here,not physical camera
acceptance or proof of material correspondence.

Budgets:60s preparation/binding,one180s fit and60s render. If prerequisites fail,
stop before fitting; do not move/rename a failed binding set until it passes.
An ordinary implementation repair needs the original evidence and independent
replay. No parameter/model/ridge/slot/reference search. Even a numerically passing
fit requires full-head/source/profile/mesh and actual visual validation. If camera
checks fail,a safe exported mesh may only be explicitly unaccepted experimental
geometry under the existing user-authorized lane,never formal reconstruction.

Save replayable isolated manifests,binding/observation arrays,input/model/producer
hashes,actual whole-head/image overlays and original failures. No training,upload,
hair/texture work,source/default change or case002 tuning. Separate scan evaluation
may read the frozen output only after inference terminates; nothing flows back.

## Executable fit details,locked after binding review and before any pose/fit

The generic binding review shows nasal,central mouth and skin supports on the
neutral licensed mesh; this is only anatomical plausibility,not calibrated
cross-person semantic accuracy. Preserve the420 bindings unchanged. Video
overlays remain detector observations,including predictions on a hidden side.
Initial OpenCV iterative PnP and RefineLM use all eligible training IDs,without
RANSAC or a residual cutoff,then exact first-hit visibility freezes the subsets.
Use native-unit3D hit gap<=1e-5 (approximately.01mm at nominal1000mm/unit),not
strict triangle-ID equality across an edge. Record every excluded ID and reason.

Optimize300 identity coefficients,then6 pose variables per each of5 fit views,
then one focal variable. At zero state pose is the initial PnP; rotation vector
changes by.1*q_rot,XY translation by.1*q_xy,and positive depth is
tZ_initial*exp(.5*q_depth). Each of these pose variables is bounded[-3,3].
Focal=1000*exp(.3*q_f),bounded400..3000. Principal point stays(360,640).
Use ordinary squared training projection residuals/4 plus beta squared,without
robust loss,depth observations or validation points. SLSQP exact analytic
Jacobians,ftol1e-8,maxiter150; no parameter/ridge sweep. Budget180s total.
Constraint generation starts with no active triangles,tests every original face
and adds only violations from this video candidate,at most5 rounds restarting
from zero. Hard inequalities use0240's generic native-geometry routine only.
Full-template cheirality and unchanged support visibility must be reported.
The62 native boundary edges are preserved and remain a full-output failure.
Sentinel poses,if reached,use only their training IDs after identity/focal freeze;
they never update identity,focal or fit-view poses. No sentinel can be described
as fresh unseen evidence. If initial coverage fails,stop before shape fitting.

## Separate frozen-output evaluation,registered before opening the scan

The single fit has terminated with a safe experimental mesh but failed detector
projection/visibility. Preserve that rejection. Do not fit sentinel poses under
this failed configuration or use scan results to repair it. Measure the frozen
output once to discriminate inaccurate camera observations from insufficient
shape recovery. No medical/source geometry has entered the inference process.

Use the unchanged0237 reference quadrature and exact BVH distances. Compute only
one evaluation similarity: native1000mm/unit,proper axes +Y-up,+Z-front,translate
the maximum-Z candidate anchor to the maximum-Z source anchor; ten fixed proper
similarity closest-surface steps on the even-indexed source facial quadrature,
with original regional area weights. Bound scale700..1300 and rotation<=15deg.
Freeze it for the full output,all regions,both distance directions and neutral
baseline renders. This registration is evaluator calibration,not reconstruction;
odd source facial quadrature is held from the alignment. No coefficient,pose,
focal,point-binding,mask or scan alignment sweep; no regional ICP or trimming.
Persist every transform step and the final4x4 before distances. Full-source
coverage and native open boundaries remain failures even if face-only numbers
improve. Original source and frozen video candidate/neutral use identical six
white cameras/lights; no similarity refit per image. Case002 stays unopened.
Budget60s registration/metric and60s actual rendering,separate from inference.

## Result: bounded video output exists; acceptance REJECT

Preparation16.04s: exact7 sequential frames,420 eligible bindings,0 patient
geometry/oracle read attempts. Initial frozen fit-view coverage274-333 training
and73-87 validation supports. All binding and zero-identity inputs are retained.
The180s fit finished in24.63s. Three predeclared constraint-generation rounds
used0,10,11 candidate-derived active faces; the final original9976 triangles
have0 normal reversals and area ratios.20001000001..3.15341672. No unsafe
intermediate was exported for review. Focal937.216px and all proper camera
rotations/whole-mesh positive depths pass their structural checks.

Detector projection remains `REJECT`,not physical-camera acceptance:

| Exact video ordinal | Validation p95 px | Used bindings losing visibility |
| --- | ---: | ---: |
| 0 | 4.748 | 7 |
| 208 | 5.935 | 7 |
| 277 | 5.383 | 5 |
| 555 | 6.075 | 11 |
| 832 | 5.373 | 3 |

Every lost ID/error remains reported; no validation or hidden residual was
removed to improve the score. Sentinel poses were not fitted after this failure.
`TECHNICAL_CHECK_PASSED` for execution,safety and replay is not `PARTIAL_SUCCESS`
or `ACCEPT` for head reconstruction. No physical material-point camera check,
frontal NME,bilateral profile IoU or user visual acceptance is claimed.

The independent post-inference evaluator completed in4.09s. Original fixed
reference masks/quadrature and one global positive similarity were used,without
shape feedback. Alignment-held1024 samples per facial region give:

| Region | Same-transform generic prior p95 mm | Video-only candidate p95 mm |
| --- | ---: | ---: |
| Nose | 5.408 | 4.591 |
| Perioral | 6.886 | 2.391 |
| Chin | 12.762 | 3.492 |
| Left-image cheek | 6.316 | 3.526 |
| Right-image cheek | 6.891 | 3.479 |
| Forehead | 6.830 | 3.467 |
| Other frontal face | 8.121 | 4.101 |

This baseline uses the **candidate's same evaluation transform**,not its own
optimal registration. It is a bounded diagnostic comparison,not a general
algorithm-performance gain claim. All seven absolute2mm targets fail. Entire
source-to-output p95(including unscoped source defects)27.865mm and whole-output
reverse56.672mm also fail; they must not be substituted with face-only medians.
Only20.3% of source area has the frozen diagnostic face scope. Native62 boundary
edges,unobserved skull/ears/neck,open eyes versus closed source eyes and source
uncertainty remain unresolved.

Actual6-direction source/neutral/video-only comparisons(total18 Blender images),
6 native canonical previews and5 actual video-camera overlays are saved locally.
All18 source-comparison images and the overlays were inspected. The experimental
face changes substantially from the generic prior,but nasal/lip/chin contour,
ears/skull and neck do not match the supplied source; no facial or complete-head
visual promotion follows. Common integer crop(165,442,553,987) across all18
images only enlarges inspection; no camera,geometry,metric or per-view scale is
changed. Both uncropped originals and crop invocation are preserved.

Independent OpenCV projection replay max1.25e-12px,native coefficient/geometry
replay3.82e-17 and exported OBJ replay4.99e-13 model units pass. The first Blender
evaluation launch imported cv2 indirectly merely to share constants; the bundled
Blender runtime lacks cv2. That import failed before opening a scan or creating
an evaluation output. Its full error capsule remains local; removing that unused
dependency changes no fit,source,alignment or metric and the evaluation then
completed. No weight installation,threshold rescue or extra fitting followed.
All188 unit tests pass,including full projection derivatives,positive depth,
shared-edge visibility,hidden/disallowed surface rejection and patient-geometry
read guards. These synthetic checks do not certify global self-intersections
or physical cross-view detector accuracy.

Private outputs: `assets/private/video-only-model-0241/{fit,render,scan-evaluation}`.
OBJ: `fit/experimental-VIDEO-ONLY-NOT-ACCEPTED.obj`. Original source/NPZ/PNG/OBJ,
consent metadata,hashes and failure capsules remain outside Git;only reproducible
tools/tests and this non-identifying summary are committed. Production defaults
and case002 are unchanged.

Stop this fixed-attachment detector-only configuration. Next discriminating
gate is a **known-geometry,scan-free attachment-transfer test**: determine whether
the same semantic pixel on a rotated/deformed licensed generic surface actually
denotes the frozen material attachment. Do not tune the current fit or fit more
subjects before that premise is measured. If material stability fails,replace
that observation model (for example with separately measured view-dependent
visible anatomical contours),rather than disguising semantic agreement as true
camera/shape evidence. A changed observation mechanism needs its own bounded
pre-registration; this rejection does not establish that all model-based image
fitting is impossible. The complete video-head goal remains active.
