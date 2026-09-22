# Experiment 0153: anatomically layered lower face

Status: solver `TECHNICAL_CHECK_PASSED`; numerical candidate
`PARTIAL_SUCCESS`; visual/default promotion `REJECT`.

This experiment keeps every camera and all non-lower-face geometry fixed. It
replaces the broad mouth field with six smooth depth modes centered on upper
lip, lip seam, lower lip, labiomental groove, chin and jaw. Pure-profile rows
drive the fit; interleaved profile rows, both 35-degree outlines, frontal
outlines, individual eyes, nose and mesh safety remain evaluation constraints.

The original strict policy selects zero because the smallest step improves
almost every measure but worsens the right held mean by 0.010 px. That result
is preserved locally. A second, explicitly experimental policy permits at most
0.05 px single-side held regression only when both training means, the combined
held mean and both oblique outlines improve. It selects scale 0.20.

At that scale, left/right training means change from 3.113/4.934 to
3.062/4.675 px. Held means change from 5.849/4.594 to 5.582/4.634 px, so their
sum improves while the right side regresses 0.039 px. Corresponding oblique
outline means improve from 2.654/1.233 to 2.421/1.098 px. Maximum displacement
is 0.00371 model units, minimum relative triangle area is 0.953 and there are
no normal reversals.

The deterministic solve and safety checks are `TECHNICAL_CHECK_PASSED`, and
the balanced numerical candidate is `PARTIAL_SUCCESS`. Exact Blender camera
overlays and five-view clay comparison show no confidently visible identity
improvement at this amplitude. Therefore visual and default promotion remain
`REJECT`; experiment-0132 stays the reference geometry.

Next gate: stop tuning small local depth fields on the current generic mesh.
The next representation must provide broader, coherent subject-identity
capacity across forehead, midface, jaw and cranium while preserving the fixed
camera evidence and exact Blender overlay review. A fit metric without visible
five-view improvement is insufficient.
