# Audit0277: a different dense observation candidate,not another solver rescue

Date2026-10-21. Read-only publisher/source/access screen after0276 cleanup
5df5a6f. No model downloaded/installed/executed,no patient material opened,
no training/upload and no reconstructed head. Overall capabilityUNVERIFIED.

## Why this candidate

0276's exact synthetic short tracks pass the complete geometric chain,where
0275's unverified real tracks fail. This does not identify the sole cause,but
supports testing a genuinely different observation mechanism before modifying
the solver. Original **RoMa outdoor** combines frozen DINOv2 semantic features
with learned dense local refinement. That differs from transportedDIS/LK IDs,
XFeat/LighterGlue and EfficientLoFTR's index-corrected matching. No old failed
integration is restored. A general scene-matching paper is not evidence of
head/skin-subpixel accuracy or medical2mm applicability.

Primary sources:[paper](https://arxiv.org/abs/2305.15404),
[publisher repository](https://github.com/Parskatt/RoMa),
[exact code](https://github.com/Parskatt/RoMa/tree/77f8d68803526dcddfd9b7a46bc76125bdc25f15).
Full RoMa is the candidate,not TinyRoMa's XFeat backbone or a checkpoint sweep.
RoMaV2/DINOv3 has different custom terms and is not approved by this screen.
Pi3/Pi3X remain excluded for NC weights under the already recorded restriction.

## Sources,rights and transport

- RoMa code77f8d68803526dcddfd9b7a46bc76125bdc25f15 has MIT terms for its own
  code and separately identifies DINOv2. Do not relabel all dependencies MIT.
- The author's separate weight-hosting repository has MIT license at
  [6fed4401e851d3c73ceaf15b885fea078a2701f1](https://github.com/Parskatt/storage/blob/6fed4401e851d3c73ceaf15b885fea078a2701f1/LICENSE).
  The author's model-zoo code selects that repository's `roma` release artifact
  `roma_outdoor.pth`,445647516bytes. No separate NC restriction is found in the
  inspected publisher release/license. This is publisher-grant evidence,not a
  warranty about every training image or a third-party mirror's license label.
- Original `dinov2_vitl14_pretrain.pth` is separately covered by Meta's explicit
  **code and model weights** Apache-2.0 statement at
  [7764ea0f912e53c92e82eb78a2a1631e92725fc8](https://github.com/facebookresearch/dinov2/blob/7764ea0f912e53c92e82eb78a2a1631e92725fc8/README.md#license).
  It is1217586395bytes. Do not fetch XRay/Cell-DINO or assume their distinct NC
  branches inherit this backbone grant. RoMa uses its limited vendored original
  DINOv2 architecture,not an unpinned current torch-hub source checkout.
- Official RoMa GitHub-release and Meta download endpoints both answer
  unauthenticatedHEAD200 with the above byte lengths. This is access metadata,
  not a completed GET,byte/hash/strict tensor validation or an account agreement.
  About1.663GB of model bytes plus runtime may be needed;actual peak/latency is
  unmeasured. No gated mirror,alternate checkpoint or paid fallback is allowed.

## Concrete integration risks found before adoption

CPU construction explicitly selectsFP32;Windows disables optional custom local
correlation. An ordinary PyTorch implementation exists,not proof of acceptable
runtime. The inference imports inspected do not require training orWandB setup;
do not blindly install every training/benchmark extra from pyproject.toml.

The encoder puts DINOv2 in a plain one-element Python list,not a registered
childmodule. Therefore checking only the RoMa wrapper's `state_dict()` or
`parameters()` would miss the1.2GB descriptor backbone. Independently verify
both complete checkpoint dictionaries,expected keys/shapes/dtypes,all finite
parameters and both model components. Pass local dictionaries explicitly so
default constructors cannot silently download substitutes. Use safe weights-only
loading,offline flags/network denial during inference and preserved notices.

Normalized coordinates use align_corners=False in query sampling. The public
pixel helper returns image-edge coordinates (first pixel center=.5),not OpenCV's
first-center0 convention. Independently verify half-pixel/grid/direction contracts
before camera calculations;do not silently apply a learned-output correction.
Symmetric dense output directions and resampling must be explicit. Confidence/
bidirectional consistency cannot be promoted to physical accuracy.

## Next bounded gate,not a performance claim

Before any inference,prospectively register one exact default560/864 CPU-FP32
configuration,one budget and stop condition. Install only official pinned model
assets;record actual SHA256 identities (publisher release API currently has no
digest),verify atomic complete downloads and fail closed before use if identity
or rights is missing. Then perform full two-component conformance/resource and
independent coordinate controls. Actual known3D physical correspondence/held
camera evidence must follow;no universal1px planar prerequisite substitutes for
the unchanged3px/2mm gates. Freeze test content/cohorts before scores,no
resolution/checkpoint/texture/threshold/precision sweep after failure.

This screen supports a next installation/conformance experiment,not deployment,
model-quality approval or an accepted head. No retrospective patient rerun is
authorized by the successful0276 toy control. Failed-route cleanup still applies.
