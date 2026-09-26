# Experiment 0196: closed anterior GNM lip-section replacement

Status: donor rights/topology/section closure, mesh guards and exact five-view
rendering `TECHNICAL_CHECK_PASSED`; reduced seam scalloping `PARTIAL_SUCCESS`;
both candidates' visual/default promotion `REJECT`; physical reconstruction,
complete likeness and KeenTools parity `UNVERIFIED`.

The user reaffirmed head-only scope. No hair, texture, lighting, camera, eye,
nose, ear or whole-head prior change is included. Five independently generated
or composited references remain soft local visual targets, not a rigid capture.

## Exact licensed donor, not the rejected whole-face fit

Reuse only the neutral model data at the previously reviewed official GNM
revision `5482149067eda4bf9d423398fe29c4436f936f10`. Local Apache-2.0 license
SHA-256 is `40c4eb506541489bfa77cc4004acfb53cbc4973b9c55e42302ddff7f58e01f39`;
model SHA-256 is
`785d62572590b1073d3f93c61d82346c1e33ffacd3f8245a1b6e0b33cf59e13d`.
Both and the revision are checked before use. No new checkpoint, learned
inference, upstream program logic or rejected identity coefficients are used.
Apache permission is not a training-data-rights or likeness claim.

Each exact upper/lower-lip group contains 145 vertices arranged as five
29-column quad rows. Quad-edge distance from the exterior mouth aperture
recovers posterior aperture, return, anterior contact, roll and outer border.
Only contact/roll/border rows are selected: 174 vertices and 224 triangles in
two **separate** strips. `skin` includes mouth-socket vertices; selection must
use `skin_exterior`. Broader lip-region masks do not equal these exact groups.
Every selected vertex is exterior and outside socket, tongue, teeth and gums.
Selecting the union's original triangles would include eight corner bridges;
they are not transferred.

The neutral donor is open. Its central anterior-contact gap is .00460362 donor
units. Each upper/lower column is translated to its shared contact midpoint;
all three rows receive that same translation, preserving section differences.
The two contact rows then agree exactly. This closes **selected section data**,
not the complete GNM mesh; posterior return/cavity rows are discarded, not
welded into a purported expression-capable head.

## One frozen local replacement

Native-front pigment-border readings and the previously frozen sparse seam
guide target height only; they are approximate, AI-assisted, unverified
anatomical correspondences. Source roll-height fractions and chord-relative
depth come from the selected closed donor sections. One similarity scale comes
from the current visible mouth width; there is no relief-amplitude sweep or
coefficient fitting. Exclude extreme donor columns with reversed height order.

Shape-preserving interpolation transfers five section depths (outer border,
upper roll, shared contact, lower roll, outer border) as a **total-depth
replacement**, rather than another bump on the current interior. Exact current
outer-rim depth anchors, small transition collars and a corner taper limit the
support. All changes stay inside the existing neutral closed patch; 8,216
vertices change. The patch boundary, support exterior, head topology and
generic eye helpers remain exactly unchanged. Frontal vertex projections stay
fixed within 2.55e-13 px before OBJ serialization. No claim of measured depth,
complete collision freedom or C1 continuity of the sampled mesh follows.

## Concrete mapping defect and one correctness rerun

Version 1 interpolates current rim depths from 37 sampled columns, while its
collar displacement is zero at the actual rim. A separate 577-column audit
finds a maximum upper-rim mismatch of .000277603 model units, lower .000071987
before corner taper. This is not exact C0/C1 alignment as a continuous field,
although the mesh remains connected and its outer patch boundary is exact.

Version 2 retains the same frozen donor residual, width scale, support and
closure. It instead ray-lifts the actual source rim at every destination x,
reanchors the residual to that chord, and computes the source triangle slope
from affine inverse camera depth. Exact projected-bounding-box culling retains
all triangles that can hit the queries; no Delaunay remeshing or approximate
nearest-point snapping is introduced. Endpoint arithmetic checks pass. These
checks repair the identified mapping error, not the anatomy; finite sampling
and piecewise source slopes still prevent a smooth-surface certificate.

| Diagnostic | Current head | v1 replacement | v2 exact-rim correction |
| --- | ---: | ---: | ---: |
| Left leading-face profile MAE | 3.624 px | 4.156 px | 4.159 px |
| Right leading-face profile MAE | 4.923 px | 5.337 px | 5.336 px |
| Maximum displacement | 0 | .024933 | .024934 |
| Minimum source-relative face-area ratio | 1 | .584346 | .584703 |
| Source-relative normal reversals | 0 | 0 | 0 |

Existing profile rows are same-reference diagnostics, not independent physical
holdouts. Both candidates pass the unchanged .03 displacement/.5 area-ratio/
zero-reversal guards. Actual five-camera Blender renders use exactly equal
key/fill positions and rotations to the current neutral-clay review. Maximum
projection replay error is .00011584 px; OBJ import error is 5.97e-8 world units.
Projection replay is not calibrated-camera accuracy.

## Actual visual verdict and next gate

Full front/bilateral-profile sheets and enlarged **all five** mouth comparisons
were inspected. The previous jagged incision is less conspicuous, but lip
relief becomes flatter, left-oblique collar corrugation remains and pure
profiles retain an upper shelf without a convincing rounded lower roll.
Correcting exact rim anchoring does not establish a visible likeness gain.
Both candidates are `REJECT`; current head and cameras remain unchanged.

Stop this fixed-rim section branch. Keeping current pigment-rim depth is a
modeling assumption, not anatomical evidence, and can retain bad base shape.
Next screen a coherent lip-to-philtrum/chin surface and visually audited
profile turning support before fitting; keep front as the main visual anchor
and independent sides as soft checks. Do not tune another lip-depth amplitude
or promote a generic licensed donor because its seam is cleaner.

Ignored local `gnm-lip-replacement-v1` and `v2` folders preserve head/eye OBJ,
closed donor sections, immutable source snapshots, hashed reports, rejected
visual verdicts, five renders and reopenable Blender scenes. Photo/identity
derivatives are not added to Git or uploaded. Public regression suite: 105
tests pass; private topology, closure, projection, rim and preservation checks
also run. No library default or product-quality acceptance changes.
