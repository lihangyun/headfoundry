# Experiment0270: fixed detector-free pair readiness, not a recovered camera

Date:2026-10-21. Preregistered before installation/download/private decoding.
The target remains an editable video-derived head with independent medical
evaluation. No new head is expected from this prerequisite alone.

Hypothesis: the historical HF EfficientLoFTR release reviewed0269 can directly
associate frames across0267's disconnected track component without depending
on a surviving sequential ID. Main variable is pair-conditioned detector-free
correspondence, not DIS/LK parameters, increased temporal density or a model sweep.
Counterevidence: it is outdoor-trained and no physical skin accuracy is known.
0268 local observability does not certify any real match or graph connectivity.

Use only model revisionface1a79050ffa3e9da28720d1cf93aaf2e8f421 and exact
safetensors SHA25600a5edc343fa222eba763643553548ad37a05aa3d00d266553c9f6cf67bb0e64
(64263488bytes), Transformers4.57.1, CPU Torch2.10.0, NumPy2.5.2, safetensors0.6.2,
Pillow12.1.0 in one exclusive environment. Lock installed transitive versions and
review metadata/notices; no nativePRL source, pickle, second checkpoint, remote
code, online worker, training or sample images. Main environment stays unchanged.
Use explicit finite strict state-key/shape/dtype checks before model use.

## Frozen inputs and transforms

Only selected consented case001 video, original rights metadata and0252 frame
hash index may be read. No STL/bone/scan-derived fixture orcase002 in this phase.
Sequentially verify the four exact source frames612,876,888,1040 against0252;
hash the original video before/after. Full frames720x1280 resize by explicit
Pillow bilinear to384x672, preserving approximately original aspect. Model output
is raw floating normalizedxy; multiply by720x1280 without the library display
helper's int32 cast. Record the small anisotropy, no post-hoc coordinate fitting.

First pair:612 and one deterministic known planar warp of itself, scale.97,
rotation3deg about image center and translation(+4,-3) native pixels, OpenCV
bilinear sampling. Use the original model's .2 coarse matching threshold and
report every valid forward correspondence with source in the fixed
[100,500,620,820] ROI and eroded R-B>12 largest-component cue. This is only a
skin-like cue, not segmentation truth. Do not prune based on predicted endpoint
accuracy or confidence after viewing errors. Require>=50 unique source outputs,
source span>=100px in both axes, known-warp error p95<=1px and maximum<=3px.
All selected outputs count. Coordinate/half-pixel and duplicate/finite controls
must pass. A positive result proves only planar precision on selected outputs,
not all-point recall, real3D motion or physical camera quality.

Only if the planar prerequisite passes, execute exactly two direct real pairs:
876→888 (component boundary) and612→1040 (separated return). Keep every eligible
match in both source/target fixed ROI/cue, count duplicates and spans. Freeze
even/odd output-index split before geometry: fit F on even only using OpenCV
USAC_MAGSAC threshold1px, seed270, confidence.999, max10000iterations; score all
odd eligible outputs with symmetric epipolar distance, without RANSAC/confidence
pruning. Require>=50 unique pairs,>=20 per split,100x100px spans in each image,
finite rank2 F and held p95<=3px. No alternate pair, crop, threshold, seed, higher
resolution or refinement. F-readiness is not calibrated camera/rigid identity:
epipolar agreement can be wrong or nonrigid and must not unlock head fitting.

## Budgets and stop

Whole phase installation through review <=20min from the persisted start before
installation; installation+asset transport<=5min. One offline worker per fixed
stage, combined strict load/planar/pairs<=180s,8CPU threads, peak working set
<=4GB; stop on deadline/nonfinite/mismatch. No GPU repair or precision change.
Implementation may precede that timed phase, but no download/input/inference does.
One two-panel source/match review<=3min if real pairs are reached. Preserve raw
float outputs/error populations, exact identities and timings before verdict.

Failure stops this exact recipe, not all learned matching. Keep compact local
reports/numeric evidence/hashes/source recovery and at most two source panels;
remove exclusive runner, active lock, downloaded weights/source, environment,
cache and raw failed outputs under0250, verify shared tests and commit before
a different route. Positive limited readiness may retain only necessary assets
for separately preregistered physical identity/rigidity/camera evaluation.
No scan2mm,3px camera, whole-head, ears/neck, mesh or actual human acceptance is
waived. Defaults/unrelated0207/original material remain unchanged; no upload.

Before any model construction/forward, the first worker fails importing Torch's
Dynamo cache helper: this controlled host lacks a Windows username variable and
getpass attempts unavailable pwd. Preserve that failure/log, make one ordinary
pre-valid-launch cache-location repair with TORCHINDUCTOR_CACHE_DIR inside this
exclusive experiment. No model/config/preprocessing change and no budget reset:
the original first-worker wall-clock180s deadline still includes this repair.
