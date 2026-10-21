# Audit0273: observation pixels are not a calibrated physical error budget

Date:2026-10-21. Preregistered before the numerical witnesses. Budget10min from
01:23:28Z to01:33:28Z. No learned model,private data,download or new dependency.
0272 remainsREJECT/retired;this audit does not change its1px contract or restore it.

Question:can a single observation-error threshold independently certify or rule
out downstream3px held projection and2mm geometry? Use the pinhole/triangulation
contract in [OpenCV's primary reference](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html),
existing project projection/DLT triangulation,independent closed-form stereo
depth and OpenCV triangulation. Main variable is geometric conditioning,not a
model/threshold sweep or actual patient accuracy.

Two fixed analytically chosen witnesses,not fitted to0272's residuals:point
(0,0,600)mm,focal1000px,principal(360,640),parallel cameras centered at±B/2.
Narrow caseB=20mm,observations perturbed(+.75,-.75)px horizontally;wide case
B=420mm,perturbations(+1.1,-1.1)px. Independent held camera center(100,0,0)mm;
its exact observation is never triangulation input. Predict that sub1px input
can still fail2mm/held3px,while>1px input can conditionally satisfy these two
point-level bounds. No camera/scene/seed search.

Require closed-form depthfB/disparity,existing DLT and OpenCV answers to agree
within1e-6mm;zero-noise replay<=1e-8mm,positive depths/proper rotations,all native
image points inside720x1280. Check a global2.3x geometry/camera scale leaves
pixels unchanged and scales metric errors2.3x. Reject nonfinite/zero disparity.

Success is onlyTECHNICAL_CHECK_PASSED for conditional synthetic point-error
counterexamples. Known cameras/metric baseline are an oracle here;this is not
unknown-camera recovery,a surface2mm test,whole-head precision,real-video
rigidity or a corrected-model pass. In particular,one-point distances cannot
replace the fixed whole-head similarity/surface evaluator.

If positive,the justified next question is a separately registered **physical
camera estimation measurement with independent3D targets**,not repeating the
planar recipe with a looser threshold or treating this audit as asset adoption.
Any future use of a retired component needs a materially different information/
estimation hypothesis and bounded registration. Existing3px/2mm/full-head/visual
gates,defaults,input rights and cleanup rules remain unchanged.
