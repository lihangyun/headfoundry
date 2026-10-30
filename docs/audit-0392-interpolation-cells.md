# 0392 fixed-state interpolation-cell attribution

0391 closed d7ff540. Budget 15 minutes, one fixed-state audit, no optimizer.
Hypothesis: the two finite-difference gradients differ because displaced image
warps cross bilinear cell boundaries, rather than because of camera arithmetic.
Use identical0390state, frames, all observations, loss and two0391steps.
Reuse archived0391verified intake in memory; never restore/run its controller.
Compute the explicit bilinear spatial gradient at each frozen target warp.
Compare (a) actual sampled loss, (b) the same displaced warps evaluated with
the frozen cell polynomial, and (c) spatial-gradient chain rule with numerical
warp derivatives. Report every crossed sample/parameter and discrepancy.
The chain rule is hybrid, NOT a fully analytic camera Jacobian. No new precision
search, held evaluation, camera fit, medical data or images written. Stop after
one pass; failure does not authorize0390retry or boundary relaxation.
Controls: an affine field has its known gradient; a deliberately crossed kink
differs from frozen-cell extrapolation. No physical accuracy inference.

## Result

One audit exited0 in7.55s. Archived intake verified original1041RGB frames,
three gray identities, consent/protected hashes and exact saved residual replay.
No parameters fitted, held rows scored, new frames saved or medical scan read.
At h=1e-6/5e-7,21/13 parameter-sample incidences cross frozen cell boundaries.
Actual gradient difference norm0.006894326791381339; frozen-cell difference
1.6682809603403123e-9; hybrid chain-rule difference5.226272516335074e-10.
Frozen-cell vs hybrid errors1.9888566526401048e-9/4.947973325916314e-10.
Thus the previously observed step sensitivity is attributable to crossing
bilinear interpolation cells in this fixed-state comparison, not evidence of
a broken camera projection derivative. This does not establish optimizer
convergence, correspondence correctness, focal identifiability or head accuracy.
No permission inferred to repeat0390with more iterations or wider bounds.

Evidence `assets/private/closed-experiments/0392-cells/evidence.zip` contains
result.json (all gradients and crossing indices) and diagnostic source; SHA256
`bc8cf0fef649f5a84cb0f1e768177e3f35bbbbb50987d7e94c6cbe4207aa55e5`.
The runner reuses only archived0391intake AST up to the constraint computation;
it never invokes its controller, NNLS or finite-difference loop. The explicit
spatial-gradient chain uses numerical warp derivatives, not a fully analytic
camera Jacobian. Synthetic controls only check affine derivatives and a simple
kink. They do not certify smoothness of real image data.

Next decision: stop treating numerical differentiation as the main unresolved
physical bottleneck. Any new reconstruction route must address the independent
correspondence/coverage and focal-identifiability evidence, not recycle0390.
0390REJECT remains; real head and medical gates remainUNVERIFIED.
