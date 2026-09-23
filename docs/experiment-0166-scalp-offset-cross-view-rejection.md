# Experiment 0166: scalp-surface offset versus five views

Status: local mesh/render path `TECHNICAL_CHECK_PASSED`; both scalar scalp
deformations and default promotion `REJECT`.

The unchanged experiment-0132 mesh has 34,753 vertices and 69,320 faces.
Instead of adding another mask-carved solid, this experiment smoothly moves
422 existing upper-scalp vertices, leaving the lower face and camera matrices
fixed. The weight tapers to zero at a higher frontal hairline and lower rear
scalp boundary. Two otherwise identical local candidates move the same
vertices by at most 0.25 model units, first along each surface normal and
then vertically upward. Both remain finite, preserve face topology, have no
normal reversals and a minimum relative triangle area approximately 1.0.
Exact-camera Blender replay is below 0.0001 px p95 in all five views.

The normal-offset candidate closes the missing frontal crown volume but
balloons above the photographed crown in both pure profiles. Restricting the
same movement to the vertical direction narrows the frontal shape, yet still
overshoots the side crowns and leaves the subject's bun absent. The local
five-view photo overlays make both failures obvious. Neither is an acceptable
hairstyle or a verified subject likeness.

An independent projection check explains why one scalar crown lift is a poor
fit: the baseline mesh's minimum projected vertex rows are 162/68/98 px in
front/left90/right90. The thresholded dark-hair masks have earliest rows
78/75/52 px, and first-percentile rows 95/95/77 px. Mask rows include hair
and loose strands, whereas mesh rows are bare scalp; they are not equivalent
anatomical correspondences. Nonetheless the required change is different
across views, while a uniform crown lift worsens the already-high left side.
This does **not** isolate camera error from hair shape or mask uncertainty;
the cameras are still unaccepted. It rejects only this one-parameter scalp
representation under the current cameras.

Both private candidate meshes, reports and exact five-view renders remain
ignored local artifacts. No photographs or derived biometric geometry are
committed. Next make crown/hairline evidence explicit and test a shaped scalp
surface jointly against all five views, with independent facial landmarks
protecting camera changes. Do not promote a crown adjustment from one view.
