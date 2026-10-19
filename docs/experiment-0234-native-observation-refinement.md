# Experiment0234: distinguish seeded local precision from large-motion tracking

Date:2026-10-19. Pre-registered before native-level measurements. Status:`REJECT` for the complete precision gate.

0233's point validity audit finds true-material color correlation0.944-0.982 and
MAE0.89-1.51 gray, versus near-zero zero-motion correlation. Its images/declared
coordinates contain a stable signal. Yet its nominal21px/pyramid3 tracker uses
native support radius84px: only0.42%-0.58% of measured source supports are fully
opaque. Median99.90%-99.92% of coarsest Scharr gradient energy comes from outside
conservative interior, despite the full-resolution11px interior margin. Nearly
correct coarse endpoints drift toward a different motion field.

Test one semantic correction: **local precision after a supplied coarse seed**
must not repeat the large-motion search hierarchy. Add a mandatory-seed native-
level refinement entrypoint with the same21px window,30 iterations/.01 epsilon,
minEigen1e-4,<=.75px cycle and<=15 gray patch-error gates. Original `track_step`
retains exactly its old pyramid3 behavior and defaults. No public pyramid knob,
intermediate-level/window sweep or silent fallback; no masks are expanded to
delete difficult points. This is a new bounded hypothesis supported by measured
support mismatch, not a relabeling of0233 as successful.

Reuse exactly0233's five saved contexts, measurement populations/IDs, native
pixel coordinates, coarse-noise arrays, true images and known geometry. Compare
native direct refinement and the **same** F-derived prewarp with native local
residuals. Assert that every F and rectification matrix equals the frozen0233
ones; only the image-refinement backend changes. Fit no new cameras or geometry.

Each of the two explicitly named native recipes (direct; F-prealigned) must
retain>=30 and>=50% measurements in **every** case with endpoint p95<=1px.
Before results, fix the next-gate priority: use direct native if all five pass,
otherwise F-native only if all five pass; otherwise stop. Never choose a different
recipe per view or silently fall back. This chooses the smallest complete
passing observation recipe, not an easier view/population or a lower target.
Save all errors/eligibility, paired old/new errors, context
matrices and actual residual sheets. No truth/error filtering. One180s run,
no parameter, pixel-origin, texture, ROI or context search. Failure stops this
mode before real localization; a pass only permits a separately bounded real
pixel/camera check with unchanged acceptance gates.

First require unit checks that old tracking still uses its prior levels while
mandatory-seed refinement uses only the native grid, preserves known endpoints,
and does not force image measurements onto contextual epipolar lines. Existing
failed sources/results remain immutable. No training/upload, case002 fitting,
production-default or source-scan changes; no head/scan/likeness acceptance.

## Result and one unavailable-seed cause check

Both complete recipes fail the fixed1px p95 budget in all five cases, so no
recipe is selected for real localization. Native F medians improve to0.231-0.772px
and retention84.12%-96.19%, but retained p95 is2.495-4.722px. Direct native also
fails. All contextual F/rectification matrices remain bit-identical to0233.
Paired errors and actual before/after sheets demonstrate the removed large
drift without proving tail accuracy. Do not promote a median-only success.

Before another method, perform one diagnostic with the unavailable **true
measurement endpoints as initial seeds**, keeping each native recipe and every
context/mask/gate unchanged. Run the same five saved populations,180s; report
both full and same-ID paired errors. If true seeds solve the tail, local-basin
failure is plausible and a bounded image-search objective may be warranted.
If bias remains, changing seed choice alone is unsupported. Neither result is
a real-use candidate or permission to relax precision or delete residuals.

The true-seed audit does not rescue the method: native F retained p95 remains
1.784188-4.041935px across all five motions, with the same context matrices and
populations. Direct native is also above1px. Thus changing seeds or adding a
larger endpoint search alone is unsupported. The retained native medians and
coverage are useful controlled progress, but no complete observation recipe
passes; do not enter real localization or fit a head from these results.

Next isolate local geometric patch deformation rather than translation alone.
An independently fitted local image Jacobian could be tested, with no free
photometric affine fit, no scan-derived warp in real inference and no measured
point used as context. This is only a next hypothesis, not permission for a
neighborhood, warp, pyramid, window or confidence sweep. Keep the full video-only
head, scan/region and reserved-case goal unchanged.

Verification:168 regression tests pass. Six frozen real-video tracking calls
(three pairs, each seeded and unseeded) preserve exactly the old eligibility
and all retained endpoint/error arrays. This compatibility result is not a
camera or anatomical accuracy claim. Private reports retain exact controls,
invocations, diagnostic arrays, rendered review and test output.
