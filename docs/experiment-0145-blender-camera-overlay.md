# Experiment 0145: locked-camera Blender photo overlay

Status: Blender camera conversion and replay `TECHNICAL_CHECK_PASSED`; current
full-head visual alignment `REJECT`; no camera or geometry promotion.

This experiment changes only the diagnostic renderer. It imports the unchanged
experiment-0132 OBJ, five world-to-camera matrices, intrinsics and authorized
local photos into Blender 5.2.1 LTS. No camera, vertex, correspondence or source
image is optimized.

`tools/blender_camera_diagnostic.py` converts OpenCV-style x-right/y-down/
z-forward cameras to Blender's x-right/y-up/-z-looking convention, recreates
focal length and principal point, and independently reprojects about 2,045
vertices per view through Blender's camera API. The five p95 discrepancies are
between 0.000049 and 0.000092 px; the maximum is 0.000127 px. Any run above
0.05 px fails before rendering. Source OBJ, camera archive and every photo are
SHA-256 bound in the private report.

Semi-transparent cyan clay overlays make the evidence human-readable. The
frontal facial envelope is broadly coincident, but both 90-degree views expose
large whole-head disagreement around cranial depth, posterior skull/neck and
the cut termination. The nose/lip/chin foreground contour is substantially
closer than the rear head. This explains why selected facial profile rows can
report approximately 3.62/4.92 px while the complete projected head is plainly
not aligned: the local metric never certified the entire head.

The camera conversion is `TECHNICAL_CHECK_PASSED`. The current full-head visual
alignment is `REJECT`; this does not by itself prove whether the remaining cause
is camera pose, hidden-hair skull shape, cut topology or a mixture. The photos
and generated `.blend`/PNG files remain in ignored private storage.

Next gate: partition pure-profile evidence into visible facial foreground,
ear/mandible, hair-occluded cranium and artificial neck-cut regions. Only the
first two may drive image-based fitting. Report complete-head diagnostics
separately, and reserve some visible rows for transfer checks before changing
geometry or camera.

Correction (experiment 0161): the OBJ import retained Blender's default object
axis rotation while this diagnostic used original-OBJ camera coordinates. The
subpixel replay above compared against rotated vertices, so these overlays and
the visual cranial-mismatch interpretation are invalid. Corrected source-frame
overlays in experiment 0161 supersede this visual evidence; do not cite the
original renderer check as proof of source-camera alignment.
