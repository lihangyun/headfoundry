# Experiment 0198: native 3D mouth deformation and visible-contact audit

Status: v1 solver/refinement/render checks `TECHNICAL_CHECK_PASSED`, front
attachment fit `PARTIAL_SUCCESS`, five-view appearance `REJECT`. V2 fails
mesh guards and is `REJECT` before rendering. Neither is grafted into or
promoted as the subject head. Hair and texture remain outside scope.

## Different representation, existing implementation

Keep the connected, closed-mouth Apache GNM donor from 0197 in its native
topology. Reuse `surface_diagnostic.fit_surface` with unrestricted XYZ
displacements, not a photo-ray depth field or sampled depth transfer. The
same single similarity placement is used before/after: the previous mouth
width scale and a front-center position/depth inherited from the current
head. This depth gauge is uncertain, not observed anatomy. No rejected
whole-face identity coefficients or new dependencies enter the experiment.

The declared native mouth-to-chin support contains 1,283 cage vertices.
Protect its exterior, boundary and two additional graph rings, including
nostril neighborhoods, leaving 805 free vertices. Fit 69 soft front-only
attachments on upper/lower pigment borders and the shared contact curve.
Central columns avoid the corner degeneracies. Graph-edge and graph-Laplacian
displacement regularization are both fixed at 30; solve once without a
parameter sweep. Pigment borders are not asserted to be exact material
correspondences.

A no-op control returns the source within 5e-16 units. Refine both before and
after cages using the same two finite Catmull-Clark steps. Report projection
errors on the **exported evaluated geometry**, not only the coarse solve.
The preserved cage exterior does not imply an identical evaluated exterior:
subdivision stencils propagate changes to neighboring samples.

| v1 diagnostic | Result |
| --- | ---: |
| Maximum cage / evaluated displacement | .045709 / .042975 |
| Minimum cage / evaluated area ratio | .695033 / .714942 |
| Source-relative normal reversals | 0 / 0 |
| Changed evaluated vertices above 1e-10 units | 23,005 |
| Evaluated vertices / triangles | 269,289 / 537,648 |
| Front fit mean error, evaluated before / after | 7.284 / 1.044 px |
| Front fit p95, evaluated before / after | 16.773 / 2.995 px |

Independent replay reproduces both solver and subdivision arrays exactly.
All 29 original contact pairs share welded indices; their zero gap is a
topological property, **not independent collision/contact validation**.
OBJ rounding stays within 5e-9 units. Current subject head, eyes and cameras
are not edited; these are complete generic-donor diagnostics, not a graft.

## Actual five-view result

Load the current head's saved Blender scene and replace only the diagnostic
mesh. Reuse its material, world/exposure, cameras and exact per-view key/fill
positions and rotations, avoiding any donor-bounding-box lighting change.
Render five before and five after clay images. Inspection uses fixed native
image crops and explicit "generic donor / not grafted" labels.

The lower lip gains height, but becomes a ledge with a conspicuous transverse
lower groove; the side mouth remains wrong. V1 is visually `REJECT` despite
better frontal attachment fit. Evaluated lip-rim two-ring dihedral p95 rises
3.445 to 4.128 degrees and maximum 7.024 to 11.780 degrees. Contact-region
angles decrease. These statistics do not explain away the visible fold or
certify appropriate lip volume; absence of flipped faces is insufficient.

At the same reference profile rows, v1 lower-peak signed forward error changes
from -10.90 to -.52 px on the left and -7.43 to +4.29 px on the right. Contact-row
errors worsen to +11.42/+15.68 px, and lower-transition errors remain
approximately +9.85/+19.61 px. Same-row outline scores do not establish that
the scored point is the intended anatomical contact or turn.

## One bilateral follow-up, rejected without relaxing safeguards

V2 keeps the same source, placement, support, 69 front observations and solver
weights. It adds eight bilateral soft observations. Upper/lower roll and
contact attachments come from their actual source curves; only the labiomental
target uses the all-face silhouette at the reference row. This avoids calling
an unrelated lower-lip point at the photo's contact height the mouth seam.
The source curves' apparent peaks remain an unverified correspondence choice.

The result has cage maximum displacement .078151 and minimum area ratio
.068019; after refinement these are .060859 and .338751. Both representations
fail the predeclared .06 displacement / .5 area guards, although neither has
a reversed normal. Preserve the rejected OBJ/NPZ for diagnosis; do not render
or integrate it as an eligible head, scale back the result to pass, raise the
thresholds or sweep weights. Improved sampled outline scores cannot rescue it.

## Corrected visibility audit changes the next action

The photo contact notches lie roughly a dozen pixels below the source's
projected seam. More importantly, a leading projected seam sample can be
occluded by another lip/skin surface. Merely reducing a seam attachment's
projection residual does not prove the visible contact has been repaired.

An initial audit of only the 29 updated original seam IDs finds both leading
points occluded. That sample set omits new subdivision edge points. A second
audit tracks the complete finite refined chain: 113 vertices, all consecutive
pairs verified as actual mesh edges. Exact nearest-triangle ray tests include
all possible projected triangles; decisive first hits agree with independent
full 537,648-face queries.

For v1's full chain, the left leading point is visible, correcting the overly
broad initial occlusion inference; the right leading point remains hidden by
.020602 camera-depth units. The foremost **visible sampled** chain vertices
are still about 9.73/13.93 px too far forward and 12.15/13.29 px too high
relative to the two photo notches. These finite samples are not a certificate
of the continuous visibility endpoint. The rejected bilateral fit changes
which source point leads; its right leading point remains occluded.

Stop this unconstrained point-pulling branch. Before another mouth fit or
integration, establish visible seam/roll/skin support and a bounded coherent
volume representation. Do not graft a donor merely because it is licensed,
closed, smooth-shaded or has low attachment residuals. A separate local-only,
free-commercial geometry-initializer screen may test a stronger whole-head
starting point; it must prove exact asset rights and actual visual benefit.

All photographs, subject-bound placements, OBJ/NPZ files, source snapshots,
Blender scenes, visible-contact audit and rejection-labeled comparisons remain
ignored locally. The public regression suite passes 105 tests; this is library
evidence, not a head-quality acceptance. The independent/composited reference
policy and all camera/visual gates remain unchanged.
