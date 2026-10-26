# 0365 frozen-evidence local camera sensitivity

2026-10-26. Diagnostic only under updated task contract; no model restoration,
patient access, nonlinear refit, output promotion or old threshold change.
Compare saved0332initial geometric state and archived0363state using their own
unchanged admitted/train populations. Different populations mean no controlled
model ranking. Known scene truth is evaluator-only, never a reconstruction seed.

At true cameras/XYZ in the same identity-anchor/unit-baseline gauge, form the
existing analytic residual Jacobian. Check every column against centered finite
differences step1e-6; max abs difference/(1+abs numeric)<=1e-5. Repeat derivative
check at each saved fitted state. No alternative step/tolerance on failure.
Project log-focal derivative orthogonally away from all nuisance pose/XYZ columns
(column-normalized NumPy lstsq,rcond1e-12). Report remaining focal information,
linear predicted logf error from actual observation residual, recorded logf error,
and per-observation signed contributions. This is local unweighted sensitivity,
not the nonlinear soft-L1 solver, causal uniqueness or a new fitted camera.
Exact-zero residual must predict zero; injected0.001logf derivative must recover
0.001 within1e-8. No source-ID pruning, weights, confidence or frame changes.

One bounded worker60s/2GiB, existing NumPy/OpenCV/shared helpers. Save complete
small report and contribution arrays. Stop on identity/finite/derivative/control
failure. If checks pass, distinguish implementation agreement from geometric
accuracy; no automatic move to head fitting or archived model replay.
