# 0381: render-conditioned semantic observation admission

2026-10-28. Source/asset review only; no detector inference, new render, camera
fit, scan read or model training. Previous0380closed at de280dc. Stop additional
loss/threshold/seed experiments on the same22archived sparse correspondences.

## What was already tried

0241 already fitted a shared FLAME2023Open identity and video poses. Its fixed
frontal420semantic-to-material bindings gave failed held projection/visibility
and all seven facial surfacep95s above2mm. It was a real video-only experimental
head, not a production success. Its mesh/code were retired by0250. Do not restore
the old coefficients, scan-derived alignment or rejected fitting pipeline.

0242 is more specific evidence: at true neutral yaw+/-45degrees the unchanged
frontal binding's held errors were10.872/12.865px. Equal detector index is not
a fixed skin point across views. This is distinct from the sparse patch failures
and does not imply every way of using semantic detectors must be rejected.
0244already tried visible envelopes, so ordinary silhouette fitting is not new.

## Candidate distinct mechanism

Compare D(render(prior,camera)) with D(target image), where D is the same locked
semantic detector. Recompute detections on each candidate render instead of
transporting a frontal detector pixel as a permanent material attachment. The
candidate changes the observation model, not the old loss threshold or prior
coefficients. No claim is made that this provides measured physical identities.
It uses a shape prior as an explicit assumption, not scan geometry as an input.

First possible experiment is a bounded known-prior camera-recovery control,
with all pose and focal parameters estimated from rendered target observations.
True camera/mesh projections remain evaluator-only. No head identity fitting or
real-video inference before this check. A same-renderer success would only prove
conditional implementation capability; it cannot establish photo-to-clay domain
accuracy, unknown-person shape accuracy, expression handling or clinical precision.
Negative checks must expose incorrect cameras/degeneracy, not just low semantic
loss. Whole detector IDs held from optimization and true3D projection must be
reported separately. Full configuration/budget still needs preregistration before
execution; this review is not permission to sweep target angles or solve variants.

Potential failure mechanisms remain: detector discontinuity and crop changes,
render/photo appearance mismatch, focal-distance ambiguity, unknown identity,
expression, occlusion and failure at extreme profiles. Optimizing semantics may
fit the detector rather than the person. In particular, this mechanism does not
solve unobserved posterior anatomy or justify full-head2mm claims.

## Rights and actual local readiness

Official current model license checked:
https://flame.is.tue.mpg.de/modellicense.html
Only FLAME2023Open has the commercial-use grant; other listed FLAME models remain
under different research restrictions. Attribution/change disclosure and stated
use restrictions remain applicable; no rights are inferred for texture assets.

Existing fail-closed FlameIdentityModel loader verified the exact local converted
asset and source/archive/readme digests without conversion or pickle execution.
5023vertices/9976triangles; neutral300identity adapter only, not an implemented
expression model. Lock SHA256
b3a5c27654504beb5845a578f71f51c2b89c18d21679ae55690cd8d2c05a64f2.
Installed NumPy2.5.2/SciPy1.18.1/MediaPipe1.0.1 metadata confirmed. Existing task
file is present; its hash/runtime inference must be rechecked before use.
Shared rasterizer and asset loader remain; no framework installation is needed.

Decision: admit only preregistration of this distinct observation-model control,
not revival of0241 or actual-head acceptance. Preserve source/currentproduction,
human inputs and case002. No outputs exist to clean up in this review.
