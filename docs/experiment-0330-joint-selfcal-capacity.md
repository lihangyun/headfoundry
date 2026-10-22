# Experiment0330:one complete joint three-view unknown-camera solve

Registered 2026-10-22T19:54:24Z;whole900s,deadline 2026-10-22T20:09:24.000Z.
0329closedab4d63fproves local common-three-view focal information and shows
source-excluding per-track holdout removes it. Single algorithm variable:
estimate sharedfjointly with all free poses/XYZ,not from pairwiseFsingular values.
No new library/model/weight or failed integration is restored. Reuse analytic
native Jacobian,NumPy/OpenCV/SciPy and existing descendant budget monitor.

Use identical0329owned120points/three poses/Kfrom SHA-verified capsule. First96
WHOLEpoint IDs supply all three training observations;last24wholepoints are
absent from estimator,held known3Dprojections independently evaluated in ALL
three cameras. Thus no held row leaks and every training point retains three
views. This fixture split is justified by available owned3Dtruth,NOT directly
transferable to actual-video validation. No holdout is cancelled. No comparison
to old recipe claims a single-variable causal improvement across different folds.

One deterministic sigma.5px/axis Gaussian coordinate draw,seed330,training only.
Estimator sees96XYtriplets only,unknownsquarefseed1280(native center359.5/639.5).
Essential RANSAC1.5px/.999and recoverPoseat that arbitrary seed initialize two
relative poses;unit translation seeds,all96XYZtriangulated from0/1. No inlier
pruning,GTpose/focal/depth/surface seed or accepted physical prior. All initial
depths positive and>=90%recoverPosepositive support,else stop. AnchorI/unit
baseline1only fix similarity gauge. Sharedlogf,freeRodrigues/translation camera2,
baseline direction2angles,allXYZjointly free. No spherical-motion/pivot prior.

One TRFsoft_l1fscale1.5,analyticJac,x_scalejac,max100nfev,tols1e-8,
f640..5120only;no pose/XYZprior/bounds or seed/count/noise/iteration sweep.
Full residual +infinity for invalidZtrial,never points dropped/clamped;initial
invalid/domain or coding failure stops. Require solver success and all proper
finite/positive states. Independent evaluation uses native gauge,baselineunit:
frel<=2%,ALL24heldknown3Dprojectionp95<=3pxEACHcamera,allpositiveheld/training
depths,nonboundf,training-pointp95<=.01sceneunit,OpenCVreplay<=1e-9and wrong
camera+.1radnegativep95>3px. These are conditional owned-scene results,not
medical2mm,actualvideo camera or head acceptance. Keep initial/final separately.

Prepare then one worker<=120s/2GiB,CPU4threads,fullsuite<=120s;whole900s includes
cleanup. Worker read audit denies truth/held/STL/unrelated private/network/
subprocess(cooperative not hostile sandbox). No human/case002/training/upload/
source/default change. Failure freezes recipe,archives tiny states/scores/source,
retires exclusive entry/output/cache,verifies38protected hashes and commits
independent cleanup before new method. Pass retains opt-in replay,not promotion.
