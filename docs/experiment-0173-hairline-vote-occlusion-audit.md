# Experiment 0173: why hair-mask votes cannot label the bare scalp

Status: fixed-input visibility audit `TECHNICAL_CHECK_PASSED`; direct
five-view hair/skin label fusion on the current bare head `REJECT`;
anatomical hairline and whole-head shape `UNVERIFIED`.

This read-only local test keeps the experiment-0132 head/cameras and all five
consented photos unchanged. The existing dark-hair masks are eroded by seven
pixels at half resolution so boundary pixels are not called confident. Each
bare-head vertex is projected under the locked cameras and counted only when
it passes the existing z-buffer visibility check. Original photos, masks,
per-vertex votes and reports remain ignored local data.

Of 9,364 examined upper-head/face vertices, 5,429 have confident labels in
at least two views. Hair and skin labels contradict at 1,228 (22.6%). The
naive front-surface disagreement is only 118/3,458 (3.4%), but that number
is diluted by vertices always labelled skin. Among the 267 front-surface
vertices with at least one confident **hair** vote, 118 (44.2%) also receive
a confident skin vote. On the rear surface, the analogous figures are
1,110/1,597 (69.5%). The lower Y band contributes 1,043/1,107 (94.2%)
conflicts among multi-view hair-evidence vertices. For example, the
front/right30 shared confident region disagrees at 478/3,376 vertices, and
right30/right90 at 676/2,475.

These are disagreements in *projected image labels on a bare head*, not
verified same-material hair correspondences. A hair layer can occlude that
bare surface from one view while another view sees skin; model and camera
errors can also contribute. The result therefore neither proves the masks
wrong nor diagnoses a camera error. It does reject simple majority/averaged
hair-mask voting as the scalp boundary for the next mesh: an aggregate score
dominated by skin would conceal exactly the hairline conflict that matters.

The next geometry hypothesis must treat the observed front/side hairlines
as view-dependent occluding contours, separate from rear/bun volume and
from same-surface correspondence. It needs explicit cross-view silhouette
protection and real five-view visual review; no mesh or camera was promoted.
