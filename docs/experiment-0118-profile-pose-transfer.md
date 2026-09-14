# Experiment 0118: profile pose transfer outside the mouth

## Controlled question

Does fitting profile cameras outside the mouth improve excluded mouth rows on
the unchanged experiment 0117 mesh? Only the two profile camera rotations vary.
Camera centers, intrinsics, other three cameras and all geometry stay fixed.
Per-component rotation bounds are +/-0.02 rad; residual scale is 3 px and
rotation prior scale 0.02 rad. Use ten non-mouth rows per side for fitting,
excluding seven left and six right rows between y=665 and y=805.

Prediction: a useful shared pose correction should transfer to both excluded
mouth regions. Regression on either side prevents promotion. These exclusions
are local to this solve: the shape previously used mouth rows, so this is not
independent camera acceptance or a replacement for the frozen track gate.

## Executed result

Both bounded solves converge without active bounds.

| Profile | Training MAE before/after (px) | Excluded mouth MAE before/after (px) |
| --- | --- | --- |
| Left | 3.7387 / 2.4944 | 6.0280 / 6.2288 |
| Right | 6.8707 / 5.4854 | 4.3802 / 5.5794 |

Rotation vectors in radians are [-0.0013540, 0.0011452, -0.0025061] and
[-0.0018970, 0.0024092, 0.0105834]. These rotate the complete camera-from-world
matrix, preserving camera centers. The unchanged three cameras are copied.

Both excluded regions regress despite improved training scores. Camera
promotion is `REJECT`; keep the previous cameras and failed gate unchanged.
This rejects this pose-only remedy, not every possible camera correction.
The trial does not prove cameras correct or that shape alone is responsible.
Non-mouth original labels also remain uncertain after experiment 0117.

Private `profile-pose-transfer-v1` retains cameras, row residuals and a fixed
shape bilateral render comparison. Source camera SHA-256:
`98a05bf9c94685ac749e958b5ec516546916525baf6f307415996072d5ea7612`.
Source shape SHA-256:
`fbfb86271c5640f2ddf44b7d6f8c74bd21e4e3611d293d462768c61034688945`.

Next use actual cross-view anatomical support to constrain shape rather than
promoting a silhouette-only pose fit. Do not repeat this rotation fit with a
wider bound simply to reduce training error. No texture or expression path is
enabled and no private artifact is published.

Bilateral photo/source/trial renders completed and were inspected. The small
pose changes do not recover the missing lower lip or recognizable identity.
Other three views are unchanged by construction. Full public suite passes
98 tests; `git diff --check` passes. No public implementation changes.
