# Experiment0220: temporally tracked video corners

Date: 2026-10-19. Tracking/input checks: `TECHNICAL_CHECK_PASSED`.
Reconstruction viability: `REJECT`.

0219 connects only one side. Several later frames contain fewer than30 SIFT
features, below the unchanged minimum pose-inlier count; replacing descriptor
matching alone cannot fix this observation-count ceiling. Test a different
observation mechanism: Shi-Tomasi corners tracked through intermediate video
frames by forward/backward pyramidal Lucas-Kanade flow.

Keep the same52 keyframes, exact masks, source video, camera model, initial focal,
geometric verification, image-pair list, mapping options, seed and viability
gates from0219. Replace SIFT observations/matches with temporal corner tracks.
No scan geometry or detector depth is read as reconstruction evidence; case002
and frames624/1040 remain excluded.

At keyframes, seed at most400 corners using quality0.01, minimum distance5px,
block7 in the existing mask, excluding a5px disk around active tracks. Use all
even intermediate video frames. LK uses21px windows, three pyramid levels,
30 iterations/0.01 convergence and minimum eigenvalue1e-4. Retain finite in-image
tracks with valid forward/backward status, return error<=0.75px and forward patch
error<=15 gray levels. Endpoints must remain inside the unchanged keyframe mask.
No automatic retuning or widening of masks/thresholds follows failure.

Before reconstruction require at least80% of adjacent keyframe pairs share>=50
track IDs, and a raw-track graph component spans>=80% of frames and both profile
intervals. Otherwise stop before geometry verification/mapping. Reuse precisely
the previous requested image pairs. Export OpenCV pixel coordinates with+0.5
pixel-center conversion to the COLMAP convention. New image observations are
owned by explicit track IDs; descriptors are not fabricated.

Budget:180 seconds tracking,600 overall cancellation,300 mapping. Retain original
database and create a separate candidate database for tracks/matches. Record
intermediate-frame hashes, per-step retention/return errors and final tracks.
Stepwise bidirectional consistency is not a guarantee against accumulated drift
or nonrigid facial motion; retain independent geometric/held-out/visual gates.

Prediction: temporal continuity supplies a connected bilateral observation graph.
Falsification: failed raw graph, registration/coverage failure, background/nonrigid
domination, invalid poses or failed viability gates. No head mesh may be inferred
from tracking consistency or low training residuals alone. A passing screen
still requires actual reconstruction/scan and reserved-view evidence.

## Decode-integrity repair before mapping

The first tracking run stops at an exact input-pixel assertion before producing
its complete track graph or any reconstruction. A read-only sequential RGB-hash
audit finds all52 frozen keyframes exactly and uniquely: nominal0..276 match the
same sequential ordinals; nominal288..612 match ordinals289..613. Thus OpenCV's
reported seek position was not a complete guarantee of decoded-frame identity.
The original0219 images and masks are preserved byte for byte.

Repair endpoint timing by resolving each frozen image against unique exact RGB
hashes before tracking; reject missing/duplicate matches, nonmonotonic order and
offsets beyond2 frames. Include odd endpoint ordinals in the otherwise even-step
stream. This changes no observation image, mask, flow/camera threshold or fit
parameter. Preserve the failed run, exact execution source and decode audit in
the original0220 directory; execute one engineering replay in a separate
`temporal-sfm-0220-index-corrected` directory. Times remain decoded ordinals/nominal
fps, not independently verified presentation timestamps.

## Actual result and stop

After the exact frame-identity repair, one execution completes in11.17s. All52
keyframes remain byte-identical to0219.335 sequential samples yield2929 corner
IDs and394-400 observations per keyframe. Adjacent keyframes share261-398 IDs;
the raw graph spans all52 frames and both profile intervals. All three input
preflight checks pass. No flow, mask, sampling or geometric threshold changed.

The same reconstruction pipeline registers only frames72,96,108:3/52 instead of
the required80%. It exports373 points but estimates focal69701.81px, well outside
the predeclared[400,4000] range. Training p95 is0.653px; proper rotations/positive
observed depth pass. This rejects the geometry/camera screen. More tracks and low
training errors do not establish reliable3D or an acceptable head.

Actual feature-mask sheets for frames0,144,408,552 were inspected. Compared with
SIFT, many more face/ear points are present on both sides, while neutral-colored
patches remain excluded by the same conservative mask. Ear/hair-adjacent and
potentially nonrigid regions remain; point density alone cannot prove rigidity
or eliminate accumulated drift. No shape fit, source-scan alignment or case002
evaluation follows this failed configuration.

## Read-only parallax diagnosis

No pair is refit into another reconstruction. A separate homography audit of205
existing pairs with>=50 raw tracks finds27 pairs explain>=90% of matches within
2px using one homography. The two audited pairs whose endpoints both registered
have homography support99.45% (72/96,363 matches) and100% (108/96,375 matches).
Their median image displacements are21.55px and3.24px respectively. Thus image
motion/track count alone did not prevent nearly planar initialization.

This motivates a separately predeclared degeneracy-aware initialization test;
it does not prove the sole cause, validate every other pair or authorize manual
initial-pair/focal sweeps. Preserve the rejected run and inspect independent
geometry/withheld evidence if another initializer succeeds.

## Reproduction and retained evidence

```text
python -m unittest tests.test_temporal_video_tracks -v
python tools/temporal_video_sfm_0220.py
python tools/temporal_video_sfm_0220.py --audit-parallax
python -m unittest discover -s tests
```

All140 public tests pass. Tests cover known translated texture, occlusion,
invalid/empty input, exact frame remapping and missing/ambiguous/oversized-offset
rejection. The synthetic displacement fixture has sufficient border margin for
the coarsest image pyramid; it does not alter production tracking settings.

The original failed input check and corrected execution have separate private
directories with exact runner source, controls and stdout/stderr logs. Corrected
tracks, sequential hashes, decode map, raw/verified match database, camera/point
archive, source feature sheet and parallax audit remain local.0219's source
database/frames/masks and earlier reports remain unchanged. The shared report
and feature-review helpers now accept optional output/source paths; their default
0219 behavior is preserved. No new dependency, trained asset, uploaded data,
default head/camera or acceptance threshold is introduced.
