# Experiment0315:strict offline pinhole software admission

Registered2026-10-22T15:30UTC after0314closeout7ef8ab3,before dependency install,
tensor load or forward. Whole1800s,including evidence/tests/docs/local commit.
One exact0314checkpoint/ref only. This is not a camera/head accuracy experiment.
0311shows weak focal information;GeoCalib may add a learned prior,but neither
its gravity nor K establishes head SE3. Device metadata unknown per user.

Main variable:admit this new focal-prior software,not revive0308tracking.
Five candidate-only CPU packages in a private import overlay,main environment
unchanged:torch2.6.0+cpu,torchvision0.21.0+cpu,kornia0.8.0,kornia-rs0.1.8,
sympy1.13.1. Reuse existing NumPy/OpenCV/Pillow/other dependencies. Official
Torch matched pair per https://pytorch.org/get-started/previous-versions/.
Torch/vision/SymPy BSD grants and Kornia/rs Apache2notices inspected at official
tagged sources/PyPI. No model-zoo downloads or CUDA/precision/version sweep.
Install worker<=360s/4GiB;offline model worker<=300s/3GiB,4CPUthreads.

Before import verify all0313response hashes,0314weight/notice locks. Worker
blocks socket connections/download APIs,loads local weights_only=True to CPU.
Metadata-only0314pickle inspection shows exact backbone names including BN
buffers;require exact unmodified state_dict keys/shapes/dtypes/all finite,then
strict=True and bit-identical replay of EVERY parameter and persistent buffer.
No upstream flexible_load,missing running-stat exception or random fallback.
Negative controls:missing parameter,missing buffer,extra key,wrong shape/dtype,
NaN. Check dependency requirements/versions and record notice hashes pre-import.

One complete FP32eval forward,seed315(including stochastic NMF bases),on owned
procedural RGB343x259 gradient/checker image,upstream short-edge320/divisible32.
No input known focal/gravity,training or second seed. All output fields/confidence/
camera/gravity/covariance and positive model-derived focal uncertainty must be
finite;record complete native/preprocessed outputs,not default-zero uncertainty.
This artificial image has no declared physical K;no focal accuracy inference.

Coordinate oracle uses independent known rays/matrix projection,including
odd center crop and align_corners=False half-pixel resize. Upstream undo_scale_crop
uses continuous symmetric crop/scaling,not exact integer pixel resampling;record
both conventions and discrepancy,do not silently call either physical calibration.
Require independent pixel-transform replay<=1e-9px in float64 mathematical test;
this is not a new arbitrary NN precision or actual3pxgate.

Stop on identity/rights/state/nonfinite/dependency/resource error;no rerun to
rescue predictions. Ordinary runner-only engineering fixes require proving no
NN forward occurred. Successful software may retain one provisional overlay
pending a separately preregistered known-camera/domain test. On substantive
failure archive compact/source hashes then retire exclusive runner/overlay/
weights/source before a new route. No human images/scans/case002/uploads.
Protect originals,shared gates/defaults/0207. No ACCEPT/SE3/head/medical claim.

## Actual software result

Producer c3c4f2c. Both isolated wheel installs pass;Torch/vision63.875s,the
remaining three5.359s. Main package inventory unchanged. All889state items
(28925637learned scalar parameters,141persistent buffers) exactly match keys,
shapes,dtypes,finite values and post-load tensors. All six negative controls
reject before changing state. No prefix rewrite or ignored BNstatistics.

Offline worker14.531s,conservative process-tree peak940142592bytes. One full
RGB forward1.875s,seed315,all requested outputs finite with actual positive
focal uncertainty. The arbitrary gradient image has no known physical K;
its624.49pxprediction is NOT calibration evidence. No second model forward.

Coordinate algebra replay0px. Known software convention difference at343x259:
upstream versus integer-crop/half-pixel-resampling principal points differ
about+.31087px(x),-.09532px(y). Float32reported-scale rounding contributes
~1e-5pxfocal-matrix difference. Both mappings are saved,not declared physical
truth. These small differences do not explain earlier tens-of-pixels failures.

TECHNICAL_CHECK_PASSED software only. Physical focal/head SE3/3px/2mm/likeness
remainUNVERIFIED.148shared tests pass7.014s;28original ledger hashes plus4prior
generic amendments verified. Overlay13163files1200923828bytes retains notices
and a complete SHAinventory,not installed into main. No human input or upload.

Private software-evidence.zip3096552bytes/17members/CRCverified,SHA256
083348dd08ebc6db640a096ac94ca272dbc8140490e11d6f4f6340914f3c84fc.
Includes raw procedural outputs/metadata/executed source/protocol,not runtime
binary backup. Verified15:34UTC;closeout within registered16:00UTCdeadline.
Retain single provisional candidate pending separately registered domain test.
