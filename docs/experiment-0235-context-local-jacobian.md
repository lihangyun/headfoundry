# Experiment0235: independent-context local patch geometry

Date:2026-10-19. Pre-registered before implementation and measurements.
Status:`REJECT` for the complete precision gate.

0234's true-endpoint seeds still fail all five1px tail gates. That evidence
does not support another endpoint search. Test one different hypothesis: a
translation-only patch cannot describe local surface deformation. Estimate a
fixed local image Jacobian from independent context, not from the measured
patch and not from supplied scan geometry. This is not a revival of0227's
failed free six-parameter photometric ECC fit.

Freeze0233/34's five patterned images, known geometry, populations, IDs, noise,
pixel conventions and coarse measurement seeds. Use unchanged0231 F consensus
only to reject bad context. For each measurement, take the12 nearest surviving
context source pixels. Fit their target coordinates to source offsets scaled
by the12th distance, weighted1/(1+(distance/scale)^2). Extract only the2x2
Jacobian, explicitly discard its fitted intercept. Reject design condition>1000,
nonpositive determinant or singular values outside[.5,2]. No neighborhood,
conditioning, singular-value, ROI or context-threshold sweep.

Sample a39x39 source crop and a39x39 target crop warped by this fixed Jacobian
around the **unchanged coarse measurement seed**. Size39 follows the existing
21px window (radius10), interpolation margin1 and ceil(5*1.5)=8 coarse-noise
radius. Apply0234 mandatory-seed native2D refinement at crop center19. Map its
free residual through the fixed Jacobian. Do not insert the context intercept,
snap onto an epipolar line or impose a projected target endpoint. Require full
native image/crop support, final local center within[11,27], unchanged .75px
cycle and15gray patch-error gates. Save every failure code, neighbor IDs,
Jacobian, conditioning and error; no measured/truth error filtering.

Require>=30 valid and>=50% retention with endpoint p95<=1px in **all five**
motions. Compare with frozen0234 native results on full and paired IDs; no
per-view fallback or winner selection. Unit-test known affine image motion,
wrong contextual translation (which must not pull endpoints), missing or
degenerate context, and unchanged original tracker behavior. One180s run.

If this final context-assisted patch-precision recipe fails, freeze this patch
family, including new window/scale/neighborhood/seed/confidence combinations;
do not transfer a failing recipe to real localization. Record what was ruled
out and return to a distinct full-head method decision, retaining the video-only
target and scan/region/visual gates. A synthetic pass only authorizes one frozen
real observation/camera check, not a head, anatomy or likeness acceptance.
No training/upload, production-default change, case002 use or source-scan edits.

## Single frozen result and exit

The180s budget completes in2.9s with unchanged context F matrices and source
populations. Four yaw cases fail1px p95; only pitch passes. No recipe advances.

| Motion | Retained / original | Endpoint p95 px | Result |
| --- | --- | --- | --- |
| yaw-10 | 668 / 688 | 2.034602 | REJECT |
| yaw+10 | 683 / 716 | 1.531589 | REJECT |
| yaw-30 | 384 / 513 | 2.681581 | REJECT |
| yaw+30 | 382 / 529 | 1.778174 | REJECT |
| pitch+10 | 627 / 657 | 0.944324 | TECHNICAL_CHECK_PASSED |

Median errors0.208-0.404px and same-ID native comparisons improve, but neither
one passing view nor median gains satisfy the whole-recipe rule. Actual review
shows remaining localized outliers; large-motion slope validity also removes
108/513 and131/529 points before image refinement. Full errors, all failure codes,
context-neighbor indices and matrices remain private and replayable. This is a
procedurally patterned supplied scan diagnostic, not a generated human head.

**Exit enforced:**freeze context-assisted patch refinement. Do not add another
neighborhood, local model, window, scale, initialization or confidence-selection
variant to this chain. No real localization/camera/shape solve uses this recipe.
0230 ruled out one global plane;0233/34 isolated large search support and remaining
native bias;0235 shows local context slopes alone still fail the tail budget.
These are bounded negative conclusions, not proof that all photogrammetry fails.
The next decision must address the full-head reconstruction/observation contract
through a genuinely different mechanism and acknowledge still-missing evidence.

Verification:171 regression tests pass. The source-only five-view comparison
sheet was inspected. Private controls bind the frozen images/populations, unchanged
native refiner/context estimator, exact producer and the hash-verified original
pre-result registration. No private source images or scan geometry enter Git.
