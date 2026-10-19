# Experiment0221: reject planar-dominated initialization

Date: 2026-10-19. Preliminary viability checks: `TECHNICAL_CHECK_PASSED`.
Physical camera accuracy, scan accuracy and head acceptance: `UNVERIFIED`.

0220 provides a connected temporal observation graph, yet its3-frame model has
focal69701.81px. The actual initialization log selects image IDs9/10, which are
frames108/96. Their375 raw matches have100% support under a2px homography. This
supports testing initializer degeneracy; it does not prove that flow or rigidity
is otherwise correct.

Primary variable: deterministic initial image-pair selection. Reuse the exact
0220 corrected match database, all observations, calibrated camera prior1500px,
verified geometry, images/masks, seed219 and mapping settings. Do not use its
failed optimized3D points/poses/focal as an initializer. No scan geometry enters.

For every existing verified pair with>=50 inliers (the unchanged initialization
minimum), measure homography support at the existing2px error. Reject support
>=0.8, using the existing verifier's max-H ratio. Rank the rest by
`verified_inlier_count * (1 - homography_fraction)`, tie by image IDs. Select
exactly one maximum-score pair before mapping, save all scores and inspect its
source-image supports. If no candidate survives or visual support is unsuitable,
stop; do not try another candidate. Otherwise set only the two initial-image IDs
and run the unchanged mapper once.

Prediction: avoiding a planar-dominated initial pair prevents immediate focal
degeneration and permits a connected bilateral model. Falsification: no seed,
invalid source support, failure to initialize, or any unchanged0220 viability
gate failure. Retain>=80% frames,>=200 points, bilateral intervals, proper poses,
positive observed depths, training p95<=3px and focal strictly inside[400,4000].
Even a passing screen remains `UNVERIFIED` until withheld/localization/scan and
visual evidence are collected; it is not a head mesh or camera acceptance.

Budget: one pair-selection pass, one mapping attempt,300 seconds mapping, no
focal bounds/threshold/pair sweep or source/mask/flow change. All prior runs and
case002 remain protected. Inspect nonrigid/accumulated-drift alternatives if the
new initializer still fails.

## Executed selection and single mapping attempt

The fixed rule selects image IDs24/25, nominal frames276/288:311 verified matches,
homography fraction0.311897, score214. All candidate scores and the selected source
support sheet are saved before mapping. Actual pre-fit review confirms facial
image supports while retaining eye/mouth nonrigidity and drift concerns. Exactly
this pair is passed to the mapper; its log confirms one initialization24/25.
No alternate pair or optimized0220 focal/3D points is imported.

One mapping run finishes in24.78s and registers **52/52 frames**, including both
profile intervals. It recovers2540 points/17339 observations, mean track length
6.826 and mean training reprojection0.895px. Focal964.646px is within the unchanged
range; training p95 is2.260px, with proper rotations and positive observed depths.
All seven unchanged preliminary gates pass. The report correctly remains
`UNVERIFIED` pending external/withheld/visual evidence, rather than `ACCEPT`.

An exact SQL-table comparison confirms cameras, images, keypoints, raw matches
and verified two-view geometries are identical to the frozen0220 source database.
Only initialization IDs differ in mapping settings. Input observations/masks,
initial focal, verification and budgets do not change. The rejected source
model/report remain intact.

## Actual sparse visual review

The video-and-cloud sheet was viewed for frames0,144,408. It shows recovered
training-point projections and all2540 triangulated points under three recovered
rotations at a common orthographic scale. White points reveal facial fragments,
holes, scatter and unobserved regions. PLY export contains vertices only, no
triangles or completed scalp/neck/eyes. Source points are neither trimmed nor
completed with a template or the supplied scan.

This is a video-only camera/structure improvement over0220's3-frame,
implausible-focal model. It is not a completed editable head, a scan-distance
result, held-out camera acceptance, population validation or KeenTools parity.

Next freeze this model and verify reserved frames624/1040, including exact
decoded identity and focal-frozen localization. Then declare scan-evaluation
alignment/valid regions and evaluate the sparse facial geometry before the next
head-fitting hypothesis. Case002 remains excluded from tuning.

## Reproduction and tests

```text
python -m unittest tests.test_parallax_initialization -v
python tools/parallax_initialization_0221.py select
python tools/parallax_initialization_0221.py map
python tools/review_sparse_head_0221.py
python -m unittest discover -s tests
```

All141 public tests pass. Known nonplanar projection versus an exact plane checks
that selection rejects larger planar support and fails closed without a viable
pair. Actual mapping and sparse review complete successfully. No download,
training, upload or reference-scan geometry enters reconstruction.

Source/selected/mapped artifacts, controls, logs, selected-pair review and the
vertex-only PLY remain under the ignored private pilot's `initialization-sfm-0221/`
directory. Existing outputs refuse overwrite; there is one select/map attempt.
