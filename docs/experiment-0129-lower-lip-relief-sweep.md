# Experiment 0129: lower-lip relief sweep

## Question

Can one compact lower-lip depth field create a human-visible improvement on the
experiment-0128 mesh without giving back its eye, bilateral-profile or mesh
safety gains?

Keep the experiment-0128 mesh and all five cameras fixed. Define one quartic
elliptical field in frontal image space, centred at `(635, 825)` px with radii
`(115, 48)` px, and move only its supported vertices along their frontal camera
rays. Sweep nine signed amplitudes from -0.016 to +0.016 template units. The
amplitude is the only experimental variable. All eight oblique eye anchors,
both corrected profile means, triangle area and relative normal orientation
remain protected diagnostics.

## Result

Only the zero step preserves every experiment-0128 diagnostic without any
regression. Negative relief improves the left profile but worsens the right;
positive relief does the reverse. The visually reviewed -0.008 trial is the
best useful counterexample because it remains better than the pre-0128 source
on both profiles while producing a visible lower-lip change:

| Diagnostic | Experiment 0128 | Amplitude -0.008 | Pre-0128 source |
| --- | ---: | ---: | ---: |
| Corrected left profile mean | 4.505224 px | 4.441216 px | 4.574355 px |
| Corrected right profile mean | 6.139392 px | 6.165001 px | 6.176893 px |
| Minimum relative triangle area | 1.000000 | 0.951450 | n/a |
| Relative normal reversals | 0 | 0 | n/a |

All eight eye errors are numerically unchanged because the field has disjoint
support. Maximum movement is 0.008044 template units and 26,471 vertices remain
exactly unchanged.

## Visual decision

The local five-view comparison and the full signed sweep were inspected. The
field can make the lower lip project farther in profile, but it behaves like a
generic bump: it does not recover the subject's lip contour, mouth corners,
facial proportions or recognizable identity. The left/right metric tradeoff
also shows that a single symmetric frontal-ray scalar cannot satisfy the
current bilateral evidence.

The experiment is `TECHNICAL_CHECK_PASSED` as a deterministic one-variable
sensitivity test and `REJECT` for geometry promotion. No baseline, camera,
texture or acceptance status changes. Private outputs retain the nine OBJ
trials, exact report, mouth sweep and photo/baseline/candidate comparison under
`lower-lip-relief-sweep-v1`; no identity-derived artifact enters Git.

The next shape experiment must add anatomically structured lip degrees of
freedom with explicit left/right coupling or independent trustworthy support.
Do not tune this scalar more finely: its bilateral tradeoff and generic visual
effect have already falsified it as the missing identity direction.
