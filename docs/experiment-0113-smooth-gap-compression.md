# Experiment 0113: gap compression on the evaluated smooth surface

Initial status: `UNVERIFIED`. Target: a naturally closed lip seam in actual
frontal, oblique and bilateral profile views, without intersections. The
previous turn established that simple post-fit subdivision removes facets but
does not close the lips. Old triangle-ID attachments are not transferred.

One primary variable: the amount (0, 0.5, 0.9) of a monotone vertical gap map
on the fixed level-1 surface from experiment 0112. Cameras, topology, photos,
profile observations and all x/z coordinates stay fixed. No mouthClose asset,
new model, texture or camera adjustment.

Sample vertical rays in the lip region of the actual smooth triangulation.
Candidate facing upper/lower heights come from opposite outward normal signs
and a bounded height/gap interval. This is a provisional geometric contact
field, not full anatomical rim labeling. A distance-weighted interpolation
extends measured column heights with a bounded spatial taper.

Compress each selected upper/lower interval around its midpoint with a
piecewise-linear, strictly monotone vertical map; exterior heights return to
identity. Independent tests cover ordering, prescribed interval shrinkage,
unchanged x/z, unchanged exterior, identity and invalid-input rejection.
The continuous column map's monotonicity does not guarantee the discretely
warped triangulated mesh has no intersections. Check triangle orientation,
area, bounded displacement and 13 actual lip sections across a wider strip
than the earlier central-only pair test.

Prediction: the visible gap narrows naturally without a folded lip shelf or
side-profile regression. Falsify promotion on remaining unnatural shape,
sampled intersections, reversed triangles or worsened bilateral photo evidence.
Render full five-view and enlarged mouth comparisons from actual exported
meshes. Report original cage profile values separately from the smooth source;
do not erase experiment 0112's left-profile regression. No camera or identity
acceptance is implied by a smaller internal gap.

## Executed result

Promotion: `REJECT` for both nonzero trials. The actual mouth crops show a
narrower frontal slit, but retain a projecting/open lip shelf in the oblique
and side views. Full five-view identity remains generic. No candidate replaces
either the original cage or the unaccepted smooth source.

The contact field contains 5,894 sampled columns; 1,701 vertices move. Every
x/z coordinate remains bit-identical, so the trial cannot correct the existing
front/back lip-shape mismatch. Both original profile means worsen even against
the already-regressed smooth source:

| Amount | Left / right profile MAE px | Maximum move | Minimum area ratio | Source-relative normal reversals | Sampled crossings |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | 4.7725 / 7.0207 | 0 | 1 | 0 | 0 |
| 0.5 | 4.8060 / 7.0752 | 0.01170 | 0.1159 | 0 | 0 |
| 0.9 | 4.8454 / 7.1062 | 0.02106 | 0.0471 | 22 | 2 |

For comparison, the unsmoothed experiment 0079 source remains 3.5891 / 7.2493
px. These are the same reused fitting/diagnostic profile observations, not a
new independent validation set. Even the half-strength trial violates the
existing 0.5 area-ratio guard; small displacement and zero sampled crossings
do not make it a valid shape improvement.

All 22 normal reversals localize near the mouth corners; the two sampled
proper crossings occur at the leftmost tested plane. A source-relative normal
dot-product reversal is a diagnostic guard, not by itself a formal topological
inversion proof. The explicit segment intersections are separate evidence.
Neither continuous monotonicity nor increasing resolution should be claimed
as collision freedom for this discretized mesh.

A follow-up read-only connectivity check finds the eligible upward/downward
facing triangle regions remain broad connected patches. Merely selecting their
largest connected components would not isolate a correct anatomical rim.
Likewise, extrapolated height support is not direct observation. Stop this
unrestricted height-field closure direction rather than increasing strength or
silently excluding corners from acceptance. Subsequent fitting needs explicit
lip-surface support and photo-consistent front/back shape, not gap shrinkage
alone. All camera, full-head and texture gates remain unchanged.

Private `smooth-contact-v1` retains the actual three exported meshes, full
five-view and mouth comparisons, sampled field, per-plane crossing records and
report SHA-256
`6b73c5408d36ac659f0969322460a1fbf57c547fae458d70a24259bfc3c27c01`.
Only public implementation/tests and aggregate findings enter Git. The
continuous map's limited contract is `TECHNICAL_CHECK_PASSED`; numerical
reports remain `UNVERIFIED`, with the visual/geometry rejection recorded here.

Verification: `python -m unittest discover -s tests -q` passes all 94 tests;
`git diff --check` passes. No appearance default or baseline changed.
