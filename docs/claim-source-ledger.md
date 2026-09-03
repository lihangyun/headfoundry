# Claim-to-source ledger

Access dates: 2026-09-03. Only public documentation, papers, repositories, and built-in public examples were used.

| Claim | Source | Strength / caveat |
|---|---|---|
| KeenTools accepts multi-view photos, estimates per-view camera parameters, builds a textured full head, and exposes ARKit blendshapes. | [KeenTools Cloud](https://cloud.keentools.io/), [API reference](https://cloud.keentools.io/docs/reference) | First-party product documentation. |
| KeenTools inputs are 2–15 images through the API; the public playground currently recommends 2–12. | [API reference](https://cloud.keentools.io/docs/reference), [Playground](https://cloud.keentools.io/playground) | First-party surfaces differ; product should recommend 5–10 and validate independently. |
| The KeenTools Cloud EULA restricts reverse engineering and using the service to create a competing service. | [Cloud API EULA](https://link.keentools.io/eula-capi) | First-party legal text; obtain counsel/written permission for any direct competitive benchmark. |
| VGGT predicts cameras, depth, point maps, and tracks from multiple views. | [VGGT repository](https://github.com/facebookresearch/vggt), [CVPR paper](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) | Primary code and paper. Commercial use requires the specifically designated commercial checkpoint and license compliance. |
| Canonical UV fusion plus topology-aware optimization is effective for multi-view face reconstruction. | [VGGTFace repository](https://github.com/grignarder/vggtface), [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/37754), [UVFaceFusion](https://github.com/grignarder/UVFaceFusion) | Primary research evidence. Published weights/dependencies are not automatically production-safe. |
| Pixel3DMM predicts dense UV/normal information but its release is non-commercial. | [Pixel3DMM repository](https://github.com/SimonGiebenhain/pixel3dmm) | Primary repository/license. Architecture evidence only. |
| FLAME 2023 Open is the FLAME release intended for broader use; other standard releases are non-commercial. | [FLAME model licenses](https://flame.is.tue.mpg.de/modellicense.html) | First-party license page. Texture assets must be licensed separately. |
| FaceScape and Multiface public datasets are not suitable as commercial training data. | [FaceScape](https://nju-3dv.github.io/projects/FaceScape/), [Multiface](https://github.com/facebookresearch/multiface) | Primary project/license pages. Evaluation or research use does not imply product rights. |
| PyTorch3D is BSD licensed; nvdiffrast has restrictive commercial terms. | [PyTorch3D](https://github.com/facebookresearch/pytorch3d), [nvdiffrast license](https://github.com/NVlabs/nvdiffrast/blob/main/LICENSE.txt) | Primary repositories/licenses. |

