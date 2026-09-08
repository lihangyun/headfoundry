# Experiment 0027: bounded depth/camera registration

Status: `REJECT`; no accepted head or camera promotion.

The new `refine_depth_cameras` jointly fits camera pose and a scalar depth
multiplier for each non-reference view from supplied 3D camera-coordinate
correspondences. The first camera and depth scale remain fixed. Residuals are
world-point deviations from their per-track mean, robustified with soft-L1 at
0.01 input units. Increment bounds are +/-0.1 radians per rotation component,
0.1 input units per translation component, and 0.1 log scale. These are local
experimental choices, not calibrated metric uncertainties. Collinear input is
rejected; no dense deformation is performed.

Actual local driver: `assets/private/subject-001/fit_depth_cameras.py`. Rights
and prediction hash are rechecked. The 40 frozen training tracks alone enter
the optimization. All 11 held tracks (33 third-view predictions) are evaluated
after fitting. This experiment covers front/left30/right30 only; profile views
are not corrected or validated. Learned depths are sampled bilinearly at the
existing matched pixels. The ray camera initializer from 0026 is unchanged at
entry; no extra weights, services or training data are introduced.

The solver converged in 10 evaluations without active bounds. Depth scale
multipliers: 1, 0.9818845, 0.9832401.

| Diagnostic | Before | After |
| --- | ---: | ---: |
| Training third-view projection p95, px | 33.4066 | 18.4993 |
| Held third-view projection p95, px | 25.7596 | 11.6610 |
| Held depth disagreement p95, input units | 0.014702 | 0.005925 |
| Frozen manual third-view p95, px | 32.4658 | 20.4766 |

Both held checks improve relative to the raw ray initializer but fail the 3 px
gate. The 11.661 result does not beat the older independently fitted bundle's
~7.5485 px result. No scan truth exists for the depth-disagreement statistic.
Manual readings remain approximate; their worst errors persist around an eye
corner. No mesh was regenerated to imply that these numeric changes deliver
improved side-profile likeness. Existing accepted/default behavior is unchanged.

51 tests pass, including recovery of a known rotation/translation/depth-scale
perturbation, exact preservation of the reference camera and degenerate input
rejection. These tests are bounded engineering evidence only. Next reconcile
the remaining image-space residual with depth consistency; do not discard the
held populations or loosen thresholds to manufacture acceptance.
