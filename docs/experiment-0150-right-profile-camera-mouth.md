# Experiment 0150: right-profile mouth camera diagnostic

Status: diagnostic `TECHNICAL_CHECK_PASSED`; bounded direction
`PARTIAL_SUCCESS`; camera promotion `REJECT`.

This experiment keeps the experiment-0132 mesh and four other cameras fixed.
It fits one tiny physical perturbation of the right-profile camera on four
interleaved mouth-contour rows, then selects a scale only from candidates that
improve the three untouched mouth rows while preserving independent near-eye,
subnasale and chin material points, separate nose/chin contour regions,
positive depth, focal plausibility and a rigid rotation matrix. Available face
landmarks do not provide a verified ear correspondence, so no ear claim is
made.

The unconstrained mouth direction improves the held rows but regresses the
near-side inner eye by 0.52 px and is rejected. A strict 101-step line scan
finds a feasible scale of 0.19. Its rotations are only
(-0.0041, -0.0117, +0.0003) degrees and its focal change is -0.0164%. Mouth
fit error changes from 3.148 to 3.143 px and held-mouth error from 6.504 to
6.433 px. Nose and chin contour means also improve slightly, while every
protected material point stays within the predeclared 0.1 px regression
tolerance.

The physical and numerical path is `TECHNICAL_CHECK_PASSED`, and the existence
of a nonzero protected direction is `PARTIAL_SUCCESS`. It explains only 0.071
px, about 1.1% of the held-mouth error, using same-photo observations; this is
too small and too weakly independent to promote the camera or explain the
visible side-profile deficit. Camera promotion is therefore `REJECT`, and the
experiment-0132 cameras remain unchanged.

Next gate: keep cameras fixed and test whether the right-profile lower-face
observations identify a stable anatomical correspondence on the current
surface. A new shape basis must use independently protected rows and bilateral
transfer; it must not recover the rejected camera magnitude, use free 2D
offsets or weaken eye/nose/chin safeguards.
