# Experiment 0114: photo-guided neutral closed-mouth patch

Initial decision: `UNVERIFIED`, not a baseline replacement. Repeated authored
closure, pair attraction and height-gap compression failed natural closure or
produced intersections. This experiment changes local surface topology rather
than increasing those deformations. It does not claim a general expression rig.

## Scope and protocol

Primary variable: replace the existing mouth/near-mouth surface with a closed
disk, constrained by frontal photo lip curves and bilateral profile evidence.
Source is experiment 0112's level-1 mesh; all cameras, photographs and retained
head vertices remain unchanged. No texture, model inference or new asset.

Select a bounded frontal elliptical region on the front of the head. A
read-only connectivity check shows two components remain after removing it:
the main exterior head and a smaller internal cavity. Remove the isolated
cavity in the experimental copy, not the source. Recover the mouth boundary
with winding opposite the retained faces. The original neck opening remains.
This explicitly sacrifices the old oral-cavity representation and provides no
teeth, mouth-opening or expression capability; do not silently promote it into
an editable full-face product contract.

The actual projected boundary is not strictly star-shaped. A direct radial
construction rejects it; harmonic mapping of a radial grid also produces
negative projected triangle areas. Both failed preparations stop before export.
Use an independently implemented simple-polygon ear triangulation and conforming
interior-edge refinement instead. Preserve every supplied boundary edge and
vertex; reject crossing/touching polygons. Long boundary edges impose a local
sampling floor rather than being split without modifying the retained mesh.

Interpolate boundary camera-depth values harmonically over the resulting disk.
Existing frontal upper/lower lip detections and the experiment 0100 photo-seam
curve define two lip-relief regions. The [official MediaPipe lip connectivity](https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/python/solutions/face_mesh_connections.py)
is used only to interpret the already-local landmark indices, not as new
anatomical ground truth. Fit three bounded depth coefficients (broad mouth,
upper lip, lower lip) to the unchanged bilateral profile rows with a prior.
Interior points follow fixed frontal rays; the stitched boundary stays exact.

Prediction: a continuous closed neutral mouth avoids the old open shelf while
retaining natural visible lip relief and better side shape. Falsify promotion
on generic/flattened/pinched anatomy, profile regression, invalid boundary or
folding. Inspect actual original-photo/source/initial/fitted full five-view and
mouth comparisons. Topology closure is not a collision or likeness certificate;
old triangle-ID attachments cannot be reused.

## Execution continuity

The first fitting/rendering job left source and initial OBJ exports but no
complete report or comparison. Its process handle was missing and no matching
process remained on 2026-09-14. The partial files were preserved. A new local
run uses a separate output directory, writes the fit summary before rendering,
and captures its output to a local log. It is not a parallel duplicate and does
not overwrite the partial run or source.

## Completed uniform-graph result (2026-09-14)

Promotion: `REJECT`. The new patch is connected and closed, but actual enlarged
views show prominent surface striping and unnatural lip shape. Closing a disk
has not produced an acceptable reconstruction.

The cut removes 4,528 triangles and the disconnected internal cavity contains
2,057 more. The 101-vertex outer boundary is stitched exactly; all retained
head vertices are bit-identical. The resulting head has 34,753 vertices and
69,320 triangles. Every edge has one or two incident faces; the only 184
one-sided edges are on the original neck opening. This is limited topology
evidence, not exhaustive 3D collision/anatomy validation.

| Variant | Left profile MAE px | Right profile MAE px |
| --- | ---: | ---: |
| Unchanged smooth source | 4.7725 | 7.0207 |
| Initial closed patch | 9.4634 | 9.4565 |
| Profile-fitted patch | 5.3180 | 7.4700 |

The three-parameter solve converges, with the lower-lip relief at its zero
bound. Both profiles still regress against the source. These are reused
fitting observations, not held-out quality evidence. The independent camera
gate remains failed.

Private `closed-lip-patch-v2` preserves all three actual exports, complete
five-view/mouth comparisons, patch data and report SHA-256
`58e6e61a4aef0c998a7a4c7dd46430c4c7fc1aae8d59a01a392995be8f168adb`.
No private inputs or identity-derived files are committed.

Next isolate the interpolation defect: the irregular triangulation receives
uniform graph-Laplacian depth weights, which do not reproduce even an affine
depth field on an irregular mesh. A frontal crop audit finds all 16,000 pixels
belong to the new patch, with zero old-head or background hits; old/new surface
overlap is not responsible for stripes in that crop. Test metric-aware finite
element interpolation while retaining the same topology and fitting setup.
