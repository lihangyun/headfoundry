# Experiment 0046: screened eye correspondence fitting

Status: `UNVERIFIED`; no baseline promotion. The single primary variable versus
0044 is correspondence support. Mesh source, cameras, regularization, movement
bound, protected regions and rendering remain unchanged. No weights or training.

## Screening and actual run

Within two eye ROIs (four anchor bounds expanded by 15 original-image pixels),
60 valid raw clay correspondences were inspected for depth discontinuity.
Sixteen samples on a 5px-radius ring flagged centers more than 0.1 template
units behind a neighboring surface. Fifteen were flagged. The five explicitly
reviewed proposals from 0045 replace their original internal hits; ten other
points remain excluded with their raw values retained, not silently snapped:
7,144,153,160,161,163,384,385,387,466.

This heuristic is neither a general semantic classifier nor independent truth.
It deliberately exposes uncertainty rather than using photo residuals to choose
which observations to remove. Original four ray misses remain explicit.

974 visible training constraints remain. The same one-step surface solver uses
step 0.264738 and maximum displacement 0.03 template units after the same
triangle normal/area backtracking. Protected positions are exactly unchanged.
The original 0.06 movement bound and regularization 100 are not increased.

## Common-support comparison

Filtering changes the held observation set (176 to 172), so raw percentiles
from 0044 and this run are NOT directly comparable. A separate audit evaluates
all three meshes using identical corrected correspondences and source-frozen
visibility. The held split remains landmark ID modulo seven in every view.

| Mesh on common support | Training p95 px | Held p95 px |
| --- | ---: | ---: |
| Unchanged source | 29.3028 | 25.9065 |
| 0044 dense candidate | 25.1523 | 23.0857 |
| Screened candidate | 24.4806 | 23.0857 |

There is no held-p95 improvement over the earlier candidate on this common
support. Do not attribute a changed-support percentile reduction to a better
model. Largest remaining held residuals include points 168 and 196 at 27–35px;
their actual 3D point displacement is exactly zero under both fits. These
central nose-bridge points are in the deliberately protected stripe. Thus
increasing iterations or cleaning eye constraints cannot resolve those errors
under the current support policy. This does not establish whether their true
cause is anatomical correspondence bias, pose/calibration, or shape.

Frozen profile MAE: left 3.64196 to 3.66119 px, right 8.03223 to 8.00897 px.
Maximum sampled contour shifts are 0.6523 / 0.6465 px. The slight left regression
remains reported. Original approximate curves are previous fit inputs, not
ground truth or a new acceptance set.

The five-view photo / source clay / candidate clay sheet was inspected using
identical smooth shading. Changes remain modest; it still reads as a generic
head and lacks eyeballs. No clear visual identity improvement is established.

## Artifacts and next discriminating step

Private ignored outputs: `eye-supported-correspondence-v1` (full masks, flags,
depth differences, correspondence NPZ); `dense-template-v2` (actual OBJ,
five-view sheet, fit report, profile audit, common-support audit).
Candidate SHA256:
`f7a3fe874dd7e968ae292e39072adbfe7b691fa736a18f2dc0e76b8a0ce86ff0`.
The fit report locks the correspondence digest; the profile audit records the
candidate and camera digests. Photos and all identifiable derivatives remain
local and untracked. Existing fit/audit runners now take optional private input
and output directory names; their defaults preserve previous experiments.

Next inspect the frozen central anatomical mapping against the actual template
surface and photos, and distinguish that issue from camera bias before relaxing
profile protection. Do not remove held observations to achieve a pass. Eye
geometry completeness is also unresolved. This run changes no public solver;
the existing 65-test suite passes. Camera and finished-product gates stay open.
