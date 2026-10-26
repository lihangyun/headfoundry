# 0356 Track-On2 inference-boundary audit

2026-10-25; source-only follow-up0355. Exact upstream
7672a5e5432a20930d8a9fbba3340fff383138f7. No installation, weights, inference,
patient data or training. No source copied into executable repository code.

## Concrete stock-entry blockers

utils/coord_utils.py line145 attributes its grid helper to CoTracker commit
9ed05317b794cd177674e681321780614a65e073. That exact upstream LICENSE.md is
CC-BY-NC-4.0, verified directly (not inferred from the current license):
https://raw.githubusercontent.com/facebookresearch/co-tracker/9ed05317b794cd177674e681321780614a65e073/LICENSE.md
The root MIT label is therefore insufficient evidence to admit this attributed
helper under our free-commercial policy. This is a fail-closed project decision,
not a legal finding about the copyrightability of short mathematical routines.

The actual import chain is Predictor -> evaluation.evaluator -> coord_utils
and eval_utils. eval_utils also imports wandb. Core Track_On2 imports coord_utils
for coordinate conversion, so removing only the predictor evaluation import does
not eliminate the mixed-source file. No need to import evaluation/training
infrastructure in a minimal local inference adapter.
Source links:
https://github.com/gorkaydemir/track_on/blob/7672a5e5432a20930d8a9fbba3340fff383138f7/utils/coord_utils.py
https://github.com/gorkaydemir/track_on/blob/7672a5e5432a20930d8a9fbba3340fff383138f7/utils/eval_utils.py

DINOv2 adapter imports Transformers AutoModel, MMCV deformable attention and
local adapter modules. It calls from_pretrained with facebook/dinov2-small or
facebook/dinov2-base, selected by architecture, without a pinned revision or
local_files_only. This is not random initialization, but is an uncontrolled
external asset load; the predictor's allowed missing backbone keys do not by
themselves prove missing/random weights. Correct0355's risk interpretation:
verify the separately loaded complete backbone, not merely demand every key in
the tracking checkpoint. README's no-additional-download implication is not an
offline execution guarantee. Actual binary key coverage remains UNVERIFIED.
https://github.com/gorkaydemir/track_on/blob/7672a5e5432a20930d8a9fbba3340fff383138f7/model/vit_adapter/dinov2_adapter/dinov2_vit_adapter.py

## Decision and safe next work

Stock package entry REJECT under current rights/offline boundary; model quality
NOT_RUN. Candidate-specific minimal adaptation remains UNVERIFIED, not rejected
solely because a replaceable helper is problematic. Independently implement
needed regular-grid/coordinate arithmetic from mathematical requirements;
do not copy or cosmetically relabel the attributed CoTracker routine. Exclude
evaluation and training modules entirely. Audit remaining core/adapter notices
and inherited implementations before copying any inference source. Lock both
tracking checkpoint and DINOv2 backbone revisions/hashes/license independently;
require complete tensor coverage and offline loading. MMCV/Windows resource
feasibility remains to be checked before installation. No patient trial until
these conditions and a distinct physical-control protocol are satisfied.

One raw source request hit HTTP429; GitHub's same-commit page provided the
adapter code instead. HF blob metadata was not accessible through web retrieval;
no weight revision/size/hash invented. This audit did not run tests (docs only),
did not claim full dependency audit complete, and leaves production unchanged.
No failed runtime/artifacts exist to clean up. Preserve0355 as preliminary history.

## Follow-up: selected core, operator and asset metadata

Read selected modules.py,prediction_head.py,reranking.py and DINOv2 adapter modules
at the same source commit. Deformable attention is used by both prediction and
reranking, not merely an unused backbone import. No CoTracker import appeared in
these inspected files; this is not a proof of every dependency's provenance.
Selected config/test_dinov2.yaml fixes384x512 input, dinov2_s, M24/M_i72,
D256,K16 and visibility.8. No proposed configuration changes.

ViT-Adapter upstream LICENSE.md is Apache-2.0:
https://github.com/czczup/ViT-Adapter/blob/main/LICENSE.md
MMCV2.2.0 is Apache-2.0 and ships a pure PyTorch deformable-attention reference:
https://github.com/open-mmlab/mmcv/blob/v2.2.0/LICENSE
https://github.com/open-mmlab/mmcv/blob/v2.2.0/mmcv/ops/multi_scale_deform_attn.py
Its normal module nevertheless loads the compiled extension at import time.
Therefore stock CPU import cannot be assumed extension-free. A scoped extraction
of the permissive reference may avoid compilation, but would require retained
notices, exact parameter/state layout and numeric contract tests; performance
and equivalence remain UNVERIFIED. Do not write a fake mmcv package or silently
change operator semantics. No fallback code implemented in this audit.

Direct read-only HF API succeeded where web retrieval had failed. Publisher
metadata (not downloaded-byte verification):

| Asset | Revision | Bytes | Publisher LFS SHA256 |
|---|---|---:|---|
| gorkaydemir/track_on2 / trackon2_dinov2_checkpoint.pt | 672a47c4614f6d661edc36b7999a5bb5c3a5d2c9 | 93900427 | 34c35ea64ea68f3c633c901c2d7876964c34212455dfbb2d508aaea1c4978973 |
| facebook/dinov2-small / model.safetensors | ed25f3a31f01632728cabb09d1542f84ab7b0056 | 88249960 | ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1 |

Both APIs report public, ungated, enabled; tracking cardMIT, DINOv2cardApache2.
Total selected weights182150387bytes, excluding config/runtime. Do not substitute
DINOv3 or base. Metadata sources:
https://huggingface.co/api/models/gorkaydemir/track_on2?blobs=true
https://huggingface.co/api/models/facebook/dinov2-small?blobs=true
No binaries downloaded. Safe next entry is a bounded minimal-source/notice
capture with full import closure, independent coordinate helper and explicitly
offline full-state loader plan. Only after that may software admission install
an isolated runtime; patient inference remains prohibited until admission and
physical controls. No original/shared source changed; docs-only validation.

## Actual source capture, 2026-10-26

`tools/capture_trackon_0356.py` now captures ten explicitly selected files as
non-importable `.txt` evidence under `assets/private/trackon-source-0356`.
Each file's size and Git blob SHA1 are checked against the pinned repository
tree; SHA256 and AST import statements are recorded in capture.json. The root
MIT notice is retained. No weights, runtime, excluded coordinate helper,
evaluation/training code, patient files or DINOv3 source were downloaded.
This is source evidence, not an executable or commercially admitted adapter.

Actual capture succeeded; a second `--offline` run revalidated all ten files
without network access or importing vendor code. The source tree is cached for
that check. This checks integrity against the captured publisher tree, not an
independent signature or complete provenance of inherited code.

Inspection of the captured Backbone confirms the DINOv3 import is conditional,
not an unconditional DINOv2 dependency. Its DINOv2 branch still defaults on any
other name, so the eventual adapter must enforce exact `dinov2_s`, not retain
that permissive fallback. Core and reranking still import the excluded
coordinate module; predictor still imports the excluded evaluator. AST lists
are an inventory, not a claim that the remaining import closure is runnable.
MMCV operator replacement and separately pinned backbone loading remain open.

Shared regression:164 tests pass in8.734s. No production source/default changed;
unrelated0207 SHA256 remains
eebdad1f8c22de9773927ae1e8961ed3159077f84ffff9b14298c0a3290ae8ef.
No head, camera, physical accuracy or medical-surface acceptance was measured.
Next implementation: resolve the retained adapter/operator notices and implement
the minimal inference boundary, then bounded isolated software admission;
do not repeat model selection or run patient inference before physical controls.
