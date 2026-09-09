# Experiment 0043: detector-to-template surface correspondence candidate

Status: exact lifting `TECHNICAL_CHECK_PASSED`; anatomical correspondences and
subject reconstruction `UNVERIFIED`. No mesh deformation or baseline promotion.

The pinned local MediaPipe face detector was run on the actual native smooth
clay render from the current experimental head. This explores a route to dense
anatomical template correspondences without a restricted morphable model or
training data. It is not evidence that the detector is unbiased on synthetic
clay. No generated imagery, texture or external service was involved.

The detector finds one face. The first coarse pixel-buffer probe hit geometry
for 465/468 face points. Its original clay/overlay image was inspected: coverage
is available around eyes/nose/mouth, but a few contour points fall outside the
mesh. The pixel-buffer count alone is not a valid continuous correspondence.

## Exact surface lifting

The existing renderer module now provides `lift_pixels`: intersect the precise
continuous image coordinate with projected triangles, choose the closest
positive-depth surface, and return perspective-correct 3D barycentric weights.
Misses remain explicit -1/NaN; they are never snapped to the nearest face.
This changes no geometry and makes no assumption about semantic point identity.

Actual result: 464 valid intersections. Four misses (58,132,136,172) are retained
explicitly in the output mask. Maximum lift/reprojection round-trip error is
1.14e-13 pixels. This proves coordinate conversion only, not anatomical accuracy.
The 465-vs-464 difference reflects pixel-center versus continuous-coordinate
coverage; no invalid point is hidden to inflate the count.

Against the eight previously selected approximate template anchors, detector
positions differ by 0.91–5.53 pixels at 600px render width. Those anchors also
have reading/discretization uncertainty. This is insufficient to accept all
464 points as ground-truth correspondences, especially around contours/eyelids.

Private artifacts:
- `clay-landmark-probe-v1`: native render, inspected detector overlay and output.
- `clay-landmark-lift-v1`: correspondence NPZ with masks/weights/triangle IDs,
  and numerical report. No person geometry or observations are committed.

Mesh digest: `1d9b0a35f29f504af50343e3f52a3efca4eeec29a4662cf668ebc5459901a6be`.
Detector digest: `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`.
Detector report digest:
`2aa242750a48e2456ca1ce467b24febf149e809c9acbdbd7f752ed2057620634`.
Private runners check source consent and relevant asset hashes before use.
The detector runner needs repository `src` on PYTHONPATH in its isolated runtime.

64 tests pass, including perspective-weight recovery, exact projection,
nearest-surface occlusion and explicit misses. Next evaluate a bounded shared
surface fit using only supported anatomical points, excluding ambiguous contour
semantics and protecting independently observed profile evidence. Camera,
identity, eyes, ears, UV/texture and finished-product gates remain incomplete.
