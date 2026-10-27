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
