# Experiment 0154: analytic macro identity modes

Status: solver `TECHNICAL_CHECK_PASSED`; shared and side-separated geometry
`REJECT`.

This experiment keeps every camera fixed and replaces local mouth tuning with
eight coherent analytic modes: forehead, midface and lower-face depth; face,
cheek and jaw width; chin height; and lower-face taper. The first run shares
these modes bilaterally. The second run gives the two visible hemispheres
independent coefficients with no symmetry penalty, while retaining separate
35-degree outline, frontal outline, eye, profile-transfer and mesh-safety
checks.

Both bounded optimizers converge. In the shared run, the smallest step improves
the right training profile and both oblique outlines, but worsens the left
training and held profile. The side-separated run shows the same conflict even
after the symmetry coupling is removed: at scale 0.05 the left train/held means
worsen from 2.535/4.247 to 2.545/4.278 px while the right train improves from
4.450 to 4.393 px; right held also worsens to 4.403 px. No nonzero scale meets
the balanced profile and protection policy, so zero is retained in both runs.

Execution and evaluation are `TECHNICAL_CHECK_PASSED`; all macro geometry and
visual/default promotion are `REJECT`. More coefficients in the same
hand-authored depth/width family do not produce a consistent three-dimensional
identity explanation. The result does not prove the cameras or observations
are correct, but it falsifies the tested analytic representation as the next
quality step.

Next gate: stop adding hand-authored scalar modes. Use a coherent nonlinear
three-dimensional identity prior with known commercial rights, or train an
independent prior from controlled synthetic 3D heads. The first validation is
not training loss: it must beat experiment 0132 on bilateral held profiles,
both oblique outlines and exact five-view Blender overlays without weakening
eye, camera or mesh safeguards.
