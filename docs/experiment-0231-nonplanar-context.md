# Experiment0231: nonplanar contextual geometry before another image refiner

Date:2026-10-19. Pre-registered before real-context fitting.
Known3D context:`TECHNICAL_CHECK_PASSED`; real observation screen:`REJECT`.

0230's exact source-scan pairs fail the fixed planar context estimator even
without image-matching noise. Their general fundamental geometry is numerically
consistent. Test one context-class change, homography->fundamental matrix,
without treating F line distance as2D reprojection or a new camera solution.
COLMAP already uses nonplanar geometry; the changed component is the independent
observation-context preflight, not a claim to have invented a new SfM system.

Use all five upright0230 motions with the exact same primary fixed-ROI even/odd
sample IDs. Also use the frozen0229 real source612->624 and0->1040 populations:
only untriangulated source features fit context; every unique triangulated
source feature remains a separate measurement. Preserve point-ID parity; report
all measurement and all odd-ID validation line errors without residual deletion.
No extraction, matching, K,3D, image warp, local refinement, pose or shape fit.

Fit contextual F with USAC_MAGSAC3px/10000/0.999, seed231, requiring>=12 inliers,
>=50% context support and>=50px spread each axis. Require finite rank-two F.
Evaluate the larger of the two point-to-epipolar-line distances on every odd
measurement, with predeclared p95<=3px. Save all matrices, masks, errors and
identities including rejection. This one-dimensional line criterion is only a
necessary context/observation diagnostic, not the3px camera reprojection gate.
Budget:one30s run, no context, seed, confidence, reference or threshold sweep.

If exact3D passes but real held-line errors fail, the tested contextual F does
not validate those raw image observations; do not advance to another3D solve
or report scan/head improvement. A pass would only justify a separately bounded
nonplanar image-refinement screen, not final cameras or likeness. All images,
scans and outputs remain private/local; no training/upload or case002 fitting.

## Single-run result and action

All five exact known3D primary populations have100% contextual support. Odd
point-to-line p95 spans0.000013-0.000979px, passing the declared3px screen.
This reproduces general nonplanar geometry, not a physical-video camera result.

On real source612->624, contextual support is78/86 (90.70%), but all untouched
odd measurement line errors have p95=4.895543px. On source0->1040, contextual
support is61/68 (89.71%), while odd p95=4.546006px. Both real observation screens
remain `REJECT`; no odd residuals or contexts are removed to obtain acceptance.
The training contextual support cannot stand in for independent measurement
accuracy. Nor can F's one-dimensional distance be presented as2D reprojection.

The two issues are now separated more clearly: the old planar-context
precondition is too restrictive on the tested known3D motion, and a more general
context class still does not validate the real raw endpoints. Changing camera
or head geometry alone is not justified by this evidence. Next require an
image-based observation method to pass **known nonplanar3D correspondence**
precision/coverage checks, then the unchanged real measurement/camera gates.
Use existing free assets/implementations first; no new focal/ROI/context/threshold
sweep, no snap-to-epipolar-line shortcut and no scan substituted as the output.

All164 public tests pass in3.690s, including corrected source-up projection,
known nonplanar camera geometry, area-uniform barycentric replay and contextual
fit versus separately corrupted validation points. No production/default,
original scan/video or unrelated0207 document is changed.
