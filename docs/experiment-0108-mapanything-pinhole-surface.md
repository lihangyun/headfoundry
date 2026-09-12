# Experiment 0108: isolate native-ray versus pinhole surface representation

Status: `REJECT` for visual promotion after execution and inspection. The
protocol below was recorded before execution. Visual target: remove malformed cross-view sheets
without changing the photos, inferred camera or depth. Hypothesis: the native
ray-to-pinhole disagreement contributes to surface distortion. Counter-evidence:
raw depth inconsistency and camera failure remain and may dominate the result.

One primary variable is the geometric unprojection representation. Starting
from raw experiment 0106 (not the focal-conditioned candidate), reuse the
existing tested `depth_to_world` helper to unproject unchanged z depth using
unchanged fitted K and extrinsics. Preserve native output, model validity and
ellipse masks, edge threshold and rendering. Do not fit points, sweep focal,
discard held observations, change cameras or use texture.

Prediction: actual cross-view surfaces and the complete 66 frozen dense-point
transfers improve. Falsification: sheets remain or transfer fails. Exact
own-view projection is a construction identity and cannot count as improved
accuracy; the 33 camera-only checks must remain unchanged. This is a derived
experimental surface, not another model inference or a calibration fix.

Private baseline is `mapanything-apache-v1`; candidate is
`mapanything-pinhole-v1`, with a new camera/surface audit and dense audit.

## Actual result (inspected 2026-09-13)

The derived points retain exact stored z depths, poses and intrinsics. The
existing rigid unprojection helper passes both focused regression tests.
World-space point displacement has median 0.005598, p95 0.016181 and maximum
0.093408 in the model's predicted coordinate scale; this is not independently
verified metric anatomy. Float rotation roundoff leaves own-view projection
p95 below 0.001 px in all five views, as expected by construction.

The unchanged camera-only 33-prediction p95 remains **48.5814 px** and fails
the unchanged gate. All 66 direct dense-point transfers remain included: their
median decreases from 52.9663 to 48.6197 px and p95 from **96.9433 to 91.9331
px**. Positive-depth fraction remains 1.0. These residuals remain large and
track identity uncertainty remains; the decrease does not establish anatomy.

The actual five-view comparison was inspected. Own-view surfaces remain
ridged, with profile holes; the same frontal surface still produces long
stretched sheets in oblique and profile views. The visible failure is not
resolved. Reject promotion, despite numerically exact own-view alignment.
This rules out the native-ray/pinhole approximation as the *sole* cause of
the tested visual failure, not as a contributing factor.

Private immutable evidence:

- `mapanything-pinhole-v1/predictions.npz` SHA-256:
  `2147052ba3a504e59aed4ad393290c910a40a8416df8939185c03da037b85bfe`.
- `mapanything-pinhole-dense-audit-v1/report.json` SHA-256:
  `8263d871c24f338ef0b36f1b688bab7fbcc1d414fe1e9162aa598e87e59caff3`.
- `mapanything-pinhole-audit-v1/comparison.png` and five separate open OBJ
  surfaces. These are not a fused head and no texture was applied.

## Decision

Do not repeat ray replacement or use own-view exactness to promote cameras.
Do not blend these patches into the template as if they were accurate scan
data. Before further inference, inspect the remaining depth discontinuities
and whether they occur inside the facial region or only at mask boundaries;
separate that surface limitation from the independently failed camera check.
No new weights, dependencies or public helper were needed: the experiment
reuses the existing tested unprojection, triangulation and renderer. The last
full suite remains 88 passing tests; the two unprojection tests were rerun for
this experiment. No shared implementation changed.
