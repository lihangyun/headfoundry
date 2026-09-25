# Experiment 0188: front/oblique-to-profile head recovery on fixed 3D

Status: deterministic CC0 synthetic run `TECHNICAL_CHECK_PASSED`;
tested contour-only shape-recovery route `REJECT`; real-image head quality
`UNVERIFIED`.

The five user references are independently generated/composited, so a held
reference image is not guaranteed to come from the same rigid head. This
experiment instead tests whether the existing local silhouette-fitting
primitive can recover *known*, fixed 3D head shape under easier conditions.
It uses the already generated 256-identity, same-topology CC0 MakeHuman set
from experiment 0156 and the 12 indices preselected by that contact sheet:
0, 23, 46, 69, 92, 115, 139, 162, 185, 208, 231 and 255. The input
archive hash is in the ignored local report; its generator report and the
public MakeHuman target lock establish the CC0 source chain.

Each case starts from the common template. Its training input is only
rendered masks at front and +/-30 degrees with fixed known cameras; the
current `fit_profile_step` first adjusts the frontal contours, then adjusts
both oblique contours along front-camera rays. The +/-90-degree images,
true vertices and generating coefficients are withheld from fitting and
used only for evaluation. No texture, hair, paid model or subject photograph
is involved. The render is 220 x 220 px, so subpixel differences are subject
to strong mask quantization. This is an in-family algorithm test, not a
real-world generalization or identity benchmark.

Across the 12 preselected heads, only one satisfies the predeclared joint
criterion of lower *both-side* leading-face-edge error, lower 3D vertex
RMSE and safe geometry. Even that case changes 3D RMSE only
0.029321403→0.029319826 in normalized head units. Two cases improve both
side-edge means; four improve 3D RMSE. Mean side-edge errors at -90/+90
change 0.6140→0.5921 and 0.6140→0.6009 px, while mean 3D RMSE worsens
0.010677→0.010746. Mean *training* front-mask IoU also worsens
0.98622→0.98514. Eleven candidates meet the declared source-mesh safety
checks; sample 255 falls below the 0.35 relative-area floor (0.2896).
Sample 0 demonstrates the trap directly: both held side mask IoUs improve,
yet 3D RMSE worsens 0.003195→0.003424.

The route is `REJECT` as a dependable head-shape initializer even on these
controlled, in-family fixed-3D examples. Do not promote it because one
2D summary improves by a fraction of a pixel. This test does **not** prove
that every silhouette method fails, nor that the synthetic identities cover
real anatomy or the independently composed subject views. A future head-only
candidate needs a coherent 3D shape prior/constraints and must first improve
bilateral *held* profiles, 3D error and mesh safety on this fixed-geometry
benchmark, then separately pass actual five-view visual inspection. The
current head remains unchanged; KeenTools-level quality is `UNVERIFIED`.

Private runner, full per-case metrics and rendered truth/template/candidate
comparisons stay in ignored `assets/private/synthetic-head-benchmark-v1/`.
