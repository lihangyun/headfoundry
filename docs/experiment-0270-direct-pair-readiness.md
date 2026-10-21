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

## Actual result: REJECT before real-pair inference

Source recovery:`696654a` (initial runner`cd082b1`, registration`0a2a997`).
The single exact safetensors file matches SHA/length; all full state keys,
shapes,dtypes and finite values pass strict loading. Installed26-package isolated
runtime metadata/notices are preserved. All three executed HF model/processor/
config files match0269's pinned source hashes. Transport/install completes in
172.308s, under300s. No nativePRL source/account/form is used.

The initial pre-valid import failure remains recorded. One explicit local-cache
repair changes no neural/config/input values and does not reset the original
worker deadline. Completed worker total elapsed including repair is112.552s;
actual peak working set1406382080bytes. Execution isTECHNICAL_CHECK_PASSED only.

All four selected source ordinals match0252 RGB hashes;original video SHA remains
unchanged. One planar forward produces4032 raw slots,202 eligible unique source
points,spanning270.000x304.762nativepx. **Every202 eligible output counts:** known
warp p95=22.407370px,max=29.578450px, failing1px/3px. No output pruning,offset,
index reassociation,refinement,alternative frame or corrective forward follows.
The two real pairs are not executed. No physical3D,camera,scan2mm or head result
is obtained;this does not measure full material recall or prove all EfficientLoFTR
implementations/weights incapable. No source/match panel is required or reviewed,
because the registered real-pair branch is never reached.

### Concrete source-level warning,not a repaired result

Read-only diagnosis finds a coarse pairing contract problem in the exact HF
source:`_get_matches_from_scores` forms column argmax and row argmax arrays;
`_coarse_matching` treats equal array ordinals as paired coordinates/patches.
An interior3-cycle at coarse9x9 tokens30,31,39 gives true mutual pairs
(30,31),(31,39),(39,30), but that construction gives(39,31),(30,39),(31,30):
0/3 are the true pairs. All three tokens survive the fixed2-pixel coarse border;
this is not a border/threshold argument. The tiny algebraic witness is retained
privately. It demonstrates a concrete source-path hazard without assigning the
entire observed22.4px error to it, or proving a corrected port will pass.
No source patch or post-hoc repair is applied to this failed trial. Next audit
must independently test pair identities and fine-window index contracts before
any new inference,not treat a checkpoint/parameter sweep as the answer.

## Verified retirement

Private`assets/private/closed-experiments/0270-direct-pair/evidence.zip` keeps
90members,304888bytes,zero images;SHA256
`5be47bbea3ad91b9111b1d5f2e75120fbd35fda495add26f16407dd6dac45564`.
CRC and every member digest pass. It retains raw float numerical outputs/errors,
controls,original import failure,exact identities,ordering witness,runtime
metadata/notices and protocols,not full failed inputs,weights or environments.

Five validated private targets remove37069files/1268099109logicalbytes:exclusive
environment,whole raw0270 folder/cache/model/input and three downloaded HF Python
snapshots in0269. The exclusive runner is removed from the active tree. Public
grants/metadata remain small historical evidence;they do not imply runnable assets.
No matching Python/Blender/install worker is running before deletion;resolved
paths stay inside this repo,with reparse targets refused. Four selected protected
hashes (rights/confirmation,successful0230 fixture,unrelated0207) and original video
SHA remain unchanged. No STL orcase002 bytes are read in this phase.

Git recovery plus pinned public redownloads is needed for historical replay;
this compact archive is not a full binary backup. Shared runtime,source/defaults,
original human data and prior successful fixtures are untouched. Final shared
regressions pass134tests in5.404s after removal;no live imports remain. Cleanup
and verification complete632.424s after the registered start,under1200s.
Overall target remains
unfinished;no new head,visual improvement,PARTIAL_SUCCESS orACCEPT is claimed.
