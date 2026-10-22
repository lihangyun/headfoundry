# Experiment0303:continuous semantic-video acquisition,not camera/head acceptance

Registered2026-10-22T01:11:59Z after public/local asset preflight and BEFORE any
model execution.0302closedfcdf6f5;cached nine-frame graph variants remain frozen.
Goal active/account allowed at registration(short92%/weekly75%used). No duplicate
worker. Only this repo;ponytail full,no new runtime/model/paid asset.

New hypothesis:use persistent semantic IDs from continuous natural video with
the model's intended temporal crop tracking,instead of sparse texture matches.
Unlike0006's unrelated five AI views plus predicted-depth prior and0217's scan-
render anchor/PnP,this uses real sequential source pixels,NO depth prior/medical
geometry and no camera fitting in this acquisition stage. It is not another
score/point/closure variant on0299cached observations.

## Existing assets and source review

The pinned3758596byte task hash remains64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff.
Its four component hashes and three official model-card hashes are added to the
existing asset lock;no asset bytes/default changed. MediaPipe1.0.1local VIDEO API
and CPU delegate are inspected before inference. All three linked model cards
explicitly declare Apache-2.0;runtime/dependency notices remain separate obligations,
not a training-data or universal commercial-redistribution guarantee.

Official[task guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker)
links the bundle and individual cards. Public PDFs were saved locally and relevant
license/limit pages visually inspected,not only text-extracted:

- [FaceMesh V2](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf):
  tracking crop context is intended;478outputs include relative synthetic-derived
  z,not metric depth. Extreme looking-away/occlusion degrades applicability.
  The8degree tolerance concerns aligned-crop roll;do not misread it as an8degree
  raw-video pitch limit. Its80degree warning is not profile-quality clearance.
- [BlazeFace](https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf)
  supplies detection,not identity or back-of-head recovery. Card/guide input-size
  descriptions differ;do not hand-code preprocessing from those tables,use the
  pinned official task's internal processing.
- [Blendshape V2](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf)
  is separately licensed;blendshape output remains disabled.

## Fixed one-pass acquisition

Authorizedcase001video only,existing manifest/consent and0252RGBhash index.
Sequentially decode ALL1041native720x1280RGBframes from ordinal0,no seeking,
manual resize/crop/rotation/enhancement,scan/bone/case002,training or upload.
Verify EVERY input RGBhash against0252. Timestamp=round(ordinal*1000/reportedfps),
strictly increasing,nominal SDK ordering only,not calibrated physical timing.

One explicit local CPU FaceLandmarker,VIDEO mode,num_faces1,all confidence defaults
.5,no blendshapes/no transformation matrices. Internal official crop/resizing is
part of that model,not a custom resolution rescue. No fallback/reinitialization/
threshold sweep. Python networking rejected after asset/rights checks;no hosted
API. Recheck entire task hash after inference. Preserve missing detections as
missing/NaN,not zero/pseudo-3Dpoints;finite478x3required when a face is returned.

Save all normalized raw outputs/face-presence/timestamps/native XY and36fixed
review keyframes(0..1020step30plus1040),source hashes and two clearly labeled
source-only contact sheets. XYadapter is explicitly extent-normalized to OpenCV
integer-center:xy*[720,1280]-.5,validated on an independent pixel-center witness
<=1e-10px. Never use relative z as actual geometry or choose an origin after error.
No per-landmark visibility/physical identity is certified. Domain remains
UNVERIFIED even when detection succeeds,including extreme profiles.

Technical entry passes ONLY if exact inputs/assets/complete stream and finite
output contracts pass AND fixed frontal/oblique anchors0,30,210,240,300,330,
570,600,840,1020each have one face. These were chosen from0252source review before
predictions,not camera error. Other missing frames are fully reported. Detection
coverage is not accuracy,3pxcamera or2mmskin. No camera/head is fitted here.

Temporal observations are correlated with earlier frames. Future held geometry
scores are conditional on these measured predictions,NOT independent raw-frame
detector generalization;independent medical/visual gates still mandatory. Next
stage must freeze source/domain/visibility/semantic-vs-contour eligibility BEFORE
any camera solve,without error-based label deletion. No iris/occluded contour may
silently become a rigid surface measurement. Full target incl bilateral shape,
ears/neck/editability and actual visual acceptance is unchanged.

Implementation<=600s from registration,one worker,asset/init<=30s,stream<=180s,
working set<=8GiB,whole1800s from worker start including records/tests/commit.
On failed technical/anchor gate stop;preserve raw reports/hash/small evidence,
clean exclusive0303runner/derived output after protected-target checks,verify
shared tests and local closeout commit. Shared existing model/runtime/inputs and
successful fixtures/defaults/0207are protected,not exclusive disposable weights.
On technical success retain replayable acquisition and raw private observations
for separately registered camera eligibility;all physical qualityUNVERIFIED.

## Actual result:REJECT fixed coverage,not measured3Dfailure

Sourcee7546a5;one worker PID54108starts2026-10-22T01:17:12.829Z,exits1 in
20.954s,peak277671936bytes. All1041native RGBhashes match0252;all36keyframes
retained. Full task/components/cards pass,and task bytes remain unchanged.
Coordinate witness max0px.784frames have finite478-point predictions;257are
missing/NaN. Nine of ten fixed anchors detect;330does not. No retry/substitution.

Source-only sheet and full330visually reviewed. Its true angle was NOT calibrated;
the preselected oblique label is qualitative. Preserve this coverage rejection,
but do not infer all784other predictions are unusable or globally inadequate.
No material localization,camera,medical-mm,head or visual acceptance was measured.
Any later reuse needs a different justified domain/visibility/observation protocol,
not replacing330with a detected neighbor or retroactively passing this trial.

Keep all raw/absent rows and two sheets in compact private evidence;retire exclusive
runner/derived outputs. Common model/runtime/component provenance and public PDF
cards remain protected;temporary PDF page PNGs are disposable.142shared tests
pass in5.801s before cleanup. No scan geometry/case002/training/upload occurred.

## Closeout after product-quota interruption

Result commitfcc134c. Original1800s whole wall budget was NOT met because quota
stopped closeout;recovery is not a retroactive budget pass. The single inference
remains terminal/no retry. Local evidence.zip contains13members/all four raw
arrays/full frame ledger/reports/two review sheets,8578185bytes,SHA256
0c1d4e82a60f6be70bf5d49edb0b0ed056eb085549a4a953e9b65be8df24ec26.
Location:assets/private/closed-experiments/0303-semantic-video. CRC/SHA verified.

Removed53exclusive files,39685114logical bytes:the runner,derived output and five
temporary PDF page PNGs. Thirty-six native frame PNGs are not in the archive;
regenerate from protected video/0252index if needed. Source recoverye7546a5.
Shared model/runtime and improved common component/model-card provenance stay;
there is no new failed framework to uninstall. All25protected hashes unchanged,
including originals/consent/shared fixtures/0207/common model and provenance.

Observer timed out during closeout;native execution recovered after checking
actual process/file state. No Python worker remained and no inference was
restarted. A fresh shared test verification passes142tests in6.721s. Active
source/defaults unchanged;no dangling runner import. Temporary closeout-only
verification scripts are also removed separately,not counted in the53trial files.
The raw acquisition is evidence only,not approved camera input or an accepted head.
