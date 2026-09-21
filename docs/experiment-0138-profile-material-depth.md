# Experiment 0138: guarded profile-material depth step

Status: numerical replay `TECHNICAL_CHECK_PASSED`; candidate promotion
`REJECT`. Camera, identity and visual acceptance remain `UNVERIFIED`.

Keep the experiment-0132 cameras, head topology and six compact frontal-ray
depth fields fixed. Add only the six-left/seven-right reviewed material points
from experiment 0137 to the objective and require every prior outline, bilateral
profile, eye, oblique-central and material-point aggregate not to regress. The
maximum additional movement is 0.015 template units and the existing triangle
area/normal safeguards remain unchanged.

The constrained optimizer terminates unsuccessfully with `Positive directional
derivative for linesearch`. Preserve that failure. A deterministic 201-step
scan of its returned direction nevertheless contains a feasible small step at
scale 0.995:

| Diagnostic | Experiment 0132 | Feasible step |
| --- | ---: | ---: |
| Left material-point mean px | 9.008708 | 8.639912 |
| Right material-point mean px | 10.240803 | 10.240754 |
| Left profile mean px | 3.623644 | 3.623540 |
| Right profile mean px | 4.923310 | 4.923310 |
| Left30 central mean px | 8.895530 | 8.875255 |
| Right30 central mean px | 5.084762 | 5.084673 |

Maximum displacement is 0.003659, minimum relative triangle area is 0.985015,
and there are no relative normal reversals. All eye and outer-outline values are
unchanged to numerical precision.

Native-resolution bilateral nose/lip crops and the five-view sheet were
inspected. The change is effectively imperceptible and does not correct the
generic/angular lip or establish better likeness. The full-profile targets are
also provisional fitting evidence, not independent truth. Therefore the safe
nonzero step is retained only as a diagnostic and rejected for baseline
promotion. The six compact depth fields have reached a practical visible-effect
limit under the current protections; do not spend another iteration retuning
their weights.

Private output `profile-material-depth-v1` retains the meshes, cameras, complete
scan, solver failure and inspected comparisons. Authorized photographs and all
identity-derived artifacts remain local and ignored.
