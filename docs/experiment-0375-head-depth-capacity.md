# 0375 fixed head depth characterization

2026-10-27. New component: pinned Metric-Hypersim-Small0373,not retired DA3.
Hypothesis: its axial depth retains head shape after global affine ambiguity,
making it a possible independent constraint for the owned0368/0371 solver.
First test isolates depth with known cameras; it does not estimate cameras.

Use all six unchanged0230upright supplied-scan clay PNGs at720x1280, verified
against generation-report hashes. No rerender,crop,ROI,appearance or resolution
sweep. Model only receives RGB image through official518preprocessing,CPUFP32,
2threads,eval/inference_mode. Same pinned Small architecture/strict checkpoint.
One300s/4GiBworker; no GPU,xformers,training,network or patient-video access.
Python audit denies truthnpz/STL reads during inference. No truth in predictor.
Source scan-derived images are diagnostic inputs,not reconstructed heads.

After worker termination, evaluator reads frozen known-motion.npz (SHA recorded
in0230generation-report). Score every visible sample in each view; even original
IDs fit one affine predicted-depth-to-true-axial-mm mapping per view, odd IDs
are held out. No confidence trimming. This oracle calibration is deliberately
stronger than available at deployment,only measures shape capacity,never an
allowed reconstruction initialization. Calibration is not model training.
Require positive slope,positive corrected depths,held ray-lift point error
p95<=2mm and projection into each other camera on jointly visible held IDs
p95<=3px. Report raw depth error as well; source reprojection alone is trivial.
Point error is NOT fixed-region surface error and cannot satisfy final goal.
Controls: exact axial depths reproduce points/projections; constant depth
must fail full-rank affine fit. Save all errors/coefficients/populations.

No solver tuning or alternate checkpoint after results. Failed capacity stops
this recipe,retain compact evidence/source recovery and clean exclusive
integration before a new route. It does not prove all real-photo uses fail:
white-clay appearance and small head coverage are explicit domain limitations.
Pass would permit next correspondence/unknown-camera test,not head acceptance.

## Pre-output device-routing repair

First worker7.625s stops before first convolution computes: upstream infer_image
automatically chooses CUDA despite the empty CUDA_VISIBLE_DEVICES on this host,
while model stays CPU. This is our adapter error,not model accuracy failure.
A temporary input tensor reached CUDA; no predicted depth exists and no GPU
model convolution completed. Preserve original log/receipt. One explicit CPU
adapter uses identical upstream transform and interpolation,not vendor edits;
remaining worker budget292s,unchanged inputs/weights/precision/gates. No fallback
model or numerical parameter sweep. Record this protocol deviation honestly.

## Result: REJECT for this recipe

Repaired source5a8d6c6; six CPU forwards complete in30.796s with2406879232B
conservative tree peak. No further inference. Evaluator oracle ray-lift error
4.59e-13mm; constant-depth rank control rejects. All six positive-slope affine
fits fail held accuracy. Front/yaw-10/yaw+10/yaw-30/yaw+30/pitch+10 held counts
1178/1144/1167/1095/1092/1011; pointp95mm respectively
46.020544/47.505182/51.559683/59.848004/62.726813/44.957025.
Worst cross-view projection p95 is87.821092px. Raw axial p95 is558–1191mm.
These are point diagnostics,not reconstructed-surface errors or video results.

Known camera eliminates camera-estimation error from this experiment. A single
per-view affine correction is demonstrably insufficient for this fixed shape
output; not merely a global scale/offset mismatch. The relative contributions
of clay appearance,head image coverage,learned prior and interpolation remain
unisolated. No claim that a particular one is the unique root cause. No approved
geometry contribution from this model has been established for the project.
Retain owned0368/0371 solvers and0230fixture; reject this candidate integration.

Prediction SHA256c2849196cd77c139452e71685a92591bcd9c4932ac4ba72e628f40be6ce2f912.
Post-terminal evaluator additionally saves all sampled predicted/true depths,
pixels,IDs/errors for compact diagnosis; this does not rerun inference or change
scoring. Cleanup must preserve original fixture/model-license evidence and source
recovery before deleting exclusive0373–0375weights/runtime/source/runners.
Cleanup is pending; do not start a different route before its verified commit.

## Cleanup completed

Source recovery261499f. Private evidence at
assets/private/closed-experiments/0375-head-depth/evidence.zip:46members,
657040bytes,SHA2567a3e563400b9d7d1323c94dd546977fb2c4362fcbeb152308d18b99f0731698d.
CRC and every member SHA verified before deletion. Keeps all sampled depths,
truth depths,pixels,IDs/errors,results,licensing/provenance,source and receipts;
not full-frame predictions or a complete binary backup. Initial archive-check
path-separator error was repaired before deletion; failed check deleted nothing.

No experimental Python process remained. Eleven exact repository-contained
targets were resolved and checked for reparse points before native PowerShell
deletion. Removed22066files/7062807220bytes logical size:isolated runtime,
checkpoint,vendor source,complete predictions,six exclusive runners and one pyc.
49protected files hash-identical before/after:0230fixture,consent/manifest,
0368/0371results and unrelated0207. This is not a full original-dataset audit;
external original videos/STLs andcase002 were not opened or modified.
PowerShell receipt's protected_files serialized49individual ones rather than
a scalar count; plan.protected has49keys and all49hash comparisons executed.

No remaining live references to removed modules in tools/src/tests. Source is
recoverable from Git; deleted weights require redownload at locked hash and
full predictions require rerun. No new route or model experiment started.

Closeout verification:167retained tests pass in9.561s; whitespace check passes.
On2026-10-28resume,archive CRC/all46member hashes,all11target absences and all49
protected-file hashes were reverified before the cleanup commit. No deletion
or model inference was repeated. Unrelated0207 remains untracked and untouched.
