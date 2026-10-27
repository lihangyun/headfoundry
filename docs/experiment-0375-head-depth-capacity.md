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
