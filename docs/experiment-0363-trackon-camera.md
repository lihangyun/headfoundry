# 0363 prediction-only camera control

2026-10-26. New evidence0362passes smooth-view endpoint3px on owned0332scene.
Reuse successful0332camera math, not a retired model integration. Single main
variable: input associations from fixed Track-On2predictions instead of DIS.
No rerun of model, no truth-derived fitting initialization or point selection.

Use frames0,6,12; admit points finite/in native4pxbounds and predicted visibility
>=.8 at all3anchors, >=48points. This is an estimator-side rule fixed before
execution, distinct from0362truth-visibility scoring. No error-based pruning.
Whole-point deterministic SHA256331/hold/index20%holdout, >=36train/>=9held.
f1280initial, bounds640..5120, OpenCV EssentialRANSAC1.5px/.999/seed331,
recoverPose90%inlier support, all training points triangulated, shared native
analytic-Jacobian TRF100eval softL1scale1.5/tolerances1e-8. Save E/inlier/pose
evidence before gates. No direct photometric fit or parameter rescue.

Fit<=180s/2GiB; evaluation<=30s/1GiB. Evaluate against independently held scene
geometry: proper world-to-camera matrices, positive depths, nonbound focal,
focal relative error<=2%, held known3D projection p95<=3px each camera, training
3Dpoint p95<=.01baseline-normalized scene units, held observed<=3px, OpenCV
projection replay<=1e-9 and wrong-camera negative control>3px. No medicalmm claim.
Require optimizer success. Any failed gate stops before patient execution.
No changing focal/precision/mask/threshold after result. Preserve evidence and
follow cleanup policy for failed route components before a different route.

## Result: REJECT

Source recovery commit `83ad15f`. One fit and one independent evaluation only;
no model rerun or tuning. Fit converged in22evaluations, focal1186.852674px
(truth1200px, relative error1.09561%). Proper rotations, positive depths,
nonbound focal and projection replay passed, but these do not establish accuracy.

Held known-3D projection p95 per view:5.42818/8.45859/8.38117px, above3px.
Held observed p95:5.53517/8.60663/8.76843px. Training point p95 error
0.03010145 baseline-normalized scene units, above0.01. Four visibility misses
were recorded across anchor observations; this is not necessarily four distinct
points. No post-result pruning is permitted. OpenCV replay max4.55e-13px and
wrong-camera negative control136.73141px passed.

Fit worker elapsed1.875s, peak116953088bytes; evaluation1.359s,
peak99905536bytes. Worker TECHNICAL_CHECK_PASSED means process completion only;
the actual independent quality decision in result.json is REJECT.

Evidence remains local in assets/private/trackon-camera-0363 (observations,
source hash, initial pose evidence, solution, fit/evaluation reports and logs).
0362 demonstrated owned-scene 2D tracking only; it did not certify this camera
estimator. The present result does not identify one proven root cause or prove
that every use of the tracker fails. No patient reconstruction, medical surface
measurement or likeness acceptance was performed. Stop this configuration.

Closeout pending: inventory exclusive failed-route dependencies, preserve a
compact hashed archive and successful shared fixtures, then remove failed-route
components and commit cleanup separately before starting any different route.
Closeout is now recorded in cleanup-0363-trackon-camera.md. The original
trackon-camera-0363 directory was removed after its compact evidence was archived
under assets/private/cleanup-0363/evidence.zip. No new route follows implicitly.
