# 0368 physical four-parameter distance fit

Preregistered 2026-10-26, following completed0367cleanup1b0ef9a.
Single change: optimize log(f),log(s),b1,b2 directly instead of seven
independent lifted terms. Same frozen0367inputs and deterministic stress;
all780pairs, no pruning, multistart or noise/threshold sweep. No models,
patient inputs, training or scan access. This tests constraint enforcement,
not actual head quality or a depth network.

Residual: squared pairwise distances of corrected clouds X and Y, divided
by fixed median squared raw-depth difference (floor1e-6). TRF linear loss,
initial f1000,s1,b1=b2=0; bounds f[200,5000],s[.1,10],
b1[-min(d)+.01,10],b2[-min(e)+.01,10]. max_nfev200,
ftol=xtol=gtol1e-12, x_scale='jac'. One start per exact/stress control.
Reject depth-constant input (range<=1e-12), optimizer nonconvergence,
bound contact within1e-6 or nonpositive depths. Physical square/product
relations hold by construction; this is not independent validation.

Exact gate: relative focal<=1e-6, rotation<=1e-6rad, true point alignment
p95<=1e-6sceneunits. Fixed stress gate: relative focal<=.02 and true-point
projection p95<=3px in both views. Proper SVD alignment, same truth-only
evaluation as0367. Plane negative must reject. One60s/1GiB worker. If any
gate fails, stop and close out exclusive runner; retain compact evidence.
Even success only admits this synthetic mechanism for further validation.
