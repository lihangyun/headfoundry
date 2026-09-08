# Experiment 0028: joint pixel and depth objective

Status: `REJECT`; unchanged 3 px threshold and frozen validation populations.

Optional pixel-space intrinsics add image reprojection of each track's mean
world point to the bounded depth-camera optimizer. Depth residuals retain the
0.01 input-unit normalization; pixel residuals use 3 px. Same robust loss,
reference anchor, parameter bounds, 40 training tracks and ray initialization.
No held observations enter the objective, no profile camera is fitted.

Private driver `fit_depth_cameras.py --pixels` produced `depth-camera-fit-v2`.
The optimizer converged in 17 evaluations, **with an active parameter bound**.
Compared with depth-only 0027:

| Held diagnostic | Depth only | Joint objective |
| --- | ---: | ---: |
| 33 third-view predictions p95, px | 11.6610 | 8.8242 |
| 18 frozen manual predictions p95, px | 20.4766 | 14.3528 |
| Depth disagreement p95, input units | 0.005925 | 0.006136 |

Image-space errors decrease but remain above threshold; depth consistency
slightly regresses. The result does not beat the older ~7.5485 px bundle result.
Do not widen the bounds or discard inconvenient observations just to pass.
No complete mesh or verified side-profile improvement follows from this fit.

The first private report's optimization RMS fields mixed pixel and depth terms;
do not interpret them as physical depth errors. Reporting was corrected to
compute RMS on depth residuals only, without changing the objective or fitted
parameters. The separate held depth-disagreement values above are unaffected.

51 tests pass, with the synthetic known pose/scale recovery test now exercising
both objective modes. No new dependencies or external services. Next determine
whether the active bound reflects camera/depth/model mismatch before further
parameter changes; preserve independent manual validation.
