# Experiment 0104: extended nose/lip basis with bounded fitting

Status: asset verification `TECHNICAL_CHECK_PASSED`; retained numerical report
`UNVERIFIED`; candidate `REJECT` for visual promotion after actual five-view and
enlarged mouth inspection. Camera and full-head acceptance remain failed or
unverified as previously recorded.

## Target and scope

Test whether a richer local authored basis can make the nose and closed lips
visibly more faithful in frontal, oblique and bilateral profile views. The
source is the unaccepted experiment-0079 coupled head and cameras. Its mesh
SHA-256 is `b05e9e80e37d10ba0a2c7476ab3f631c6a3dd27bc097d5beb00ed45e0aab5e31`
and its camera archive SHA-256 is
`98a05bf9c94685ac749e958b5ec516546916525baf6f307415996072d5ea7612`.
Cameras, topology, annotations and rendering stay fixed. The prediction is a
visible anatomical improvement without worsening either full-profile mean,
losing original visible point support, reversing triangles or excessive motion.
Small fitting-error reductions alone do not satisfy that prediction.

`examples/makehuman-nasolabial-extended-lock.json` pins 44 graphical target files
at MakeHuman revision `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`. All 44 local
SHA-256 values and explicit CC0 headers were checked. These add 22 signed pairs
to the existing ten, for 32 nose/lip controls. Their source-vertex displacements
are parsed independently and mapped through the existing head/neck source IDs;
new cut vertices receive no guessed target displacement. No upstream application
code, new trained identity model or noncommercial checkpoint is integrated.

## Solver and changed protection

Each signed control selects one of its two authored displacement targets. The
objective combines bilateral local profile residuals, source-visible frontal
and oblique detector-derived point residuals, and coefficient regularization.
The point and profile residuals are scaled by 5 px. Occlusion screening does not
establish anatomical correspondence correctness.

The low-rank trial takes central finite differences at zero with step `1e-4`,
then retains the top eight right-singular directions of the **full residual
Jacobian**, including coefficient regularization and, when enabled, profile
protection. Despite the private report's shorthand "observation-Jacobian",
these are not derived exclusively from image observations or learned identity
statistics. Three deterministic starts use latent values 0, +0.05 and -0.05,
bounded to [-0.25, 0.25], with soft-L1 loss and at most 120 evaluations per start.
This local reduction does not exhaust the piecewise signed basis.

The first retained low-rank report uses the previous per-row protection: add a
penalty for any profile row worsening, then require every original row to be no
worse during step selection. All three starts converge, but only a zero step
survives. The mesh is unchanged.

The bounded follow-up removes that per-row penalty and recomputes the low-rank
directions. It selects among step fractions 1, 0.75, 0.5, 0.25, 0.125, 0.0625
and 0 using these source-relative guards:

- Maximum vertex displacement no greater than 0.03 template units.
- Minimum triangle-area ratio at least 0.5, with no reversed triangles.
- Both full-profile mean absolute errors no worse than their source means.
- No loss of the original screened visible point supports.

This changes protection and the resulting local basis as well as allowing an
extended shape space. It is an exploratory follow-up, not a controlled estimate
of the effect of adding 22 controls. Aggregate profile protection permits
individual rows to worsen and is weaker than the previous per-row rule.

## Retained result

The bounded run's three starts converge in 29, 26 and 29 evaluations, with
pre-retention solver costs 27.025836, 27.017246 and 27.009891. The selected
solution retains a 0.25 step. Costs are optimizer diagnostics before that step
reduction, not final pixel errors or acceptance scores.

| Diagnostic, px | Source | Retained candidate |
| --- | ---: | ---: |
| Left local profile MAE | 3.461033 | 3.453275 |
| Right local profile MAE | 7.069626 | 6.996785 |
| Left full-profile MAE | 3.589129 | 3.583253 |
| Right full-profile MAE | 7.249347 | 7.189245 |
| Frontal point mean | 5.094351 | 4.544664 |
| Left-oblique point mean | 7.281464 | 6.852077 |
| Right-oblique point mean | 5.991608 | 5.475872 |

All listed observations participate in fitting or step selection; **none is
held-out validation**. These numbers neither replace the frozen camera check
nor establish calibration or anatomical accuracy. Maximum movement is 0.004465
template units, minimum area ratio is 0.939636, triangle reversals are zero and
original visible-support losses are zero. This is not a full collision audit.

The actual five-view comparison shows only a small change and retains a generic
face. Enlarged frontal and bilateral mouth renders still have an open, angular
lip configuration unlike the photographed closed seam. The candidate is
therefore rejected for visual promotion. The private JSON remains `UNVERIFIED`
because its automatic status only checks selected numerical/mesh conditions;
this document records the subsequent visual decision explicitly.

The private output directory is `extended-nasolabial-lowrank-bounded-v1`.
Its `report.json` SHA-256 is
`d5685d5293d5b67101cf85817ba77b617c47e8ef2f8d16b09731dedeb8ece524`;
the inspected images are `joint-baseline-comparison.png` and
`mouth-comparison.png`. The preceding zero-step report is in
`extended-nasolabial-lowrank-v1`. No retained direct-32-control report exists,
so this archive does not assign independently verified numerical results to
that preliminary attempt. All photos, meshes, coordinates and renders stay
under ignored `assets/private`; only source locks and aggregate findings enter Git.

## Decision and next discriminating test

Do not promote this mesh or repeat expansion of the same MakeHuman local target
sweep as the immediate route to likeness. The tested representation and fitting
setup have not produced the required visible improvement; this does not prove
that all parametric reconstruction or these five photographs are insufficient.

Next run an independent sparse multiview feasibility check using reviewed local
tools: isolate the rotating head from the static background, inspect matched
support, recovered camera geometry and triangulated facial coverage, and retain
independent validation before considering dense surface recovery. Failure of one
such pipeline would identify a method/input interaction to diagnose, not by
itself prove that the photographs contain insufficient recoverable information.
