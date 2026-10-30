# 0391: fixed terminal-state stationarity audit

2026-10-30.0390closed8c79263; no retry or new camera/head solution. Budget15min.
Inspect ONLY archived0390terminalstate. Independently decode/check the same
1041videoRGB hashes and original consent/source, keep only240/300/630grayarrays
in memory. No saved frame copies, scan/case002, training or model invocation.

Question: is nonconvergence compatible with an approximately stationary feasible
point, or is there a measurable unresolved first-order residual? The150iteration
message alone cannot distinguish that. No prospective assumption about cause.

Use exactly saved loss/constraints/bounds at finalvalues. Normalize parameters
by half their original bound widths. Evaluate central numerical loss derivatives
at fixed normalized steps1e-6 and5e-7 as an agreement check, NOT an optimizer or
parameter sweep. Compare saved residual/loss replay first. Derivatives are local;
bilinear interpolation can be nondifferentiable at image-cell boundaries.
If disagreement is material, report it rather than declaringstationarity.

Active observation constraints: savedslack<=1e-6px_squared, matching the original
numerical feasibility allowance. Active scalarbounds: normalizeddistance<=1e-8.
With analytic normalizedconstraintderivatives, use one NNLS multiplier solve
for g=A*lambda,lambda>=0. Report residualnorm/gradientnorm, activecount/rank,
both gradient steps and feasibility separately. NNLS changes multipliers only,
not cameras/depth/observations; no held coordinates or scores enter this audit.

Controls: a known1Dactiveconstraint minimum has nonnegative multiplier and zero
stationarity residual; reversing the gradient must not be certifiedstationary.
Do not invent a physical accuracy gate fromKKTresidual. A small residual is only
local first-order numerical evidence, not convergence proof/globaloptimality or
correctcamera. A large residual does not prove insufficient iterations or give
permission to rerun. Preserve compact report/hash/source and retire diagnostic
runner after verification. All0390REJECT/medicalUNVERIFIED remain unchanged.
