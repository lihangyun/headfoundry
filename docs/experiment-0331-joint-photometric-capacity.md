# Experiment0331:raw photometric information for joint camera/depth initialization

Registered 2026-10-23T01:40:07Z;whole1800s,deadline 2026-10-23T02:10:07.000Z.
Prior0330closedabc782a:conditional cameras pass3px/2%but pointp95.01249>.01.
No fixed-seed/count/noise/threshold/iteration rescue of that coordinate fixture.
Main variable:replace final sparse coordinate residual with fixed raw image
patch residual and free affine exposures. This adds pixel information,not a
claim that more coordinate fitting or tests suffice. Reuse only retained correct
0320residual,0329analytic derivative and shared projection/budget math;no deleted
0330runner/weights/framework restored. New independently generated image context
does not support a causal claim versus0330's different coordinate-noise data.

One owned scene seed331:20separated planar textured tiles,4x5centersx[-.63,.63],
y[-1,1],Zuniform2.6..3.5,halfwidth.16/halfheight.19. Each64x64Gaussian-noise
texture blurredsigma.8and scaled.25..65,original procedural validation data,
not training. Exact analytic ray/plane image formation. Three native720x1280
views,truef1200/center359.5,639.5:anchorI,R1=Ry18@Rx15,R2=Ry(-18)@Rx15,
t=p-Rp,p=(0,0,3). Generation only;estimator has free poses,no pivot prior.
Sensor noise1/255,gain[1,1.07,.94],bias[0,.01,-.01],one8-bitPNG/camera.
No image/texture rerender or selection after results. Review one input sheet
before inference;hash all images/truth/source and deny truth/texture/geometry/
unrelated private reads/network/subprocess in inference(cooperative audit).

Image-only source queries:goodFeaturesToTrackmax96/quality.02/minDistance15/
block5,foreground>.12eroded8,subpixelwin5/30iter/.001. LKfrom0to1/2andback,
win31/level4/30iter/.001,finite/status/return<=.75px/4pxsupport both targets.
Require>=48complete3-view queries;retain EVERYadmitted query thereafter.
Freeze whole-point20%held by SHA331/hold/index;at least9held and36train.
Held target coordinates/images patches never enter initializer/direct loss.
Native input sizes unchanged;LKpyramid is explicit initialization only.

Unknown-camera geometric seed:arbitraryf1280,essentialRANSAC1.5/.999seed331,
recoverPose>=90%positive mask support;alltrainingXYZtriangulated from0/1,
no pruning. Commonlogf/freeSE3/allXYZjoint TRFsoft_l1(1.5),analyticJac,
x_scalejac,max100,tols1e-8,f640..5120. AnchorI/unitbaseline1onlygauges.
Initial proper/positive/nonbound/converged required,not truth-selected.

Then freeze admitted train IDs/source pixels/target views and use8offsets
[(0,0),(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,1),(-1,1)]. One positive host
inverse depth per patch;here source-world planes make this locally model-exact,
not a curvature or skin-radiometry proof. Geometric depth seeds plus exact
source-query rays;alltargetpose/exposure/focal/depth remain unknown. Bounds:
f640..5120,rotationseed+/-.1rad,target2translation+/-.2baselineunits,
baselineangles+/-.1rad,logrho+/-.3,loggain[-.3,.3],bias[-.05,.05]. Sparse
TRFsoft_l1(.01),x_scalejac,max150,tols1e-8;all omitted Jacobian entries
checked at seed. Full-vector+infinity on included projection/bilinear/exposure
domain failure,never sample deletion/clamping. Installed SciPyTRFchecks
nonfinite trialf before loss/Jacobian processing;initial/FDnonfinite fails.

Independent evaluator ONLYafter both fits:lift EVERYtrain/held source query
using true first-hit tiles;included GTtarget visibility must match same surface,
no truth pruning. Normalize truth by true baseline to the estimator's unit
gauge. Initial/final separate,never select better. Requirefinalconvergence,
proper/positive/nonboundf,frel<=2%,held known3Dprojectionp95<=3pxEACHcamera,
alltrainpointp95<=.01normalizedsceneunit,held observed target reprojection
p95<=3pxeach,OpenCVreplay<=1e-9and wrong+.1radcamera negative>3px.
Any incorrect included surface association rejects. Units are NOTmedicalmm.

Prepare<=120s/2GiB,geometricseed<=120s/2GiB,direct<=300s/2GiB,evaluate<=60s/
2GiB,suite<=120s;whole1800s includes code/review/cleanup. CPU4threads,existing
descendant-tree monitor;one worker/stage,no duplicates. No package/model/
patient/scan/case002/training/upload/default change. Failure stops recipe,
keeps compact raw states/scores/hashes/source and one sheet,retire exclusive
entry/bulk/cache after PID/path/CRC/hash/protected38checks,independent local
cleanup commit before new method. Pass is conditional camera/depth capacity,
not actualvideo/head/medical/visual acceptance or permission to promote defaults.
