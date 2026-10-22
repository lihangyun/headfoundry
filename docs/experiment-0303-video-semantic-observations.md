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
