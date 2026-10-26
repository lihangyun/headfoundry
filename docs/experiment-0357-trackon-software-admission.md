# 0357 Track-On2 software admission (not a physical experiment)

2026-10-26. Parent source capture7207dd6. Scope: isolated operator/runtime
engineering only; no patient inputs, model weights, camera or medical scoring.
Hypothesis: MMCV2.2.0's official pure PyTorch implementation can preserve the
selected inference operator semantics without loading its compiled extension.
This addresses a Windows dependency boundary, not the failed camera geometry.

Single implementation variable: explicit pure-PyTorch MMCV operator extraction.
Retain source license/copyright and upstream tensor parameter names; do not
create a fake mmcv package. Preserve input normalization, learned parameters,
residual addition, bilinear zero-padding and align_corners=False. No geometric
thresholds are changed. Check hand-computable samples, out-of-bounds values,
multiple levels/heads, state keys, residual and optional masks/layout behavior.

Budget: source preparation <=5 minutes, isolated CPU Torch2.8.0 environment
installation <=10 minutes/4GiB observed process-tree memory; operator controls
<=120 seconds/2GiB, single configuration, no model inference. Environment and
cache must remain within repository (or use no-cache). Stop on missing license,
source drift, numerical-contract failure, resource limit or unexpected network
load. Ordinary packaging/code errors may be corrected, not thresholds relaxed.
No reuse of a failed physical integration. Operator success is only
TECHNICAL_CHECK_PASSED; full model and real reconstruction remain UNVERIFIED.

Use full pinned Track-On2 requirements only as compatibility evidence; do not
install its training/evaluation list. Actual selected package versions and
results will be recorded after execution. Main environment/defaults unchanged.

## Actual operator result

Preregistration746c471. Installation succeeded in115.843s, conservative observed
process-tree peak88416256bytes. Isolated `.venv-trackon0357` has Torch2.8.0+cpu
and nine supporting packages, now frozen in
`examples/trackon-0357-operator-requirements.txt`. Initial install resolved those
supporting packages; this is not a claim they were all pinned before resolution.
No MMCV compiled package, transformers, tracker/backbone weights or patient
inputs were installed/loaded. NumPy is absent in this isolated environment;
Torch emits an initialization warning, but these controls do not use NumPy.

Operator check succeeded in4.578s, conservative observed peak208703488bytes.
AST equality confirms the official CPU reference function was not changed.
Independent scalar bilinear oracle covers2batches,3queries,2heads,2levels,
4samples,3channels and out-of-bounds samples. Maximum absolute errors:
FP64 2.220446049250313e-16; FP32 1.3219964589694655e-7.
Analytic center/outside samples, eight parameter names, identity projection,
all-masked values, residual addition,2D/4D references and sequence-first layout
also pass. These are finite software controls, not exhaustive equivalence to
the CUDA implementation, checkpoint compatibility or model quality evidence.

Sources/notices retained at `assets/private/trackon-software-0357`, with pinned
SHA256 validation before reuse. Generated `hf_deformable.py` SHA256:
4a48eb47c274f5cc888cfe75a0761a53701dc106c90ea70626c73a30397a4137.
Changes from upstream: remove extension/registry/decorator imports, use nn.Module
and local equivalent initialization helpers, explicitly choose official CPU
reference. No fake mmcv namespace and no altered learned parameter names.
Reports:source-record.json,controls.json,install/check-worker.json and logs.
Network socket connect is denied during controls; this is an in-process guard,
not an OS-level sandbox. No model code is imported by this control.

Shared164 tests pass in8.898s; unrelated0207 hash remains unchanged. Status is
TECHNICAL_CHECK_PASSED for operator controls only; real reconstruction remains
UNVERIFIED. Keep this successful component for the candidate integration.
Next: inference-only Track-On2 adapter with independently defined coordinates,
strict local DINOv2 loading and complete checkpoint tensor accounting. Full model
runtime permission in0356 remains false until those boundaries are implemented.
