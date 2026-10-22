# Experiment0321:image-only direct-patch unknown-camera capacity

Registered2026-10-22T17:50UTC,before generation,tracking or a scored solve.
Whole2400s,deadline18:30UTC. No patient/scan/case002,model,download,new dependency,
training,upload or production-default change. Use ponytail's existing-math-first
rule and CAMERA/INPUT_DATA diagnosis,not appearance promotion or Peek code.

Hypothesis:shared-camera direct raw image-patch observations can refine an
image-only initializer into physically correct unknown focal/SE3/depth. This is
the first full solve using0320's original residual,not0251's known scan/SHpose
fit or0310's archived noisy point-coordinate recipe. The new independently
generated contexts supply depth variation and noncollinear camera centers.
LK is only initialization:0220's retired temporal-video/COLMAP integration is
not restored,and no current or archived real-video camera is retried.

Single main variable:replace the final point-coordinate objective with the
fixed direct photometric patch objective;record both initialized and final
states without choosing between them after scoring. Two prospectively ordered
contexts:20 disjoint frontoparallel textured panels at multiple depths,then a
curved textured ellipsoid. Seed321,owned procedural material,not synthetic
training data. First is locally model-exact;second tests constant-depth patch
approximation under curvature,not head likeness. No scene/seed/angle/count/
noise/iteration/solver sweep;first failure stops the recipe,second stays
UNVERIFIED if not run. Synthetic success cannot admit patient cameras.

Six720x1280images:truef1200,integer center359.5/639.5;anchorI,other rotations
yaw+12,-12,+24,-24and pitch+16degrees about(0,0,3). Estimator receives only
images,not K,poses,depth,mesh,visibility or truth-file bytes. Renderer uses
edge-coordinate center360/640and its+.5sample convention. Grayscale vertex
material plus fixed gains[1,1.07,.94,1.10,.92,1.03],biases[0,.01,-.01,.005,0,-.005],
Gaussian intensity noise sigma1/255. No adaptive image selection or rerender.

Image-derived initialization:goodFeaturesToTrack max96,quality.02,minDistance15,
block5;image>.12foreground eroded6pixels,cornerSubPix win5/30iter/.001.
Anchor-to-each-target LK win31,maxLevel4,30iter/.001;bidirectional valid status,
finite return<=.75px and4px support in every view. Require>=48complete tracks;
retain every admitted track thereafter,no GT/residual pruning. Native pixels.
Existing short_track_camera.fit is called once,unchanged defaults,300maxnfev.
One hash-frozen held target row per track;source queries ineligible. Its existing
all-view-held metric therefore REJECTs zero independently held source rows:
record that honestly,not relabel as a physical pass. Require>=6held rows in each
target for final recipe;independent known3Dprojection controls cover ALL six
cameras,including anchor,without pretending a supplied query is held evidence.

Reanchor initializer to pose0I and unit largest estimated baseline. Reanchor
points then initialize positive inverse depth at exact source query rays.
Patch offsets[(0,0),(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,1),(-1,1)].
Unknowns:shared logf,free targetRodrigues/translation except unit-baseline
direction2angles,per-point log inverse depth,positive loggain and bias/image.
Anchor exposure zero. Train photometric rows exclude frozen held target rows.
Bounds:f640..5120;Rodrigues seed+/- .1rad;nonbaseline translation+/- .2baseline
units;baseline direction angles+/- .1rad;logrho+/- .3;loggain[-.3,.3],bias[-.05,.05].
TRF sparse finite differences,soft_l1 f_scale.01,x_scalejac,maxnfev200,
ftol/xtol/gtol1e-8. No priors or true-camera/geometry initialization. Check omitted
sparse derivative entries at initial state before optimization. No known-camera
parameter fixes except ordinary similarity gauge.

Invalid domain has extended loss +infinity for the ENTIRE fixed-length residual
vector,never deleted/clamped samples. Only explicit0320 support/depth/exposure
domain failures are caught;schema/coding errors fail. Initial or finite-
difference nonfinite residual stops. Installed SciPy TRF's nonfinite-trial
rejection is inspected before use. Final state must be finite/valid,optimizer
success true,and physical criteria below pass;termination alone is not success.

Truth available only in separate evaluator after fit. Lift ALL admitted source
queries to visible triangles and require first-hit target visibility,without
dropping failed points. Align all six noncollinear camera centers by ONE proper
positive similarity;rank and OpenCVprojection replay checked. Fixed known3D
points projected by estimated cameras must have p95<=3px in EVERY camera;
focal relative error<=2%,center max<=.01sceneunits,point p95<=.01sceneunits,
proper rotations,positive depth,nonboundf and>=6target held rows withp95<=3px.
Wrong+.1rad camera must fail3px. These are conditional unit-scene controls,
not patient-mm or medical2mmmeasurements. Report initial/final separately.

Budgets:prepare each<=120s/2GiB;image-init<=300s/3GiB;direct<=300s/3GiB;
evaluation<=60s/2GiB;shared suite<=120s. Four math threads. Existing Windows
descendant-tree monitor,immutable outputs perstage,no duplicate jobs. Inference
read audit denies truth/STL and unrelated private assets;this is a cooperative
audit,not a hostile native-code sandbox. Hash all inputs/outputs/source versions.

Stop immediately on resource/coverage/domain/physical failure,no post-score
engineering rerun. Before a new route:compact raw states/scores/logs/source hash
and at most one input sheet;CRC/SHA/archive inventory and original/shared-source
hash checks;remove exclusive controller/solver/generated bulk/pycache,retain
0320correct pure arithmetic/shared regressions;independent local cleanup commit.
Passing both controls retains only opt-in solver plus minimum runnable check,
and requires a separately registered real-observation admission,not blind headfit.

## Pre-generation entry repair

Initial implementation07bdcab stops before entry.json,any image generation or
worker:the protected-ledger reader chose short_track_camera.py's older
prior_expected instead of its current expected hash. Actual byte SHA4a9196cb...
79d0b equals the ledger's expected and Git source has no diff. Correct the
reader to expected (explicit generic amendments still take precedence),not
rebaseline the shared file. Only the positively verified empty own output
directory can be reused;nonempty refuses execution. Preserve this first stop;
no tracker/optimizer/scored input has run and no experiment setting changes.

## Actual fixed execution and stop

Executed source eb10d0b after the documented pre-generation repair. Panel image
generation completes13.219s/225689600peak bytes. The one image-only initializer
detects96source corners but only34meet the fixed full-six-view FB/support
screen (minimum48). It stops1.609s/197435392peak bytes before geometric fit.
No threshold,count,angle,seed,image,pyramid or repeat is changed after seeing
this count. No source-video pixels or scan geometry are used in this experiment.

REJECT complete registered recipe at observation coverage. Direct residual
optimization,unknown-camera physical precision and curvature context are all
UNVERIFIED,not measured precision failures:the direct optimizer never runs.
The independent true-pose evaluator is also not run after this stop. This does
not establish that direct optimization or patient-video reconstruction is
impossible,and it is not a new acceptable camera/head/medical result.

The inspected fixed input sheet confirms multiple depths and noncollinear
view motion;it is not a human-reconstruction comparison. Complete-view LK
coverage is a prerequisite imposed by this minimum prototype,not a fundamental
requirement of all direct methods. Freeze this exact capacity recipe;do not
lower48,add corners or change LK/angles to rescue it. A new direct design must
justify an actually different initialization/observation architecture before
registration,not quietly recycle this34-track set or assume trueK/pose.

Only0320's previously verified pure residual/regression stays active. Exclusive
0321solver/controller and generated bulk retire under cleanup0321. Full target
is still active and unmet;no patient camera,head or2mmmeasurement exists.
