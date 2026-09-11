# Experiment 0076: total-displacement and bending priors

Status: source-prior-only candidate `REJECT`; bending candidate `UNVERIFIED`.
No baseline, camera or identity acceptance. These are two sequential ablations,
not an attribution of a combined change to one variable.

## A: reference the unchanged source

0075 regularized each incremental solve's displacement. Test regularizing
total displacement from the original mesh instead, retaining current candidate
silhouette support selection, all observations, regularization 30, editable
region and step/triangle/movement guards. The first step is exactly identical.
Subsequent source-prior solves still develop the visible tip crease in enlarged
actual renders. This falsifies the claim that incremental accumulation alone
caused it. Final fitting norm 25.3802px, left/right nasal MAE 1.7938/4.6391px,
maximum displacement 0.025639, minimum area ratio 0.511049; no reversed faces.

## B: graph-Laplacian displacement penalty

Starting from A's procedure, add an optional `bending_regularization=300`.
The existing public sparse solver now supports a penalty on each vertex's
displacement minus the mean displacement of its one-ring neighbors. Include
protected boundary rows neighboring free vertices. This is a uniform graph
Laplacian proxy, not exact geometric curvature, collision prevention or an
anatomical prior. Default zero preserves every existing caller's behavior.
Reject negative and nonfinite weights. No additional library or model is used.

A deterministic test checks reduction of a local spike, exact preservation
of protected vertices, unchanged non-flat input as a fixed point, and invalid
weight rejection. Full suite: 78 tests pass.

| Diagnostic | Original source | Source-prior A | Bending B |
| --- | ---: | ---: | ---: |
| Fitting residual norm px | 34.4429 | 25.3802 | 24.8343 |
| Left nasal row MAE px | 2.8416 | 1.7938 | 2.2979 |
| Right nasal row MAE px | 6.4675 | 4.6391 | 4.6472 |
| Front alar mean px | 8.8148 | 6.1724 | 5.3135 |
| Left-oblique alar mean px | 5.1659 | 3.8913 | 4.6611 |
| Right-oblique alar mean px | 4.8562 | 2.3693 | 3.1560 |

B retains four steps; the fifth violates the total 0.03 movement limit and
is not retained. Final maximum displacement 0.029933; minimum source area
ratio 0.527021; zero reversed triangles. All 3973 protected source vertices
remain exact. The clipped exported mesh was separately checked and rendered.

Actual enlarged front/oblique comparisons show less of the sharp central
tip pinch from 0075/A, but the nose remains angular and unlike the photo.
The complete five-view comparison still shows a generic head. B trades some
profile/oblique point fit for smoothness versus A, so do not claim all-view
improvement over the previous candidate. All metrics are fitting diagnostics,
not independent held-out evidence. No claim of a natural or finished nose.

Private outputs `local-nasal-source-prior-v1` and `local-nasal-bending-v1`
contain numerical history and actual meshes; their support-audit directories
contain enlarged renders and ray visibility. B's full photo/source/candidate
sheet is retained locally. No identity data is committed.

Next inspect the residual angularity and source support around the nasal tip
and nostril boundary before increasing displacement or smoothness. A smooth
wrong anatomical correspondence is still wrong; do not introduce texture to
hide it. Camera accuracy, broader face identity and product completeness remain
unresolved.
