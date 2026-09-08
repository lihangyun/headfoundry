# Experiment 0019: original-pixel correspondence inspection

Date: 2026-09-08. No baseline replacement; camera gate remains REJECT.

All eleven previously frozen validation tracks were inspected as original-pixel
crops from all three views, not just the largest residuals. Observed positions
were used for crop placement; camera predictions did not move any marker.
The set includes eyebrow hair, eyelid/eye edges, lip texture and weakly textured
skin. One low-error point lies at an iris boundary, so even a small reprojection
error does not establish that it is a rigid skin correspondence. Several larger
errors occur in eyebrow regions where exact strand identity is uncertain.
These observations do not prove the cameras are correct or the photos unusable.

A camera-independent local translation tracker was then tested on all 51
original tracks. Parameters were fixed before the run: 31x31 window, two pyramid
levels, at most 50 iterations, epsilon 0.001, supplied initial match coordinates.
Each frontal/intermediate pair was tracked forward and backward. Acceptance
requires both tracking statuses, at most 6 px displacement from the original
endpoint and at most 1 px roundtrip error. Original observations are preserved.

Only 1/51 tracks passes both pairs: one training track and zero held-out tracks.
The first pair accepts 1/51 and the second 9/51. Large proposed displacements
are rejected, not clipped or silently accepted. A deterministic known-translation
image fixture confirms the same tracker settings recover the supplied 5/3 px
translation within 0.1 px; this is a bounded implementation check only.

No new camera fit uses these failed refinements. This local translation model
does not supply adequate cross-view corrections for this capture; viewpoint,
appearance and feature ambiguity remain possible explanations. It does not
justify deleting difficult validation points or changing the 3 px camera target.
The next image-based check needs to account for local affine distortion and
verify texture support independently of camera residuals. Identifiable crops
and complete per-track measurements remain private and git-ignored.
