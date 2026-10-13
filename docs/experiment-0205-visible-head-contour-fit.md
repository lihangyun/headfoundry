# Experiment 0205: actual visible head-contour support

Date: 2026-10-13. Head only; fixed cameras, no hair or texture work.

Replace0204's hidden static jaw/upper-lid bindings with actual source-visible
supports. The head prior, posterior closure, first30 identity directions,
coefficient prior/bounds, similarity and input observations stay unchanged.
All reference-derived data and candidate geometry remain local.

## Representation check

The new public `occluding_edges` helper identifies two-sided front/back
transitions using camera-space geometry. It excludes open boundaries and rejects
invalid geometry, near-plane inputs, nonmanifold edges and inconsistent winding.
These are candidate contours, not visibility certificates: another surface can
hide them. An independent first-hit ray check is still mandatory.

The deterministic cube test checks expected contour edges, triangle-order and
world/camera-transform invariance, open-boundary exclusion and malformed inputs.
Two nested shells have the same projected contour, but only the nearer shell
passes the first-hit check. This explicitly tests the distinction between a
normal-facing transition and a visible fitting support.

A replay-checked sparse finite subdivision map provides derivatives at arbitrary
refined supports. Jaw samples come from visible anatomical occluding edges;
they are not ray hits at observed target pixels. Eyelid samples come from the
first-hit skin/eyeball ownership transition, keeping the binding on its visible
skin side. The initial source has10 supports on each upper/lower eyelid arc
and23 along the jaw. All pass exact first-hit visibility. Observed curves come
from the same installed MediaPipe graph; they remain uncertain appearance cues.

## Falsified revisions

The first two-round fit reduces frontal jaw distance from9.851 to3.561 pixels
and stable front/oblique mean errors, but its cage-only safety constraints miss
the exported surface: minimum refined triangle area ratio is0.3062, below0.5.
Two previously visible oblique eye-corner bindings become hidden. This version
is `REJECT`, is preserved locally, and is not promoted or rendered as an accepted
result. Mesh density and smaller image residuals cannot override these failures.

The next revision adds active constraints on the actual refined triangles and
on newly found occluding surfaces. Its triangle-membership switch is
discontinuous at tiny face boundaries; SLSQP reaches its120-iteration limit and
the two eye-corner bindings remain hidden. Despite minimum refined area0.50036
and no normal reversals, this candidate is also `REJECT`.

A conservative continuous supporting-plane variant makes those bindings visible,
but the solver reports a line-search failure and produces0.07445 maximum motion,
0.4426 minimum cage area and0.3824 minimum refined area. It is also `REJECT`.
Extrapolated tiny triangle planes are not a successful visibility constraint.

The next declared representation replaces fixed oblique eye-corner material
assumptions with source-visible aperture curves in all three fitting views.
It keeps the8 frontal anchors and4 chin/nose/mouth anchors in each oblique;
fixed oblique eye-corner projections are no longer training observations or
certified visible features. Actual aperture first-hit validation, refined
area/orientation and displacement bounds remain unchanged. Supports are
re-estimated once during fitting and again for final evaluation. This is an
explicit correspondence-model change, not relabeling hidden points as visible
or claiming camera acceptance.

## Verification and boundary

The public regression suite passes108 tests in4.33 seconds. This is
`TECHNICAL_CHECK_PASSED`, not a complete-head acceptance result. The independently
generated reference views cannot certify physical cameras or a single true
subject mesh. Hair/texture remain paused and no head/camera default changes.

## Actual corrected-fit and visual result

The three-view aperture revision converges, including one constrained solve with
4499 active cage displacement checks and50 active refined triangles. Minimum
cage/refined area ratios are0.64845/0.50001; neither representation has a normal
reversal. Maximum cage shape motion is0.059997, below the unchanged0.06 cap.
An independent audit undoes the similarity on the exported vertices and obtains
minimum area0.50001, zero reversals and maximum exported shape motion0.059992.
It reconstructs143 actual visible curve supports; maximum absolute first-hit
depth gap is8.15e-13. These are bounded `TECHNICAL_CHECK_PASSED` results, not
collision, watertightness or subject-shape certificates.

Frontal visible jaw mean distance falls9.851→4.049 pixels. The four frontal
eyelid distances fall3.350/7.422/3.532/7.473→1.036/1.641/1.270/1.918 pixels.
The final sparse training-only means are5.502 pixels over8 frontal anchors and
7.760/5.568 over4 anchors in each oblique. The fit report's all8 oblique means
also include omitted eye-corner diagnostics; do not present them as training-only
scores or valid common material tracks. Neither detector curves nor these
independently generated references establish one physical neutral subject.

The independent replay audit finds a serialization bug: the final jaw-support
loop shadows the variable holding32 static attachment IDs, so the original
archive stores23 jaw IDs alongside32 static weights. Preserve that archive and
write separately hashed corrected replay metadata from the locked preparation.
Coefficients, exported vertices/faces, OBJ and rendered geometry are unchanged.
Fix the exporter to use explicit static fields. Corrected static replay error
is1.11e-15; `fit-replay-corrected.npz` is the usable replay archive. This is an
executed metadata repair, not another fit or a hidden mesh alteration.

All five actual Blender renders finish successfully in the unchanged saved
scene. Worst projection replay is0.000147 pixels. Two comparison controls use
identical native crops, exposure, lights and cameras: reference/current head/new
head, and reference/registered source/new fitted source. Inspect all five views,
not only the selecting front. Hair and texture remain absent.

The head is more coherent than the current irregular mouth/cheek surface and
short neck, and actual eyelid/jaw shape changes are visible versus the registered
source. This is `PARTIAL_SUCCESS` for representation/fitting. The nose and lip
protrusion remain generic in both pure profiles; the obliques retain an unnatural
lower-lip roll/groove. Subject likeness and default promotion remain `REJECT`.
No current head/camera bytes change and no visual acceptance is claimed.

Next constrain coherent nasal and lip-to-chin profile anatomy on the actual
visible source surface, protect both profiles and frontal identity, and check
local section/fold behavior before any promotion. Do not resume the rejected
per-pixel donor-depth transfer or conceal geometry with texture.

Private candidate OBJ SHA-256:
`5887394b3d751e80cd3b91de4995ceeac33d9ae27ef38365ede1b1fcff4bc19b`.
Corrected replay archive:
`c9e66cd84aaef5f86c71e71c0d462eed49f3577b56d028f0938553dea4872381`.
Visible support archive:
`bec3deb82b77fca459d9e6a6e856a08117143a18bdc820d8dbab7a6415efb4ca`.
Final verification:108 tests pass in3.85 seconds;63 artifact/source-reference
hash checks pass, including both comparison controls, all five photo/render
identities, executed-source snapshots and corrected metadata. Current head and
camera hashes remain unchanged. Public diff whitespace checks pass.
No reference image, coefficients, mesh or render is added to Git or uploaded.
