# Experiment 0195: native lip readings and structured relief candidates

Status: native-coordinate checks, Hermite execution, mesh guards and five-view
rendering `TECHNICAL_CHECK_PASSED`; locally clearer lip relief `PARTIAL_SUCCESS`;
both candidates' visual/default promotion `REJECT`; physical reconstruction,
complete likeness and KeenTools parity `UNVERIFIED`.

This is head-only. Hair is excluded; current head, eyes and all five cameras
are frozen. No licensed donor, texture or learned inference changes this trial.
The independently generated/composited references remain local visual guides,
not an accurate shared physical scene.

## Re-read native image evidence

The front and both oblique mouth crops were visually re-read in original
1254-pixel coordinates. Sparse upper/lower pigment-border polylines have
subjective reading radii mostly 4--5 px centrally and 6--8 px at ambiguous corners.
These are AI-assisted readings, not human-verified annotations, calibrated
uncertainties, measured depth or anatomical turning boundaries.

Front/right30 broadly agree with previous detector curves (median differences
about 1--2 px). Left30's central lower pigment border is about 4--6 px below
the detector (median polyline distance 4.55 px, maximum 5.52 px); this supports
an image-local fuller/lower appearance cue, not a cross-view material match.
The labiomental region is a diffuse shade band with 7--11 px subjective
tolerance, not an exact crease. It is not embossed into this candidate.

## Current surface, not stale archived depth

The current 34,753-vertex, 69,320-face head matches the patch ownership map
exactly. Archived patch UV differs from current frontal projection by up to
1.36476 px and archived subdivision boundary positions differ by up to .0133453
world units after later legitimate deformations. Only vertex/face ownership is
reused; native UV, camera depths and control slopes come from the current head.
Neither archived harmonic depth nor old triangle attachments replace it.

## One frozen authored representation

Unlike the broad Gaussian fields in experiment 0153, each native-front column
uses piecewise cubic Hermite displacement controls: upper skin, upper border,
upper roll, one shared closed seam, lower roll, lower border, lower skin.
The upper roll has two longitudinal peaks; the lower roll a broad central one.
Peak outward camera-depth changes are .012/.015 model units and the central
seam moves inward .003. These are authored artistic values, **not** measured
millimeters or recovered anatomy. Skin-anchor displacement/derivative is zero;
the field tapers before corners. Total depth slope is set to zero at roll/seam
controls by subtracting finite-difference source slopes. The analytic field's
segment joins are C1; the sampled triangle mesh is not certified C1.

All 7,457 changed vertices are inside the current mouth patch. Boundary,
support exterior, eyes, nose, ears, cameras and topology stay unchanged. No
coefficient optimization or table sweep is performed. Endpoint/value/derivative
checks execute before export, and each candidate gets the same five-camera
neutral-clay preset as the existing head, with exactly equal recorded light
positions and rotations.

The initial dense 41-point luminance seam causes visibly scalloped incision
and left-oblique vertical puckering. A single follow-up changes only this
input to seven fixed sparse control points. Its maximum/RMS native displacement
from the dense trace is 1.87156/.69661 px, within an explicitly authored 2 px
reading band (not a measured statistical confidence interval). The same depth
tables, support policy and baseline-slope sampling are retained. No further
variation is tried after inspecting the result.

| Diagnostic | Unchanged head | Dense-seam ribbon | Sparse-seam ribbon |
| --- | ---: | ---: | ---: |
| Left leading-face profile MAE | 3.624 px | 3.817 px | 3.803 px |
| Right leading-face profile MAE | 4.923 px | 5.214 px | 5.242 px |
| Maximum displacement | 0 | .015094 | .015095 |
| Minimum source-relative face-area ratio | 1 | .718899 | .632956 |
| Source-relative normal reversals | 0 | 0 | 0 |

These profile rows are existing same-reference diagnostics, not independent
physical holdouts. Mesh checks do not certify all self-intersections or
anatomy; the neutral closed patch still has no expression/teeth representation.

## Actual visual decision

Both full five-view and enlarged mouth photo/current/candidate sheets were
inspected. Lower-lip relief becomes more apparent in front/obliques, so there
is narrow representation capacity evidence. Sparse input reduces seam
scalloping, but the seam remains too dark/deep, left-oblique puckering remains,
and pure profiles retain an unnatural upper shelf with no convincing rounded
lower roll. Neither candidate is a meaningful likeness improvement. Both are
`REJECT`; the unchanged head remains the experimental reference.

Stop this additive ribbon branch rather than tuning amplitudes or slopes.
It inherits the existing surface's artifacts and insufficient base anatomy.
Next seek a replacement lip surface with credible relief, not another field
added to the same patch. The already pinned Apache-2.0 GNM asset has lip groups
and official mouth anchors, but its neutral mouth is **open**: upper/lower lip
groups share no vertices and oral components exist. A future donor trial needs
explicit closure, exterior-only selection and bounded local transfer; the
previous rejected whole-face GNM candidate must not be silently adopted.

Private inputs, readings and grids are in `native-lip-readings-v1`; two complete
OBJ/eye-combined candidates, immutable source snapshots, visual verdicts,
five exact-camera renders and reopenable scenes are in `native-lip-ribbon-v1`
and `native-lip-ribbon-v2` under ignored `assets/private/subject-001`. No identity
derivative or photograph is uploaded. The existing public package suite remains
105 passing tests; private interpolation checks and actual Blender runs verify
this experiment, not production quality.
