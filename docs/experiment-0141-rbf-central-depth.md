# Experiment 0141: optimized smooth central-depth basis

Status: deterministic replay `TECHNICAL_CHECK_PASSED`; candidate and visual
promotion `REJECT`. Camera and identity acceptance remain `UNVERIFIED`.

The target is visible subject-specific central-face relief without changing the
experiment-0132 cameras or outer head. The hypothesis is that optimizing a
smooth basis directly, rather than smoothing a per-vertex solution after the
fact, can improve bilateral profile/material evidence while preserving all
prior groups. The counter-hypothesis is that the fixed-camera evidence is
incompatible within a smooth front-ray depth family. The sole experimental
variable is a 30-dimensional grid of Gaussian central-face depth fields, tapered
to zero through the eye region.

Finite differences build the local measurement Jacobian. A bounded,
regularized constrained solve protects four outer-outline aggregates, both
profile means, four individual eye errors, both oblique-central means, both
reviewed material means, 0.02 maximum movement, 0.5 minimum relative triangle
area and zero normal reversals. The optimizer reaches its 300-iteration limit;
that failure is retained rather than relabelled as convergence. A deterministic
101-step replay of its returned direction selects alpha zero.

The first nonzero step, alpha 0.01, is already worse overall: objective
216.873511 becomes 216.875866. Profiles improve slightly from
3.623644/4.923310 px to 3.623537/4.922359 px, but one oblique outline worsens
from 2.653957 px to 2.657867 px and the right reviewed-material mean worsens
from 10.240803 px to 10.240903 px. The mesh itself remains well behaved at that
step (0.000392 maximum movement, 0.997407 minimum area ratio, no normal
reversals), so the rejection is evidential rather than a topology accident.

The selected mesh is bit-for-bit the experiment-0132 source and the inspected
five-view comparison has no candidate change. This falsifies the tested smooth
front-ray depth family under the current bilateral protections; do not loosen
the guards or add more centers to force a nonzero result. The next shape route
must supply a genuinely learned or parametric identity prior and be evaluated
with evidence independent of the fitting targets.

Private output `rbf-central-depth-v1` retains source locks, coefficients, solver
termination, all 101 trials and the visual comparison. Authorized photographs
and identity-derived artifacts remain local and ignored.

