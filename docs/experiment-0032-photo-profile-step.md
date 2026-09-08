# Experiment 0032: bounded direct photo-profile constraint

Status: `REJECT` as a usable head; bounded fitting path implemented.

Approximate original-pixel side-profile readings now drive a local shared-mesh
step. The 17 left90 and 16 right90 points trace the forehead/nose/lips/chin region.
They were read with AI assistance, not human verified; estimated uncertainty
5-10 px. They are fitting inputs, not independent validation or scan truth.
Private `profile-shell-v1/contours.json` retains the readings. The green overlay
on the original photos was inspected alongside the actual mesh renders.

The fitter chooses extreme projected vertices within +/-5 vertical pixels of
each contour point. This is a coarse envelope association, not exact continuous
silhouette correspondence. It reuses the existing sparse surface solver with
fixed ray cameras, six neighboring topology rings, regularization 100 and a
0.015 input-unit maximum displacement. All vertices outside the neighborhood
remain fixed. A backtracking check prevents triangle-normal reversal and
triangle area collapsing below 10% of its original value. It does not prove
absence of self-intersection or validate the camera.

Actual step: all 17/16 readings associated; maximum displacement 0.015; global
step fraction 0.1974278. Private driver `fit_shell_profiles.py` rechecks consent,
preserves the original shell and records its hash. Output `candidate.obj` is an
experimental mesh only. `comparison.png` shows original photographs with fitting
curves, unchanged baseline, then candidate at exactly the same source cameras.

Visual inspection: small local profile changes, but severe roughness and wrong
coarse facial/cranial shape persist. No meaningful likeness improvement is
established. These two fitting views are not held-out visual evidence; frontal
and oblique regressions have not been accepted. No baseline is replaced.

54 tests pass, including displacement bounds and unchanged geometry when no
profile rows match. The current coarse head representation needs improvement
before repeated local nose/lip fitting can plausibly meet the requested quality.
