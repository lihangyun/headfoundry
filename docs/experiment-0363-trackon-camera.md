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
