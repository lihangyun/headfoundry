# Experiment 0071: real-data target-point contract ablation

Status: `REJECT` for shape promotion. Public numerical integration works;
original shape/camera defaults remain unchanged.

Connect the public fitter from 0070 to the twelve eligible alar observations,
four paired nasal controls and original cameras used in 0068. Each sign
branch passes barycentric sample positions and matching target displacements
to `fit_target_points`, with explicit masks and supplied 5px scales. This
point-only ablation omits profile and frontal-projection-prior residuals;
it is not a replacement for the combined objective. Evaluate both profiles
outside the solve, retaining their earlier source-fitting history.

Real integration exposes a specific unsupported degree of freedom: neither
tip-up nor tip-down moves any of the eligible alar samples. Previously the
optimizer returned an arbitrary tiny tip coefficient (~0.000102). The public
fitter now excludes controls with exactly zero displacement on all eligible
samples, returns exact zero weights for them, and reports fitted/unsupported
indices. An entirely unsupported basis fails closed. A regression test
covers this behavior even with zero coefficient regularization. This is an
exact-support check, not a general Jacobian-rank or identifiability proof.

Rerun v2 after this fix: all sixteen branches explicitly flag control 0 as
unsupported. Best tip/depth/width/base weights are 0, approximately 0,
-0.087367, -0.305529. Maximum movement 0.015501 template units, no reversed
triangle normals, minimum area ratio 0.584958. Not a collision/anatomy proof.

| Diagnostic px | Source | Point-only candidate |
| --- | ---: | ---: |
| Front alar mean | 8.8148 | 4.1506 |
| Left30 alar mean | 5.1659 | 6.9930 |
| Right30 alar mean | 4.8562 | 4.8609 |
| Left nasal profile MAE | 2.8416 | 3.2009 |
| Right nasal profile MAE | 6.4675 | 7.8432 |

Actual five-view source/candidate renders were inspected. Better frontal
point error comes with worse side evidence and no established identity
improvement. Reject promotion; a point-only score does not substitute for
the required multi-view reconstruction result. The new unsupported-control
guard is useful implementation correctness, not evidence of better likeness.

Private `authored-nose-point-contract-v2` retains actual OBJ, per-branch
public fit reports, explicit masks, asset provenance, full diagnostics and
native renders. v1 is retained as pre-fix evidence. All 76 tests pass. No
private photos or meshes enter Git. Next retain mixed point/contour evidence
and investigate the remaining anatomical mismatch, without amplifying this
rejected point-only nasal-base update.
