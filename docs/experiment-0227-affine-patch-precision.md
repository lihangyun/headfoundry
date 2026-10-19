# Experiment0227: affine rather than translation-only patch alignment

Date:2026-10-19. Pre-registered before measurements. Status:`REJECT`.

0226's exact-truth initializer converges to the same biased endpoints on the two
failed known projective cases. This supports changing the **local patch motion
model**, not stronger coarse matching, more camera iterations or lower gates.

Use exactly0226's16 saved images/matches, not fresh feature extraction. Keep
source/descriptor endpoints, known homographies, source masks,3D/cameras and
precision/retention gates fixed. Primary variable: independently implement an
opt-in affine patch solver using existing OpenCV ECC. No learned weights,
training, scan usage or production defaults change.

Use21x21 float32 grayscale patches centered on the source point and descriptor
target estimate. Solve affine ECC from identity,30 iterations/correlation-delta
1e-5, gaussian filter1. The affine warp maps source-patch coordinates into the
target patch; map the center back to image coordinates. Require finite proper
affine maps with singular values in[0.5,2], and>=50% valid source-patch support
inside the target patch with a1px interpolation margin. Compare photometric MAE
only on valid support, in original0-255 gray units; it must be<=15. Reverse-align
from the refined target center into the original source patch; require the
existing<=0.75px forward/backward check. No truth, geometry or pose residuals
enter this solver or its eligibility decisions. Export warps and failure codes.

Known noise-texture affine/unit-direction tests must pass first. Then run once
on all16 original cases,180s budget. Every case still needs>=30 valid endpoints,
>=50% raw-match retention and p95<=1px. Report baseline-all, paired baseline and
affine errors separately, including every rejected point. No ECC window,
iteration, blur, eigenvalue, overlap, confidence or homography-strength sweep.
Failure stops before real localization. A pass permits only a separately bounded
real-video sentinel test, not camera/head/scan/likeness acceptance.

All data/outputs stay local. Case002, source scans, original/rejected outputs
and production defaults remain protected; no subject data is trained or uploaded.

Unit implementation note before pilot execution:5/6 known-affine noise patches
localize below0.118px. One finds a0.814px error with0.806px cycle discrepancy and
is correctly rejected by the unchanged0.75px guard. The unit test checks retained
accuracy and mandatory rejection, rather than incorrectly demanding every random
patch be valid. Neither the solver nor experiment gates are changed to rescue it.

## First result and one read-only cause check

The6.749535s single run rejects all12 nonidentity cases. Eligible retention is
only3.26%-18.94%, despite retained p95 below0.798px. All four identity controls
pass. Do not adopt a small selected-cohort error as a usable matching result.

Before selecting another method, run one unavailable-input diagnostic on the
same source0/612 projective matches, with true endpoints used solely as affine
initial seeds. Keep21px patches, all solver settings and all gates unchanged.
Budget30s; export every result. If even this oracle loses most supports, stop
this small-patch affine solver family rather than assuming a better seed fixes
it. If oracle coverage is sufficient, a future separately registered composition
with available0226 seeds may be justified; no outcome is presumed. Oracle data
must not replace the real matching input or authorize head/camera promotion.

The oracle also fails coverage: source0 retains49/336 (14.58%) and source612
7/204 (3.43%), with eligible p95=0.557406/0.432508px. Exact known targets
regenerate successfully. Better initial points alone do not solve this affine
patch estimator's usable-support problem. **Stop this small-patch ECC family**;
do not combine it with0226 or tune patches/blur/iterations/warp bounds to rescue
coverage. Tiny selected-cohort errors do not support real camera/head fitting.

A distinct next hypothesis may regularize the local image warp using a separate
context population, rather than solving6 free affine parameters from each weak
skin patch. Its final measured endpoints must still come from image alignment,
never be replaced by a fitted plane's projection. Any context/model fitting
must exclude the points used for measurement validation. No new real solve is
authorized until the same known-transform precision/retention gates pass.

All158 public tests pass in3.597s, including known endpoint truth, seeded-flow
argument checks, affine direction/cycle rejection and unchanged default cases.
This is reproducible technical verification, not camera/head acceptance.
