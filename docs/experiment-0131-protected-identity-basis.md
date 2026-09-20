# Experiment 0131: protected broad identity basis

## Question

Can a broader set of audited CC0 head and central-face directions produce a
visible five-view identity-shape improvement over experiment 0128 without
trading away the protected eye anchors, bilateral profile evidence or mesh
safety?

The experiment keeps the experiment-0128 cameras, observations and closed-mouth
mesh construction fixed. Its single primary variable is a nine-direction shape
basis: four whole-head presets plus eye spacing, bilateral cheek volume, chin
height, chin prognathism and chin width. Every direction is transferred from
the exact locked MakeHuman source IDs through the same one-step Catmull-Clark
construction and harmonic closed-patch extension used by the current mesh.
The assets are pinned at revision
`a8bc2d54ff0ac92e78ff71431b1023eda42bf482`, individually hash checked and
licensed `CC0-1.0`.

A local linearized fit proposes coefficients from the four five-view outline
groups, the two corrected profile groups and ten provisional point targets. A
constrained solve then requires every one of the eight oblique eye-anchor errors
to be no worse than experiment 0128. The exact nonlinear evaluator selects one
scale on a fixed 0.05 grid while also requiring maximum displacement at most
0.05 template units, minimum relative triangle area at least 0.5 and zero
relative normal reversals. This is fitting and protection evidence, not held-out
identity validation.

## Results

The eye-protected solve terminated successfully after 11 iterations. It retained
four material directions: rectangular head `0.129199`, cheek-volume increase
`0.221498`, chin-height increase `0.029021`, chin-prognathism decrease `0.035083`
and chin-width decrease `0.201013`; the remaining coefficients were zero or
numerically negligible. Exact reevaluation selected scale `0.95`.

| Diagnostic | Experiment 0128 | Protected candidate |
| --- | ---: | ---: |
| Outline mean 1 | 7.077767 px | 6.424589 px |
| Outline mean 2 | 10.088738 px | 8.080233 px |
| Outline mean 3 | 4.378266 px | 2.653957 px |
| Outline mean 4 | 2.998037 px | 1.233153 px |
| Corrected left profile mean | 4.505224 px | 4.342488 px |
| Corrected right profile mean | 6.139392 px | 5.776622 px |
| Maximum displacement | 0 | 0.021726 template units |
| Minimum relative triangle area | 1.000000 | 0.727712 |
| Relative normal reversals | 0 | 0 |

All eight protected eye-anchor errors are unchanged to numerical precision
(the largest absolute change is below `1e-9` px). This is a stronger feasible
outer-shape result than the unconstrained linear fit, which slightly regressed
two individual eye anchors.

The provisional non-eye point evidence does not improve: the front, left
oblique and right oblique point means move from approximately `0.000000`,
`8.014362` and `5.785299` px to `0.066395`, `8.076252` and `5.830737` px. These
small regressions are reported rather than hidden. The point identities outside
the protected eye anchors remain provisional, so this experiment does not force
them into additional hard constraints or reinterpret them as anatomical truth.

## Visual decision

The five-view photo/baseline/candidate sheet and a photo-space silhouette
overlay were inspected. The candidate visibly changes the forehead, cheeks and
lower-face outline, and the fitted jaw/side contours move in the expected
direction. Much of the profile contour still overlaps the baseline, however,
and the nose, eyelids and lips remain recognizably generic. Hair also makes the
upper scalp silhouette an unreliable bare-cranium target. The overlay uses the
same observations that drove selection; it is not independent validation.

Asset locking, exact transfer, constrained optimization and mesh-safety checks
are `TECHNICAL_CHECK_PASSED`. The candidate is `PARTIAL_SUCCESS` as evidence
that a broader protected basis can improve visible outer proportions without
damaging the guarded eye/profile/mesh checks. It is `REJECT` for default
promotion and does not change camera, identity, texture or product acceptance.
KeenTools-level quality remains `UNVERIFIED`.

Do not repeat another generic macro-target expansion. The next gate needs
subject-specific central facial structure—especially the nose, eyelids and
closed-lip form—supported across views. Any new candidate must preserve the
current eye, bilateral profile and mesh safeguards and must be judged in actual
photo comparisons, not accepted from fitting cost alone.
