# Experiment 0063: contour-supported screened pose

Status: `UNVERIFIED`; no production camera promotion or identity claim.

Add profile-arc constraints to the screened-anchor solve of 0062. Source
mesh, focal length (1800px), screening mask, pose initialization/bounds,
soft-L1 loss and 5px scale remain unchanged. Front and oblique solves are
identical to 0062. On each profile, freeze 64 source silhouette edge samples
over the observed facial vertical range and minimize their projected distance
to the ordered photo profile polyline along with retained anchor residuals.
Use the existing closest-polyline residual implementation. This avoids
assigning arbitrary same-row point identities during the optimization, but
the frozen source arc is not guaranteed to remain the candidate apparent
contour. Re-evaluate actual candidate edge envelopes separately.

All solves converge without active bounds; entire-mesh minimum camera depth
is 4.0560 template units. The mesh is unchanged. Both profile curves now
participate in fitting: they must not be described as held-out validation.
The private report and runner explicitly record this changed evidence scope.

| Diagnostic, pixels | Original | Screened only | Screened + contour |
| --- | ---: | ---: | ---: |
| Left actual-envelope MAE | 3.6420 | 4.4372 | 2.7445 |
| Right actual-envelope MAE | 8.0322 | 17.3383 | 4.7013 |
| Left retained anchor mean | 9.9285 | 9.8387 | 10.3402 |
| Right retained anchor mean | 14.1399 | 11.1127 | 16.1883 |

Frozen-arc mean distance decreases from 3.1687 to 1.9061px on the left and
7.0755 to 3.8139px on the right. These are training diagnostics. Lower arc
or envelope error trades against worse anchor correspondence; there is still
no independent camera or geometry truth.

Actual bilateral photo/original/screened-only/contour-supported clay renders
were inspected. Adding the arc visibly restrains the gross right-side pose
drift of 0062, but does not recover identity: eyes, nose and lips remain
generic and the upper-head outline is unconstrained by the face arc. No
candidate is accepted merely because it outperforms the deliberately rejected
screened-only result. Original source cameras remain unchanged.

Private `contour-anchor-pose-v1` retains the camera arrays, 64-point source
arcs, complete diagnostics and native comparison. Existing private runners
accept `--contours` and preserve prior outputs. All 72 tests pass. Next use
this evidence to distinguish silhouette support from anatomical point support
in subsequent fitting, and verify cross-view visible features before any
baseline promotion. Repeated contour optimization alone cannot establish
KeenTools-level reconstruction quality.
