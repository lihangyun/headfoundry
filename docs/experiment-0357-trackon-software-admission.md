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
