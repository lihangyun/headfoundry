# Audit0289:runtime-wheel transport contract,not a model retry

Registered2026-10-21T15:02:48Z before official wheel metadata/range probes.
0288 is closed/cleaned at19478c0. No installer/model is running for this route.
Whole900s including records/commit,metadata/probes<=180s. No wheel/checkpoint
installation,model inference,private input read,training,upload or driver change.

Question:can the SAME official Torch2.10.0+cu128/Windows/Python3.12 wheel be
fully pinned and fetched in independently verified byte ranges,then installed
offline?0288's combined UV path leaves partial staging and no useful progress;
separating transport from install is a materially different engineering path,
not a longer deadline,checkpoint/precision/frame/threshold or scientific retry.

Read official PyTorch index/version instructions only;lock URL/full SHA256/size
and ABI for Torch and matching TorchVision. One HEAD and one1MiB request at
offset0 for the locked Torch wheel,plus eight concurrent1MiB nonoverlapping
requests at offsets1..8MiB. Require206and exact Content-Range/length. Bound each
response<=1MiB and reject200instead of accidentally downloading the wheel.
No second endpoint/parallelism/range/timeout attempt after failure. Preserve
hashes/timings/header facts,not wheel fragments. Small cached probes cannot
predict full download/install time;do not present their speed as that guarantee.

If the contract passes,a future single fixed parallel-range full-byte download
and offline installation still needs separate prospective scope/budgets/full
hashes/dependency-license locks. Original0288stays installationREJECT;model
precision/native capacity remainUNVERIFIED. No candidate/head/scientific gate
changes. Leave no experimental framework or duplicated binary after this audit.
