# Experiment0299:fixed real-image sparse observations,not a recovered head

Registered2026-10-21T23:49:32Z before preparation/inference/scored observations.
0298admissiondffa30fis complete. Goal active,short32%/weekly66%used at last check,
ordinary usage allowed. No other worker alive. Only this repository is modified.

Hypothesis:independently detected L-v2/B sparse repeatability/descriptor matches
can supply actual skin observations across turns,unlike chained DIS/LK/manual
corner refinement. This is the new observation mechanism,not an old solver/focal
or tracker rescue.0298software equality does NOT establish this hypothesis.
Do not test solely on the old unlit noise silhouette as a natural-video proxy.

Inputs:authorizedcase001video only,manifest/consent and0252full RGBhash index.
Fixed frames0,60,120,240,300,360,420,600,690;decode sequentially from0,no seeking.
Native720x1280RGB,no resize/enhancement. After source preparation and BEFORE any
model result,annotate nine conservative face-interior polygons using only those
source pixels. Exclude cap/hair/background/neck;exclude outer occlusion edges
where possible. This is source hygiene,not medical segmentation or identity
truth. Freeze polygons/hashes before inference;never crop by resulting errors.
No skin/bone/case002 content in any estimator. No training/upload.

Exact0298source/assets/runtime,FP32noAMP/noTF32;14wheel identities,core hashes,
canonical model hashes and strict full state/unchanged copied bytes rechecked.
All4096global keypoints per native frame,then only polygon-interior points enter
matching. Descriptor cosine dual-softmax inverse temperature20,mutual maxima,
probability>.1. Equal-score conflicting endpoints withheld from independent
support with ALL raw pairs retained. No threshold/point/frame/precision sweep.
Confidence is not visibility. No default downloads/network after asset checks.

One known2Dcontrol:frame240,one native affine transformation about359.5,639.5:
OpenCV5degree roll/scale.97/translation(+7.25,-5.5),INTER_LINEAR,constant zero
border. Same4096detector points/descriptor/matcher;target face polygon is exactly
transformed from source. Require>=32unique matches,source and target occupy>=4
of fixed3x3polygon-bounding-box cells,and ALL retained matches' localization
p95<=3nativepx. Report every error,maximum and missing support,not only inliers.
Nearest-grid quantization alone can contribute at most(1+.97)*sqrt(.5)=1.393px;
3pxis a prospective total FRONTEND error budget including detector/interpolation
error,not a proof of3Dmaterial accuracy or a change to the actual3pxcamera gate.
Stop this recipe immediately if this necessary control fails;no real-video pair
inference or head fitting then. Never silently relax to make this control pass.

Only after2Dcontrol passes,extract the remaining eight fixed frames once. Match
ALL36unordered actual pairs with the same contract. Save full face-cohort
coordinates,descriptors,scores/global identities and full matches,plus all4096
native coordinates;outside-face descriptors are not a matching population.
Geometry diagnostic in main
existing OpenCV/NumPy environment,not another installed framework:deterministic
SHA256 endpoint-index split70%train/30%held,USAC_MAGSAC1.5px/confidence.999/
10000max iterations on train only. Score EVERY held match with symmetric
point-to-epipolar-line RMS distance,no residual filtering. Eligible edge requires
>=16train/>=8held/each side>=4of9cells and heldp95<=3px. Record training inliers
but never use them to select the held population. F/epipolar passing cannot
certify physical identity:0286's along-line counterexample still applies.

Readiness check only:the passing-pair graph must connect all nine fixed frames.
This is this bounded recipe's sufficiency screen,not a general theorem about
video observability. Form raw multi-view graph from unique matches;report all
duplicate-frame components and all consistent track lengths without rescue.
Before any camera follow-up,inspect deterministic spatially spread raw pair
overlays for(0,60),(240,300),(300,360),(600,690);retain at most two panels at
closeout. Manual plausibility is not independently measured subpixel accuracy.

All gates pass=>TECHNICAL_CHECK_PASSED scoped2D/pair readiness only;physical
identity/rigidity/cameras remainUNVERIFIED. Any control/readiness failure=>REJECT
this fixed sparse observation recipe,not all free/self-developed reconstruction.
No actual-camera3px/medicalp95<=2mm/head/ears-neck/mesh-safety/visual gates changed.
No head fitting orACCEPT in this experiment. Camera continuation must be separately
registered using new observations,not fabricated from the diagnosticF matrices.

Whole2400s from source preparation start,implementation<=600s,prepare<=60s,
source polygon review<=240s from first prepared-image view,strict state<=60s,
2Dcontrol<=120s,nine total native extractions<=120s,all matching<=120s,
geometry<=180s,remainder evidence/tests/cleanup/local commit. GPUreserved<=7GiB,
worker peak working set<=8GiB. One fixed attempt,no live-process duplicates.
On failure:preserve report/raw control and pair arrays/hashes/Git recovery point,
at most two private source panels and notices;remove0299exclusive source/output
AND now-failed0298model/runtime/weights/wheels/cache/framework/lock/runners after
its successful software evidence is verified. Protect original inputs/consent,
0230/0293/shared code/defaults/unrelated0207. Verify and commit cleanup BEFORE
another different route. Do not silently retain the failed model infrastructure.

## Source-only freeze before inference

Preparation started2026-10-21T23:50:27.062Z;one sequential worker PID6644exits0
in2.016s,all nine native RGBhashes match0252. First source review23:50:37.528Z,
regions/control frozen171.726s later,inside240s. Only source pixels were inspected.
Frozen-input receipt SHA256
e717a6887ab6a968d2c3a6dae67b6658c9e998e11578e6ff1c578b895a4927d3.
Conservative polygons omit cap/ears/neck and may omit some occlusion-edge skin;
this limitation stays fixed and cannot be corrected after matching results.

## Actual result:REJECT the fixed raw sparse observation recipe

One preparation PID6644exits0. Inference sourceccbd3e4,one worker PID53412exits0
in13.515s;geometry source19fa961,one worker PID22040exits1 with completed
REJECT report in0.688s. No second forward,threshold/precision/frame/mask rescue.
Before spawn,a Node variable scope error prevented dispatch;the exact frozen
receipt was re-read and verified before the ONLY worker started. No input/model
or scientific configuration changed. Strict complete state/copy checks before
and after pass;GPUreserved6272581632bytes,peak working set1770373120bytes.

Known affine control has117unique mutual matches/8cells per side,p95=2.09303px,
so its prospectively registered interpolated-p95/count gate passes. It is NOT a
clean correspondence set:6/117errors exceed3px,max141.90852px. Preserve those
outliers and the exact interpolated percentile,not an invented claim that every
match or at least95%of empirical rows is within3px. No equal-score endpoint ties
occurred;semantic lookalikes can still be grossly wrong without numeric ties.

Actual face-cohort counts for0/60/120/240/300/360/420/600/690 are
114/89/123/168/85/104/80/146/197. All36pairs were matched once.22pairs lack the
registered16train/8held minimum and are NOT measured physical-precision failures.
All14eligible numerical checks exceed3pxheld epipolar RMS p95;range4.44560–
166.61433px. Exact perspective software witness max0.000662873pxpasses. Selected
actual pairs:0/60=78.43923px,240/300=8.56932px,300/360=68.21262px,
600/690=166.61433px. Even near-repeat240/600=4.44560px. Passing edges0/36;
root component onlyframe0. No actual camera or head is estimated.

Raw multi-view graph has91components,12with duplicate-frame identity conflicts;
consistent lengths2/3/4/5 are60/16/1/2. Neither graph counts nor training-RANSAC
inliers are physical identity acceptance. Predeclared raw spatial panels reveal
forehead-to-cheek and forehead-to-chin mismatches. Other semantically plausible
matches do not establish rigid tissue or subpixel truth. Full arrays/statuses
remain in compact private evidence;the two panels are diagnostic input matches,
not a reconstructed white head or the user's visual acceptance.

Scope:reject this one-shot detector/descriptor+raw dual-softmax observation
contract,not the entire DeDoDe family,all robust SfM pipelines,all video evidence
or every free/self-developed method. Normal robust geometric association was
NOT evaluated as a reconstruction pipeline here. A future materially different
identity/outlier mechanism needs independent controls and preregistration;do not
reinterpret this failure as permission for threshold/mask/point/focal sweeps.
Actual3pxcamera/2mmskin/head-completeness/mesh/visual gates remainUNVERIFIED.

Failure closeout must preserve0298successful software archive,0299full raw
face-cohort/control/pair/held evidence and two source panels,then retire the
exclusive0298/0299integration. It is not an accepted reusable observation asset.

## Verified cleanup and recovery

Result commit97b1dea;complete inference sourceccbd3e4/geometry source19fa961.
Compact private assets/private/closed-experiments/0299-real-sparse-observations/
evidence.zip contains76members/two raw review panels,2003208bytes,CRCverified,
SHA256=479842be79bb6f272b4792dac05d1303b9dca6ba55a8e8a36860dd5f432d6f3d.
It includes full face-cohort feature/descriptor arrays,all36raw match sets,all14
held-error arrays,control outliers,graph components,source-only regions/input
hashes/protocols/receipt references.0298successful software archive stays separately
verified;its50actual dependency notice texts are retained there,not discarded.

After exact root-contained targets,all-file reparse/inventory guards,archive
hashes and zero scoped live workers were verified,five exclusive source/lock
files and two runtime/output directories were removed. Total32165files/
12331420239logical bytes(12.33decimalGB),not measured disk-space gain. Native
directory cleanup PID49812exits0 at2026-10-21T23:59:35.633Z. No model-specific
cache or live import remains.140shared tests pass in5.244s. All seven protected
hashes match after deletion;original video/skin,authorization,0230/0293shared
fixtures,defaults and unrelated0207are intact. No case002content was read.

Git can recover source and the exact asset lock,not deleted public binaries.
Checkpoints/framework/wheels would require reacquisition at their recorded
hashes;full native source frames would need sequential re-decoding. Compact
evidence is not a full binary backup and stays private/local. There is no
background model worker and no accepted head. Whole closeout is within2400s.

Next research question is materially different robust multi-view identity/outlier
verification,not rescoring raw matches or another threshold sweep. Raw putative
matches are not final SfM observations;neither their rejection nor normal
training-RANSAC inliers establish physical identity. Any new geometry pipeline
needs its own independent unknown-camera/outlier witness and fixed held-view
validation before patient fitting. Do not restore this runtime automatically.
