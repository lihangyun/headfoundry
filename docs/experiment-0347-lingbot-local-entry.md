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
