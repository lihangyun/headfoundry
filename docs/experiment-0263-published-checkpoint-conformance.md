# Experiment0263: released checkpoint conformance before costly inference

Date:2026-10-20. Registered before binary download/execution. Previous0262 at
feaf3a3 is completed progress,not model/head acceptance. Goal remains active;
current ordinary account use is allowed. No duplicate work process is live.

## Hypothesis and one variable

The published fixed32-frame OpenD4RT artifact may strictly match the reviewed
architecture without changing keys,precision or weights. Main variable is
replacing0262's artificial loader state with the actual published state,not
another model,accuracy threshold or unknown-pose/head fit. This necessary
conformance check is distinct from retired2D recurrent tracking;it does not
establish physical3D correspondence. No source/variant/precision sweep.

Use source403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3 and all0262 source hashes,
the same model.yaml,isolated Python3.12.13/Torch2.10.0+cpu/NumPy2.2.5/PyYAML6.0.3.
PublisherHF revision7099b1fc760475de3b7409acd6b63f801b015d07,object
checkpoints/OpenD4RT_32CLIP_9Dataset_NoAUG/opend4rt.ckpt only,13950006682bytes,
SHA2561f63305422fdc2000b057fbbc1d37459ac1a8063bbfcd0e3b7d473f5485943f5.
0261 records explicit Apache code/model grants;no gated account,paid service,
extra VideoMAE initializer or unreviewed asset is allowed. Retain notices.

## Resource and safety gates

Fresh snapshot:34269908992bytes physical RAM,5045317632bytes available,
451656204288bytes disk free. Full FP32 parameters alone require4649733172bytes;
there is inadequate prudent headroom for actual inference. Do not force it,
kill unrelated jobs,change precision or equate available disk with RAM.

Download the single exact object using existing system curl,HTTPS verification,
one worker,resumable partial file and hard1800s parent deadline. No credentials
or private material are sent. Verify exact whole-file length/SHA256 before any
Torch deserialization;rename only after success. No unchecked partial-file load.
Network retries may resume the same object within the original deadline,not
change revision/model. Disk free must exceed25GB before starting.

Then one<=300s process uses explicit weights_only=True,mmap=True and
map_location='meta'. The installed Torch source shows mmap overall storage
slices are mapped and restored to meta without reading parameter values.
This is **metadata structural inspection**,not full weight materialization or
the finite-value/actual-resource gate. Require available RAM>=2GB before this
process and process peak working set<1GB. Construct the full source class on
meta,strictly load every exact key/shape and preserve FP32 dtypes. Require all
1162433293 parameters/4649733172bytes and no unexpected learned/buffer state.
Record top-level payload categories and exact metadata inventory/hash locally;
never execute stored optimizer/config or allow arbitrary pickle globals.

Unsupported serialization,wrong hash/length/key/shape/dtype,non-meta parameters,
resource overrun or incomplete evidence stop this fixed attempt;no unsafe
weights_only=False fallback,prefix stripping,missing-key waiver or tensor cast.
Ordinary pre-valid IO/OS errors may be repaired with logs,not numerical rescue.

Whole phase<=40minutes from download start including verification/records.
No human video/photo/scan/bone/case002 is read,no training/upload or model
forward. In particular,do not use the scan as an initializer or label a meta
graph as real inference. Production defaults and shared source stay unchanged.

## Exit and next real gate

Pass onlyTECHNICAL_CHECK_PASSED structural released-artifact conformance.
Actual parameter finite values,materialized peak/runtime,known3D material and
occlusion,camera3px,scan2mm,whole-head editability/visual acceptance stayUNVERIFIED.
Retain a successful candidate for the next separately registered known3D screen
only when fresh available RAM>=8GB;never infer it from the tiny0262 peak. No
resource bypass,automatic cloud/paid execution or user-process termination.

If the recipe actually rejects,record cause/source recovery/compact evidence,
remove the exclusive failed artifact and integration under0250 rules,verify and
commit before a new route. Preserve raw inputs/consent,shared/successful fixture
evidence and unrelated0207. Transient network/resource unavailability is not
proof of model inaccuracy,head improvement or completion.
