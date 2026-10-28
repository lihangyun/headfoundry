# 0382: known-prior camera recovery with render-conditioned semantics

Registered2026-10-28 before rendering/detection. One observation mechanism:
re-detect candidate renders, rather than transport fixed frontal material anchors.
Only generic licensed FLAME2023Open neutral mesh, existing locked MediaPipe task,
shared rasterizer, NumPy/SciPy/Pillow. No human input/scan/model training/download.
Exact model lock b3a5c27654504beb5845a578f71f51c2b89c18d21679ae55690cd8d2c05a64f2;
task64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff.

Normalize neutral mesh by AABB center and maximum vertex radius. Same512square
smooth clay raster for target/candidates, fixed light/background, principal256.
True camera R=Rodrigues(-.12,.32,.03)@diag(1,-1,-1), t=(.04,-.03,4.2), f740.
Evaluator saves/reads truth separately; inference reads only neutral mesh and
target PNG. This is a same-renderer/known-identity control, not domain validation.

Seven unknowns from zero start: R=Rodrigues(.1*q[:3])@diag(1,-1,-1),
t=(.1*q3,.1*q4,4*exp(.1*q5)), f=700*exp(.1*q6). Bounds rotations+/-6,
remaining+/-4. No true-pose or target-landmark PnP initialization.
Use all first468 detector IDs, IDmod5!=0train and IDmod5==0held. No semantic
point is declared a rigid material ID. Plain training pixel residuals, TRF,
max15nfev, ftol/xtol/gtol1e-6, x_scale=jac, fixed central-difference step.05 in
q. No adaptive step/alternate solver/seed/frame/lighting/crop sweep. Any no-face,
nonfinite prediction, invalid render domain or resource stop records failure.
All detector calls/reported progress count, max260 rendered candidates/420s.

Controls: same target detection replay<=1e-3px, independent OpenCV projection
replay<=1e-8px, improper/negative-depth camera rejected by explicit validation;
inject.1rad evaluator rotation and require>3px true projection displacement.
After terminal inference, evaluator reports ALL5023vertex projection p95/max
against true camera, all held semantic p95, focal relative error, proper rotations,
positive depths and convergence. Require projection<=3px, heldsemantics<=3px,
focalrelative<=2%, convergence and negative controls. No selection by visibility
or residual. Even pass is TECHNICAL_CHECK_PASSED conditional capacity only.

Prepare<=60s/2GiB, fit<=420s/2GiB, evaluate<=60s/2GiB, total30minutes incl
closure. Failure stops and archives minimal evidence/source before exclusive
code/output cleanup; protect existing model/runtime, shared helpers and inputs.
No complete-head fitting or actual-video run automatically follows a pass.

## Result: REJECT

One fit terminated normally in349.422s, peak198529024bytes,170candidate
render/detect calls,15objective evaluations. Solver reached its registered
evaluation limit without convergence. Execution success is not scientific pass.
Held semantic p95=2.509015229px passed, but ALL5023 true vertex projection
p95=8.840041794px/max15.582479098px and focal relative error14.670989692%
failed. Same-image detector replay0; independent projection/invalid-camera
controls passed; injected wrong-camera p95=10.117429997px. Candidate and target
clay renders were inspected; no human inputs or medical accuracy measured.

This establishes a semantic-pass/physical-fail counterexample for this fixed
configuration. It does NOT establish an irreducible detector ambiguity or prove
all render-conditioned methods impossible: optimization was not converged.
Do not spend another seed/iteration/step sweep on this control. Redetection
avoids asserting fixed material IDs, but semantic agreement alone is still
insufficient camera evidence. Any later use needs an independently justified
physical observation, not relaxed thresholds. No real-head promotion.

Source recovery:74b87c1. Closeout archives complete small control evidence,
then removes only0382runner and generated working outputs; shared licensed
assets, renderer, runtime, tests, original human data and0207 remain unchanged.
