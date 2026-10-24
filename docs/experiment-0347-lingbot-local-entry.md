# 0347: fixed LingBot local entry

Registered2026-10-24T00:45:06Z,basea05b73d,before weight acquisition.
Same candidate as0346,not a new hypothesis or failed-route retry.
Primary variable for eventual reconstruction is its temporal camera/depth
initializer. This stage establishes the fixed local artifact/runtime boundary.

Whole40minutes,through01:25:06Z; acquisition max900s/4632303465bytes, one
checkpoint only, no fallback or credentials. SHA256 must equal
ee665103348e07e6b826d529b8e61de8f413d5432a4f2e84970d6c8fd2e1cd72.
HF revision204754b72bb24f561f8d7e7e1e4e4cd9e809adf9,lingbot-map.pt.
Source pinned by0346. Model-card Apache2 statement permits this local attempt.
Verify exact bytes and ZIP inventory before weights_only=True loading; no
unsafe deserialization retry. Reject executable/unexpected archive content.

Isolated runtime only,main environment unchanged. Select Torch2.8.0 CUDA12.8,
direct GCTStream,use_sdpa=True,enable_3d_rope=True,camera/depth enabled,
point/track disabled,4camera iterations,KVwindow64. Camera/depth heads FP32,
aggregator BF16 as in official non-FP32 mode; no precision sweep if failure.
No optional DINO weights,visualization,skyseg,Kaolin or model hub auto-fetch.
Strict complete state key/shape loading is mandatory. Model construction and
loading may be done without inference; record capacity honestly. Runtime
installation max600s,strict-load worker max180s/16GiB system RAM. On resource
failure stop; do not silently change backend,frames,architecture or precision.

No patient inputs,scan fitting,training or head export in this entry. Prior
to any physical prediction run,freeze exact owned fixture identity,views,
correspondences,crop affine/native calibration and complete scoring rules.
The source stage has not yet selected a physical fixture; this record does
not authorize choosing it after prediction. Actual3px/2mmgates unchanged.
If asset unavailable,retain compact diagnostic as UNVERIFIED. A software/model
failure stops this configuration; preserve evidence and clean exclusive failed
integration according toAGENTSbefore selecting another route.

## Implemented entrance, before model loading

Original NumPy/SciPy camera adapter uses XYZW C2W, independent fx/fy and
the actual PIL integer-center crop affine. Three regressions pass0.016s:
floating PIL ramp, OpenCV projection with nontrivial rotation/translation,
and invalid encoding rejection. These are implementation checks, not predicted
camera accuracy. No model forward or patient data was used.
Acquisition records ZIP inventory; before safe loading, separately inspect
the complete member types/names. A path-safe ZIP is not itself a safe pickle.

## Resource stop and bounded packaging recovery,00:57:49Z

Weight acquisition passed671.718s,exact4632303465bytes/hash;1348ZIPmembers
passed a separate allowlisted inventory check. No pickle execution.
The first installation worker was stopped at600.360s,peak172052480bytes;
retain its REJECT resource-budget result. Its final log now shows Torch
download COMPLETE and all13packages prepared in9m51s. This is new operational
evidence: the cache is prepared, not an unknown incomplete download.

Ordinary packaging recovery is separately bounded to240s,within the original
40minute whole-stage deadline: install the SAME Torch/TorchVision versions
from that cache with --offline, then install the already registered small
support packages. No Torch redownload,model inference/configuration/precision
change or quality-threshold retry. Preserve both worker logs; do not relabel
the first worker as passed. If cache installation fails, stop this recovery.

## Resume before first load,2026-10-24T07:25:15Z

The packaging recovery completed26.797s/142061568bytes,25packages compatible.
Product quota interrupted the agent before first loading. Previous goal turn
was a product-state check,not a live worker wait. Goal is nowactive;short/weekly
usage6%/17%. Original wall deadline has elapsed; do not claim it was met.
Register a10minute resume window for the previously unexecuted load and report,
keeping its original180s/16GiB worker limit and all model/configuration choices.
No acquisition/install retry or inference. Both earlier workers are terminal.

## Actual first strict load:TECHNICAL_CHECK_PASSED

2026-10-24,load-worker.json:48.156s,conservative worker-tree peak10307256320B,
exit0. Safe weights_only=True checkpoint loading matched all1342expected keys,
zero missing/extra/wrong-shape entries.1157943540parameters,RTX3070,
Torch2.8.0+cu128,aggregatorBF16 with other headsFP32 as registered.
CUDA allocated peak2814724096B. Optional DINO initialization was explicitly
omitted while preserving the fixed backbone architecture; full final state
coverage passed. No upstream snapshot was modified. Network connect was denied
inside the constructor/loading section. No model forward was executed.

Evidence remains in assets/private/lingbot-entry-0347: acquisition.json,
container-check.json,state-coverage.json,load-result.json,load.log,
load-worker.json,setup.log/setup-worker.json and separate packaging-recovery
logs/record. Initial installation timeout remains a resource REJECT; successful
recovery does not erase it. Model quality is UNVERIFIED,not ACCEPT.
The candidate is not rejected; retain verified weights,source and isolated
runtime for the next fixed physical prediction test. No failed head or
prediction exists to clean. Source recovery includesf97c21dplus this closeout.

Next gate: one pre-registered physical prediction with fixed inputs and all
observations scored,not another software-only pass. Existing owned0332fixture
is available but has procedural planar patches; its suitability must be stated
before use and its outcome cannot alone prove real-skin feasibility/impossibility.
Actual video3px,medical2mm,full editable head and visual acceptance remain open.
