# 0380: distinguish linear-estimator error from observation inconsistency

Preregistered2026-10-28 after0379closeout0353d99. 0379training pair300/630p95
22.439px is not proof of irreducible input error: algebraic estimation followed
by rank projection does not minimize the reported pixel-domain error. Test this
specific numerical mechanism, not another matcher, point selection or focal seed.

Single variable: optimize signed native-pixel Sampson residuals instead of the
linear algebraic objective. Original0352partition SHA
d0ef30239cfed66ec573dd529ec2037976f71499ae7eed77168855b4ed33f41a;
0379result SHA3276acb38bd8d09e5c65a138ee0b6ddaca441ce467a90de75d3f15b8160fa9f3.
Initialize each of exactly3pairs from its saved0379F; preserve all13training and
9held IDs. No new data, refined0378points, RANSAC, robust loss, filtering,
weighting, focal, pose, 3D, images/scans, learned models, training or upload.

Own rank2 chart: Hartley-normalized training coordinates; F=U diag(cos(t),sin(t),0)
Vtranspose, U/V proper rotations with rotation-vector increments, angle between
1e-8 and pi/2-1e-8. Denormalize before evaluating native residuals. These bounds
exclude rank1, not a camera prior. One TRF/linear-loss/max200nfev fit per pair,
x_scale=jac, ftol/xtol/gtol1e-10. No alternate start or rerun. Save convergence,
angles, matrices, full per-point distances and initial/final training SSE.

Controls first: exact nonplanar scene remains<1e-6px; matrix reconstruction agrees
with initialF up to sign/scale; signed residual magnitudes agree with shared
sampson_distance; every reconstructed matrix has rank2. Flat/degenerate input
must be rejected by the existing normalized estimator. Check one fixed noisy
owned scene for finite convergence/non-increased training SSE, not guaranteed
held improvement. Failure stops before patient data. Full worker<=60s/1GiB,
whole30minutes including tests/closure. Use existing NumPy/SciPy only.

Actual screen requires every pair convergence, nonincreased training SSE and
all9heldp95<=3px (diagnostic only). Report all pairs even if one fails; no physical
identity, rigid camera, true focal or medical2mm claim even on pass. If it fixes
training but not held errors, conclude objective mismatch is not sufficient;
do not declare deformation uniquely proven. If passes, prerequisite geometry
still remains: independent common three-view metric calibration, not pairwiseF
assembled into an assumed camera. Preserve small complete evidence, source Git
recovery, remove exclusive runner after diagnosis, tests and cleanup commit.

## Actual fixed diagnosis

Recovery51467d0. One worker1.437s/88219648B conservative peak, exit0. All three
fits converge (7/7/30evaluations), all controls pass. Exact held max2.55e-13px;
fixed noisy control training SSE.604884→.500283. No physical acceptance follows.

| Pair | Linear trainp95 → native trainp95 px | Linear heldp95 → native heldp95 px |
| --- | --- | --- |
| 240/300 | 1.780245 → 1.101437 | 4.298664 → 5.176557 |
| 240/630 | 1.200907 → 1.192951 | 2.154371 → 2.244160 |
| 300/630 | 22.439483 → 2.564343 | 8.551298 → 8.170887 |

This directly demonstrates that the previous22.44px training error was not an
irreducible property of these observations: changing only the objective/rank2
optimization greatly reduces it. However, all-point held screen still REJECT;
two held pairs remain above3px, one worsens. Objective mismatch alone is not a
sufficient fix. No proof of a unique wrong point, expression cause, or global
optimum follows. Pairwise agreement still cannot certify a common metric camera.
Do not try another loss/seed/threshold on this cohort as an automatic next step.

Complete small JSONs/logs retained under
`assets/private/closed-experiments/0380-native-objective`, all3F/per-point residuals
and controls included; protected input/rights/shared-source hashes reverified.
No images, weights, environments or mesh generated. Retire the one-shot diagnostic
to source51467d0, keep shared math unchanged. No3D/medical/visual result exists.
