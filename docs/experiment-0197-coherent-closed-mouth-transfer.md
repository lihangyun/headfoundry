# Experiment 0197: coherent closed donor and broader mouth transfer

Status: source closure/refinement and destination mesh/render checks
`TECHNICAL_CHECK_PASSED`; lower-transition support `PARTIAL_SUCCESS`; both
transferred heads `REJECT`; likeness, physical reconstruction and KeenTools
parity `UNVERIFIED`. No head or camera default changes. Hair is excluded.

## Source geometry, not a checkpoint substitution

Use the same neutral Apache-2.0 GNM graphical model as experiment 0196, pinned
at revision `5482149067eda4bf9d423398fe29c4436f936f10`. Model SHA-256:
`785d62572590b1073d3f93c61d82346c1e33ffacd3f8245a1b6e0b33cf59e13d`;
license SHA-256:
`40c4eb506541489bfa77cc4004acfb53cbc4973b9c55e42302ddff7f58e01f39`.
Check both before use. No learned inference, expression coefficients, rejected
whole-face identity fit, noncommercial fallback or new dependency is used.

Unlike 0196's separate sections, this source keeps connected skin exterior.
Remove 116 posterior lip vertices, translate each anterior three-row section
to its shared contact midpoint and extend that translation harmonically into
adjacent skin, with zero displacement outside the declared source support.
Weld 29 contact pairs and remove two explicitly collapsed corner triangles.
The result has 11,315 vertices and 22,402 triangles, zero contact gap, minimum
source-relative area ratio .667710 and no normal reversals, nonmanifold
vertices/edges, duplicate faces or inconsistent edge winding. The mouth loop
disappears; five eye/nostril/bust boundary loops remain. This is a closed mouth,
**not a watertight complete head** or global self-intersection certificate.

A separately recorded source applies exactly two finite Catmull-Clark steps:
269,289 vertices, 268,824 quads, 537,648 exported triangles. Updated original
vertex IDs retain valid lip/contact attachments; seam pairs still coincide.
All child normals agree with their ordered parent orientation. This changes
actual geometry, not just shading, and is not an evaluated limit surface.
Source-only clay inspection finds rounder lip rolls and less coarse scalloping,
not measured anatomy or subject likeness. No subdivision-level sweep occurs.

## Two executed transfers and a support defect

Version 1 queries exact donor exterior triangles, choosing the nearest front
surface without Delaunay remeshing, oral fallback or hole filling. One frozen
mouth-width scale and monotone image-to-donor height mapping cover philtrum,
lips and chin transition. An affine depth plane is registered only to 88
surrounding-skin controls: current pigment-rim depths are not pinned. The
resulting total depth is blended into the current head along front-camera
rays. This remains an image-space donor-depth transfer, not coherent 3D
surface deformation merely because its source mesh is coherent.

Native side-photo review distinguishes upper/lower lip peaks, contact notch
and labiomental inward turn. These are AI-assisted readings with several-pixel
uncertainty, not verified anatomical/material correspondences or rigid-capture
truth. The contact notch is not the lateral commissure. An exact visibility
audit finds the actual lower-transition supports outside the old local patch;
v1 therefore cannot move them at all.

Version 2 uses the geometrically refined donor and a broader lower band,
selecting all exact front-visible vertices within it. It modifies 100 retained
skin vertices outside the old patch and preserves the exterior of its **new**
support. The old patch boundary is deliberately not invariant. Source geometry,
support extent/eligibility and corresponding periphery registration change
together; this is a representation/support correction, not an isolated
subdivision ablation or evidence attributing improvement to subdivision alone.

The broader-anatomy displacement guard was declared as .06 model units before
execution, with minimum area ratio .5 and zero normal reversals. It is separate
from 0196's compact lip-only .03 guard, not a post-hoc release-gate relaxation.

| Diagnostic | v1 | v2 |
| --- | ---: | ---: |
| Changed head vertices | 16,753 | 16,853 |
| Maximum displacement | .038171 | .037317 |
| Minimum face-area ratio | .585556 | .574839 |
| Source-relative normal reversals | 0 | 0 |
| Maximum front projection drift before serialization | <3e-13 px | <4e-13 px |

The head topology and appended eyes are unchanged. Actual five-camera Blender
renders use the same camera archive, photos, preset and key/fill positions and
rotations as the baseline. Maximum projection replay error is .000116 px; OBJ
import error is below 6e-8 world units. Neither proves camera accuracy.

An independent reopen audit confirms all 17,900 support-exterior vertices and
the 144-vertex/280-face eye suffix exactly unchanged. The 16,853 v2 count is
before serialization: 10 tiny displacements round away in eight-decimal OBJ,
leaving 16,843 changed stored vertices. Maximum serialization error is
5e-9 units and stored frontal projection drift 2.81e-6 px. All donor queries
have valid barycentric reconstruction; 201 exhaustive nearest-depth queries
and 508 complete-head visibility checks agree with the recorded selection.

## Visual result governs rejection

All five mouth views and full front/bilateral-profile sheets were inspected.
Version 1 has coarse faceted blocks. Version 2 reduces those facets, but the
front/right oblique become diffusely flat, the left oblique develops radiating
folds and both profiles lack a convincing upper/lower roll and contact recess.
Both are `REJECT`, not a new recognizable head.

At the same reference rows, signed forward contact error worsens from
8.01/9.55 px to 12.95/15.96 px in v2. Lower-transition error falls from
13.63/16.91 px to 6.11/14.81 px; the small right-side change is comparable to
reading uncertainty. These are same-reference soft appearance diagnostics,
not independent holdout results or physical 3D errors. The local gain cannot
outvote worse mouth appearance.

Stop this tested image-space donor-depth transfer family: no further smoothing,
warp or depth-amplitude sweep. Next test a continuous 3D surface deformation
with explicit contact and skin/lip transition checks, preserving the licensed
source topology where possible. Screen it before any head promotion. This is
an untested hypothesis, not a guaranteed remedy or rejection of every possible
image-space method.

Ignored local donor/transfer folders retain exact source snapshots, hashes,
OBJ/NPZ files, actual five-view clay images, reopenable Blender scenes and
rejection records. A local comparison-helper UTF-8 fix allows the recorded
verdict to be displayed on the sheet; it changes no geometry. The public
regression suite passed 105 tests during this experiment. Photos, readings and
identity derivatives remain local-only and are not committed or uploaded.
