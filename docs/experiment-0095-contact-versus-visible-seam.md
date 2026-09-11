# Experiment 0095: contact proximity versus visible seam

Status: `UNVERIFIED`; no deformation or anatomical promotion.

Extend the lateral section inventory to +/-0.35 template units. Two cropped
paths persist through +/-0.20, change markedly near +/-0.25 (8 and 37/38 points),
and become one near +/-0.30. This does not uniquely locate anatomical corners:
the explicit crop also changes connectivity. Do not blindly extrapolate the
central two-path rule.

On the thirteen existing central sections, compute closest pairs between the
two piecewise-linear paths. For each segment pair evaluate the interior least
squares solution when feasible and all four boundary projections, then select
the shortest. Preserve triangle barycentric support by locating the original
segment corresponding to each ordered path edge. This replaces separate
vertical extrema only; mesh and cameras remain unchanged.

The resulting vertical separations range 0.006090..0.012858 template units.
Only 11/7/2 of the 26 samples are visible in front/left/right oblique views.
Inspected actual overlays place most candidates behind the visible seam.
Nearest contact candidates therefore must not be fed into visible-image
landmark fitting. Conversely, hidden contact surfaces are not invalid merely
because they cannot be seen. Proximity alone does not establish anatomical
contact labels or collision freedom.

Next keep contact-surface constraints separate from apparent seam observations,
with a changing visibility mask during deformation. The corner transition still
requires explicit review. Private `lip-nearest-pairs-v1` retains supported pairs,
ray checks and inspected overlays; no public production code changed. Checks
include actual section inventory, bounded segment-distance candidates, positive
upper/lower ordering and real rendering. No likeness improvement is claimed.
