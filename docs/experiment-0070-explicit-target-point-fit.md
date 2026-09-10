# Experiment 0070: explicit target-point fitting contract

Status: `TECHNICAL_CHECK_PASSED` for deterministic implementation checks only.
Real-photo geometry and complete product quality remain `UNVERIFIED`.

Correct the next-step premise from 0069: existing private fits already use
soft-L1 and a 5px scale. Merely changing that weight does not resolve shape,
camera or correspondence errors. Add a reusable numerical implementation in
`headfoundry.target_fit.fit_target_points` instead of claiming a new visual
solution from weaker constraints.

The function fits nonnegative bounded graphical-target weights at supplied
fixed-camera surface samples. Inputs explicitly contain point identities,
matching target displacements, per-view observation eligibility and per-point
pixel scales. Callers still verify asset rights/hashes and surface visibility;
the numerical function does not infer either from a detector result. Masked
observations may be unavailable without influencing the solve. Active inputs
must be finite with positive scales. Degenerate perspective matrices and
initial/final points behind cameras are rejected. All results report
`UNVERIFIED`, never identity acceptance.

The point-only function deliberately does not perform contour correspondence,
asset installation, camera fitting, mesh collision handling, sign-branch
selection or rendering. Existing numerical consumers can pass barycentric
surface samples and their matching target displacements. No dependency beyond
the existing optional SciPy geometry extra is added. Start strictly inside
the coefficient bounds to avoid premature termination at a nudged zero bound.

Three executable tests cover known coefficient recovery, explicit mask
exclusion (including NaN and extreme values in excluded observations), invalid
uncertainty and support rejection, camera degeneracy/cheirality, active weight
bounds, and the influence of different supplied observation scales on
conflicting views. Changing uncertainty demonstrably changes fitting influence;
it does not change the reported raw pixel residual or any acceptance gate.
All 75 tests pass.

No new real-photo candidate is produced or promoted by this engineering step.
The new function has not been demonstrated to improve subject likeness and
must not be advertised as calibrated uncertainty estimation. Its purpose is
to make the repeatedly used observation/mask/weight behavior reproducible and
testable in the public project, while private identity data remain private.
Next integrate the point-only contract into a controlled real-data comparison
with explicit silhouette checks; do not replace the combined objective merely
because a simpler point-only score is easier to reduce.
