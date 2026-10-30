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
