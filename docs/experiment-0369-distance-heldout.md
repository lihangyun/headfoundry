# 0369 independent held-out capacity

2026-10-27 preregistration. No change to0368fit, thresholds or initialization.
Question: does the conditional distance mechanism predict points never fitted
on a different fixed geometry/camera, rather than only its first fixture?
RNG369,60points x/y uniform[-.6,.6],z uniform[2.5,3.5];
f900,Rodrigues(-.15,.18,.06),translation(-.12,.09,.16).
Axial inputs d=z1-.3,e=z2/1.2+.2. First40fit,last20evaluation only.
Exact and one stress: .5px*sin(arange120 reshaped60x2), view2offset2;
depth .005*sin(arange60+4/6). No sweeping or retrying.
Exact: focal relative<=1e-6,held transformed-point p95<=1e-6sceneunit;
stress: focal relative<=.02,both held true-point projection p95<=3px.
Require0368admission and positive held predicted depth. Report rotation,
translations,shifts,training and held errors; do not confuse scene units with
medical millimetres. This is not a proof for all geometries or real depth maps.
One60s/1GiB worker, source committed before execution, no assets installed,
no human inputs. Failure stops this transfer test; retain0368conditional
success,archive0369result and retire only this exclusive runner if failed.
Success advances toward real-component input assessment, not head fitting.

## Result: REJECT transfer admission

Pre-run source92e8ab5. One worker1.406s,98447360B conservative process-tree
peak,exit0. Exact8evaluations,f900.000000000001,held projection
2.07e-13/2.42e-13px,pointp95 8.92e-16sceneunits. Stress7evaluations,
f880.471429 (2.169841%error),held projection4.527163/4.579813px;
training projection5.178589/5.970280px,pointp95 .01804128sceneunits.
Optimizer converged without bounds and positive held depths, but actual2%/3px
gates fail. Numeric admission is not physical admission. No parameter retry.

Established: the exact four-parameter model fits this noiseless geometry;
enforcing algebraic coupling alone is insufficient for this deterministic
perturbation. Failure also occurs on training true-point projection, so this
is not evidence of a holdout-only overfitting problem. Residual RMS .097878
versus0368's .094365 yet substantially different projection error illustrates
that the raw objective is not a calibrated accuracy certificate. The evidence
does not isolate whether sensitivity, the squared-distance noise objective,
or other mechanisms dominate. Do not claim a proven root cause beyond these
observations, nor reject all depth-assisted methods or pretrained networks.

Keep0368's conditional fixture, not a production initializer. No model download
or patient reconstruction. Next justified action is a read-only sensitivity/
residual audit of the frozen solution, not another solver/seed/noise sweep.
Real input assessment remains deferred until a defensible admission method.

Compact evidence retained at assets/private/distance-heldout-0369: original
60point input NPZ,result JSON,worker receipt/log. Input SHA256
f1dfa1959688ea999822d5542067c4a56df5993c000750c5193d09ca3d292862;
result SHA256d2f89e60258a8e8651458b5d62f86ff2c32ef9a4e7fd0a43a8dce02a50891bb6.
Only exclusive checker retired (2508Git-source bytes); no live callers or0369
bytecode found. Source recoverable from92e8ab5. No weights/environments or
human assets were created,read or deleted; no shared default changed.
After cleanup167shared tests passed in8.703s. Unrelated0207 remains untouched.
