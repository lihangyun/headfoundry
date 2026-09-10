# Experiment 0072: explicit mixed point/curve target fitting

Status: candidate `REJECT` for shape promotion. Numerical contract tests
pass; there is still no accepted reconstruction.

Extend `fit_target_points` with optional curve observations: view index,
explicit source sample indices, ordered pixel polyline and positive pixel
scale. Reuse closest-polyline residuals; validate view/index/scale/polyline
inputs, include curve-supported samples in target eligibility, and report
point and curve errors separately. Default point-only behavior is preserved.
This does not extract an apparent contour or infer anatomical correspondence.
At least one eligible point observation remains required by the API.

A deterministic test recovers two known coefficients, one supported only by
curve samples, and checks malformed curve rejection. Existing mask, bound,
uncertainty and unsupported-control tests remain active. Full suite: 77 tests.

Real-data integration retains the four nasal control pairs, fixed source and
original cameras from 0071. Add two 32-sample source nasal arcs with 5px scale
to the twelve alar points (also 5px). Source samples use exact edge weights,
their target displacements use the same weights, and no frontal projection
prior is added. Evaluate all sixteen sign branches. Profiles now participate
in fitting; their final actual-envelope checks are diagnostics, not held-out
truth. The explicit sample count affects weighting and is recorded.

Best tip/depth/width/base coefficients: 0.5, 0.007798, -0.072976, -0.232509.
The tip reaches its upper bound; unlike the point-only trial it now has
curve support. Maximum displacement 0.011877 template units; zero reversed
normals, minimum area ratio 0.682781. No collision/anatomy acceptance.

| Diagnostic px | Source | Candidate |
| --- | ---: | ---: |
| Eligible alar-point overall mean | 6.9129 | 5.2015 |
| Fitted left frozen-arc mean | 2.4262 | 2.3165 |
| Fitted right frozen-arc mean | 3.8934 | 3.8229 |
| Actual left nasal envelope MAE | 2.8416 | 3.2381 |
| Actual right nasal envelope MAE | 6.4675 | 7.2195 |

Actual five-view clay renders were inspected. The candidate remains generic;
both true-envelope diagnostics regress. Do not equate the smaller fitted
arc distance with improved apparent silhouette: source samples, nearest-line
distance and candidate edge envelopes are different measurements. This
experiment retains all of them explicitly and does not promote the candidate.

Private `authored-nose-mixed-contract-v1` contains the actual OBJ, all public
fit reports, complete diagnostics, asset provenance and five-view comparison.
The public reusable implementation contains no private images or identity
data. Next address the difference between fitted fixed arcs and the actual
candidate contour before enlarging the tip bound or claiming a better fit.
