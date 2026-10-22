# Audit0305:frozen bundle stationarity,not another patient fit

Registered2026-10-22 after0304closeout332c0bb,before diagnostic results. Previous
goal turn progressed through actual camera scores and verified cleanup. Goal
active/account allowed. No model/private service/training/upload/new dependency.

Evidence:0304reaches the unchanged300evaluation cap with optimizer_successFalse,
so its rejected result is not a converged lower bound. Main diagnostic variable:
numerical stationarity/conditioning of the frozen training-only objective. No
new camera/point optimization,held-data selection or alternative patient result.
Do not rescue0304's failed gates/one5-IDvalidation split or relabel it passed.

Read only frozen K/poses/points/train/metadata in0304's verified compact archive
b4098c99c478dc223c3d489dddb662dce61f4003712585fbf111355d07385a52.
Do not read held point fields,source images,model Z,medical/case002 geometry.
Reconstruct exact original parameterization with fixed anchor/unit baseline;
forward replay must<=1e-8px. Compute central finite-difference training Jacobian
at fixed relative1e-5step plus independent half-step consistency witness,not
physical precision search. Require relative Jacobian difference<=1e-5. Report
soft_l1objective/gradient,current-column-normalized singular spectrum/rank and
linear normal-equation residuals for fixed default LSMR vs dense SVD solutions.
Do NOT apply either linear step to a patient camera/point or score held errors.

Use the original procedural control solution as an independent near-optimum
comparison. It has known3Dtruth from0304,not an accepted natural-image result.
The linear comparison is an undamped local diagnostic;SciPy's actual trust
region/damping/history-dependent column scales differ,so a difference does not
by itself prove the actual optimizer's root cause or authorize a real rerun.
No bound,iteration count,mask or production/shared camera source change.

One read-only audit<=60s,working arrays<=128MiB;whole600s from execution for
report/tests/local commit. Fail on replay/Jacobian mismatch,do not fit around it.
Keep concise reports/hashes and generic verified numerical checks;remove failed
exclusive application if necessary. Original archives/protected inputs unchanged.
Full reconstruction/camera acceptance/medical2mm/visual target remains active.

## Actual result:TECHNICAL_CHECK_PASSED diagnostic,no physical promotion

Source928e4a3;one audit completes.328s,no patient refit/held-field read/step applied.
Exact forward replay maxima9.095e-13px(control)/7.958e-13px(real);half-step
Jacobian relative differences6.191e-11/4.942e-11. Independent procedural positive
and wrong-pose negative regression passes without modifying input arrays.

Control normalized gradient infinity norm5.141e-11. Real frozen training cost
11.181554 and normalized gradient.000221216(unscaled.560260) are not exactly
stationary. Its normalized Jacobian rank102/102,smallest singular.00269030.
LSMR local normal residual2.7464e-5vsSVD9.2027e-15,but residual norms differ only
5.257780187vs5.257759494(~3.94ppm). This does NOT identify a large linear-solver
failure or prove that another real solve/extra iterations would pass held data.
Actual damped/history-dependent trust-region behavior was not reconstructed.
Do not use the tiny numerical difference as a pretext for an iteration/solver
knob sweep.0304remainsREJECT,all physical/head/medical/visual gatesUNVERIFIED.

Working arrays6.06MBcontrol/.414MBreal,within cap. Raw report privately retained
atassets/private/bundle-stationarity-0305/report.json. Generic no-fit auditor and
one procedural positive/negative test stay as successful mathematical checks;
the one-off private-archive wrapper is retired(source928e4a3). No framework/model
or failed geometry was added.143shared tests pass in6.460s. Production/defaults,
original evidence and unrelated0207unchanged. Next work must improve independently
justified actual observations,not rerun the same28semantic points.
