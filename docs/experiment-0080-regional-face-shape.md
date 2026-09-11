# Experiment 0080: regional face controls with coupled camera comparison

Status: both candidates `REJECT` for promotion. No likeness or camera acceptance.

Revisit the existing four pinned CC0 head controls without adding more presets
or moving unobserved bare scalp. Multiply their displacements by smooth
source-space support: frontal image height 450..1010 with 100px transitions,
and front-half depth with a 0.2-template-unit transition. This is an explicit
experimental ROI, not an anatomical segmentation. 1084 source vertices with
zero support remain exactly unchanged; 3375 have positive support, not
necessarily nonzero target displacement.

Both comparisons use identical regional controls, source mesh, frontal and
oblique outlines, both complete profile curves, and the reviewed six non-nasal
anchor supports with far mouth exclusions. Profiles are now fitting data.
The fixed-camera solve is the baseline; the joint solve additionally optimizes
two actual-mesh oblique rotation vectors with component limits +/-0.02rad and
a 0.05rad prior. Camera centers, intrinsics, frontal and profile cameras stay
fixed. Shape weights remain nonnegative and bounded at 0.5. Use two starts
(all shape weights 0.01 and 0.25); both finish successfully in each comparison.

| Diagnostic px | Original source | Regional fixed camera | Regional joint |
| --- | ---: | ---: | ---: |
| First frontal outline MAE | 4.6891 | 3.7207 | 3.5978 |
| Second frontal outline MAE | 7.6932 | 4.1130 | 4.1513 |
| Left-oblique outline MAE | 3.1510 | 2.6966 | 3.0521 |
| Right-oblique outline MAE | 2.3937 | 1.8960 | 1.4116 |
| Non-nasal anchor mean | 5.2265 | 5.3324 | 4.9374 |
| Left profile MAE | 3.6420 | 3.6439 | 3.6430 |
| Right profile MAE | 8.0322 | 8.0320 | 8.0321 |

Joint fitting is not uniformly better: one frontal outline and the left
oblique regress versus the fixed-camera candidate. Central profile changes
remain negligible. Actual five-view photo/source/candidate comparisons were
rendered and inspected for both. Cheek/face outline changes do not resolve
generic eyes, nose, lips or identity. Restricting the controls avoids unsupported
scalp changes but does not provide missing subject-specific central anatomy.

Maximum displacement fixed/joint: 0.048694/0.047324 template units. No reversed
triangles, but minimum area ratios are 0.482868/0.494291, below the conservative
0.5 guard used in recent local surface trials. This target fitter did not
enforce that guard during solving; do not claim these candidates pass it or
weaken the guard to promote them. Coefficient/camera bounds are not active.
All quantities are fitting diagnostics, not independent visual evidence.

Private `face-local-shape-v1` and `face-local-joint-v1` retain separate actual
meshes, matrices, reports and five-view comparisons. Original results were
not overwritten. The regional pipeline reuses existing assets and numerical
functions; no paid/noncommercial models or private external services are used.
Full existing public suite: 78 tests pass. No production API/default changed.

Decision: these four coarse presets are insufficient for the required identity
improvement, even with regional restriction and joint small camera rotations.
Do not repeat this preset sweep. Next requires direct, anatomically reviewed
central-feature shape support and shape-quality constraints, rather than more
outline-only tuning. The full product goal remains unmet.
