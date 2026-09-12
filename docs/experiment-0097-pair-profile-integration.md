# Experiment 0097: profile constraints alongside surface pairs

Status: `UNVERIFIED`; no promotion.

First audit the exported pair-only candidate from 0096: thirteen sampled lateral
planes show zero proper 2D segment crossings in source and candidate. The check
excludes tangencies, collinear overlap and unsampled 3D intersections, so it
does not establish collision freedom. Actual whole-profile MAEs change from
3.589129/7.249347 to 3.582587/7.309081 px; mouth-only errors change from
4.618532/8.928231 to 4.602644/9.034424 px. Right-side regression remains.

Single integration change: add sixteen original-row bilateral mouth contour
observations to the same thirteen surface pairs. Keep source/cameras, protected
region, half-gap targets and regularization unchanged. Photo observations use
source-selected silhouette edges for one linearized step; contact candidates
remain separate from visible-image supports.

The new candidate retains reduced pair gaps but whole-profile MAEs become
3.606997/6.438382 px: material right improvement with a small left regression.
Maximum displacement is 0.039487 template units, considerably larger than
the pair-only 0.004233. Minimum area ratio falls to 0.509159, verified on the
exported OBJ, with zero reversed triangles. The soft solver does not enforce
the 0.03 movement guard used in earlier local trials; this result must not be
described as passing that guard. No baseline promotion is justified.

Actual five-view photo/source/candidate renders were inspected. Lip/face shape
remains generic and angular, with no demonstrated identity improvement. This
result motivates a bounded step and updated silhouette support rather than
unrestricted acceptance of the linear proposal. Collision auditing of the new
candidate remains outstanding; the pair-only planar check does not cover it.

Private `rim-section-audit-v1` stores the bounded planar audit and actual
profile errors; `rim-pair-profile-v1` stores the separate integrated candidate,
matching cameras and inspected five-view sheet. No personal data is committed.
Public production code unchanged; verification used actual solver execution,
exported triangle checks, recomputed silhouettes and rendered evidence.
