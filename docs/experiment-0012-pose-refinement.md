# Experiment 0012: nonlinear pose refinement and prior-free bundle

Status: REJECT for the real three-view camera candidate. Pairwise optimization
is implemented, but no formal head or texture acceptance is implied.

## Correcting the previous inference

Experiment 0011 suggested testing calibration because enforcing essential
structure enlarged epipolar errors. That result did not isolate calibration
from the limitations of linear initialization. This experiment first refines
five relative-pose parameters with calibration fixed. Translation is a unit
direction, rotation is rigid, and final training cheirality is checked again.
Signed Sampson residuals use soft-L1 scale 2 px; stopping uses training only.

| Pair | Fixed-focal held Sampson p95 px | Variable-focal held p95 px | Estimated focal px |
| --- | --- | --- | --- |
| front / left30 | 3.304384 | 3.281900 | 1966.572 |
| front / right30 | 2.208585 | 2.207949 | 1605.045 |
| left30 / right30 | 3.128868 | 2.990244 | 900.000 |

The fixed focal length is 1800 px. The controlled comparison permits one common
focal multiplier per pair, bounded to 0.5–2.0. All six runs converge with 100%
positive training depths. Large improvement occurs without changing focal
length. The variable-focal benefit is small and the intermediate-pair estimate
hits the lower bound. There is no evidence here for adopting those focal values.
The library retains fixed calibration; all six experimental results are kept.
Neither pairwise metric is a substitute for the 3 px multiview reprojection gate.

The fixed-focal pair rotations have a 0.869536 degree loop discrepancy. Fitting
translation scales gives positive ratios 0.822222 and 1.764972 relative to the
first unit baseline, with loop residual 0.001304. This is diagnostic evidence,
not a newly invented acceptance threshold.

## Three-view check without a frontal shape prior

Using these initial cameras, a private sparse nonlinear bundle jointly refines
380 interior points and two cameras. First camera and focal lengths stay fixed;
the first relative baseline is constrained to unit length. The same 60 held-out
observations remain excluded. Each point is initialized from two training views;
no frontal depth prior, contour regularization, or held-out early stopping is used.

- Converged in 33 function evaluations.
- Training reprojection p95: 3.220709 px.
- Held-out reprojection p95: 11.801050 px.
- Positive depths: 100%.
- Decision: REJECT; original 3 px gate remains unchanged.

Removing the face prior does not resolve the held-out mismatch. This strengthens
the need to independently audit the detector's cross-view correspondences and
conditioning, rather than treating its dense vertex labels as exact physical
correspondences or changing the head to hide their residuals. It does not prove
the source photos are unusable. Next gate is a physically identifiable sparse
correspondence check independent of detector-predicted cheek/forehead locations.

The reusable pose refinement is tested with exact nonplanar camera recovery,
unseen synthetic projections and noisy training data objective reduction, while
retaining positive-depth checks. All private outputs and scripts stay ignored;
no images were uploaded, and no new library or weight was installed.
