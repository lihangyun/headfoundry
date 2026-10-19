# Experiment0222: frozen-model localization on reserved frames

Date: 2026-10-19. Pre-registered before observations/localization.
Status: `REJECT` for frozen-model reserved-frame localization.

Freeze0221's52-view model,2540 points and focal964.646px. Its training screen
passes, but no withheld or scan accuracy is established. Test whether existing
3D points predict new video observations with only per-frame pose estimated.
No shape, point, intrinsic or source-model bundle adjustment is permitted.

Use the original held frames624 and1040 from0216. Resolve their exact sequential
identity and the last training frame612 with unique RGB hashes; do not trust
nominal seek indices alone. Unknown/ambiguous/nonmonotonic or >2-frame offsets
stop the run. Hash all frozen binary model and camera/point archives before and
after the run.

Start with every reconstructed3D point actually observed in frame612, with its
original2D location. Track these identities through the later raw video using
the unchanged0220 forward/backward LK settings. No new points or descriptor
replacement are introduced. Export pixel-center coordinates with+0.5. At each
held frame, split retained point IDs by even/odd parity, a rule fixed before
observing reserved pixels. Even IDs fit pose; all retained odd IDs evaluate it.
Validation points may not be removed by pose RANSAC or their residuals.

Pose uses fixed camera K, zero distortion, EPNP RANSAC3px/10000 iterations/0.999,
seed222, then iterative refinement on training inliers only. Require>=30 points
per partition,>=30 training inliers, validation span>=50px in both axes, proper
rotation, positive depth for the entire frozen cloud and held validation p95<=3px
in both frames. Missing track support is a failed validation screen, not evidence
that the frozen3D shape itself is wrong.

Budget: one observation/localization run,300 seconds overall. Do not loosen flow,
inlier, validation, survival or camera thresholds after results. Track survival,
image spread, errors and actual held-image projection sheets accompany results.

These frames share one video and observations are temporal transfers from source
points. They are not independent subjects, anatomical scan truth or absolute
physical-camera calibration. A pass only supports this frozen-model validation
stage; actual scan comparison and complete head/visual evidence remain required.
Case002, all original/rejected outputs and production defaults remain protected.

## Read-only follow-up diagnostic protocol

The run rejected both frames. Do not change observations or fit a new3D model.
Check the identical point-ID split in reference frame612, then fit an essential
matrix to even-ID612/held pixel pairs with fixed K,1px RANSAC,10000 iterations,
seed222. Report symmetric point-to-epipolar-line errors on every odd-ID pair,
with the same3px p95 target. This determines whether transferred pixels have
gross pairwise rigidity violations independently of frozen3D predictions. An
epipolar pass is weaker than2D reprojection: it does not verify displacement
along an epipolar line, non-degenerate baseline, point depth or anatomy. No
result may override the failed localization screen. One read-only audit only.

## Observed results

The single run completed in8.393s, with original binary model/NPZ hashes unchanged.
Exact source RGB identity maps nominal612->ordinal613,624->625,1040->1040.

| Frame | Pose / validation points | Pose inliers | Validation p95 | Decision |
| --- | --- | --- | --- | --- |
|624|115 /128|68|9.658699px|REJECT|
|1040|55 /47|17|not scored: insufficient pose inliers|REJECT|

The reference612 replay using the identical parity split passes at2.707275px
validation p95. No source612 residual exceeds2.951975px. Thus a simple mismatch
in the pose helper or pixel-center convention does not explain the new-frame
failure. Of245 source points,243 survive to624 and102 to1040; high track survival
does not guarantee correct material identities. Source612 support has median
track length4 and median maximum viewing-ray angle10.978440deg; this is a
diagnostic, not an additional post-score eligibility filter.

Read-only two-view essential fitting also rejects: untouched odd-ID point-to-line
p95 errors4.467832px (624) and15.704559px (1040), despite fitting even IDs only.
This establishes a failure of the implemented pixel-rigidity screen, not a
unique causal diagnosis: drift, nonrigid expression, rolling shutter, camera-model
mismatch and poor estimation remain possible. It is not justified to repair
head geometry to absorb these observations.

Actual held photo overlays were inspected. Facial supports cover forehead,
nose, cheeks and mouth; no background supports are accepted as anatomy. The
private `reserved-frame-review.png`, observation archives, poses, controls,
`report.json` and `rigidity-audit.json` preserve the evidence. No full head,
millimeter scan error or likeness improvement is established. Case002 remains
out of fitting. These two frames are now development diagnostics, not fresh
unseen test evidence for future changed observation methods.
