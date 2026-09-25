# Experiment 0190: frozen coherent-head method on new synthetic heads

Status: predeclared split, frozen-code checks and execution
`TECHNICAL_CHECK_PASSED`; strict synthetic reliability `REJECT` (5/12
per-case `PARTIAL_SUCCESS`); actual local-photo likeness `UNVERIFIED`.

Experiment 0189 was a method-development test on twelve already inspected
CC0 synthetic heads. Before this run, the separate, ignored private record
fixed new indices 11, 34, 57, 80, 103, 126, 150, 173, 196, 219, 242
and 254; the two original runner SHA-256 digests; the ±0.35 coefficient
bound, ridge 4, twelve active controls, 0.01 finite-difference step and
single template-edge linearization. The runner asserts the source-code
digests. It uses the same pinned 82 paired CC0 MakeHuman controls and known
cameras. Only front/±30° masks enter the local and coherent fits; the true
vertices and ±90° views are scored afterward. This is a disjoint *method*
holdout within one synthetic family, not an independent source or real-image
holdout. No hair, texture, subject photograph or paid model is involved.

The predeclared per-case gate requires safe geometry, both held-side
leading-face edges strictly better than the template **and** local fitter,
true 3D vertex RMSE strictly better than both, and frontal training-mask
IoU at least as good as the template. Every one of the 12 cases would have
to pass for this run's aggregate `PARTIAL_SUCCESS` status.

| New twelve-case mean | Template | Local fit | Frozen coherent fit |
| --- | ---: | ---: | ---: |
| Left held leading-face edge, 220 px image | 0.68421 px | 0.66228 px | 0.46930 px |
| Right held leading-face edge, 220 px image | 0.68421 px | 0.67105 px | 0.46930 px |
| True 3D vertex RMSE, normalized head radius | 0.0115040 | 0.0114687 | 0.0074741 |
| Front training-mask IoU | 0.981096 | 0.983341 | 0.992226 |

All 12 fitted meshes pass the implemented area, normal and displacement
guards. Five cases improve *both* held side edges over both alternatives;
ten improve 3D RMSE; nine preserve frontal IoU. Only indices 34, 57, 80,
242 and 254 meet the complete joint gate. Indices 126 and 150 regress on
held side, 3D and frontal checks simultaneously despite being mesh-safe;
196 regresses on the frontal check. Thus the improved averages are real
within this controlled test, but the method is not reliably better per head
and remains `REJECT` for default or subject-geometry promotion.

Both generation and fitting use the same MakeHuman control family, and
oracle cameras remove a difficult real-world uncertainty. At 220 px many
silhouette differences are subpixel/quantized; the largely symmetric heads
make the two side scores correlated rather than two independent tests.
The strict all-case gate itself has a floor problem: three new cases start
at **zero** template error on the sampled side rows, so no candidate can
strictly improve their side score. We retain the predeclared `REJECT` and
do not retroactively loosen its threshold. Separate from that floor,
cases 126 and 150 have material side and 3D regressions; they are actual
reliability failures, not merely un-improvable ties. A future benchmark
must predeclare a non-regression rule for zero-error cases and report
material-error cases separately.
Whole-crop vertex RMSE includes neck/shoulder fragments, and current mesh
safety does not test every self-intersection. This run cannot verify a
physical head, camera or likeness for the user's five independently
generated/composited local references. No current subject mesh was changed.

Next: stop promoting this one-pass contour fit. A head-only method must
address the per-case side failures with a predeclared, stronger 3D/shape
constraint and be retested on fresh identities before any five-view local
subject trial. If a later candidate reaches that stage, its actual enlarged
photo/old-white-mesh/candidate-white-mesh comparison—especially both
profiles and mouth-to-chin relief—will determine visual acceptance, not
these synthetic means. Experiment 0157 already rejected a photo fit of the
same 82 controls transferred to the current subject mesh; the in-family
synthetic mean improvement does not overturn that real-image result. Full
private per-case metrics and clay panels are under ignored
`assets/private/synthetic-head-benchmark-v1/coherent-holdout/`.
