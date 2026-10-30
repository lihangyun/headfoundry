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

## Actual evidence

One fixed-state worker7.656s/227536896B, controls pass. All1041RGB hashes and
three exactgrayPNG identities match; residual replaymax0, cost0.1355238746664193.
No held scoring or parameter update, all original training rows retained.

22observationconstraints active at the predeclared tolerance, plus scalarupper
columns13and15 (the two target brightness biases). Normalizednormalmatrix44x24,
rank24. Both brightness biases are at+.05; this contradicts any assumption
that0390had no active exposureboundary (0387's earlier interiorbound result
does not transfer to0390). It does not prove relaxing that bound improves truth.

| Normalized difference step | Gradientnorm | NNLS stationarity residualnorm | Ratio |
| --- | ---: | ---: | ---: |
| 1e-6 | 0.513256169 | 0.018255379 | 0.035567774 |
| 5e-7 | 0.516849284 | 0.021314172 | 0.041238660 |

Relative gradient disagreement1.333914%. The two-step results are not identical
enough to assert precise KKTstationarity from this audit; neither independently
proves physical accuracy or global uniqueness. Finite-difference sensitivity,
bilinear cell boundaries and constraint activity remain relevant numerical
questions. Nonzero residual under both tested estimates is evidence against
simply declaring a solved optimum; no unregistered convergence threshold is
introduced and0390nonconvergence/REJECT remains unchanged.

Action: do not additerations or expandexposurebounds blindly. An independent
piecewise bilinear image-gradient calculation at the frozen state could check
whether the discrepancy comes from interpolation knots vs derivative error;
it would be a derivative audit, not permission to rerun0390. More accurate
derivatives still would not establish the correct focal or medical geometry.
No new head/camera accepted, no surface millimeter improvement measured.

## Closeout

Source/result recovery commit: b0b413e. Private evidence:
`assets/private/closed-experiments/0391-stationarity/evidence.zip`, 6285 bytes,
4 members, SHA256 `bbea7583e92a2faf7f23cfd93459cbcd6e07f24ed794bdb52e8d64579f999a70`.
CRC, every member hash, all 11 protected identities and the0390archive checked
before and after cleanup. Removed exactly3loose files/7127bytes and the exclusive
runner `tools/stationarity_0391.py` (7593bytes); source is recoverable from Git
and the archive. No weights/environments created or removed. No live worker or
remaining code caller. All170shared tests pass in8.786s. Unrelated0207preserved.
This closes the diagnostic only;0390REJECT and head/medicalUNVERIFIED unchanged.
