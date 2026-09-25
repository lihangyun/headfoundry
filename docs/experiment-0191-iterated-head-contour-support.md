# Experiment 0191: relinearizing coherent head silhouette supports

Status: bounded synthetic execution `TECHNICAL_CHECK_PASSED`; this iterative
silhouette-only method `REJECT`; actual five-reference head quality
`UNVERIFIED`.

Experiment 0189 used one contour linearization at the common template.
This development-split diagnostic changes just that assumption: after the
original bounded solve, it recomputes front/±30° contour supports at the
candidate and solves the residual twice. It retains the same 82 pinned CC0
head controls, selected 12 directions, ±0.35 coefficient limits, ridge 4,
known cameras, fixed training rows and mesh-safety thresholds. True 3D
vertices and ±90° images remain outside the fit. It reuses the original
12 already inspected identities, so it is **not** a fresh method holdout.
No user photo or head was changed; hair and texture are absent.

All twelve meshes pass the implemented safety checks. The mean held-side
leading-edge error on either side falls from the one-pass 0.4430 to
0.4167 px at 220 × 220, and mean true 3D vertex RMSE falls from 0.008490
to 0.007748 in normalized head units. Nevertheless, compared with the
one-pass fit, only three individual cases improve their held side edge,
five worsen and four tie; 3D RMSE improves in five and worsens in seven.
The previous strict combined side/3D/front/safety gate stays at 4/12
`PARTIAL_SUCCESS`, eight `REJECT`. Case 139 materially regresses from
0.632 to 1.526 px held side error despite a safe mesh; case 115 improves
from 1.316 to 0.211 px. This split makes the mean gain unsuitable as a
reliability claim.

Two template side errors in this split are exactly zero, so the existing
strict-improvement rule cannot be passed there; several others are near
the quantization floor. That scoring limitation is separate from case
139's actual degradation. The fit also observes only silhouettes, not
internal mouth, cheek or eye anatomy, and all examples come from the
same synthetic control family with oracle cameras. Recomputing edge
supports alone does not resolve the information deficit or justify
another fit of these controls on the user's head. Do not use the new
identity split to tune this rejected iterative variant.

Next gate: find evidence that constrains **interior 3D facial shape**,
particularly mouth-to-chin relief, while protecting both side profiles.
An oracle-correspondence synthetic capacity test may establish what this
licensed basis could recover under ideal observations; it would still not
validate real-photo correspondence or likeness. The ignored local
`assets/private/synthetic-head-benchmark-v1/iterative-prior/` retains
per-case metrics and held-side clay panels.
