# Experiment0288:full-state native-capacity control,not patient reconstruction

Registered2026-10-21T13:59:18Z before installation/worker controls.0286 is cleaned
at25e619c;0287 is preflight-only atd553727. Previous goal turn is progress:
actual pair evidence changes the observation direction,with no camera/head claim.

Main engineering variable:replace all-pairs correlation MATERIALIZATION by
chunked bilinear target-feature sampling followed by the same feature dot product.
Linearity makes the requested lookup algebraically equal;FP32 reduction/order
differences still require an actual loaded-network pixel-output audit. Preserve
query/reference state,weights,FP32,all pixels,spatial padding,16-frame window,
four iterations,temporal update and both confidence channels. Chunk512query
locations,not a point subset. No crop/downscale/window/precision/checkpoint sweep.

Use full alltracker.pth/revisions/hashes from0287 only. Install a private runtime
inside this repository:Python3.12 from existing interpreter,Torch2.10.0+cu128,
TorchVision0.25.0+cu128,einops.8.0,NumPy2.5.2,dependencies resolved/recorded. The
[official version pairing](https://pytorch.org/get-started/previous-versions/)
lists this Windows CUDA runtime. No torchaudio/training/demo dependencies.
Do not change system drivers or main venv. All caches/temp/source/weight/env
inside assets/private/alltracker-0288. Verify source and checkpoint full-byte
hash/size,rights entries and complete finite FP32 state with strict load.
Net(init_weights=False);block all later network/download calls. No missing state,
unlicensed external backbone or noncommercial/alternate checkpoint fallback.

Controls(seed288,one configuration,no human inputs):
1. Torch CUDA allocation/matmul and actual device/free-memory check. Disable
   TF32/autocast;record runtime/device/licenses. Not an NVML-based CPU fallback.
2. Compare original and sampled CorrBlock at64x96feature image,4channels,batch2,
   fivelevels/radius4,random fractional/outside coordinates,dilation1and1.3;
   include constant/affine boundary probes. Record all raw maximum differences.
3. One full original-vs-sampled network on16 RGB128x192frames,full released
   weights,FP32/fouriterations/window16. All flow-vector deltas<=.001nativepx,
   finite/all confidence decisions at.5unchanged. This is an implementation
   equivalence budget(1/3000of3px),not a universal tensor1e-6/physical accuracy gate.
   Record all confidence differences,not treat raw logits as millimeters.
4. Only after equivalence passes,one sampled full-network native RGB1280x720,
   16frames,procedural nonhuman fixed moving texture. No resize. Count all output
   pixels/channels,finite values,peak GPU reserved<=7GiB,worker peak RAM<=8GiB,
   native forward<=180s. This proves resources/shape only,NOT motion precision.
   Original dense native would exceed VRAM and is NOT attempted to force OOM.

InputPadder actually pads to64,discovered while tracing the lookup:0287's
unpadded native/512correlation counts are lower bounds,not exact padded peaks.
Record this correction before capacity checks;do not silently ignore padding.
No source video/medical/bone/case002 read,upload,training or head/camera fitting.
No model-quality interpretation of a runtime control. Actual correspondence,
occlusion/camera/2mm/head/visual gates require a separate prospective next phase.

Whole2400s includes install/implementation/controls/reports/cleanup/tests/commit;
transport/install<=600s,implementation<=600s,operator<=60s,paired-network<=180s,
native<=180s. Save errors/progress before stopping;no replays after a failed
numerical/resource gate. Ordinary code-contract errors may be repaired before
the first scored execution and must be recorded. Failed exclusive integration
is archived minimally/recovery-committed and removed before any different route;
protect originals/shared tests/defaults/0207. A technical pass may retain only
the now-verified runtime for the NEXT separately bounded precision trial.
