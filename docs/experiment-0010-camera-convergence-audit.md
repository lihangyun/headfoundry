# Experiment 0010: camera convergence and shape-independent audit

Status: REJECT for dense camera reprojection; UNVERIFIED for the separate
epipolar diagnostic. Neither metric establishes full-head or profile quality.

## Controlled iteration experiment

The hypothesis was that the twelve-iteration alternating solver had stopped
too early. The only changed setting was the predetermined iteration count,
from 12 to 60. Photos, training/validation split, intrinsics, initialization,
protected boundaries and surface regularization were unchanged. No iteration
was selected using validation error. All previous private artifacts remain.

| Iterations | Training p95 px | Held-out reprojection p95 px |
| --- | --- | --- |
| 12 | 3.683767 | 10.437478 |
| 60 | 3.382030 | 9.729990 |

Sixty held-out observations remain above the 3 px gate. More iterations alone
do not resolve this failure. A twelve-panel original/clay-overlay/held-out
comparison was rendered and visually inspected. Intermediate-view outer jaw
and face boundaries do not align reliably. The overlay is translucent clay,
not recovered texture; photo details seen through it are not model geometry.
This remains a face patch, without a full head, ears, neck or eyeballs.

## Independent diagnostic, not another accepted candidate

A normalized eight-point fundamental-matrix fit removes the frontal depth
prior and assumed focal length from a pairwise consistency check. For each
pair, the union of both views' held-out indices is excluded from fitting;
protected boundary indices are excluded identically to experiment 0009.
The metric is Sampson distance, NOT full reprojection error and cannot replace
the existing 3 px camera gate.

| Pair | Held-out count | Held-out Sampson p95 px |
| --- | --- | --- |
| front / left30 | 29 | 2.510886 |
| front / right30 | 31 | 4.269969 |
| left30 / right30 | 60 | 3.268535 |

Inference: insufficient iteration count is not the sole issue. A smaller
pairwise epipolar residual suggests investigating assumed calibration and
prior/boundary constraints, but does not prove either is the root cause.
Residual detector inconsistency also remains. Fundamental matrices alone do
not establish a rigid calibrated multiview camera solution, positive depths,
or correct facial shape. Correlated detector estimates are not scan truth.

The reusable NumPy implementation rejects insufficient/degenerate data. Its
synthetic test checks held-out exact recovery, rank two, and sensitivity to
corrupted validation coordinates. Next experiment should test calibrated
camera initialization independently of the frontal depth prior, retaining
the same held-out observations and explicit cheirality checks. Do not tune
away difficult points or lower the quality gate to make the run pass.

Identity-specific scripts, numerical outputs, OBJ and comparison image stay
in git-ignored local storage. No photos were uploaded or new weights used.
