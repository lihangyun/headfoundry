# Experiment 0201: posterior lip support and corner-order correction

Date: 2026-10-13. Source representation `PARTIAL_SUCCESS`; fitted donor and
head/default promotion `REJECT`. Current subject head and cameras stay unchanged.

## A concrete source-construction assumption

Experiment 0200 repaired mean/basis closure consistency but still produced a
shallow contact section and a lower-lip bulge. The source topology has five
29-vertex rows in each lip region. Our BFS numbering assigns no anatomy.
The previous construction discarded rows0/1 and welded row2, preserving each
remaining section by translating its three rows together.

Row2 is not an arbitrary or incorrect upstream landmark index: official sparse
68-point inner-lip attachments lie mainly on row2, and outer-lip attachments on
row4. Those 2D contour attachments do not identify a physical closed-mouth
contact surface. In the original model, row1-to-row2 upper/lower strips cross in
three tested common-X sections. Posterior rows0/1 are hidden under first-hit
queries in the front and both source-side views. Row1 is an interleaved inner
edge, not a demonstrated anatomical contact line.

At the central source column, anterior closure preserves only 0.001622 native
units of upper-row4 relief and 0.000964 of lower-row3 relief relative to contact.
Using row1 retains 0.003554 / 0.002644 respectively. The resulting test can
isolate a truncation-induced shallow section. It cannot establish that row1 is
the true contact or that independently generated reference notches represent
that material line. No expression basis, new model or semantic label is inferred.

## Single row-choice control and diagnosed failure

Retain rows1–4 instead of rows2–4, weld the 29 row1 pairs, and use the same
column-wise midpoint translation and frozen harmonic support. Remove only the
58 posterior row0 vertices; keep all other source exterior faces except the
two exactly collapsed corner triangles produced by welding. This first control
has a valid edge/fan topology but reverses two source-relative corner faces and
has minimum area ratio 0.467091. It is `REJECT` and is never put through the
subject-camera comparison or grafted into the head.

The failure is traceable: paired row1 corner positions differ laterally.
Translating the complete upper/lower forward rows to match those X coordinates
swaps the upper/lower row2 corner-side order. The two failed triangles contain
the welded row1 point and the upper/lower row2 points in the same end column.
Moving the shared endpoint and the entire column together cannot fix them:
it translates the triangle without changing its normal.

The correction preserves forward lip-body X coordinates, welds only contact X,
and keeps the original shared Y/Z translations. Harmonic continuation uses
the same source exterior graph/support. This deliberately changes lateral
section relations, reported explicitly; Y/Z section relations stay exact.
No noncollapsed face is deleted, winding changed, or quality threshold relaxed.

| Source check | Row1 full translation | Row1 with body X retained |
| --- | ---: | ---: |
| Source-relative reversed faces | 2 | 0 |
| Minimum area ratio | 0.467091 | 0.560625 |
| Nonmanifold edges / vertex fans | 0 / 0 | 0 / 0 |
| Duplicate triangles | 0 | 0 |
| Mouth boundary left open | 0 | 0 |
| Contact gap | 0 | 0 |
| Retained lip-body X motion | Nonzero | 0 |

The repaired cage has 11,373 vertices and 22,518 triangles. Its five intentional
eye/nostril/bust boundary loops remain; it is not a watertight full head. The
0.000329 maximum changed lateral section relation is recorded, rather than
claiming complete section preservation. Source-model/license bytes and revision
are the already pinned Apache-2.0 GNM assets. No additional weights or services
are used.

## Actual five-view source review

Apply precisely the previous frozen similarity, without recentering on the new
seam. Two finite Catmull-Clark steps preserve the reviewed representation;
ray-test full inserted contact/upper-border/lower-roll chains. Render in the
same saved five-view Blender camera/material/light/exposure setup and compare
identically cropped images.

Both side white meshes show a clearer contact indentation than anterior closure.
The source-visible upper-border/contact gaps are about 8.70 / 8.79 px and
lower-roll/contact gaps about 6.57 / 6.04 px in the fixed cameras. These are
finite-curve diagnostics, not the reference's measured physical contours or an
independent likeness score. The neutral lips remain generic. Source support
and corner repair are `PARTIAL_SUCCESS`; subject/default promotion remains
`REJECT`. This useful control is not a replacement head result.

## Frozen identity replay and one corresponding constrained fit

Apply experiment0200's exact fixed coefficients through the *same repaired
closure operator* used for the mean. Mean replay is exact; central derivative
error is 4.67e-12 and linearity error 5.56e-17. This controlled replay fails the
unchanged protected-point limit (0.0200575 > 0.02) and cage/evaluated area limit
(0.499134 / 0.499062 < 0.5). Preserve it as `REJECT` without rendering. Do not
round a near-threshold failure into a pass or scale it down after fitting.

One new constrained fit uses the repaired posterior donor, rebinds the middle
front observations to its actual welded contact row, and uses the upper source
forward border instead of the previously presumed row3 peak. Cameras, placement,
photo targets, coefficient bounds, prior strength and mesh gates are unchanged.
This is a representation/correspondence correction, not a parameter sweep.

The fit passes its cage/evaluated mesh checks: maximum displacement
0.021313 / 0.020959, minimum area ratio 0.796474 / 0.801206, no reversals, and
protected maximum 0.019999. Front fitting mean/p95 fall from 3.918 / 8.231 to
1.904 / 3.788 px; these are in-sample residuals with newly bound contact points,
not a directly interchangeable score against experiment0200's old bindings.
The coefficient norm is 2.424, versus 5.138 for the previous fitted donor.

Actual five-view white meshes still show the inferior lower-lip bulge/groove
and an incorrect upper-lip form. The left contact is clearer, but this does not
repair overall anatomy. Both fitted lower-roll samples become hidden after
fitting; complete refined-curve visibility records the replacement leaders.
This fitted donor is `REJECT` and is not grafted into the current head.

## Consequence and next evidence

Preserve the repaired posterior closure and distinguish physical contact support
from 2D inner-lip attachments. Stop using stale hidden material bindings as
visible-profile evidence. Any subsequent head candidate must improve actual
front and both side anatomy, including the lip-to-chin transition, while passing
protected mesh and visibility checks. Lower residuals alone still fail that
requirement. The five references remain independently generated/composited;
head likeness, camera acceptance and KeenTools parity remain unverified.

All source control scripts, meshes, fitted coefficients and renders are local.
The public research commit excludes photographs and identity-derived artifacts.
The existing public suite passes 105 tests; a final audit verifies 48 unique
script/mesh/render and unchanged current-head/camera digests across0201–0202.
These are execution/regression checks, not visual acceptance.
