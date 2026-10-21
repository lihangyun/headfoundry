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
ALL36unordered actual pairs with the same contract. Save full coordinates,
descriptors,scores/identities and full matches. Geometry diagnostic in main
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
