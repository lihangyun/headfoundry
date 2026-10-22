# Experiment0316:known-camera head-domain calibration,not patient fitting

Registered2026-10-22T15:40UTC after software fcccbdd,before new input acquisition,
rendering or prediction. Whole1200s to16:00UTC includes closeout/tests/commit.
Hypothesis:the additional learned focal prior can meet the existing3pxcamera
budget on a head/blue-wall domain,not merely run on arbitrary gradient pixels.
Single main variable scene context:a simple owned Manhattan room control versus
CC0generic head against uniform blue. Head yaw0,+60,-60are fixed coverage,not
an angle/seed/focal/config sweep. Same K/f1200px/native720x1280throughout.

Use only previously pinned MakeHuman CC0graphical base asset and grants from
examples/makehuman-base-asset-lock.json. Active base.obj is absent outside an
excluded/unclassified temporary investigation path(which is NOT read/copied).
Reacquire exactly these three public files at the frozen revision/hash,<=8MiB
each/30srequest,not MakeHuman application/framework or rejected fit code.
Extract generic head/neck/eye helpers using retained shared extractor. No scan,
patient photos/video,case002or training. No inference cue from medical geometry.

Owned Blender5.2rendering and shared camera conversion/projection replay;source
geometry/frame/K hashes frozen before NN. Skin-colored untextured generic head
is a conditional domain control,not a photorealistic or real-person benchmark.
Review the image sheet before NN for orientation/framing/render corruption.
If invalid stop input test;do not change appearance after seeing predictions.
Pixel truth is integer-center OpenCV K(cx359.5,cy639.5);Blender edge-coordinate
principal point360,640,explicit .5conversion. Geometry projection replay<.05px.

Four complete separate FP32CPUeval forwards(default320short edge/30LMsteps),
same exact0314checkpoint/full strict state and0315runtime inventory,seed316
reset identically per image. No priors/trueK passed to NN,network disabled.
Both recorded upstream-native and exact pixel-resampling K mappings scored;
neither may be chosen post-hoc to rescue. Preserve raw outputs/all four images.

Fixed independent native ROI grid25x25,x140..580/y330..950 converted to true
unit-depth rays. Score predicted-K projection error on these fixed rays:all
three head contexts must have p95<=3nativepx under BOTH mappings,finite positive
nonboundaryfocal,relative focal error<=2%(same known-focal control budget0310).
This isolates K error with true pose,not a full SE3or correspondence admission.
Room is a contextual control,not allowed to rescue head failure. Record actual
model covariance but do not treat it as verified calibration uncertainty.

Input/render worker<=180s/3GiB,NNworker<=180s/3GiB,4CPUthreads,no version/
precision/scene/seed/output selection/retry. Fail stops actual-video/head use.
Archive compact reports/hashes/Git source and at most2image sheets,then remove
exclusive0313source/0314weight/0315overlay/0316inputs/runners/tests/lock after
protected-file checks and independent local cleanup commit. Shared renderer,
extractor,licenses/originals/defaults/0207remain. No physical camera/head/medical
claim can follow a software pass;even this conditional fixture pass would need
independent actual-video correspondence/pose evidence. No upload or Git push.
