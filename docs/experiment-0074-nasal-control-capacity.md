# Experiment 0074: local nasal control capacity

Status: `UNVERIFIED` diagnostic. No new reconstruction candidate or promotion.

The actual views from 0073 still lack identity. Before another four-control
optimization, test whether those controls can explain the current discrepancy.
Keep the source, cameras, eligible alar correspondences and fourteen original
nasal annotation rows fixed. Form 38 scalar residuals: 24 alar x/y components
and 14 actual horizontal-envelope errors. This deliberately uses original
turning-point rows rather than the 32-row uniform metric. All are existing
fitting data, uncertain, and not independent anatomical ground truth.

For each of sixteen signed target branches, estimate a 38-by-4 one-sided
Jacobian at the source. Compute its rank, singular values, the residual
component orthogonal to its column space, an unconstrained least-squares
diagnostic and a nonnegative 0..0.5 bounded linear solution. Reevaluate the
bounded solution against actual nonlinear projection and edge envelopes.
Use equal pixel-component weights and no robust loss for this capacity audit;
its scores must not be compared numerically with earlier robust objectives.

Finite-difference steps 0.001, 0.0001 and 0.00001 produce consistent results:

| Step | Minimum orthogonal residual fraction across branches | Best bounded exact residual norm (px) |
| --- | ---: | ---: |
| 0.001 | 0.894277 | 31.994727 |
| 0.0001 | 0.894361 | 31.994692 |
| 0.00001 | 0.894369 | 31.994688 |

Source residual norm is 34.442901px. At the central step the best bounded
branch uses negative tip/depth/width/base directions with magnitudes
approximately 0, 0.057315, 0.085338 and 0.170577. Its Jacobian is rank four
with singular values 116.1640, 64.0534, 41.8147 and 29.2623. The predicted
residual norm is 32.338474px versus the reevaluated 31.994692px. This is not
a near-singular numerical fit. Across branches, at least 89.4% of residual
norm remains outside the local four-dimensional span even before bounds.
That is a norm fraction, not a per-point error percentage or reconstruction
accuracy. It does not prove global nonlinear impossibility.

Decision: stop routine four-control nasal coefficient sweeps. Current local
expressivity, source correspondences and unaccepted cameras constrain progress;
this audit cannot assign all residual to geometry. Next investigate the
unexplained spatial residual and broader anatomically supported deformation,
checking correspondence/camera alternatives before attributing it to shape.
Do not loosen the shape bound or camera gate based on this diagnostic.

Private `nasal-capacity-audit-v1`, `nasal-capacity-audit-0.001` and
`nasal-capacity-audit-1e-05` retain all branches, residual components, singular
values, input hashes and exact reevaluations. The private runner reuses asset
rights/hash validation and existing numerical functions. No private data is
committed; no model, renderer, camera or production default was changed.
