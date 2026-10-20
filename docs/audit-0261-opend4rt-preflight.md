# Audit0261: OpenD4RT provenance and local resource preflight

Date:2026-10-20. Registered before integration/download/inference. UNVERIFIED.
0260 is completed progress at22871d1;0259 remains retired. This is not another
model trial or permission to relax full camera/material/head acceptance.

Pinned candidate:independent OpenD4RT source403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3,
HF model7099b1fc760475de3b7409acd6b63f801b015d07,32CLIP_9Dataset_NoAUG only.
No fallback variant,original-D4RT attribution substitution or tiny replica.

One question:can the published artifact and its actual inference path be
cleared for free commercial use and credibly tested on this local machine?
Inspect direct code/checkpoint grants,pretrained initialization,required imports,
load strictness and CPU/device support. Separate necessary published rights
from inference accuracy or a general legal opinion. An Apache repository badge
alone does not clear an independently licensed upstream asset/code component.

Budget:20minutes wall time from registration. Public text/source/metadata only;
no full/binary checkpoint retrieval,pickle execution,model/framework/environment
installation,training,private human-file access or uploads. Use standard library
and existing NumPy for source/parameter/resource arithmetic if necessary.
Read actual local physical/available memory and GPU evidence;do not inherit
historical hardware assumptions or promise unmeasured CPU/GPU latency.

Pass only a justified next **bounded independent known3D screen**,not private
video fitting or head quality. If explicit rights cannot be established or the
released runtime cannot fit a credible local resource budget,stop that lead
without precision/model/architecture/downstream gate changes. Preserve small
source/hash/report evidence;no unused integration should be created. Do not
pretend unknown provenance,unknown peak memory or unknown model accuracy passed.

## Actual published-rights and inference-path findings

No checkpoint bytes,model code installation,Torch environment,training or human
material are loaded by this audit. Public text is inspected and hashed,not run.

- [OpenD4RT code license](https://github.com/Lijiaxin0111/Open-d4rt/blob/403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3/LICENSE):Apache-2.0.
- [Publisher model repository](https://huggingface.co/Lijiaxin0111/OpenD4RT/tree/7099b1fc760475de3b7409acd6b63f801b015d07):its31byte model card explicitly declares Apache-2.0;the32-frame checkpoint is ungated,13950006682bytes,LFS SHA256
  `1f63305422fdc2000b057fbbc1d37459ac1a8063bbfcd0e3b7d473f5485943f5`.
- The [training guide](https://github.com/Lijiaxin0111/Open-d4rt/blob/403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3/docs/training.md)
  identifies VideoMAEv2 ViT-g initialization. Its upstream [software license](https://github.com/OpenGVLab/VideoMAEv2/blob/master/LICENSE)
  is MIT;the separate [official weight repository](https://huggingface.co/OpenGVLab/VideoMAE2/tree/706cc172d65ebd4dedbee3f9c0183a93df9fa125)
  declares Apache-2.0 and is ungated. The older model-zoo/form instruction does
  not establish a current account requirement:the official README says weights
  migrated toHF in2024. No form is submitted and no account is requested.
- The pinned [inference model config](https://huggingface.co/Lijiaxin0111/OpenD4RT/blob/7099b1fc760475de3b7409acd6b63f801b015d07/checkpoints/OpenD4RT_32CLIP_9Dataset_NoAUG/model.yaml)
  sets pretrained.enabled=false. The inspected model returns before the extra
  pretraining loader,so that4.11GB upstream asset is not an inference dependency.
- Direct model modules import standard library and Torch;the normal package
  builder additionally reaches NumPy/PyYAML/common core utilities. No NC model
  or mandatory external CUDA extension is found on the inspected model path.
  Published full requirements include training/visualization packages that are
  not justified for a narrow adapter. No package-install or complete transitive
  binary verification is claimed here.

This supports reliance on the publishers' permissive code/weight grants,not
an independent audit of every training-data contract or a general legal
freedom-to-operate opinion. Checkpoint bytes/dtypes/strict keys still need actual
verification. Do not silently switch to an original-D4RT or other variant.

## Actual runtime and resource limitations

The released evaluation path calls `model.load_state_dict(...,strict=False)` and
only logs mismatches. It is unsuitable as our acceptance loader:require strict
full-key/shape matching,not warning-only partial inference. Its checkpoint helper
uses plain torch.load without explicit mmap/weights_only arguments. Torch2.6's
default weights-only behavior must not be confused with an explicit fail-closed
adapter,and there must never be an unsafe pickle fallback after rejection.
The trainer builds model+optimizer+scheduler+scaler/config payloads. That source
explains why file size need not equal live model weights;the actual released
serialized payload has not been read or executed.

There is an explicit CPU device branch and no_grad inference path. A CUDA wheel
in upstream requirements is not proof that a working local GPU is required or
available. Current local evidence:Ryzen7 5700X,16 logical CPUs,34269908992bytes
physical RAM;first available-memory snapshot9452539904bytes. nvidia-smi exits255
with NVML Unknown Error. This does not prove every CUDA path impossible,but
provides no usable-GPU evidence;plan CPU only unless independently reverified.

Static arithmetic from the reviewed source and pinned config,not a tensor
census or measured peak:

| Item | Bytes / count |
| --- | ---: |
| Model parameter count | 1162433293 |
| All parameters ifFP32 | 4649733172 |
| Checkpoint file | 13950006682 |
| Naive file-plus-parameter accounting | 18599739854 |
| Global attention score tensor if materialized,4097 tokens/16 heads | 1074266176 |
|4096-query source-frame advanced-index copy,FP32/256x256 RGB | 3221225472 |
|128-query equivalent source-frame copy | 100663296 |

The18.60GB sum is an explicit planning scenario,not a measured RAM peak or a
claim every checkpoint byte becomes a live tensor. Even so,blind ordinary
loading has no credible headroom against current available memory. The reviewed
query embedder copies an entire source frame per query before sampling its9x9
patch;query count is therefore a real memory term,not just output size.

Unlike0259's jointly interacting tracker,these decoder queries have no query
self-attention. Built-in fixed query chunking can bound this copy without
changing the declared query population. Independence/eval-mode output equality
must be checked before relying on it;do not drop IDs or change model precision.
No CPU throughput,actual checkpoint peak,chunk equivalence or3D accuracy is
measured by the static audit.

## Justified next gate,not model acceptance

Published-rights review and source-level CPU availability are
TECHNICAL_CHECK_PASSED only in those narrow scopes. Overall executable readiness,
strict loading,actual peak memory,latency,camera/head accuracy remainUNVERIFIED.
The naive published launch is rejected as our proposed launch recipe,not a
measured rejection of this model's3D quality. No user action is required yet.

The next bounded engineering step is a fail-closed **low-peak strict loader**
precondition,not a model/precision/architecture replacement. The
[official PyTorch recipe](https://docs.pytorch.org/tutorials/recipes/recipes/module_load_state_dict_tips.html)
documents mmap=True,meta-device construction and assign=True for versions>=2.1.
Use explicit weights_only=True and strict=True,preserve every dtype/value and
reject unsupported serialization or missing keys without fallback. This model
has a nonpersistent Fourier-frequency buffer;meta construction cannot silently
leave it unmaterialized. Recreate only that exact documented deterministic
buffer and verify it against ordinary construction before a real model trial.

First test the loading/independent-query invariants on a tiny deterministic
fixture in a separately registered isolated runtime. Only after that and a
fresh memory check may a single hash-locked32-frame artifact be downloaded for
a hard-budget known3D screen. No large allocation,checkpoint download,environment
or candidate inference is authorized/executed by this audit itself. Never treat
these IO controls as the requested head result. Camera/material gates and
2mm/whole-head/human visual acceptance remain unchanged.

Scene-camera motion and head-relative motion must also stay separate. This
model's3D time/camera queries do not by themselves label a neutral head pose.
A later screen must test rigid material consistency/head motion separately from
sensor-camera coordinates,not substitute scene-camera output for a moving head.

Private text hashes,static arithmetic and hardware evidence are under
`assets/private/opend4rt-preflight-0261`. No failed model integration was created;
there is no disposable framework/weight/runtime to clean. Original human data,
case002,shared fixtures,production defaults and unrelated0207 draft are untouched.

133 retained tests pass in4.913s. This is unchanged shared-regression coverage,
not an executed OpenD4RT benchmark. A complete large-model runtime is still not
installed. No reconstruction quality or completion claim is made.
