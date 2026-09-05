# Experiment 0011: shape-independent calibrated pose initialization

Decision: REJECT as a replacement camera initialization. No head reconstruction
or visual improvement is accepted.

Implemented NumPy essential-matrix pose decomposition with all four rotation /
translation alternatives and training-only positive-depth disambiguation.
The first camera is identity and translation has unit length: scale is unknown.
The function reports UNVERIFIED even when positive-depth support is sufficient.
It does not certify the supplied focal length or perform the full camera gate.

The experiment preserves experiment 0010's train/held-out splits and boundary
exclusions. Intrinsics remain the assumed 1800 px focal length, principal point
(627,627). Only initialization changes: no frontal depth prior is used.
Validation measurements are excluded from matrix fitting and pose selection.

| Pair | Positive training depth | Held-out Sampson p95 px |
| --- | --- | --- |
| front / left30 | 100% | 30.410997 |
| front / right30 | 100% | 30.937200 |
| left30 / right30 | 100% | 8.742459 |

These are Sampson distances, not full reprojection errors. Relative to the
unconstrained fundamental matrices in experiment 0010, enforcing calibrated
camera structure worsens the same held-out metric substantially. This supports
testing the assumed calibration; it does NOT establish focal length as the
sole cause. Detector correspondence noise and weak facial depth variation
can also bias the eight-point solution. Positive depth alone is insufficient.

A deterministic nonplanar fixture verifies recovered rotation and translation
direction against known cameras, with all training points in front. The complete
suite passes 34 tests. The real-photo numerical record remains local and ignored.
No new weights, external service, or photo upload was used.

Next gate: test calibration/pose refinement against the unchanged held-out
observations, choosing optimization and stopping using training evidence only.
Do not feed this failed initialization into formal head or texture generation.
