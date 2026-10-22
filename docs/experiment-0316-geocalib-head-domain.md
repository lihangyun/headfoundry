# Experiment0316:known-camera head-domain calibration,not patient fitting

Registered2026-10-22T15:39UTC after software fcccbdd,before new input acquisition,
rendering or prediction. Whole1200s to15:59UTC includes closeout/tests/commit.
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

Pre-forward runner repair15:42UTC:initial Blender script imported Pillow,which
is absent in its bundled Python. It failed before ANY render/image/NN invocation;
Blender default exit0masked the Python error at process-exit level. No input
completion sentinel existed,so inference was never allowed. Move only contact
sheet construction to existing main Pillow,require render.json and request
Blender --python-exit-code1. Keep first log/record,one render-only rerun from
unchanged acquired mesh/config,not another NN trial or appearance adjustment.

## Actual conditional domain result:REJECT

Initial producer7bfdf0a;pre-forward-only runner repair12f53f1. Reviewed the
four-image input sheet before prediction:upright front/bilateral generic heads,
complete face/ears and blue background;lower open-neck crop and untextured
surfaces remain limitations,not patient or photorealistic data. Room input is
also procedural. Shared Blender projection replay max<=.000183px(all contexts).
The repaired render worker7.234s,conservative tree peak653492224bytes.

One exact sequence of four NNforwards(seed316each),no priors or refits. Worker
60.375s,conservative tree peak1045823488bytes;individual forwards2.875,3.031,
2.719,2.922s. Full runtime/weight/source inventories verified before import.
All matrices finite/positive/nonboundary and all four outputs retained locally.
Runtime exit/resource pass is not the physical result below.

| Context | True focal | Predicted focal(nativepx) | Relative error | Fixed-ray p95px(upstream / exact-resampling) |
| --- | --- | --- | --- | --- |
| Room | 1200 | 733.297 | 38.89% | 131.869 / 131.855 |
| Front head | 1200 | 2275.081 | 89.59% | 303.763 / 303.749 |
| +60 head | 1200 | 1212.997 | 1.083% | 3.964 / 4.672 |
| -60 head | 1200 | 1581.898 | 31.82% | 107.898 / 107.989 |

None of the head contexts passes both3pxmappings. Different coordinate choices
cannot rescue this result;do not select the one near-correct side. Room also
fails,so this is NOT evidence of an exclusively head-domain failure or universal
failure on real photographs. Small conditional untextured controls establish
no calibrated population uncertainty or real-patient error lower bound. They
DO prevent treating this learned focal prior as verified high-precision K in
our pipeline. Stop candidate;no other scene/seed/renderer/weight/precision run,
no cached0308camera rescue,actual video/head fit or new medical-mm score.

Next technical investigation must add independently constrained camera/material
information;another unvalidated monocular focal guess is not sufficient.
Main task remains unmet and active. Source/defaults/actual3px/2mmgates unchanged.
