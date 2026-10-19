# Experiment0248: exact Apache MapAnything asset and offline runtime boundary

Date:2026-10-19/20. Pre-registered before installation/inference.
Asset/runtime status:TECHNICAL_CHECK_PASSED. Head/geometry accuracy:UNVERIFIED.

0247 rejects naive latent gauge locking;coordinate normalization adds no new
observation. Refresh a genuinely different geometry initializer rather than
another version of the failed contour loss. Official MapAnything publishes a
separate Apache2.0 code/weight variant,unlike the default noncommercial model.
No performance/face accuracy is assumed from its model card.

Only `facebook/map-anything-apache`,revision
`00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`,is eligible. Exact safetensors
SHA256=`fa06c0fdccefc5048e072c85935d5789b1e36b307f3859033c17f9dcb9fd5201`,
size4914062480bytes. Pin original config/card bytes. Official API reports ungated;
use unauthenticated public downloads,no account agreement/cookie/token workflow.
Reject default`facebook/map-anything`,Pi3/Pi3X noncommercial weights and all
unreviewed automatic replacements. Never use remote inference or upload photos.

Pin MapAnything code`3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`,DINOv2 code
`7764ea0f912e53c92e82eb78a2a1631e92725fc8`(Apache2.0,no separate DINO weights),
and original MIT DPT code`cd3fe90bb4c48577535cc4d51b602acca688a2ee`. Store
source/license/model-card snapshots,complete file hashes and notices privately.
UniCeption0.1.7's top-level BSD label is **insufficient**:its core DPT path
imports `libs/croco/dpt_block.py`,which explicitly saysCC-BY-NC-SA4.0. Optional
eager encoder/global-attention imports also touch restricted CroCo code.
Therefore original runtime is NOT cleared simply because checkpoint is Apache.

Before any model execution,provide a narrow separately tested permissive route:
only DINOv2/dense/global encoders;original MIT DPT residual/fusion/scratch blocks
or independent equivalents;no actual NC CroCo/RoPE module execution. Preserve
upstream MIT/BSD/Apache notices and record all interface modifications. Reject
unsupported variants rather than pretending an alternate RoPE/encoder works.
Strict state-dict key/shape coverage is required;no random decoder,partial load,
default-weight fallback or secretly dropped tensor. Run offline with explicit
local DINO architecture code and pretrained=False;the exact full Apache
checkpoint supplies learned parameters. Inspect imported module provenance.

Asset installation and execution clearance are separate statuses. An installed
checkpoint may remain `runtime_clearance=UNVERIFIED`;load must fail closed until
the restricted dependency path is replaced and tested. Do not modify production
environment packages;reuse already installed compatible basics or install only
missing reviewed dependencies into a private target. No optional UI,training,
external-model extras or service scaffold.

Both current Python environments reportCPU-only and NVML cannot initialize;
do not claim the historical RTX3070 is currently usable or repair system drivers
without new authority. Disk space currently suffices. Download budget20min,
bounded known-geometry CPU inference budget300s after runtime clearance. Keep
partial downloads and live handles,never duplicate a live transfer. CPU timing
or import success is not reconstruction accuracy. If cost/compatibility fails,
retain evidence and stop that exact configuration,no checkpoint/precision sweep.

First geometry screen,only after runtime/asset gates:reuse coherent known3D
six-view source-clay benchmark0236 with unchanged cameras/points and image-only
inputs. Official image preprocessing/no geometric conditioning;pin actual API
and CPU precision before execution. Evaluate proper camera/convention,focal,
cheirality and independent visible-point3px projection gate with one declared
global similarity,not a separate pose per held view. No real-video head fitting
or new source metrics from this model before that screen. case002,production
defaults,all failed candidates and local-only consent boundaries stay unchanged.

## Pre-inference interface repair,not partial checkpoint loading

Public source/card/license snapshots and exact4.914GB Apache weight download
complete;the raw weight hash matches the pinned publisherLFS identity. The
initial offline MIT dependency probe passes tensor residual/fusion algebra
(max2.39e-7),with no actual restricted CroCo code execution. Weight construction
then exposes a concrete packaging interface mismatch:the BSD DPT wrapper expects
`scratch.layer_rn` plus original named convolutions;the MIT scratch factory
provides the named convolutions only. Preserve its original failure before any
checkpoint parameter or image inference. Add a ModuleList referencing the
**same** MIT convolution objects,not new layers.

The Apache safetensors also declares shared-parameter aliases in its header.
Preserve strictness by proving each alias is the identical model Parameter
before expanding names,then `load_state_dict(strict=True,assign=True)`;every
actual file tensor must be consumed with exact shape/F32 dtype. Do not call
strict=False,drop keys,guess alias equivalence from shape or initialize missing
decoder weights. An independent shared-versus-unrelated toy-model test enforces
this. Low-memory native meta construction and strict assignment match a normal
F32 toy model exactly;no precision/architecture downgrade is made.

One new interface-replay directory preserves the original attempt. No photo or
geometry prediction is run at this stage. Runtime clearance and geometric
accuracy remain separate;even successful strict loading cannot pass a head.

## Actual asset/runtime result

Public checkpoint transfer finishes435.03s with exact publisher SHA256 and size.
Offline interface-replay strict load finishes12.00s:736 stored tensors,812 model
keys,76 publisher-declared aliases independently proven identical Parameters,
1228491222 parameters,allCPU float32,no meta/unassigned parameter. No partial
load,external DINO checkpoint,random replacement or actual NC CroCo execution.
Original failed scratch-interface load and successful replay remain separate.

`assets/private/mapanything-apache-0248/` retains asset-lock,all public pinned
source/license snapshots and hashes,download receipts,dependency probe,original
failure,strict-checkpoint-probe-interface-replay/report.json and execution
capsules. Nothing private is committed. `validate_assets` checks the complete
source inventory,license evidence,strict-load report hash and actual adapter
identity before image execution;changed or missing evidence fails closed.
This is a reviewed execution-path boundary,not a blanket legal/FTO opinion on
unexecuted transitive packages. Original MIT/BSD/Apache notices are retained.

Follow-on0249 separately pre-registers the exact CPU image-only known3D test.
No runtime success changes existing head rejection or production defaults.

Official evidence:
- [Apache model card](https://huggingface.co/facebook/map-anything-apache)
- [Publisher model selection/code license](https://github.com/facebookresearch/map-anything)
- [UniCeption restricted DPT header](https://github.com/castacks/UniCeption/blob/main/uniception/models/libs/croco/dpt_block.py)
- [Original MIT DPT license](https://github.com/isl-org/DPT/blob/main/LICENSE)
- [Pi3 current weight restriction](https://github.com/yyfz/Pi3#-license)
