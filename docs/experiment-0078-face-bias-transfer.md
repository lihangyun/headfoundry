# Experiment 0078: cross-face transfer and small relative rotations

Status: shared nasal bias `REJECT` as a global camera correction. Relative
rotation candidate `UNVERIFIED` as a joint-initialization diagnostic and
`REJECT` as a standalone replacement for the current mesh's cameras.

## Shared vertical bias fails outside the nose

Apply 0077's six-alar-only biases unchanged to four canthi and two mouth
corners. Exclude the previously occluded far mouth corners; use the reviewed
candidate canthus support for fixed-mesh checks. No shape, camera or observation
is saved over the source. These non-nasal points did not estimate the biases,
but were used in prior development, so they are not pristine calibration data.

| Original-camera diagnostic | Unchanged | Nasal bias |
| --- | ---: | ---: |
| Left-oblique fixed-support mean px | 3.9506 | 9.5183 |
| Right-oblique fixed-support mean px | 6.6334 | 8.4851 |
| Free non-nasal point mean px | 1.8348 | 4.3030 |

With canthus-contour cameras, left/right fixed-support means likewise worsen
3.2547/5.5547 to 9.5209/7.4448px; free-point mean 1.6054 to 3.8991px.
Fitting only oblique canthus observations also worsens frontal predictions.
Thus a uniform image translation inferred from the nose does not generalize.
Do not relabel it as a proven crop or principal-point error.

## Small relative-rotation diagnostic

Fit twelve shared free 3D points (four canthi, eligible mouth corners and six
alar points), together with two oblique camera rotation offsets. Keep camera
centers, intrinsics, frontal camera and both profile cameras fixed. Exclude
nasal IDs 4 and 2 entirely from this solve. Rotation-vector components are
bounded to +/-0.05rad and regularized at scale 0.05rad; observation components
use supplied 5px scales. This introduces no new learned component.

Left/right offsets are [0.002456,-0.016083,-0.016503] and
[0.002826,0.014637,0.019581] radians. No active bounds. Free-point mean
decreases 2.6990 to 1.9169px. For each excluded midline point, fit its 3D
position from the two oblique observations and predict the frontal observation:
ID 4 error decreases 16.2707 to 11.0112px; ID 2, 10.9251 to 5.6345px.
These checks remain inadequate for camera acceptance, especially the tip.

Crucially, the free points are not a valid reconstructed head. Apply these
cameras to the unchanged current mesh and the non-nasal fixed-support means
degrade from 3.9506/6.6334 to 32.0041/29.6433px in the two obliques. Actual
photo/original-camera/candidate-camera clay views were rendered and inspected;
the visible displacement confirms the regression. The frontal image is
unchanged. A better free-point objective is not a drop-in camera correction.

Next any use of this initializer requires a jointly constrained head/camera
fit, not independent promotion of the rotations. Shape regularity and all-view
photo alignment must be checked together. Preserve the existing cameras and
all failed alternatives; no camera gate, likeness or product claim is made.

Private `nasal-bias-transfer-v1` records every per-anchor comparison.
`face-ray-pose-v1` records real matrices, masks, source hashes, excluded-midline
checks, fixed-shape audit and actual image comparison. No private data or
camera candidate is committed; existing public APIs/defaults are unchanged.
