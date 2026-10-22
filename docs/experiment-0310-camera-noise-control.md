# Experiment0310:one independent pixel-noise camera robustness control

Registered2026-10-22after0309metadata closeout6c53b6b,before implementation/run.
Evidence:0301/0308software control corrupts20%association edges but all admitted
coordinates are exact noiseless projections. Passing it does not establish that
the camera backend tolerates subpixel measurement noise.0308failed at signed
edge-scale initialization;this control does not assume that all NNpoints caused
the failure or that fixing an initializer would recover a physical head.

Single variable:add deterministic independent Gaussian noise,sigma0.5native
pixels per axis,seed310,to EVERY raw coordinate of the unchanged0301five-camera
procedural control. Noise is a diagnostic condition,not a claim that actual
video/model errors have this distribution or magnitude. Same scene/270IDs,
visibility,20%wrong association edges,cycle selection,held hash,all camera
parameters/iterations/objectives/rank/positive-scale/focal/3px gates. No model,
human pixel,medical/bone/case002asset,download,training or network access.
No threshold,noise-level,seed,pose-population or initializer sweep.

Freeze/save all raw noisy and clean arrays,edges,labels,selected tracks and
train/held split before fitting. Exactly one fit of the unchanged shared backend.
Keep truth separate;use it only after fitting for similarity gauge and scoring.
Report noisy-held error and noise-free truth projection separately. Apply the
original control accuracy criteria to noise-free physical scoring:proper/positive
five cameras,shared focal relative error<=2%,center max<=.01scene units,point
p95<=.01scene units,noise-free held truth projectionp95<=1px;all noisy held
views still need>=6rows andp95<=3px. Wrong+.1rad camera witness must exceed3px.
Do not interpret scene units as medical millimeters. Graph purity>=99%,recall
>=40%unchanged. No factual assertion that every0.5pxsample must pass these gates.

Implementation<=300s;one child<=180s/1GiB,CPU4threads;whole900sfrom registration
including report/compact archive/failed-only runner cleanup/tests/local commit.
Stage exception stops;do not retry real data or alter the camera algorithm.
On failure,record a demonstrated limitation under ONE declared condition,not
proof that all previous real failures have the same cause. Preserve shared
software/math/defaults and local original material. Remove one-off runner after
compact evidence and source recovery ref;no framework/weights/environment exists.
This audit alone authorizes NO0308cached rescue or new real-head experiment.
