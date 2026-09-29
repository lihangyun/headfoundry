# Experiment 0200: bounded identity prior and closure-consistency correction

Date: 2026-09-29. Actual donor/default promotion: `REJECT`. The current subject
head and cameras remain unchanged. This is geometry-only work, not hair or
texture optimization, and no donor is grafted into the subject head.

## Hypothesis and fixed conditions

Experiment 0198's independent vertex fit damaged the mouth despite lower front
residuals. Replace those free coordinates with the already pinned GNM model's
170 head/skin identity directions. Exclude its eyeball/teeth directions and all
expression or demographic-conditioned sampling. Use the same source-neutral
closed exterior, placement, cameras, observations and two-step finite geometric
refinement. The source and license are unchanged from experiments 0179/0197;
this is an adapted model experiment, not upstream expression execution.

A preliminary rigid-core diagnostic finds that translating the mouth can reduce
some side offsets but conflicts with the front placement, and cannot provide
the missing upper/lower-roll relief relative to contact. This is a local
capacity diagnosis, not a proof against every possible rigid alignment.

The new solve evaluates observations on the actual twice-refined surface. Its
sparse affine stencils reproduce the existing subdivision implementation to
1.12e-15, including face/inserted-edge order. The 69 front bindings are soft
5 px residuals; both side views supply soft 8 px *relative* roll/contact cues,
not exact common-3D ground truth. The source-visible material samples are fixed
while fitting, then the complete finite refined curves are ray-tested again.
Visibility or curve-leader changes invalidate correspondence assumptions.

Coefficient bounds are [-2, 2]. An explicit coefficient prior and 0.008-unit
outside-RMS preservation term prevent unrestricted use of extra coordinates;
these are engineering choices, not calibrated population probabilities. No
camera, placement, independent vertex or texture variables are optimized.
Native/evaluated mesh guards remain maximum displacement 0.06, minimum relative
face area 0.5 and no source-relative face reversals; protected outside points
also have a 0.02 maximum displacement. These checks do not prove absence of
self-intersections or natural anatomy.

## Three retained runs, two actual visual rejections

The first solve violates the protected-point maximum and cage-area guard.
It is `REJECT` before rendering. RMS preservation does not imply a per-point
bound. The second solve enforces those *same* pointwise displacement, area and
orientation inequalities inside optimization. Constraint generation retains
every discovered witness; its first constrained solve leaves no all-mesh
violations. It does not rescale a failed answer or relax thresholds.

| Check | Initial fit | Pointwise-constrained fit | Closure-corrected fit |
| --- | ---: | ---: | ---: |
| Protected maximum displacement | 0.050822 | 0.019999 | 0.019999 |
| Cage minimum area ratio | 0.492372 | 0.591344 | 0.538429 |
| Evaluated minimum area ratio | 0.606025 | 0.638383 | 0.643688 |
| Cage/evaluated reversals | 0 / 0 | 0 / 0 | 0 / 0 |
| Front mean fitting residual, px | 2.270 | 2.338 | 2.656 |
| Front p95 fitting residual, px | 5.255 | 5.442 | 6.310 |
| Actual visual result | Not rendered: mesh reject | `REJECT` | `REJECT` |

The initial front mean/p95 are 7.284 / 16.773 px. All listed front scores are
training diagnostics, not held-out improvement. Both rendered candidates use
the unchanged five-view Blender clay scene, material, exposure, camera matrices
and explicit per-view light transforms. The inspected crops use identical
native-image coordinates and scale, with no independent alignment.

Both candidates still produce an oversized lower-lip bulge, a deep inferior
groove and unnatural corners. Both profiles lack the intended lip-contact
indentation. A separate full-head sheet shows that the donor is generic and is
not an integrated replacement; it must not be presented as an improved subject
head. Better front binding errors and technically valid meshes do not override
these actual visual failures.

## Concrete closure-basis bug and controlled correction

The neutral donor translates all three retained rows of each lip by the same
column-specific contact displacement, then extends that displacement harmonically
to surrounding skin. The first two identity fits only averaged source basis
vectors at welded contact pairs. Roll and surrounding-skin basis vectors still
belonged to the original open template. This is an inconsistent adaptation of
the closure operator, not an index swap or a conclusion that GNM itself is wrong.

The third run applies the original frozen linear closure operator to every
identity direction before the unchanged world transform. Rebuild the original
pre-weld graph, including the two subsequently collapsed corner faces:
22,404 triangles, 1,429 free and 9,915 fixed vertices. Do not build the closure
operator from the final 22,402-face welded mesh. Midpoint equality and harmonic
continuation now affect the mean and basis consistently.

Controls on the corrected implementation:

- Neutral donor replay maximum error: 2.78e-17 native units.
- Central finite difference through closure versus transformed direction:
  4.80e-12 maximum error.
- Relative lip-section derivative preservation: exact at checked precision.
- Basis changes outside the frozen closure support: zero.
- Projection and mesh-constraint Jacobians pass their independent finite
  difference checks; actual exported subdivision matches fitted observations.

A read-only fixed-coefficient check estimates at most about 2.71 px lip-curve
motion from this correction. It also exceeds the outside guard slightly
(0.0200062 > 0.02), so it is not a promotable result. Re-solve with the original
guards, rather than rounding that failure away. The third run passes mesh
guards but remains visually rejected. Its fitted contact and lower-roll
material samples become occluded on both sides; the complete finite visible
curve audit records the replacement leaders. Small reprojection residuals at
those hidden samples are not visible profile evidence.

## Stop decision and next gate

Stop coefficient-count, weighting and point-pulling sweeps for this tested fit.
The source-neutral closure already has shallow roll-to-contact depth, and a
mathematically consistent basis adaptation does not validate that authored
contact section. Before another subject fit, inspect a connected closed-mouth
representation with plausible lip-to-philtrum/chin sections and actual visible
contact support. Preserve this corrected operator in any reuse; do not silently
revert to the inconsistent basis. This rejects the tested adaptation and
correspondences, not the entire licensed GNM model or all identity fitting.

The independently generated/composited references remain appearance targets,
not measured views of one physical subject. Camera acceptance and head likeness
are still unverified. No KeenTools-quality, physical-reconstruction, benchmark
acceptance or complete-head result is claimed.

## Verification and local evidence

The existing public suite passes 105 tests with the repository's installed
Python environment. These test library regressions, not visual reconstruction
quality. A final audit verifies 29 unique source/script/mesh/render hashes,
including unchanged current-head/camera bytes; `git diff --check` passes.
Private records retain three OBJ/NPZ candidates, numerical controls,
immutable script snapshots, all ten new fixed-scene renders, labeled comparisons
and separate visual decisions. Input rights and pinned model/source/asset bytes
are checked; no new weights, data, packages or external services are used.
No photos, fitted coefficients, subject meshes or renders enter Git. The public
change records this evidence and its limits; the current head is not replaced.
