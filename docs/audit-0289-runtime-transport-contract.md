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
and ABI for Torch and matching TorchVision. One HEAD per wheel and one1MiB request at
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

## Actual contract result:TECHNICAL_CHECK_PASSED,not installation success

Official index selects exactly one matchingcp312-cp312-win_amd64wheel each:

| Distribution | Bytes | Official full SHA256 |
| --- | ---: | --- |
| torch2.10.0+cu128 | 2867409626 | fbde8f6a9ec8c76979a0d14df21c10b9e5cab6f0d106a73ca73e2179bc597cae |
| torchvision.25.0+cu128 | 9632349 | 068e519838b4a8b32a09521244b170edd8c2ac9eeb6538b7bf492cd70e57ebf5 |

URLs are published by the[official CUDA128 index](https://download.pytorch.org/whl/cu128/torch/),
using download-r2.pytorch.org;names/hash/ABI fixed in private range-report.json.
Both HEAD200with byte-range support. Torch really is2.867GB compressed;0288's
2.83GB partially expanded tree was not a complete download measurement. Neither
its original bottleneck nor future whole-wheel throughput is thereby proven.

One first-MiB response206/exact1048576bytes/.595s. Eight predefined disjoint
MiB responses all206/exact Content-Range/length,1.23s total parallel wall. Nine
sample hashes retained,no fragment files survive. No retry/sweep. These cached
small samples are NOT a full-transfer or speedup guarantee. Official Torch/
TorchVision detached metadata read once:SHA
d969f0ff6611d019b9d8cc883fc15a4b78c8818b069a0b7bd413b777bc6b4106/
5382da695e2c85aab07c0f60613169c3ac5995840ac87fe4837a7ed74a74062d.
Their declared BSD runtime licenses and required/non-extra dependencies are
recorded for separate locked offline installation;optional training extras are
not needed. Native model/correspondence/camera/medical qualityUNVERIFIED.

Range probes complete15:03:37Z,metadata15:04:27Z,within180s. Private archive
assets/private/closed-experiments/0289-runtime-range-audit/evidence.zip has
2members1889bytes,zeroimages,SHA
f75b1b58acb0c391d452500b661f4ad5318c8ade665fe4d2a7fdd9fe0ac44337;
CRC/byte equality verified. No source/env/weight/framework installed,so none to
retire. Public-only read requests,no person/case/scan material sent or opened.
Future engineering hypothesis is parallel pinned range transport with full
hashes and OFFLINE installation,not UV combined online downloading or more
of0288's elapsed budget. No hidden restart or rewrite of its failure.
