# Experiment 0187: one-factor chin-width ablation

Status: locked CC0 transfer, mesh safety and exact-camera replay
`TECHNICAL_CHECK_PASSED`; head-shape/default candidate `REJECT`.

Experiment 0186's initial visual impression that the frontal lower face was
too narrow was checked before changing the model. The photo's broad lower
skin-color region includes neck and is not a jaw contour. Existing MediaPipe
oval points suggest a different width direction, although they too are
same-image fitting evidence rather than independent truth. To resolve the
sign question cheaply, this experiment ablates only the chin-width-decrease
control already present in the current head; it does not fit another target
or change cameras, eyes, mouth, hair, texture or lighting.

The single source is the reviewed CC0 MakeHuman
`chin-width-decr.target`, locked by SHA-256 in
`examples/makehuman-central-face-lock.json`. Its displacement is transferred
through the established source-index, one-step subdivision and harmonic-patch
mapping onto the current 34,753-vertex head. The previous 0.201013
coefficient is removed at predeclared fractions 0, 0.25, 0.5, 0.75 and 1.
The unchanged generic eye components are included only for exact-camera
visual display. At full removal, maximum head-vertex displacement is 0.00969
model units, minimum relative triangle area 0.9750, no triangle reverses,
and the region above frontal y=700 is exactly unchanged.

On the already-used frontal jaw readings, left/right mean absolute errors
move from 6.4246/8.0802 px to 6.4533/8.0903 px: both get slightly worse.
On the already-used pure-profile traces, left changes 3.6236→3.6279 px
(slightly worse), right 4.9233→4.8802 px (slightly better). These tiny,
opposing changes are diagnostics only. Direct source-photo/current/full-
ablation clay overlays in front and both pure profiles show no confident
visible head-likeness improvement. The candidate is `REJECT`; the current
head remains unchanged. Do not reverse the existing chin control or treat
skin/neck segmentation as a jaw target.

The fixed five references were generated or composited independently, so
these scores do not validate one physical head or camera. Private script,
candidate OBJ, exact five-view renders and report remain under ignored
`assets/private/subject-001/chin-width-ablation-v1/`; no input or biometric
derivative enters Git. The next head-only shape route needs evidence for an
anatomically meaningful factor, not another width scalar chosen from an
ambiguous silhouette.
