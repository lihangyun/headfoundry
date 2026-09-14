# Experiment 0123: coupled actual surface and oblique pose

## Controlled change

Replace disconnected free-point pose fitting with a coupled actual-surface
trial on experiment 0117's closed-mouth mesh. Use three compact frontal-ray
depth fields centered on nose, mouth and chin, plus two oblique rotations.
Field radii in frontal pixels are 110x100, 125x65 and 150x90. Compact quartic
weights are restricted to source z < -0.6; that depth eligibility boundary is
not a proven smooth anatomical segmentation. Coefficient bounds are +/-0.03
template units; rotation component bounds +/-0.02 rad. Keep front/profile
cameras, intrinsics, topology and 14,417 vertices outside field support fixed.

Ten actual frontal ray-lifted barycentric supports bind four eye corners, two
nose and four mouth detector observations. Do not use chin ID 152 as a fixed
material point. Corrected bilateral profile rows constrain apparent contours.
All image residuals use 3 px scale, with depth prior .03 and rotation prior .02.
Eye/profile regressions and source-relative area ratio below 0.5 prevent
promotion. These guards are evaluated after optimization, not claimed as hard
constraints on the least-squares proposal. No failed candidate becomes default.

## Executed candidate

The solve converges with no active bounds. Depth coefficients are
[-0.0049729,0.0016335,0.0071439]. Maximum vertex movement is 0.0072293 units.

| Diagnostic | Before left/right px | After left/right px |
| --- | --- | --- |
| Four-eye mean | 5.4719 / 4.8479 | 6.2191 / 4.2822 |
| Corrected profile mean | 4.6814 / 5.9367 | 4.4956 / 5.9768 |

Several nasal/mouth support errors decrease, but the left eye and right profile
regress. Minimum triangle area ratio is 0.21508, with four source-relative
normal-dot reversals. Those reversals are diagnostic rotations, not formal
topological inversion proof. The area guard alone is already failed.
Candidate promotion is `REJECT`; no source mesh or cameras are replaced.

Unlike 0121's free-point camera, the actual-surface fit does not create a
20-plus-pixel eye displacement. That is a useful coupling distinction, not
identity acceptance: the trial still violates protected evidence and surface
safety. Do not increase deformation limits to chase its lower aggregate cost.

Private `shared-surface-pose-v1` preserves before/after OBJ, candidate cameras,
per-point errors, parameter bounds and actual five-view comparisons. Source
mesh SHA-256 is
`fbfb86271c5640f2ddf44b7d6f8c74bd21e4e3611d293d462768c61034688945`.
All observations remain provisional and training-derived. The independent
camera gate, local-only consent and clean-room boundary remain unchanged.

Actual five-view renders completed and were inspected. Changes are small and
the generic face/flat lower lip remain; there is no visual basis for promotion.
All 98 public tests and `git diff --check` pass. Public code is unchanged.
