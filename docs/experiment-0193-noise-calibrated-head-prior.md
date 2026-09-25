# Experiment 0193: noise-calibrated oracle head prior on new identities

Status: predeclared synthetic execution `TECHNICAL_CHECK_PASSED`;
noise-calibrated mean recovery `PARTIAL_SUCCESS` as a diagnostic,
casewise reliable reconstruction/default promotion `REJECT`,
real-reference quality `UNVERIFIED`.

Experiment 0192 exposed instability under 1 px noise in exact synthetic
facial correspondences. Before this run, twelve new identity indices
(5, 18, 41, 64, 87, 110, 133, 156, 179, 202, 225, 248) and one changed
factor were fixed in an ignored local plan. All 39 existing exact material
anchors are visible in all three training views for every case. They are
projected with known front/±30° cameras, then perturbed by deterministic,
independent Gaussian 2D noise with standard deviation 1 px at 220 × 220.
The ±90° views and true vertices are scored only after fitting. This is
still an in-family **oracle material-correspondence** test, not a way to
find corresponding points in the five independent/composited references.

The original estimator's ridge weight was 0.05. The single replacement
weight is not fitted to held views: the synthetic generator activates
12/82 controls, each uniformly sampled from ±0.35. A Gaussian
approximation gives unconditional coefficient variance
`(12/82) × (0.35²/3)`; dividing the assumed 1 px noise variance by it
sets the ridge to 167.34694. The 82 pinned CC0 controls, strongest-12
selection, coefficient bounds, sign-specific fit and mesh guards remain
unchanged. The sparse, safety-conditioned generator is not actually a
Gaussian population, and none of its variance is a measured human-head
prior.

| Twelve-case mean | Unchanged template | Old noisy fit, ridge 0.05 | Noise-calibrated fit |
| --- | ---: | ---: | ---: |
| Held left/right leading-face edge | 0.443/0.443 px | 0.487/0.487 px | 0.202/0.202 px |
| True whole-mesh 3D vertex RMSE, normalized head radius | 0.009491 | 0.009965 | 0.003891 |
| Front mask IoU | 0.987700 | 0.985577 | 0.990608 |

Every mesh passes the implemented area, normal and displacement checks.
The calibrated method's true 3D RMSE beats the old noisy fit in 10/12
cases. Yet the predeclared joint condition—*both* held side edges lower
than the unchanged template, 3D RMSE lower, front IoU nonworse and mesh
safe—holds in only 3/12 cases. Four examples start at zero sampled
template side-edge error and cannot strictly improve, but there are
actual regressions too: index 225 rises from 0.11 to 0.53 px side error,
and several other cases lose front overlap. The large mean gains partly
come from correcting a few hard cases; they are not stable per-head
identity evidence. Left/right scalar scores coincide because this
synthetic family is largely bilateral at 220 px.

The regularizer fixes a measurable average instability in this *ideal*
setting, but does not pass the casewise reliability gate. Do not apply
these oracle coefficients to the user's head or substitute new generic
geometry for the current mesh. The user's five views were generated or
composited independently, their material correspondences and noise law
are unknown, and they cannot prove one true physical head or camera.
No user mesh, camera, hair or texture was changed.

Next gate: obtain or independently build a commercially permitted
correspondence source with measured error and use a genuinely fixed-3D,
cross-person validation set at higher side-view resolution. Any later
head-only candidate must show enlarged front and both-side photo/old-
white-mesh/candidate-white-mesh comparisons, especially the lip–chin
relief, before visual promotion. Private per-case metrics, visibility
preflight and the predeclared plan are under ignored
`assets/private/synthetic-head-benchmark-v1/oracle-noise-calibrated/`.
