# Experiment 0107: one assumed-focal conditioning trial

Status: execution `TECHNICAL_CHECK_PASSED`; camera and visual promotion
`REJECT`. No baseline/default replacement. Protocol below was written before
the single candidate run.

Visual target: a coherent nose/lip/chin surface across frontal, oblique and
profile views, without the stretched cross-view sheets in experiment 0106.
Hypothesis: raw extreme focal estimates contribute to failed pose/depth
recovery; supplying a plausible existing focal hypothesis may help. Counter-
evidence: correspondence errors, background/static-scene assumptions, depth
prediction and mask boundaries remain independent possible causes.

One primary variable: condition the same Apache checkpoint on centered
pinhole intrinsics with focal 1800 pixels at original resolution. This value
is the previously used head-fitting hypothesis, not newly selected from the
held tracks and not calibrated ground truth. No camera poses, depth, masks,
annotations or held observations are supplied to the model. Input photos,
weights, CPU inference settings and raw surface rendering remain fixed.

Prediction: the same 33 frozen third-view errors decrease and actual cross-
view surfaces become more coherent. Falsification: persistent failed alignment
or malformed surfaces. Passing focal plausibility because a focal was supplied
is not a recovered-calibration success. No held point may be discarded, no
mask/texture may conceal a failure, and the 3 px camera gate is unchanged.

Baseline: private `mapanything-apache-v1` and `mapanything-audit-v1`.
Candidate: the same runner with `--focal-px 1800`, new private
`mapanything-focal1800-v1` and `mapanything-focal1800-audit-v1`. Run once;
do not sweep focal values against held-out results.

## Actual result

The candidate completes in 85.175 seconds on CPU with unchanged model and
photo hashes. The complete 33-prediction camera p95 **worsens from 48.5814 to
51.4793 px**. Positive-depth fraction remains 1.0, but both focal plausibility
and alignment gates fail. Inspection of the actual five-view comparison again
shows rough ridged own-view patches and stretched cross-view sheets. Reject
promotion; supplying this hypothesis has not delivered visual improvement.

Importantly, **conditioning is not enforcement**. The upstream inference path
converts supplied K to rays and encodes them as additional features; its
returned intrinsics are fitted to newly predicted rays. The output focal
values remain approximately 5115–6373 original pixels, not 1800. Maximum
returned-versus-supplied K difference is 1888.82 processed pixels. Therefore
this result cannot falsify reconstruction with genuinely calibrated fixed
intrinsics; it rejects this one soft-conditioning run. No output K or points
were silently overwritten to imply the assumption was satisfied.

## Separate camera/depth-contract diagnostic

Private `audit_mapanything_dense.py` evaluates the same eleven frozen tracks
by bilinearly sampling native predicted world maps, then projecting directly
into the other two views. All 66 directed transfers remain; no triangulation,
point fitting or selection occurs. Their p95 changes from **96.9433 to 95.6737
px**, still materially inconsistent. These are a different metric from the
33 triangulate-then-predict camera checks and must not be interchanged.

The same diagnostic projects every native camera point back into its own
predicted pinhole camera within the fixed ellipse masks. Raw own-view p95
errors span **18.06–25.24 original pixels**; conditioned errors span
**18.60–25.61 px**. The fitted pinhole K is therefore not an exact projection
model for these predicted ray maps. Pose/world conversion had passed in 0106,
so passing that conversion alone misses this ray-to-pinhole discrepancy.
This is an integration limitation and model-output diagnostic, not proof of
ground-truth shape error or a complete explanation of the stretched surfaces.
All ellipse-supported pixels are included regardless of predicted confidence.

## Evidence and next gate

Private immutable evidence:

- `mapanything-focal1800-v1/predictions.npz` SHA-256:
  `1934d8506b418028b7066537b2307fa07d932d83845f3baa151b53dbd5602360`.
- `mapanything-focal1800-audit-v1/report.json` SHA-256:
  `4e8a8446386c358ed5773c2a76f7f3424321e60c8ca952d86098e9b0bf270a0f`.
- `mapanything-dense-consistency-v1/report.json` SHA-256:
  `445839cc0218760985194be7ec4e78a1bacf7a4a5d8ac2b2cf951c6125486c4c`.
- Actual inspected `mapanything-focal1800-audit-v1/comparison.png`.

The public runner adds an explicit optional focal hypothesis and preserves
supplied K separately from output K. It records the runner digest and
conditioning metadata; omitting the option retains image-only behavior.
One new test checks resize-consistent projection and invalid focal/dimensions.
All **88 tests pass**.

Do not repeat a held-metric-selected focal sweep. Before another model run,
isolate the native-ray/pinhole approximation using unchanged depths and poses:
an explicitly labeled pinhole reprojection experiment can distinguish that
component from inconsistent depth. Such an operation changes geometry, is
not a calibration fix, and must retain the native surface and compare all
original held observations and actual views. No acceptance or fusion follows
merely from making own-view reprojection exact by construction.
