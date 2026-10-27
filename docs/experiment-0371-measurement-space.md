# 0371 measurement-space correction

2026-10-27 preregistration, after0369closeout6111136 and0370auditc0cd196.
Main change: objective in pixel/axial-depth measurement space with latent
3D points, instead of treating780shared-point distance equations equally.
Unchanged0368/0369inputs, first40points only. Compare with stored distance
solutions, which initialize this explicitly new correction; no retired runner
restored. Exact and stress each, same four observations, no subset or sweep.

Parameters logf,logs,b1,b2,Rodrigues3,t3,40latentXYZ. Residuals per point:
(project(X)-u)/.5,(project(RX+t)-v)/.5,(Xz-b1-d)/.005,
((RX+t)z/s-b2-e)/.005. These fixed scales are the registered synthetic
perturbation amplitudes, NOT calibrated real-model standard deviations.
No robust loss, prior or truth geometry in estimator. InitialXYZ from noisy
first-view pixels and corrected depth of stored distance solution.
f[200,5000],s[.1,10],shifts[-10,10],XYZx/y[-100,100],z[.01,100];
rotation/translation unbounded, reject nonpositive second-view depth.
TRF linear loss,2point Jacobian,x_scale=jac,max_nfev100,tolerances1e-10.
One start each; record init/final parameters,evaluations,convergence and
measurement residuals. No changing budgets after failure.

Independent evaluation: fixed true points transformed/projected through
estimated camera, same gauges.0368all40 and0369held20. Exact gates unchanged
focalrelative1e-6,alignmentp95 1e-6; stress2%focal and3px both views.
All four must pass,converge,remain away from bounds and have positive depths.
One120s/1GiB worker. No models/human/scans/training. Save compact states and
result; failure stops/cleans exclusive runner,protect prior successfulfixtures.
Even success validates only correction with these synthetic inputs and starts,
not real-video initialization,independent noise calibration or medical2mm.

## Result: conditional TECHNICAL_CHECK_PASSED

Pre-run sourced3d9a7c. One worker1.610s,103370752B conservative tree peak.
All four converge, positive and away from bounds. Exact cases each2evaluations,
focal relative error<=1e-15 and evaluated point p95<=8.68e-16sceneunits.
0368stress5evaluations:f1191.780369 (0.684969%error),projection
2.094813/2.270301px,pointp95 .00831131sceneunits,measurementRMS
.797343 to .570144. This regresses from distance-only .793906/1.153575px,
though remains within registered gates. Do not report universal improvement.
0369stress6evaluations:f891.358879 (0.960125%error),held projection
2.003207/2.070420px,pointp95 .00849891sceneunits,measurementRMS
.803412 to .581422. Prior held projection4.527163/4.579813px failed.
Both noisy cohorts now pass the same2%/3px thresholds without changing points,
noise,starts,solver settings or thresholds after execution.

Scope: evidence for this measurement-space correction initialized by stored
distance solutions,not a standalone initializer or proof of real depth quality.
Exact controls start at nearly exact solutions,so they check preservation,
not a convergence basin.0368has no heldpoints;0369has20neverfitted points.
Two constructed deterministic noise samples are not a general success rate.
Pixel/depth scales remain synthetic amplitudes,not calibrated uncertainty.
No medical2mm result,mesh,patient reconstruction or visual acceptance.

Retain conditional strengths: distance-based physical initialization and joint
measurement correction. Next blocking technical question is actual depth
semantics,correspondence reliability and error scales,not more synthetic seed
selection. Inspect a free-commercial depth source under a fixed provenance/
capacity protocol before any patient run; do not restore retired integrations.
Shared0332backend is three-view,translation-norm gauge and pixel-only; using it
unchanged would silently discard axial-depth scale/shift constraints. Therefore
this small two-view checker reuses installed libraries and bounded worker,not
the incompatible camera parameterization. No production default changed.

Private evidence assets/private/measurement-space-0371/result.json SHA256
52802d140b7a958620c2225a93cb656977df909a17ac056a7c3671d996b53a77;
states.npz SHA256a81105aacad7c2b6e188726da0133157763e523a7bb3ab32372c00998e706c6d.
Original inputs and historical results were read-only. No new dependency,
network access,weights,training or human data access. Unrelated0207 untouched.
Verification:167shared tests pass in9.783s; experiment gates above are separate
from this regression-suite result.
