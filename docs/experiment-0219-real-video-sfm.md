# Experiment0219: masked real-video structure from motion

Date: 2026-10-19. Sparse execution/checks: `TECHNICAL_CHECK_PASSED`.
The pre-registered viability screen is `REJECT`.

0217's scan-render detector associations fail visibility and withheld checks;
0218's color boundary fails lip/chin uncertainty checks. Real video supplies
continuous appearance tracks unavailable in the five independent generated
references. Test that observation mechanism using existing pinned BSD COLMAP4.2
and SIFT. No scan geometry, detector depth or learned camera checkpoint enters
the reconstruction.

One main variable: camera/structure initialization from continuous real-video
texture tracks. Extract52 frames0..612 inclusive at stride12 from case001.
Frames624/1040 are excluded from reconstruction for subsequent localization
checks. Case002 remains reserved.

Feature selection is a conservative foreground interior, not accepted whole-skin
segmentation: positive R-B>12 in fixed ROI[100,500,620,820], largest connected
component then8-pixel square erosion. This excludes blue room/cap and most
clothing/neck. Actual feature locations must be reviewed.0218 rejects accurate
boundary claims from the color cue, not every interior pixel; do not reuse its
trace as a verified mask boundary.

Use one SIMPLE_PINHOLE shared camera, initial focal1500px and centered principal
point(360,640), zero distortion. CPU SIFT at most4096 features/image, four threads,
default peak/ratio settings; sequential overlap8, quadratic pairing, no loop
retrieval. Two-view RANSAC error2px; initialization needs50 inliers and retains
the default16-degree angle. Absolute-pose/filter errors are capped at3px with
30 pose inliers. Refine shared focal only; seed219. All other options are saved
before execution. No parameter/model/mask sweep follows a failed run.

Budget:600 seconds overall cancellation,300 seconds mapping, one run. Preserve
partial database/model/log evidence on failure. Preliminary viability requires
>=80% registered frames,>=200 points, both profile temporal intervals120..168 and
396..444 registered, proper rotations/positive observed depths, training p95<=3px
and focal inside[400,4000]px without a limit hit. These are development screening
conditions, not physical camera/visual acceptance. Independent withheld evidence
and actual source-scan/white-mesh review remain required before head fitting.

Prediction: coherent real texture permits a connected facial reconstruction.
Falsification: no connected model, insufficient bilateral coverage, background
domination or failed metric/physical checks. A numerical/feature failure stops
this configuration; do not deform head geometry or import reference scan points
to make it appear successful.

## Executed result

One run extracted features, matched sequential pairs and produced one saved
COLMAP model. Only10/52 frames registered (19.23%), spanning frames48..156;
there is no opposite-profile interval coverage. The model has92 points and525
observations, mean track length5.71, focal694.51px. Observed depths and rotations
pass their implemented checks; training reprojection p95 is1.508px. Neither low
training residual nor a local model overrides failed coverage/point-count gates.

SIFT feature counts range7..141. A read-only source-mask/keypoint sheet for
frames0,144,408,552 was actually viewed. Extracted locations are on the moving
face/ear region rather than the blue room, but the registered-side sample has
many ear/hair-adjacent features and little central-cheek texture. Opposite-side
samples have fewer features (34/32 in the reviewed frames). Color-interior
selection excludes neutral/dark patches. The review does not establish that
masking alone caused failure or that all retained features are rigid anatomy.

Stop this SIFT/sequence/mask configuration. No denser sampling, ratio, focal,
feature threshold, pose-bound or mask sweep and no geometry fitting follows.
The next distinct evidence check is whether explicit temporal feature tracking
can supply reliable bilateral tracks under independently measured tracking error.
Do not use a supplied scan to fill the missing reconstruction or label92 sparse
points as a complete head.

## Engineering repair and preserved evidence

The original run finished mapping but its final summary hit a Python API error:
`CancellationToken.is_cancelled` is a bool property, not a callable. The exact
executed runner is retained privately and verified against the pre-run controls
SHA. Correct the report writer and load the already saved binary model/database;
do not rerun extraction, matching or optimization. Recovered camera/point arrays
must replay the already exported NPZ at1e-12 tolerance without overwriting it.
That recovery succeeds and records `report_recovered_without_rerun:true`.

The original process also printed a BLAS memory-unallocation warning. Its exact
stdout/stderr are retained; numerical reload agreement is a bounded check, not a
diagnosis of that library warning. No runtime/dependency swap is introduced to
make this rejected candidate pass. Original precise total elapsed time was not
recorded before the summary error and remains null, rather than invented.

Private evidence is in `video-sfm-0219/`: source-image/mask hashes, controls,
database, original sparse model, NPZ replay, recovered report, execution source
and `feature-mask-review.png`. Frames624/1040 remain excluded; case002 is unused.
All model outputs and identifiable artifacts stay local and excluded from Git.

```text
python tools/real_video_sfm_0219.py
python tools/real_video_sfm_0219.py --recover-report
python tools/real_video_sfm_0219.py --review-features
```

Recovery is only for a completed run lacking its summary; normal runs and review
outputs refuse overwrite. The feature review is read-only. Existing masks and
original scan/video inputs remain unchanged.

All137 public tests pass after these changes. No production head/camera or
acceptance thresholds were modified.
