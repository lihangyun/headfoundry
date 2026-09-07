# Experiment 0016: coarse-to-fine and symmetric endpoint matching

Status: insufficient correspondence support; no camera acceptance or baseline
replacement. This continues experiment 0015 with the same locked XFeat weights,
CPU runtime, original images, top_k=4096 and eroded face masks. No new weights
or services are used. Consent and asset digests were checked before inference.

The upstream coarse-to-fine matcher provides 171 / 273 / 49 face-region pairs
for front-left / front-right / left-right. Its fine matcher updates only the
first endpoint; the second remains a coarse detected location. A conservative
three-view join requires all corresponding endpoints within 2 px and a unique
partner on both sides. It does not average inconsistent points or use camera
errors to select matches. Only one cycle survives.

That cycle's original-photo crops were inspected: it lies near the same inner
canthus in all views. Its third-view reprojection p95 is 1.426259 px against the
already-rejected cameras. This single point cannot establish camera quality,
spatial coverage, calibration, or head reconstruction accuracy.

A second fixed experiment applies the same checkpoint's fine matcher in both
directions and requires confidence >0.25 for both endpoints. This yields
95 / 160 / 16 face-region pairs, but zero unique three-view cycles at 2 px.
The symmetric candidate therefore provides no camera initialization replacement.
This does not prove all pair matches are false or the photos are unusable.

The reusable NumPy cycle join preserves original observations and rejects
ambiguous partners, broken cycles, invalid shapes and invalid tolerances.
It does not claim closed cycles are necessarily physical correspondences.
Its deterministic test checks a true cycle, a broken third edge, duplicate
endpoint ambiguity, empty input and invalid tolerance. The full suite passes
36 tests. Runtime outputs and identifiable crops remain private and ignored.

The bounded sparse/coarse-to-fine XFeat checks have not supplied enough tracks
for the required camera gate. Further work should not inflate match counts by
loosening checks and then claim acceptance. A different independently licensed
correspondence approach or additional capture/calibration evidence is needed
before formal geometry and texture can proceed under the existing policy.
