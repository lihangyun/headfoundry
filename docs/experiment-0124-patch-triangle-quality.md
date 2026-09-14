# Experiment 0124: remove a numerical weakness before further deformation

Audit experiment 0123's smallest area-ratio triangles. The worst exported
triangle has ratio 0.21540 (export rounding differs from the in-memory
0.21508), source doubled area 4.2471e-8 and three nearly collinear vertices.
Its vertex displacements are only approximately 1e-5 to 5e-5 template units.
All its source z coordinates are near -0.99, far from the -0.6 field cutoff.
The worst inspected rows are not explained by crossing that cutoff; very thin
source triangles amplify small deformation changes. Do not waive the guard.

## Controlled planar connectivity trial

Keep all existing patch UV vertices and all boundary edges exactly fixed.
Flip only shared internal diagonals whose new triangles have positive original
winding and strictly improve the minimum quality of the pair. Reject existing
opposite diagonals and process disjoint face pairs per pass. No new vertices,
boundary movement or new shape coefficients. Stop when no improving flip remains.

Quality is 2*sqrt(3)*signed-double-area divided by sum of squared edge lengths;
it is 1 for an equilateral triangle and tends to zero for a sliver.

| Percentile | Original | Reconnected |
| --- | ---: | ---: |
| Minimum | 0.00007428 | 0.00297932 |
| 1% | 0.00051563 | 0.08227681 |
| 5% | 0.01082039 | 0.13307074 |
| Median | 0.23968179 | 0.46606679 |

The run converges after 23 passes and 46,275 flips. It verifies identical
boundary edge sets, edge incidence 1 or 2, positive winding, and preserved
total signed planar area. This is a local-quality method, not a guarantee of
globally optimal triangulation or a 3D collision certificate.

Private `patch-triangle-quality-v1` preserves the new planar triangulation.
The metric harmonic depth is recomputed on that connectivity with original
boundary depth and experiment 0115's frozen lip coefficients. A separate OBJ
and updated patch data are exported; reconnecting edges changes the piecewise
surface, so the old surface is not claimed invariant. This is an `UNVERIFIED`
3D candidate pending actual-view and deformation-stability tests, not a new
identity fit, default or accepted result. All old outputs remain untouched.
