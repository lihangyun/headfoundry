# Experiment 0203: full-head similarity and refined surface attachments

Date: 2026-10-13. Alignment `PARTIAL_SUCCESS`; complete-head/default promotion
`REJECT`. Current head and cameras remain unchanged; hair/texture stay paused.

The existing0180 initializer fits only ten semantic pairs, uses30 shape
directions and permits independent horizontal scaling against fixed vertical
and depth scales. That does not preserve a source head's intrinsic proportions.
Start a corrected full-head route with one positive uniform scale, a proper
rigid rotation and translation. Shape and expressions are fixed for this first
screen; no camera parameter changes.

Use the repaired posterior-closure head from0201 and restore the same model's
two neutral eyeballs in *both* comparison meshes. Fresh local observations from
the previously locked MediaPipe task bind model/runtime and each photo hash.
Only front and both30-degree views fit the alignment. The two pure profiles are
excluded: their learned predictions exceed the declared80-degree detector
domain and cannot be treated as valid quality metrics. They are still visually
reviewed. All processing stays local.

Retain eight stable semantic pairs from0180 (chin, nose, eye corners and mouth
corners). Omit its internal-lip points because their row2 source attachments do
not represent the posterior closure. Normalize the rounded sparse source
barycentrics explicitly and report that operation. Bind points to triangles on
the **actual twice-refined exported surface**, rather than blending updated
cage corners while pretending the old triangle survives refinement.

The public `refine_triangle_attachments` helper re-embeds original triangle
charts on the finite subdivided triangles. Its chart corners/inserted centers
have independently tested vertex references, it follows affine transforms,
and it rejects malformed face ids or non-normalized/negative weights. This
finite chart construction is not limit-surface evaluation or proof of physical
anatomical correspondence. On the actual source, it reproduces the previously
rendered geometry and faces exactly, preserves attachment ids, and changes
weights by at most1.12e-16.

First-hit checks keep8/7/7 source-visible pairs in the three fitting views.
All those bindings remain visible after the solve. A no-op recovery control
and exported-triangle affine replay pass. The fit uses a1.066971 uniform scale
and6.2665-degree rigid rotation. Mean errors over all eight diagnostic pairs
change13.512→7.749 px in front,15.174→7.547 in left30 and14.699→7.081 in right30;
the oblique summaries include the one omitted hidden pair each. These are
in-sample/image-group diagnostics, not physical camera or identity validation.

Ten fixed-scene before/after white-mesh renders preserve cameras, material,
exposure and per-view lights. Front placement is closer, and restored eyeballs
make inspection more complete. The stock eye aperture, nose, lip form and jaw
remain different from the references. Registration alone changes no intrinsic
head anatomy, and this candidate is `REJECT` for default/head likeness promotion.

The next candidate uses the same licensed source with coherent whole-head
shape directions and weak frontal contour/eyelid observations. It must pass
actual surface replay, shape/visibility guards and five-view visual review;
position fit is not sufficient. No dimension/weight sweep or unseen commercial
checkpoint follows from this registration result.

The public suite passes107 tests, including the two new meaningful attachment
tests. Local evidence retains the original and helper-integrated driver,
observations, source/eye subsets, transformed meshes and all ten renders.
Neither photos nor identity-derived coordinates are added to Git.
A final audit verifies19 source/script/mesh/render and unchanged head/camera
digests across0203–0204; the public diff passes whitespace checks.
