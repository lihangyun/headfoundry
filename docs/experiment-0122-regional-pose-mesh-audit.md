# Experiment 0122: apply the free-point cameras to the real head

Before using experiment 0121's camera hypothesis in shape work, project the
unchanged actual experiment 0117 mesh through both original and trial cameras.
Frontal detector rays at four eye corners and chin ID 152 define five exact
visible barycentric surface supports. Do not substitute the freely fitted
points from 0121 for these actual head points.

| Fixed head support | Original left/right error px | Trial left/right error px |
| --- | --- | --- |
| Four eye mean | 5.4719 / 4.8479 | 25.2430 / 23.4726 |
| Chin | 13.7039 / 11.6232 | 15.0754 / 13.7894 |

Frontal errors stay numerical zero because the frontal camera and source
support are unchanged. All supports remain visible in front and both obliques
with ray-hit differences below 3e-14 template units. Visibility cannot explain
the large new eye mismatch. The camera candidate is `REJECT` for use on the
unchanged head; lower free-point mouth residuals were not mesh alignment gains.

Separately lift chin ID 152 in each original view. Pairwise distances between
the three actual surface hits are 0.04171, 0.03923 and 0.08012 template units.
These different points are consistent with a view-dependent outline, but also
with inaccurate shape, camera or observation. Do not assert that this proves
contour semantics, and do not silently remove chin evidence to accept 0121.

Private `regional-pose-mesh-audit-v1` retains support coordinates, per-point
projection errors and visibility checks, along with actual photo/original/trial
three-view rendering. The source mesh SHA-256 is
`fbfb86271c5640f2ddf44b7d6f8c74bd21e4e3611d293d462768c61034688945`.
Both profile cameras and the full mesh remain unchanged; no texture or
expression path is enabled and no reconstruction improvement is asserted.

This reproduces the earlier free-point-versus-fixed-head failure mode on the
current closed-mouth geometry. Stop further standalone free-point camera
promotion attempts. Any new coupled trial must use actual shared surface
supports, preserve eye projection and evaluate view-dependent contours.

The actual three-view renders completed and were inspected: oblique placement
changes without a geometry/identity improvement; frontal output is unchanged.
The two untouched profile cameras need no duplicate rendering for this check.
`git diff --check` passes; public implementation and tests are unchanged.
