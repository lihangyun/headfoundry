# Experiment 0149: neutral identity and profile-expression split

Status: solver `TECHNICAL_CHECK_PASSED`; neutral/expression candidate `REJECT`;
expression explanation remains `UNVERIFIED`.

This experiment keeps every camera fixed and separates the rejected 0147
bilateral lower-face direction into one shared neutral-identity scale plus
three bounded, per-profile nuisance modes: jaw hinge rotation, lip protrusion
and vertical lip closure. Nuisance meshes are evaluated only for their source
photograph and are never exported as identity. The interleaved within-photo
fit/transfer split, nose checks and mesh-safety checks are recomputed on the
final dynamic silhouettes.

The first numerical run started the shared scale exactly on its lower bound
and stagnated at zero; it is preserved but excluded as an initialization
failure. The corrected deterministic run converges, drives the shared neutral
scale to its upper bound and improves the left transfer mean from 5.849 to
4.579 px after nuisance adjustment. The right transfer mean still worsens from
4.594 to 5.320 px. The right adjusted mesh also reaches a 0.195 minimum
relative triangle area and reverses 536 triangle normals. Even without the
nuisance modes, the shared neutral candidate worsens the right transfer mean
further to 5.703 px.

The optimizer and measurement path are `TECHNICAL_CHECK_PASSED`, but both the
shared-neutral and photo-adjusted candidates are `REJECT`. The tested physical
expression basis does not explain the bilateral conflict, and topology failure
cannot be waived to obtain a better same-photo fit. No camera, mesh or default
is promoted.

Next gate: test whether one small physical right-profile camera perturbation
can explain the coherent subnasal/lip residual while preserving independent
eye, nose, ear and chin evidence on the unchanged mesh. This is a diagnostic,
not permission to repeat unconstrained silhouette pose fitting. If no feasible
camera perturbation transfers to the protected regions, retain the cameras and
revisit profile correspondence or a better-supported anatomical shape basis.
