# Experiment 0132: subject-derived central depth basis

## Question

Can subject-specific local shape freedom improve the visible bilateral
nose/lip profile where the generic CC0 basis in experiment 0131 remained
generic, without changing cameras or sacrificing the established outer-shape,
eye and mesh safeguards?

The source is the unpromoted experiment-0131 candidate. Cameras, topology,
observations and all outer-shape coefficients are frozen. The single primary
variable is a six-direction central-face basis: one compact smooth field around
each frontal nose/lip support (MediaPipe IDs 4, 2, 0, 13, 14 and 17). Each field
moves vertices only along their own frontal camera rays, so frontal projection
is preserved while oblique and profile depth can change. These are deterministic
subject-derived fields, not a trained identity model or generic asset library.

The constrained solve uses the same provisional frontal/oblique point evidence
and corrected bilateral profile curves. It requires all four experiment-0131
outline means, both profile means and all eight oblique eye-anchor errors to be
no worse. A 201-step exact line scan then requires maximum displacement at most
0.03 template units, minimum relative triangle area at least 0.5 and zero
relative normal reversals. The five photos and all derived geometry remain
local under the existing consent.

## Results

SLSQP terminated successfully after 18 iterations. Exact reevaluation selects
the full proposed step. The six coefficients are `-0.006414`, `0.004968`,
`-0.016116`, `0.015356`, `0.015796` and `-0.030000`; the final direction reaches
its lower bound and is therefore not evidence that this compact basis is
sufficient.

| Diagnostic | Experiment 0131 | Central-depth candidate |
| --- | ---: | ---: |
| Corrected left profile mean | 4.342488 px | 3.623644 px |
| Corrected right profile mean | 5.776622 px | 4.923311 px |
| Left-oblique central-point mean | 10.069627 px | 8.895539 px |
| Right-oblique central-point mean | 6.793462 px | 5.084773 px |
| Maximum displacement | 0 | 0.029824 template units |
| Minimum relative triangle area | 1.000000 | 0.796018 |
| Relative normal reversals | 0 | 0 |

The four outer-outline means and all eight protected eye errors are unchanged
to numerical precision. The frontal central-point mean remains effectively
zero (`0.000066` px) because movement follows the original frontal rays. The
fit objective decreases from 173.211020 to 139.716205. All these measurements
participate in fitting, protection or step selection; none is held-out camera
or identity validation.

## Visual decision

The actual five-view comparison, silhouette overlay and enlarged bilateral
profile sheet were inspected. Both side views show a visible, directionally
consistent change around the nose tip, lips and chin, and the candidate contour
moves closer to the photographed boundary used by the fit. This is a larger
and more relevant side-profile change than the generic macro controls alone.

The overall identity is still generic. The lip surface remains angular and the
bounded final coefficient indicates local stretching pressure rather than a
resolved neutral closed-lip anatomy. Frontal appearance barely changes by
construction, and the same photos and curves used for fitting provide the
visual comparison. No independent camera, texture, expression or likeness gate
has passed.

The deterministic basis, constrained solve and mesh checks are
`TECHNICAL_CHECK_PASSED`. The candidate is `PARTIAL_SUCCESS` for protected,
human-visible bilateral profile progress and `REJECT` for default promotion.
Full identity and KeenTools-level quality remain `UNVERIFIED`.

The next discriminating gate is an anatomical neutral-lip surface with bounded
smoothness/contact freedom, evaluated against an evidence split rather than
another larger point-fit. It must retain the current bilateral contour gain,
remove the sharp generic lip form, and preserve eye, outer-outline, profile and
mesh safeguards. Do not increase the saturated coefficient or interpret the
fitted photo contours as independent validation.
