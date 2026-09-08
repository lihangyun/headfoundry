# Claim-to-source ledger

Access dates: 2026-09-04. Only public documentation, papers, repositories, and built-in public examples were used.

| Claim | Source | Strength / caveat |
|---|---|---|
| KeenTools accepts multi-view photos, estimates per-view camera parameters, builds a textured full head, and exposes ARKit blendshapes. | [KeenTools Cloud](https://cloud.keentools.io/), [API reference](https://cloud.keentools.io/docs/reference) | First-party product documentation. |
| KeenTools inputs are 2–15 images through the API; the public playground currently recommends 2–12. | [API reference](https://cloud.keentools.io/docs/reference), [Playground](https://cloud.keentools.io/playground) | First-party surfaces differ; product should recommend 5–10 and validate independently. |
| The KeenTools Cloud EULA restricts reverse engineering and using the service to create a competing service. | [Cloud API EULA](https://link.keentools.io/eula-capi) | First-party legal text; obtain counsel/written permission for any direct competitive benchmark. |
| VGGT predicts cameras, depth, point maps, and tracks from multiple views. | [VGGT repository](https://github.com/facebookresearch/vggt), [CVPR paper](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) | Primary code and paper. Commercial use requires the specifically designated commercial checkpoint and license compliance. |
| VGGT extrinsics are 3x4 OpenCV camera-from-world matrices with x-right, y-down, z-forward; intrinsics are 3x3 pixel-space matrices. | [VGGT pose encoding source](https://github.com/facebookresearch/vggt/blob/main/vggt/utils/pose_enc.py) | Primary source-code contract used by the local adapter and fixture. |
| The commercial checkpoint is gated, requires agreement/contact sharing, and is published as `facebook/VGGT-1B-Commercial` under `vggt-aup-license`; the original `VGGT-1B` remains non-commercial. | [Commercial model card](https://huggingface.co/facebook/VGGT-1B-Commercial), [VGGT repository](https://github.com/facebookresearch/vggt) | First-party sources. License compliance remains the user's/legal entity's responsibility; HeadFoundry records acceptance and fails closed. |
| Canonical UV fusion plus topology-aware optimization is effective for multi-view face reconstruction. | [VGGTFace repository](https://github.com/grignarder/vggtface), [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/37754), [UVFaceFusion](https://github.com/grignarder/UVFaceFusion) | Primary research evidence. Published weights/dependencies are not automatically production-safe. |
| Pixel3DMM predicts dense UV/normal information but its release is non-commercial. | [Pixel3DMM repository](https://github.com/SimonGiebenhain/pixel3dmm) | Primary repository/license. Architecture evidence only. |
| FLAME 2023 Open is the FLAME release intended for broader use; other standard releases are non-commercial. | [FLAME model licenses](https://flame.is.tue.mpg.de/modellicense.html) | First-party license page. Texture assets must be licensed separately. |
| FaceScape and Multiface public datasets are not suitable as commercial training data. | [FaceScape](https://nju-3dv.github.io/projects/FaceScape/), [Multiface](https://github.com/facebookresearch/multiface) | Primary project/license pages. Evaluation or research use does not imply product rights. |
| PyTorch3D is BSD licensed; nvdiffrast has restrictive commercial terms. | [PyTorch3D](https://github.com/facebookresearch/pytorch3d), [nvdiffrast license](https://github.com/NVlabs/nvdiffrast/blob/main/LICENSE.txt) | Primary repositories/licenses. |
# XFeat local initialization evidence (2026-09-06)

- Official source and bundled checkpoint: https://github.com/verlab/accelerated_features/tree/e92685f57f8318b18725c5c8c0bd28c7fe188d9a
- Repository license: https://github.com/verlab/accelerated_features/blob/e92685f57f8318b18725c5c8c0bd28c7fe188d9a/LICENSE (Apache-2.0; preserve attribution/license; no training-dataset grant inferred).
- Exact source/checkpoint digests: `examples/xfeat-asset-lock.json`.
- Local result: experiment 0015. Successful extraction does not establish valid matches, cameras, or reconstruction quality.

## LighterGlue and next-camera evidence (2026-09-07)

| Claim | Source | Strength / caveat |
|---|---|---|
| The pinned accelerated_features bundle and Kornia 0.8.1 publish Apache-2.0 licenses. | [Pinned upstream license](https://github.com/verlab/accelerated_features/blob/e92685f57f8318b18725c5c8c0bd28c7fe188d9a/LICENSE), [Kornia 0.8.1 license](https://github.com/kornia/kornia/blob/v0.8.1/LICENSE) | Preserve license/attribution; no training-dataset grant or unrelated checkpoint rights inferred. Exact local matcher/runtime/implementation digests: `examples/lighterglue-asset-lock.json`. |
| The local LighterGlue candidate supplies 69 cycles, but the frozen 40-train/11-held-track joint fit remains rejected at 7.5456 px p95. | `experiment-0017-lighterglue-camera.md`; hashed private numerical reports | Local engineering evidence only. No photos, coordinates or identifiable meshes are published; no visual parity, performance or full-head claim. |
| The specifically named DA3-BASE model card lists Apache-2.0 and camera pose estimation. | [Official DA3-BASE model card](https://huggingface.co/depth-anything/DA3-BASE) | Next candidate only; not a local execution result or license grant for Large/Giant variants. Asset/runtime review and camera gates still required. |

## DA3-BASE execution evidence (2026-09-07/08)

- Model license/identity: [pinned official model card](https://huggingface.co/depth-anything/DA3-BASE/blob/f4a6c9b3c95e41c82048423d3493a81ec3fa810e/README.md).
- Code/license/conventions: [pinned official source](https://github.com/ByteDance-Seed/Depth-Anything-3/tree/3d835ec1a5802d64a8b8b15f817a1ab54809bfe4); the model zoo distinguishes Apache-2.0 BASE from noncommercial Large/Giant variants.
- Local numerical evidence: experiment 0018 and hashed private reports. Five-view inference completed, but the frozen camera checks remain REJECT. Source/weight/runtime identity is recorded in `examples/da3-base-asset-lock.json`; no training-dataset rights or visual accuracy follow from the model license.
