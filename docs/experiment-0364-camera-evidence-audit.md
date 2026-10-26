# 0364 read-only camera evidence audit

2026-10-26. 0363 is REJECT and cleanup22ade36 is complete. Before another model
or estimator, test whether evaluation scope/gauge or association bookkeeping
explains the failure. This is arithmetic on archived evidence, not reactivation
of the retired integration. No fitting, model inference, point pruning,
parameter/threshold modification, image generation or patient access.

Budget: one script run,60seconds, existing NumPy/OpenCV only. Check archive
identity, source prediction hash and frame/source-index correspondence; verify
identity first camera and common unit-baseline gauge. Recompute held known-scene
errors and exact-camera zero control. Separately report first-view focal-only
error, training reprojection residuals, and identity of occluded observations.
These are diagnostics, not a revised acceptance decision or a rescue run.
Stop on unexpected identity/shape failure and preserve the original evidence.

## Result

Source00f0083; one run exit0 in1.342s. No process memory ceiling was instrumented
for this small archive-only audit; no measured-memory claim. Prediction hash,
frame/source indexing, first-camera identity and unit-baseline assertions pass.
93points were admitted,75training/18held. Recomputed known-scene p95 values
exactly reproduce0363:5.42818/8.45859/8.38117px. First-view error equals the
analytic focal-only radial displacement5.42818px to rounding. The reported
exact-camera zero uses the same projector twice: it is a redundant sanity
check, not independent validation of that projector (0363OpenCV replay is the
independent numerical comparison).

Training reprojection p95 is1.02901/0.93060/0.89405px, despite known-geometry
failure. This demonstrates that a low fitted residual is insufficient evidence
of correct calibration in this configuration. It does not isolate a unique
optimizer/model defect or prove that focal bias alone explains other views.

Four distinct occluded source observations have predicted visibility:
view1/source33=.970999, source60=.959738, held-source86=.967855;
view2/source38=.926364. High model visibility is not a reliable geometric
visibility guarantee on this fixture. No points were removed after the result.

Audit status TECHNICAL_CHECK_PASSED; reconstruction status remains REJECT.
Next selection must address independent calibration observability and/or
independent correspondence evidence, not tighten this model's confidence
threshold or accept low training residuals. No new estimator is selected by
this audit alone. No private case data was accessed. Private result is
assets/private/camera-audit-0364/result.json; original archive remains unchanged.
