# Experiment0262: strict low-peak loading and query invariants

Date:2026-10-20. Registered before environment/source installation or execution.
0261 completed at548c73a;prior turn is progress,not head/model acceptance.

## One variable and safety basis

Compare ordinary strict CPU loading with mmap/meta/assign strict loading of
identical deterministic fixture tensors. Main variable is loading strategy,
not model identity,precision,architecture,thresholds or a reconstruction fit.
Use the exact Apache source403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3 reviewed0261.
No released13.95GB checkpoint,patient file,scan,case002,upload or training.

Pin isolated runtime Python3.12.13,Torch2.10.0+cpu,NumPy2.2.5,PyYAML6.0.3.
Do not copy upstream Torch2.6 pin:the official
[GHSA-63cw-57p8-fm3p advisory](https://github.com/pytorch/pytorch/security/advisories/GHSA-63cw-57p8-fm3p)
reports a weights-only loading vulnerability through2.9.1,fixed from2.10.0.
This security choice is made before model trials,not a numerical rescue. It
does not establish complete absence of vulnerabilities or model compatibility.
Do not install TorchVision,training,visualization,service or CUDA components.
Keep runtime/temp/download paths inside this repository;shared environment and
retired0259 integration stay unchanged. Retain bundled notices and source hashes.

## Fixed checks

Use the actual source class with an explicitly tiny **test-only** configuration:
2frames,8x8 RGB,encoder/decoder width16,2layers,4heads,MLP ratio2,patch1x4x4,
8 Fourier bands,9x9 source patch and13 output components across6 heads. Seed262,CPU FP32,eval,
8threads,no gradients. Save its tensor state and harmless training-style extra
states to a tiny zip checkpoint;never fit/train or use it on human images.
This is a loader fixture,not a substitute reconstruction model.

Require checksum verification before weights_only=True/mmap=True deserialization,
strict complete key/shape matching,FP32 preservation and finite model tensors.
Construct on meta,assign the same storages,then recreate only the exact source
nonpersistent Fourier-frequency buffer. No unresolved meta tensor may remain.
All learned tensors must be bit-equal to ordinary construction and share loaded
storage pointers,not silently reinitialize,cast,interpolate or approximate.

Evaluate fixed9 queries with different source/target/camera times on a fixed
arange RGB clip. All13 output components must agree with ordinary strict loading
within1e-6 absolute/relative. Splitting the same9 queries into fixed chunks of3
must preserve every query and output within1e-6;no changing support populations.
Missing key,extra key,wrong shape,wrong dtype,nonfinite tensor,wrong checksum and
unsupported non-tensor serialization must fail closed without unsafe fallback.

Finally construct the **full pinned32-frame architecture on meta only**. Verify
1162433293 parameters/4649733172 FP32 bytes and all parameters remain meta. Do
not allocate those data or substitute this empty graph for actual model inference.
Record actual process peak working set and wall time separately from the source
arithmetic. The fixture process must stay under2GB peak working set/120s.

## Budget,exit and next gate

One isolated setup<=20minutes wall time;one fixed check process<=120s. Whole
phase<=30minutes from installation start,including records and verification.
Ordinary pre-valid engineering errors may be repaired with exact logs;no model,
dtype,shape,gating or tolerance sweep. Do not retrieve any full released model
checkpoint in this phase even if checks pass.

Pass isTECHNICAL_CHECK_PASSED IO/structural invariants only;real checkpoint
compatibility,full inference memory/runtime,cameras,geometry and actual visual
acceptance remainUNVERIFIED. It may justify one separately registered bounded
hash-locked32-frame known3D model screen after fresh resource checks,not a head
claim or a return to a rejected recipe. Failure preserves compact logs/source
recovery then removes exclusive failed code/source/runtime/fixture before any
new route. Preserve original inputs,shared tests and successful prior fixtures.

## Actual result and replay

Result:TECHNICAL_CHECK_PASSED for the declared synthetic IO/structural scope.
Pre-execution source recovery:ce1aab5;preregistration:85f2ece. The exact16 source
file hashes and pinned config match `examples/opend4rt-loader-0262.source-lock.json`.
The actual source constructor is used;the tiny state is not a trained model.

- Isolated setup exits0 in141.625s;Python3.12.13,Torch2.10.0+cpu,NumPy2.2.5,
  PyYAML6.0.3 and pip dependency check are confirmed. Installed package versions,
  metadata and bundled license/notice paths are retained locally. No TorchVision,
  CUDA,training or service dependencies are installed in the shared environment.
- All learned tensors are bit-equal,assigned storage pointers alias the loaded
  tensors,and the nonpersistent Fourier buffer equals ordinary construction.
  Ordinary versus low-peak output max error0;9 queries split3+3+3 have maximum
  absolute error3.2782554626464844e-7,within the fixed1e-6 tolerance. No query is
  discarded,parameter changed or tensor downcast.
- All7 negative fixtures are rejected:missing/extra keys,shape,dtype,nonfinite
  values,checksum mismatch and unsupported serialization. There is no unsafe
  unpickling fallback. Synthetic fixture SHA256:
  `7f3176c8f90b3f55528c63cc4c22c310ad768dbe5fb34cfd4290f8c287e73400`.
- The full pinned architecture is constructed **on meta only**:1162433293
  parameters,4649733172 FP32 bytes,all parameters remain meta. This is not actual
  checkpoint tensor inspection or evidence its values/keys/dtypes are compatible.
- Valid worker:5.655s inside script,6.331s parent wall,282841088bytes peak working
  set. Those are fixture/empty-graph measurements,not a full-model memory saving
  benchmark or a promise of actual inference speed/capacity. Shared133 tests
  pass in7.019s;no reconstruction-quality threshold or production default changes.

One ordinary pre-valid environment error is retained rather than erased:
the first6.403s attempt imports Dynamo through meta arange;its default cache
path calls getpass.getuser without an available Windows account environment,
then tries the Unix-only pwd module. Set TORCHINDUCTOR_CACHE_DIR explicitly
inside this repository before importing Torch. No architecture,model,dtype,
numerical tolerance or framework version changes. The next fixed run passes.
Original logs and the precise repair reason remain private.

Private records:`assets/private/opend4rt-loader-0262/` contains the executed
protocol,setup/check parent invocations and terminal records,source/licenses,
installed packages/notices,small fixtures,report and shared-test log. Replay
in the retained isolated environment:

```powershell
.venv-opend4rt0262/Scripts/python.exe tools/check_opend4rt_loader_0262.py
```

No released checkpoint,patient file,scan,bone or case002 is read;no training,
upload or head fit occurs. Existing raw-human integrity is not rehashed in this
phase because private inputs are deliberately outside its read scope. The new
code is isolated from shared source/defaults and original data. Keep this
successful prerequisite,not an accepted reconstruction. Real checkpoint
compatibility,full inference resource use,physical3D correspondence,cameras,
2mm head accuracy and actual full-head visual acceptance remainUNVERIFIED.
