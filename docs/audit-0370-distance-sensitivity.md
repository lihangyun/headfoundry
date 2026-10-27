# 0370 frozen distance sensitivity audit

2026-10-27 preregistration. Diagnostic only; no optimizer, model or patient.
Read original0367/0369inputs and stored0368/0369solutions. First40points,
unchanged fixed stress. Evaluate analytic four-parameter Jacobian at truth;
check each column against central differences1e-6, normalized maxerror<=1e-5.
Compute local response -lstsq(J,residual) for fixed pixel-only,depth-only and
combined perturbations. These are attribution diagnostics, not candidate fits;
do not promote predicted parameters or use their results for tuning.
Report normalized singular values, focal column after nuisance projection,
predicted versus saved actual logf shift and nonlinear remainder. Exactzero
and injected .001*J[:,0] controls must produce0 and-.001 logf response.
One60s/1GiB worker. This distinguishes local error propagation from gross
solver failure without claiming a unique cause or independent noise statistics.
