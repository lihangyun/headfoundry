# Experiment 0178: bounded hair silhouette fit

Status: local optimizer and exact-mesh replay `TECHNICAL_CHECK_PASSED`;
selected-view mask overlap `PARTIAL_SUCCESS`; visible hairstyle, identity and
default promotion `REJECT`.

The experiment-0177 connected hair surface, original head, five cameras,
head colors and hair masks were frozen. A private local optimizer used
24,000 hair vertices as a Gaussian-alpha silhouette proxy and varied only
six bounded, smooth crown/rear/bun deformation coefficients. Front, left30,
left90 and right30 masks drove 160 steps; right90 supplied no loss. The
selected deformation moved hair vertices at most 0.0849 model units and
kept a minimum triangle-area ratio of 0.930.

The proxy is not the acceptance renderer: its front IoU *fell* from 0.432
to 0.424 while both pure profiles rose slightly. Exact fixed-camera mesh
renders were therefore repeated at 512 px with unchanged flat hair and
head colors. Hair-mask IoU changed as follows:

| View | Before | After |
|---|---:|---:|
| front | 0.685 | 0.682 |
| left30 | 0.584 | 0.614 |
| left90 | 0.606 | 0.636 |
| right30 | 0.638 | 0.664 |
| right90 | 0.623 | 0.630 |

The private five-row contact sheet places each authorized photo beside the
old and new actual-mesh renders. Visual inspection still shows a featureless
helmet-like crown, a ball-shaped bun and poor ear/nape transitions. The
left-profile mask gain is real for this rendering, but it is not a meaningful
likeness gain. Do not promote or keep tuning this six-parameter family.

Right90 was excluded only from this *latest silhouette loss*. The head,
cameras, connected hair source and earlier bun work had already used all
five photos; right90 is not an independent subject reconstruction test.
Photos, model-derived meshes, masks, renderings and the contact sheet remain
ignored local data and were not uploaded. The camera and visual gates remain
open. Next change shape representation, then demand five-view visual review
with both pure profiles and face/ear occlusion protected.
