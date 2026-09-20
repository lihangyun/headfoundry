# Experiment 0126: coupled fit on the reconnected patch

Run the existing actual-surface/pose fitter on the experiment 0124 reconnected
base, re-lifting all frontal supports on the new topology. Keep the three
depth fields, two oblique rotations, bounds, priors and observation selection
unchanged. Compare this candidate against its own base, not experiment 0123:
the reconnected base uses 0115 coefficients, while 0123 started from 0117.
Experiment 0125 already provides the controlled identical-deformation replay.

The coupled solver converges without active bounds. Maximum displacement is
0.0072324 template units; minimum triangle area ratio is 0.88360, with zero
relative normal-dot reversals and 14,417 unchanged outside-support vertices.
Thus the prior triangle-area failure does not recur in this fitted candidate.

| Diagnostic | Before left/right px | After left/right px |
| --- | --- | --- |
| Four-eye mean | 5.4719 / 4.8479 | 6.2177 / 4.2815 |
| Corrected profile mean | 4.5744 / 6.1769 | 4.4694 / 6.0796 |

Both profile means decrease, but the left eye regresses. Candidate promotion
is `REJECT`, even though the local geometry checks pass. Depth coefficients
are [-0.00494185,0.00494423,0.00714706]; other detailed parameters and per-point
errors are in private `shared-surface-reconnected-v1` with actual OBJ/cameras.
No visual improvement is inferred from these fitting metrics.

Next test non-regression constraints within the solve rather than relying
only on post-fit rejection. Keep both eye-view means and both profile means
no worse than their starting values. Geometry/visibility and actual all-view
inspection remain additional checks, not waived by constrained optimization.
