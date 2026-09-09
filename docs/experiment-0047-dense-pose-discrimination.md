# Experiment 0047: pose-only dense correspondence discrimination

Status: pose candidate `REJECT` for promotion; cause attribution `UNVERIFIED`.
This experiment changes only rigid pose in the three frontal/oblique views.
The source mesh, intrinsics, screened correspondences and split from 0046 stay
fixed. Both profile cameras remain untouched. No geometry displacement occurs.

## Hypothesis and test

The frozen nose-bridge residuals in 0046 might partly reflect initial pose,
rather than requiring deformation of protected profile geometry. Use the
existing bounded rigid template solver on visible training points only.
Visibility is frozen from the source mesh/cameras; every seventh landmark ID
is withheld in all views. Rotation-vector components can change by at most
0.15 radians, translations x/y by 0.15 and z by 0.5 template units. Intrinsics
remain the assumed focal model, not calibrated measurements. All three solves
converge with no active parameter bounds.

| View | Held detector p95 before / after, px | Manual anchor mean before / after, px |
| --- | ---: | ---: |
| Front | 23.32 / 16.04 | 6.63 / 9.22 |
| Left30 | 28.43 / 17.83 | 5.04 / 11.04 |
| Right30 | 24.46 / 16.47 | 7.75 / 11.51 |

The manual regression uses six previously read canthus/mouth anchors and their
original template vertices mapped through the neck clip. Those annotations
are approximate and were used by the original pose fit; they are not a fresh
independent gate. Nevertheless they expose a tradeoff hidden by detector-only
evaluation: all three manual-anchor means become worse, with maxima reaching
16.25 / 16.44 / 17.14 px. This is not evidence of uniformly better calibration.

Held central point 168 improves from 28.10 / 35.00 / 33.75 to
22.45 / 21.26 / 21.35 px, but remains materially displaced. Point 196 also
remains at 17.71 / 17.82 / 15.91 px. Pose can absorb some dense residual but
does not resolve the conflict between correspondence sets and template shape.
The outcome neither proves all residuals are shape error nor vindicates the
original cameras. Do not adopt these cameras to make geometry tests look better.

## Actual visual review and next step

Inspected the photo / original pose / dense pose proposal sheet, rendering the
exact same mesh and lighting. Orientation/alignment changes are visible; it
still looks generic and the comparison supplies no accepted likeness gain.
The original camera bundle remains the experimental reference, not an accepted
calibration. No candidate was silently promoted.

Private outputs in `dense-pose-audit-v1`: candidate cameras, full fit report
with source hashes and split counts, manual-anchor audit and comparison PNG.
Local runners `audit_dense_pose.py` and `render_dense_pose_audit.py` reuse the
existing solver/renderer and keep photos and identifiable outputs outside Git.
The fitting runner checks local input consent before use.

Next establish anatomically supported central template anchors instead of
trusting raw detector semantics on generic clay. The eye-hit failure and this
pose tradeoff show why globally increasing deformation or re-estimating pose
from all detector points is not yet justified. Preserve the fixed profile
evidence while resolving that ambiguity. Camera/identity/product acceptance
remains unmet. No public code changed; all 65 tests pass.
