# Audit0297:one sparse3D-repeatability candidate,source preflight only

Registered2026-10-21T23:14:18Z before pinned source/release inspection.0296closed
at56439e3. Goal active/account available;previous turn yields real source-label
and local-refinement evidence,not accepted cameras or a head. This audit does
not relax camera3px,skin2mm,full editable head or actual visual acceptance.

Existing reference check,not a new render:0230upright controls explicitly fix
+Yup/+Zface. Actual retained front/yaw+30clay images were viewed and show eyes,
nose,lips and ears. The tentative wrong-front-camera hypothesis is not supported;
do NOT rotate/re-render the fixture or retry a failed model on that pretext.
The later unlit noise images suppress such facial shape cues;domain equivalence
to real skin is unproven. This does not establish a unique cause of0295failure.

A genuinely different observation hypothesis is sparse keypoints learned for
3Drepeatability plus a separately learned descriptor,instead of manual junction
corner-attraction,old SIFT/LK/DIS chaining or all-pixel temporal tracking. Inspect
only official Parskatt/DeDoDe source,paper and releases. Preliminary public
README explicitly licenses code/models MIT except descriptor-G's DINOv2 Apache.
Select only detector-L-v2 and descriptor-B,no G/DINO/alternative checkpoint sweep.
Published scene benchmarks do NOT establish face applicability or patient quality.

Bounded preflight900s whole,source/metadata<=300s. Record immutable revision,
source/license hashes,exact publisher checkpoint/release asset identities/sizes/
published digests when available,preprocessing/pixel conventions,dependencies,
default external downloads,state-loading strictness and CPU/GPU/resource hazards.
Read at most bounded public source/metadata,no checkpoint/environment install,
private video/scan/case002 bytes,training/upload,matching/camera/head fitting.
Do not read third-party wrappers or import code from Peek or private vendors.

Rights gaps or unsupported identity stop adoption. Publisher metadata is not
full-file byte verification;missing digest remainsUNVERIFIED,not silently filled
from an unrelated wrapper. Source/license/readiness pass permits only a future
separately registered bounded acquisition/control/physical test,not a head claim.
Do not reinstate retired AllTracker/MapAnything/DA3/LK/SIFT recipes. No production
source/default changes. Any future sparse test must report missing associations,
precision and spatial/graph support,not count pruned outputs as dense-point recall.

## Source/metadata result,not execution or head acceptance

Official source revision6d156183f4dc84cd704ae779eebc8350995c5b06,commit date
2025-05-12. Pinned[README/model grant](https://github.com/Parskatt/DeDoDe/blob/6d156183f4dc84cd704ae779eebc8350995c5b06/README.md)
explicitly includes models underMIT;[root notice](https://github.com/Parskatt/DeDoDe/blob/6d156183f4dc84cd704ae779eebc8350995c5b06/LICENSE)
SHA6f02ad61c3fd4509343d619b55501354bcebfd67ad5460c853d02c7ab46ff4bd,
README SHAd1bbec492b33ad40b2c4609c3ad068ff78b568624cd64893c43302db354cbca9.
This is the publisher's scoped grant,not independent dataset/privacy/patent
clearance or blanket rights for copied third-party helpers.

| Fixed proposed asset | Official release/asset IDs | Published size |
| --- | --- | ---: |
| dedode_detector_L_v2.pth | v2 /151373853/162415420 | 58483585bytes |
| dedode_descriptor_B.pth | dedode_pretrained_models /112954869/117830512 | 54257185bytes |

Official API returns null published digest for both. No weight file was acquired;
full-byte SHA/contents/strict compatibility remainUNVERIFIED. Do not fill this
from a third-party wrapper. A future bounded official-asset acquisition must
bind exact release/asset identity,size and actual hash BEFORE any inference;
computed hash alone is not an independently published authenticity signature.
No alternative detector/descriptor-G or DINO backbone is selected.

### Source hazards and concrete integration boundary

- The selected constructors use VGG19(pretrained=False) and registered module
  lists,then load supplied complete state with default strict=True. No chosen
  constructor needs DINOv2. This is source inspection,not verified downloaded
  tensors/forward. Default weights=None still triggers network downloads;never
  permit that in the future offline inference worker.
- Factory defaults enable CUDAfloat16 autocast in encoder/refiners. Prospective
  precision/device must be explicit and fixed before tests,not silently inherited
  or changed after failure. Native memory/accuracy under any chosen recipe is
  still unmeasured. G's hidden unregistered backbone is outside this selection.
- Path convenience methods default to784x784PILresize. Native tensor input avoids
  hidden square rescaling but needs exactly one RGB/ImageNet normalization and
  explicit dimensions. Path readers do not force RGB;RGBAinputs need validated
  channel conversion. No enhancement or resized-image quality claim follows.
- get_grid uses align_corners=False cell centers. Publisher to_pixel_coords maps
  to pixel-edge coordinates(.5..W-.5);HeadFoundry/OpenCV uses centers0..W-1.
  A future adapter needs a documented-.5conversion,including reverse mapping,
  independently replayed with existing dense-grid/ramp controls. Do not guess a
  half-pixel shift from model errors.
- Dual-softmax matcher ignores P_A/P_B arguments;score is NOT visibility.
  Equal mutual maxima can return multiple matches per source/target. Preserve
  missing/ambiguous/all emitted matches and test ties,do not inflate support or
  evaluate only high-confidence successful rows. Top-k/coverage also does not
  establish spatially independent or rigid3Dsupport.
- Native256channel1280x720FP32descriptor map alone is943718400bytes. One10000x10000
  FP32correlation is400000000bytes before multiple softmax buffers/features.
  These are static array sizes,not measured peaks/speed or proof an8GB GPU fits.
  The VGGfactory initially constructs a larger classification network before
  slicing features;CPU transient allocation also requires an actual check.

Full utils.py cannot be described simply asMIT:it explicitly copies pose helpers
from[fixed DenseMatching source](https://github.com/PruneTruong/DenseMatching/tree/40c29a6b5c35e86b9509e65ab0cd12553d998e5f),
whose[license is GPLv3](https://github.com/PruneTruong/DenseMatching/blob/40c29a6b5c35e86b9509e65ab0cd12553d998e5f/LICENSE),
and attributes other transforms/warps separately. GPL is not a noncommercial
license,but this is NOT an all-permissive product redistribution clearance.
Do not vendor/install the whole package while claiming plainMIT. A prospective
narrow inference port must use clearly scoped model/core rights and independent
small grid/matcher/preprocessing utilities,or explicitly resolve/comply with all
inherited terms. No borrowed pose/augmentation helper is needed for this chosen
inference flow. No such port or rights-compliance verification is implemented
by this preflight;full-package adoption remainsUNVERIFIED.

Official source bodies/metadata retrieved by220.995s;inspection closed23:19:10Z
at291.917s within300s. No further upstream source inspection after this point.
Twelve source hashes,exact publisher asset records and unverified fields are in
assets/private/sparse-repeatability-preflight-0297/metadata.json. No framework,
weights,environment,inference/head outputs or human material copied/installed.
Source/metadata technical inspection complete;binary compatibility/resources,
physical correspondence,camera/medical/head/visual quality allUNVERIFIED.
Next is a separately bounded narrow-port/asset/control decision,not model adoption
or reactivation of a retired configuration. Production defaults unchanged.
