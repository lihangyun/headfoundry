# Experiment 0186: head-only visual baseline after source correction

Status: local rights replay and exact-camera rendering
`TECHNICAL_CHECK_PASSED`; previously added generic eye-surface completeness
`PARTIAL_SUCCESS`; current complete head likeness/default use `REJECT`;
physical camera and real-subject identity `UNVERIFIED`.

The user paused hair work and clarified that the five authorized references
were generated or composited independently. Thus front is the primary visual
anchor and the two oblique and two pure-profile images are separate, softer
shape references. They cannot form an independent real-capture holdout or
prove that one rigid head/camera system generated all pixels. The current
head and all five experimental cameras were left unchanged.

For a concrete hair-free baseline, the already documented experiment-0139
CC0 eye-helper candidate was replayed through the exact-camera Blender
renderer at 1254 x 1254 in all five views. The original head's 34,753
vertices are unchanged; only the two separate, closed generic eye surfaces
are present. Local input rights/hashes validate. The OBJ import maximum
coordinate error is 5.96e-8 model units; the worst per-view Blender-versus-
matrix projection maximum is 0.000116 px. These numbers establish rendering
alignment, **not** camera truth, likeness or anatomy. The SHA-locked
`head-only-eye-camera-v1/report.json`, five clay renders and five photo
overlays remain under the ignored local subject directory.

Directly inspecting the front and both pure-profile clay/overlays shows a
coherent but visibly generic bare head. The eye holes are covered, but eye
contact and gaze are generic. The lip-to-chin relief is stiff, and the lower
neck ends at an obvious cut. The side nasal outline is comparatively close.
The *direction* of frontal jaw-width error is not established by this visual
sheet: the outer skin-color boundary at lower rows includes visible neck and
is not interchangeable with the facial jaw contour. Existing MediaPipe jaw
points are fitting evidence with different semantics from a rendered outer
envelope. A width change needs a targeted comparison before selection.
Hair silhouette, hairline and garment are excluded from this head-only
comparison. Previous experiments 0146–0154 document conflicting bilateral
mouth/chin responses and rejected low-amplitude local fields; 0157 and 0180
reject the tested broader target/GNM fits. None should be silently promoted
because the new source classification changes interpretation, not geometry.

Next trial: seek one visible, anatomically coherent **head** change under
the fixed experimental cameras, with the front lower-face shape as primary
visual evidence and both side profiles reported separately as soft checks.
Protect nose/eyes/ears and mesh safety, then compare source image, unchanged
head and candidate in all five exact-camera renders. Reject a prettier single
view if another view or anatomy visibly worsens. Do not count fitted-profile
pixels as independent ground truth or claim KeenTools-level quality.
