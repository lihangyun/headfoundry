# Experiment 0115: metric-aware interpolation of the closed-mouth patch

Initial status: `UNVERIFIED`. One primary variable: replace uniform graph
averaging of camera depth with piecewise-linear finite-element Laplace
interpolation on the same projected triangles. Same boundary, topology, three
shape controls, original profile targets, optimizer configuration and cameras
as experiment 0114. No new training/model, smoothing of photographs or texture.

Prediction: remove artificial surface ripples caused by irregular vertex
sampling while preserving the exactly stitched boundary and producing natural
closed-lip relief. Falsification: striping persists, shape remains generic or
incorrect, or bilateral profile evidence regresses. Do not use a lower fitting
cost to substitute for all-view visual inspection.

The independent implementation assembles triangle-area/gradient stiffness
weights and solves a scalar Dirichlet problem with the existing optional SciPy
dependency. Tests reproduce an affine field at a deliberately off-center
interior vertex, unlike uniform graph averaging. Scaling the planar coordinates
and reversing triangle winding leave the result unchanged. Degenerate or
unconstrained singular input is rejected. These tests cover interpolation,
not anatomical validity or collision freedom.

## Executed result (2026-09-14)

The actual five-view and enlarged mouth renders substantially reduce the
uniform-graph striping. The patch is a continuous closed surface rather than
the prior template opening. However, the fitted lower lip becomes nearly flat,
the patch transition remains visible and full-head identity stays generic.
This is not natural, accepted likeness. Final promotion remains `REJECT`.

| Variant | Left profile MAE px | Right profile MAE px |
| --- | ---: | ---: |
| Original smooth source | 4.7725 | 7.0207 |
| Uniform-graph fitted patch (0114) | 5.3180 | 7.4700 |
| Metric initial patch | 9.9381 | 8.6193 |
| Metric fitted patch | 5.6565 | 6.2076 |

The right fitting metric improves while the left worsens, both relative to the
uniform fitted patch and the unchanged smooth source. The lower-lip coefficient
again reaches its zero bound. Do not equate solver convergence, lower aggregate
cost, eliminated opening or reduced numerical striping with anatomical quality.
The unsmoothed source remains 3.5891 / 7.2493 px and all camera gates remain
unchanged. These profile rows are fitting observations, not independent tests.

Topology and exterior preservation remain as in 0114: exactly 101 stitched
boundary vertices, unchanged retained head, 34,753 output vertices / 69,320
triangles, and only the original 184 neck boundary edges. No complete 3D
intersection certificate or expression capability is claimed.

Local `closed-lip-patch-metric-v1` preserves source/initial/fitted OBJ files,
both inspected comparisons, patch data, early fit summary and report SHA-256
`7e38ead8b82db2c41e7d12447bf1b320e5793d4991e747854ff2d6ee5b5bfee9`.
No images or identity-derived geometry enter Git. The polygon triangulation
and metric interpolation contracts have deterministic tests; their technical
status is separate from the rejected reconstruction.
Verification: `python -m unittest discover -s tests -q` passes all 98 tests;
`git diff --check` passes. No default reconstruction is replaced.

Next gate: boundary tangent continuity and photo-consistent lip relief need
explicit constraints. The current patch only fixes boundary positions and
fits three depth coefficients to profiles; it can flatten a lip to reduce
error. Do not repeat that unconstrained three-coefficient fit or substitute
the visually poorer minimum-cost candidate for actual all-view acceptance.
