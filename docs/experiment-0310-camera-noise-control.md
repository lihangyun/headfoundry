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

## Actual result:physical-control REJECT despite conditional3pxpass

Executed source8881e50,one fit,worker start09:07:28.862Z. Whole parent6.079s,
camera+scoring4.750s;conservative observed process-tree peak105082880bytes,
three observed processes including actual payload. No assets/dependencies were
installed;no human data opened. Same141tracks,100%identity purity,52.2222%recall;
noise radialp95=1.267672px. These are Gaussian samples with sigma.5per axis,
not an assertion that every point is displaced less than.5px.

All five matrices/depths/focal-bound checks pass and each heldp95is2.14..2.39px.
Fitted focal1098.434938px versus true1200px:8.463755%error,above the registered
2%physical control. Backend uses all300evaluations without convergence. Thus
its TECHNICAL_CHECK_PASSED status describes conditional pixel/matrix consistency,
not calibrated physical recovery. The audit-level result is REJECT. No increase
in iterations or precision/solver/focal/point/seed/noise rerun follows.

Other originally registered scores are retained:centers max.027402scene units,
pointsp95.195420,noise-free truth projectionp95=65.741977px. These use the
unchanged three-camera-center similarity gauge(0,2,4);those centers are nearly
collinear,so orientation alignment can be noise-sensitive. Do not interpret the
large projected/point errors as a gauge-independent lower bound,medical-mm
measurement or proof of one optimizer cause. The8.46%focal error is itself
gauge-independent. Max300termination also prevents claiming a converged optimum
or fundamental impossibility. This ONE control demonstrates that the current
bounded unknown-focal chain does not satisfy its physical fixture at this noise
sample,not that all real-video failures share this cause or that all noise levels
fail. Noisy-held consistency alone is insufficient,as already required by the
technical-versus-physical distinction.

Consequent decision:do not download another tracker on the assumption that the
camera backend has been excluded by noiseless controls. Establish a physically
accurate,noise-tolerant camera mechanism on independent controls before another
real camera/head route. This is not permission to restore0308or sweep its cached
points. Keep actual3px/2mm/whole-head/user visual gates unchanged.

## Verified closeout

Source recovery8881e50,result1f0e193. Private compact evidence:
assets/private/closed-experiments/0310-camera-noise-control/evidence.zip,
105548bytes,15members,no images,CRC verified;SHA256
02904964cc00551dd15ee1a44cf28e6388508afdb5c89fd08575c1389399352b.
Preserves all raw clean/noisy observations/labels/edges/folds/truth,bearing and
BA solutions/scores,worker records,exact source/protocol. No input/model output
selection. Thirteen exclusive generated files139537bytes and one-off runner
removed after source/archive/resolved-target/reparse/inventory/no-live-worker
checks. No weights/framework/environment existed. All four shared camera/graph
sources unchanged;archived runner bytes match the pre-run source hash.

145retained tests pass in7.929s;39installed packages compatible. Thirty protected
original/fixture/unrelated files remain exact with the two earlier explicitly
recorded generic resource-monitor repairs preserved. First final-verification
script used a slash-specific source-name comparison;Windows backslash names
caused a missing-runner error after intentional deletion. Normalize path names
and verify archived bytes;no camera fit re-executed. Actual max OpenCV thread
count was not measured;the4thread configuration is the BLAS/OMP environment,
not an independently certified process-wide thread maximum. Worker memory/time
records cover the actual descendant tree. No production default or quality gate
changed. Closeout within the900swhole budget from the conservative09:06:01Z
start. No new route begins before this independent cleanup commit.
