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

## Actual result:conditional cameras pass,point precision rejects the recipe

Source8adb91a,registration41bbbad. One worker2.328s/123637760peak bytes,
26evaluations,ftoltermination success. No second solve or setting change.
Focal1280initial->1204.712525final(true1200),relativeerror.00392710438.
All24independent heldknown3Dprojections in each of three cameras:initialp95
18.5151/70.4061/25.3884px;final1.090659/2.328945/2.171750px. Proper matrices,
positive held/training depths,nonboundf,OpenCVreplay5.116e-13px,wrong-camera
negative126.2941pxall pass. This is TECHNICAL_CHECK_PASSED conditional camera
subgate on owned noisy coordinates,not actual-video camera acceptance.

TrainingXYZp95error.31063226initial->.0124901413sceneunits final,still greater
than registered.01. Whole recipe REJECT. Scene units are NOTmedicalmm;do not
convert this into a patient2mmclaim or relax.01after seeing the near miss.
All truth/whole held IDs stayed outside inference;no inlier/held pruning or
selected initial/final promotion. The result supports joint estimation rather
than pairwisefocal inversion,but does not admit a head or guarantee actual
image correspondences match this independentGaussian coordinate model.

Compact evidence assets/private/closed-experiments/0330-joint-selfcal/evidence.zip:
27497bytes/11members/no images,CRCverified,SHA256
05063e446b81dcc05197d589111d14859e68a68bf58dbb7364e3cfa1aa367e46.
Keep ALLsmall input/truth/initial/final/score arrays,logs/identities/source.
After actual worker PID checks,10loose files24978bytes compacted,exclusive
entry retired. All small fixtures recover exactly from archive;sourceGit
8adb91arestores the runner. No weights/packages/framework to uninstall.
38protected identities verify before/after;production defaults and0207unchanged.
No extra noise/seed/point/iteration trial follows this stop. Full target remains
active:real-video cameras,editable head,medical error and visual acceptance unmet.
