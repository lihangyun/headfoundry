# Experiment 0182: side-hair support and bun shape

Status: fixed-camera diagnostic `TECHNICAL_CHECK_PASSED`; local silhouette
changes `PARTIAL_SUCCESS`; complete hair, identity and default promotion
`REJECT`.

The experiment-0181 smooth connected hair, head mesh, five cameras, head
colors and photo masks were frozen. Exact 512 px photo/render residual maps
show a large unmodeled sheet behind each ear and down to the nape. A bounded
manually selected image window (not an anatomical mask) still contains
7,611 missing pixels at left90 and 12,537 at right90. Those values are
slightly **better**, not worse, than the previous connected-hair version's
7,989 and 12,721 pixels. The right90 *whole-image* missing-pixel count
increased under experiment 0181; attributing that increase to the nape
window would be incorrect.

A fixed-geometry clay pass preserves render face IDs. It shows that the
patchy ear/neck color mainly comes from photo-projecting poorly observed
skin vertices, while the ear shapes themselves remain generic. More
importantly, missing hair includes both visible head surface and pixels
with no model surface at all. On the exact right90 residual labels,
10,787 of 19,478 missing-hair pixels are over background; on left90,
4,671 of 11,669 are. Recoloring the head cannot add this side-profile
volume. The current cap was clipped above this region; a smooth
displacement of its existing vertices cannot generate the absent
ear-to-nape layer.

One head-following, feathered posterior layer then tested that geometric
hypothesis without moving the original head or hair. It added 1,632
vertices and 3,052 triangles, with 0.06 model-unit maximum offset,
0.570 minimum triangle-area ratio and zero normal reversals. The exact
five-view renders reduced ear-to-nape missing pixels 7,611→4,015 at
left90 and 12,537→7,733 at right90, but increased extra pixels in the
same windows 262→1,839 and 215→966. The ear-clearance windows also
gained false hair. The photo comparison shows a vertical dark neck patch
and worse ear boundaries, not naturally swept hair. This open overlapping
sheet is a diagnostic only and is `REJECT` for visual/default use.

Separately, two bun-only deformations tested whether moving the existing
round bun and connector could solve their visual mismatch. In the second,
7,165 hair vertices behind the scalp changed by at most 0.107 model units;
all 34,753 head vertices, cameras and colors remained identical. Minimum
face-area ratio was 0.883, with no normal reversals. Exact-mesh left90
hair-mask IoU rose 0.640→0.647 and right90 0.634→0.640; front and left30
were unchanged. Yet the five-view photo comparison still showed a ball
on a narrow stalk, not the photographed gathered bun. The first local
variant also regressed right90. Both bun variants are `REJECT`, despite
the second's small numerical gains. Stop local smooth-bun parameter tuning;
the missing structure needs a different gathered-hair representation.

The target photos, mask/error maps, clay views, OBJ candidates and contact
sheets remain ignored local assets; none are in Git or uploaded. All views
were used earlier in the mesh/camera development, so this is not an
independent reconstruction holdout. Camera and whole-head acceptance stay
open.
