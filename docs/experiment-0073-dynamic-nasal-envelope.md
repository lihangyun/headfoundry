# Experiment 0073: recompute the candidate nasal envelope

Status: `REJECT` for promotion. No accepted camera or identity result.

Replace the frozen source-arc correspondence in 0072 with the actual
candidate outer edge envelope at every residual evaluation. Keep the same
four signed control pairs, sixteen sign branches, original cameras, twelve
eligible alar observations, two sets of 32 evenly spaced nasal rows, nearest
polyline residual, supplied 5px scales, 0.5 bounds and soft-L1 regularization.
No frontal source-projection prior. Reuse the existing envelope and curve
functions; this is a private experimental runner, not a new production path.

Prediction: refreshing apparent-contour support should remove the fixed-arc
proxy mismatch. Falsification: final side evidence regresses despite fitting.
Keep source/cameras unchanged, inspect all five actual clay views, and reject
triangle reversals. Collision/anatomical validity is not proven by this check.

All sixteen branches terminated successfully. Best tip/depth/width/base:
0.5, -0.004073, -0.070274, -0.209059. Maximum movement 0.012793 template
units; no reversed triangles; minimum area ratio 0.714685. Tip remains bound.

| Diagnostic (px) | Source | Frozen candidate 0072 | Dynamic candidate |
| --- | ---: | ---: | ---: |
| Left original annotated-row nasal MAE | 2.8416 | 3.2381 | 3.3116 |
| Right original annotated-row nasal MAE | 6.4675 | 7.2195 | 6.9584 |
| Left dynamic 32-row nearest-curve mean | 2.4262 | 2.0902 | 2.2201 |
| Right dynamic 32-row nearest-curve mean | 3.8934 | 4.0259 | 3.9428 |
| Left dynamic 32-row horizontal MAE | 2.8189 | 2.3804 | 2.5332 |
| Right dynamic 32-row horizontal MAE | 4.7792 | 5.1052 | 4.9824 |

Important correction to the previous hypothesis: the mismatch is not solely
frozen versus apparent contour. Even a recomputed contour improves the dense
left sampling while worsening the original annotation rows. Uniform sampling
and sparse anatomical turning-point rows weight different portions of the
curve; closest-polyline and horizontal distances are also different metrics.
On the right, both dense and sparse errors still regress. These are overlapping
fitting diagnostics, not independent validation and not ground truth.

Alar mean errors front/left-oblique/right-oblique change from
8.8148/5.1659/4.8562 to 5.5726/6.0112/3.9318. The objective still trades
one view against another; merely updating contour support does not solve it.
The actual photo/source/candidate five-view sheet was rendered and inspected:
the model remains visibly generic and the local change is small. No baseline
replacement, quality claim, texture concealment or larger-bound retry.

Private output `authored-nose-dynamic-contract-v1` retains the OBJ, provenance,
all branch costs, geometry checks, cross-candidate contour audit and photo
comparison. Private photos and scripts remain excluded from Git. Existing
public suite: 77 tests pass. No public numerical implementation changed.

Next distinguish fitting support at anatomical turning points from long
near-linear spans, and diagnose the remaining cross-view conflict. Preserve
both sparse and dense measurements; do not select whichever makes a candidate
look better. Increasing target strength alone is not supported by this result.
