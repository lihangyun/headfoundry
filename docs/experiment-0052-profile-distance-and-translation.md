# Experiment 0052: profile distance and translation diagnostic

Status: camera candidates `REJECT` for promotion; closest-curve primitive
`TECHNICAL_CHECK_PASSED`. Actual reconstruction remains `UNVERIFIED`.

To discriminate global alignment from nose/lip shape error, the source mesh,
rotation, intrinsics and camera depth are frozen. Only right-camera x/y
translation is fitted within +/-0.05 template units. Eight alternating original
profile samples train the fit; eight are evaluated separately. These samples
were previously fitting inputs and are not a new independent acceptance set.

## Horizontal scanline failure

The horizontal-envelope objective fits translation (0.01819,-0.02535), without
active bounds. Training MAE decreases 8.17 to 4.79px but evaluation MAE increases
7.89 to 31.19px. The last chin sample jumps to 205.88px error: after translating
the head upward, that horizontal row intersects a rear/neck contour instead of
the facial chin endpoint. This is a correspondence failure, not a 205px local
deformation. The mesh never changes. Preserve the failed record rather than
silently dropping this sample.

## Ordered facial-arc distance control

The new `curve_residuals` primitive measures closest-point 2D residuals against
an ordered open polyline, including endpoints. It handles repeated vertices
and rejects invalid coordinates. It does NOT identify semantic curves or
connect disconnected silhouettes automatically. Existing horizontal-envelope
behavior and acceptance gates remain unchanged.

For a controlled comparison, freeze the actual source facial arc from rows
430–869 as 3D edge-intersection points, project this same arc under each camera,
and optimize closest-curve residuals instead of horizontal row intersections.
The last target now remains near the chin endpoint instead of switching to the
rear neck. Only the objective changes relative to the first translation trial.

Translation becomes (0.01822,-0.02297). On the same arc-distance metric:
training mean 7.30 to 4.47px; evaluation mean 5.99 to 4.72px. Do not compare these
values directly with horizontal MAE as though they were the same metric.
The original horizontal metric is also retained in the report, including its
205.68px endpoint mismatch. No threshold or gate is weakened.

The candidate still fails broader evidence: approximate original landmark
anchor mean worsens 15.85 to 17.42px, and the actual final chin target's arc
distance worsens 1.69 to 10.65px. The former anchors also have uncertain semantics
and were original pose inputs; they are regression checks, not ground truth.
Inspected the original-photo old/new arc overlay: a global shift changes nasal
alignment but does not fix the lip shape and moves the chin endpoint away.
Thus no camera promotion, geometry change or likeness claim follows.

Private outputs `right-translation-v1` and `right-translation-arc-v1` retain both
failed candidates and full metrics. The latter also contains the inspected
photo overlay. Runners check local input consent and record source hashes;
identifiable outputs remain ignored by Git. Source and all other views remain
unchanged. All 69 tests pass, including curve endpoints, reversed orientation,
repeated/degenerate segments, empty query points and invalid input checks.

Next use semantic nose/lip/chin curve segments and explicit endpoint handling
when evaluating local shape changes; a global camera translation is not an
adequate fix. Camera, full identity, texture and product gates remain unmet.
