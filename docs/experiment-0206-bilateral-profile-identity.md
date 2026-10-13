# Experiment 0206: frozen-pose bilateral profile identity fit

Date: 2026-10-13. Head only; current defaults remain unchanged.

Experiment0205 produces a coherent head but fails nasal/lip/chin profile
likeness. Add bilateral skin/background profile envelopes to that same
first30-direction identity fit. Freeze all7 scale/pose values from its corrected
replay archive exactly. Keep the repaired source closure, shape prior2.5,
coefficient box[-2,2], total shape-motion cap0.06, minimum cage/exported area0.5,
normal orientation checks and three-view visible aperture/jaw constraints.
No new learned model, expression, hair or texture is introduced.

## Frozen observations and source support

Read the locally authorized pure-profile photos before this refit. Explicit
RGB skin/background separation, a3-pixel median filter and fixed search windows
provide appearance-edge samples from nasal bridge through chin. Visual review
on the source images confirms both traces follow the declared boundaries;
window-boundary hit count is zero. This is a local observation method, not a
general segmentation product or scan truth. Left/right have38/41 fit rows and
38/40 alternating evaluation rows. Prior heads/cameras and visual reviews have
already seen these photos, so evaluation rows are only local refit diagnostics.

A first support screen rejects the source nose/lip/chin region mask: its right
profile stops at y863.857, before the last supplied y868 row. Adding two source
face rings does not resolve this boundary. Both failed preparations are retained;
no optimization or candidate promotion follows and no observed row is discarded.
Region names do not define the visible chin-to-neck contour.

Instead use the complete bare-head skin envelope in the audited row band.
Exclude triangles only when a projection bound derived from the unchanged total
motion cap proves them row-disjoint. The source subdivision map is convex and
affine, so refined vertices cannot exceed the cage displacement cap. Full-mesh
first-hit rays remain mandatory. The third screen covers all fit/evaluation rows
and verifies their actual visibility. Initial mean absolute errors are10.925/
9.772 pixels on fit rows and14.010/9.218 on evaluation rows, left/right. Large
terminal errors expose the source chin ending above the photo contour; they are
not hidden by dropping rows or by counting a source region's nearest interior
point as the profile.

The existing single-row perspective-correct envelope operation is batched with
one mesh projection. Its scalar entry point delegates to the same computation.
Tests independently check projected segment positions, depth-correct weights,
horizontal edges, misses, both directions and invalid row arrays. The full
regression suite passes109 tests before subject fitting. This is bounded
`TECHNICAL_CHECK_PASSED`, not a subject-head acceptance result.

## Required result evidence

The refit must satisfy the same exported mesh and actual-visible-support gates,
retain the exact frozen pose/cameras, and produce all five fixed-scene white
renders. Inspect source/previous/new controls together, including both pure
profiles and mouth-to-chin sections. Numeric edge improvements do not establish
coherent lip relief, likeness, physical camera accuracy or KeenTools parity.
Keep the goal active and defaults unchanged unless complete evidence permits
promotion. Do not return to the rejected image-space donor-depth transfer family.

## Results (2026-10-14)

The local refit completed with all seven camera/scale pose values frozen. The
bounded optimizer terminated successfully; the exported OBJ moved no vertex
more than 0.05998 (cap 0.06), retained a minimum face-area ratio 0.5622 (gate 0.5),
and had zero normal reversals. The independently written full-head audit
returns `TECHNICAL_CHECK_PASSED`: it reprojects all profile rows against every
exported head triangle, confirms fitted supports are first-hit visible, and
checks the actual exported topology. Maximum support depth disagreement is
below 6e-13 model units. Blender 5.2.1 imported the OBJ with at most 1.2e-7 model
unit coordinate error and rendered front, ±30°, and both pure profiles in the
unchanged fixed clay scene; the worst camera replay error is 0.000141 px.

The training-row mean absolute profile error changes left/right from 10.925/9.772
to 3.649/3.924 px; alternating diagnostic rows change 14.010/9.218 to 3.984/3.639
px. The full-head audit independently measures 301/321 sampled rows at 3.766/3.735
px mean and 11.058/10.775 px p95. These values support only a local contour-fit
`PARTIAL_SUCCESS`: rows are not a subject holdout, and the photos were generated
or composited independently rather than captured from one known rigid scene.

The fixed-crop reference/current/candidate sheet and a magnified mouth/profile
sheet were inspected. Both side contours change in the intended direction, but
the white candidate still has visibly generic whole-face proportions and a
mouth/chin shape that does not match the references. Visual likeness and default
promotion are `REJECT`; renderer/fitter status remains `UNVERIFIED` for identity.
The current head and camera are unchanged; no hair, texture, training, or new
model asset was introduced. The final public regression suite passes 110 tests.

Local-only evidence is under `assets/private/subject-001/whole-head-profile-fit-v2/`:
`independent-audit.json`, `fixed-scene/`, `final-review-reviewed/`, and
`mouth-review-reviewed/`.
The image-derived assets remain ignored by Git. Next gate: seek a coupled
front-and-profile facial-anatomy improvement that preserves the side contour;
do not treat another row-only reduction as likeness evidence.
