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

## External goal-state interlock before any scored execution

2026-10-21T14:03:28Z:authoritative get_goal now reports blocked,whereas this
turn began active;account ordinaryUsageAllowed remains true. No goal status
mutation,new goal,duplicate installer or model/control execution is authorized
to work around this transition. One existing installation remains live under
its600s timeout(parent50284/base-interpreter34768/uv12600 observed). Let that
already-authorized atomic installation settle;do not launch inference. Assets
are staged,not model-qualityREJECT and not verified inference. The goal-card
manual-resume reminder is issued once for this interlock;unchanged monitor
checks must stay quiet. Need actual user/product goal recovery before scoring.

Pre-execution source tracing also finds that five correlation levels perform an
extra final feature downsample. The planned128x192full-network fixture would
end at a zero spatial extent;it has NOT run. On recovery,prospectively correct
that implementation-control input to256x384(min feature axis32) before scoring,
retaining all weights,16frames,iterations,native-capacity test and pixel gates.
This is an unexecuted fixture-contract issue,not an observed precision failure
or permission to retry a failed numerical gate. No operator runner exists yet.

## Actual result:installation timeout;precision and capacity NOT measured

On product goal recovery2026-10-21T14:57:38Z,get_goal is active again;quota is
available. The original worker is terminal0 but its installation reportREJECT:
UV pip install exceeds its remaining581.328s,total600.016s. This is not a
successful install merely because Python caught the timeout and returned0.
All seven pinned public source/license/checkpoint files pass full-byte hashes;
the66005722-byte full checkpoint is verified. Environment site-packages has
only the two virtualenv seed files,no Torch. No model/operator/CUDA tensor,
equivalence/native-capacity/private-input/head/medical scoring ever ran.

Read-only exclusive-tree inspection finds staged Torch CUDA DLLs in a temporary
cache directory,15111files/2833104304logical bytes,no reparse points. This proves
partial extraction/staging,not whether network throughput,unpacking or another
transport issue caused the deadline. UV--version succeeds0.11.16;there is no
captured stderr to identify a narrower cause. Do not blame model precision,
GPU memory or license,and do not extend/replay this installation to hide failure.
The original2400s wall budget is exceeded across the external goal interlock;
no work/optimization was performed during that wait. Do not relabel it met.

Closeout has a separate300s verification/cleanup budget from14:57:38Z. Private
archive assets/private/closed-experiments/0288-native-capacity-installation/
evidence.zip contains4members,3385bytes,zeroimages,SHA256
f3e3e4514b1345cb5b9101c5515f06b986c7fe8e7f6e9ff26314db98985d3284.
Report,source/diagnostic,protected hashes and complete captured worker output
survive;source recovery4bf0195,interlock record3c3e01a. Archive is NOT a binary
checkpoint/runtime backup. Future use requires redownloading pinned assets.
All five protected hashes unchanged. Main runtime/source/defaults and0207
remain untouched. Targeted cleanup and full shared regression precede a local
closure commit. Any renewed installation needs a materially different documented
transport hypothesis and prospective budget,not more of the same timeout.

### Verified closeout

Terminal own-process/path/reparse/archive/count/byte checks precede deletion.
Removed15111exclusive asset/env/cache files2833104304bytes plus4167-byte
installer:15112files2833108471logical bytes. No source weight/binary backup
kept;public pinned files need downloading again. No sampled-correlation runner
or failed-route-only test was ever created. Main environment untouched.
Archive CRC/all four member hashes pass after deletion. All five protected
hashes unchanged;140shared tests pass5.799s;shared src/tests/pyproject unchanged.
Unrelated untracked0207preserved. Verified15:01:05Z,local cleanup commit before
another route;300s closeout met,no push. Goal remains active/unachieved. A
later transport audit may explain this stop,but may not rewrite0288as success.
