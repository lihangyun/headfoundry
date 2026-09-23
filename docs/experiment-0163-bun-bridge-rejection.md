# Experiment 0163: convex bun bridge rejection

Status: controlled geometry/render `TECHNICAL_CHECK_PASSED`; bridge geometry
and visual promotion `REJECT`.

This follows the isolated ellipsoid in experiment 0162. The unchanged head,
cameras, photos and rendering setup are used again. The only change is one
continuous **convex** bun-to-rear-scalp volume formed from overlapping bun and
connector ellipsoids. The resulting component has 686 vertices and 1,368
triangles; it intersects the head but is not a watertight union with it.

Within the same bounded dark-hair regions, the full candidate mask's IoU rises
from 0.610/0.552 to 0.709/0.788 left/right. That number is misleading as a
quality score: corrected 30- and 90-degree Blender photo overlays show a long,
nearly horizontal tube projecting from the back of the head, unlike the
subject's swept and gathered hair. The region mask includes broad dark scalp
hair, so filling it with a convex bar improves overlap while harming the human
visible hairstyle. No face geometry or camera was changed.

The convex bridge is `REJECT` despite its higher mask IoU. Do not promote it,
retune its ellipsoid sizes for that same region score, or interpret area overlap
as full-head likeness. A later hair route needs a nonconvex scalp surface,
explicit crown/hairline and gathered connection, plus held views and curvature
or contour checks in addition to regional overlap. Both private candidates and
their five-view renders remain preserved locally; no photos or derived meshes
are committed.
