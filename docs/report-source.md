# HeadFoundry technical research report

Date: 2026-09-04
Decision: proceed with a clean-room, optimization-first product.  
Quality status: `UNVERIFIED` until the full benchmark passes.

## Executive conclusion

Reaching KeenTools Cloud-class output is technically plausible, but not by assembling one public model. The credible path is a controlled system: learned multi-view camera and point-map initialization, a commercially usable full-head prior, canonical UV/vertex fusion, topology-aware per-subject optimization, and deterministic view-aware texture compositing. The strongest recent papers validate the components; the remaining moat is licensed data, engineering integration, and rigorous visual acceptance.

The project will not consume KeenTools sessions or outputs. Their EULA currently restricts reverse engineering and use of the service to create competing services. Public product documentation defines the target; owned or independently licensed captures and scans define acceptance.

## 1. Target product contract

Input is 5–10 ordinary photographs of one person, preferably neutral and sharp: frontal, intermediate yaw, and both near-profile views, with ears and hairline visible. The minimum may eventually be three, but quality claims will be based on the recommended capture set.

Output is a fixed-topology full head with crown, sides, ears, neck transition, separate eyes/teeth assets, a 4K UV texture, and per-view cameras. GLB and OBJ are first. Neutral identity quality comes before expressions and ARKit-compatible blendshapes.

The public KeenTools contract includes automatic intrinsics/extrinsics, multi-view shape, texture projection/blending with color correction, full-head topology, expressions, 51 ARKit blendshapes, and downloadable GLB/OBJ. Public timing claims range from tens of seconds to a few minutes depending on photos and requested outputs. Those features are a product reference, not evidence that our implementation already matches them.

## 2. Evidence synthesis

### Camera and scene initialization

VGGT is the best current starting point because it jointly predicts camera parameters, depth, point maps, and tracks from multiple images. Only the specifically designated commercial checkpoint is acceptable. We will refine its output with facial landmarks, silhouette constraints, and robust bundle adjustment because identity reconstruction is sensitive to small focal-length and pose errors.

The local RTX 3070 8 GB is suitable for unit tests and reduced experiments, not assumed sufficient for the final 5–10 view production workload. GPU worker sizing is deferred to measured profiling; 24 GB or more is a planning estimate.

### Geometry and topology

VGGTFace and UVFaceFusion demonstrate the central idea: convert per-view geometric observations and dense correspondence evidence into a canonical domain, then fuse them under topology-aware constraints. Their released dependency chain is not production-ready for our commercial purpose, especially where Pixel3DMM weights are non-commercial. We will independently implement the method family and train any dense correspondence/detail model only on cleared data.

FLAME 2023 Open is the leading coarse head prior candidate. Its asset and attribution obligations must be pinned in the asset manifest, and its texture space is not assumed licensed. A proprietary shoulder/neck extension and our own eye/teeth assets avoid ambiguous downstream rights.

The first production-quality version should use per-subject optimization. A 1–3 minute budget buys explicit failure visibility and reduces dependence on a huge training corpus. A feed-forward fusion model is justified only after the benchmark, data rights, and optimizer establish trustworthy targets.

### Texture fusion

Every source pixel is projected to UV space and weighted using surface visibility, normal/view angle, focus, occlusion, segmentation confidence, and distance to uncertain boundaries. Robust color/exposure calibration precedes view selection. Multi-band or Poisson-style blending removes low-frequency seams without erasing pores. Inpainting is restricted to genuinely unseen scalp/back regions and never replaces observed facial identity.

Geometry and texture are evaluated separately: attractive texture must not hide wrong shape, and accurate shape must not excuse seams or identity-changing synthesis.

## 3. Commercial and data constraints

Several attractive public resources are research-only or non-commercial: Pixel3DMM weights, FaceScape, Multiface, VHAP, standard FLAME releases, and common BFM-derived pipelines. They may inform reading but cannot silently enter the product. nvdiffrast is also excluded; PyTorch3D's BSD release is the renderer candidate.

The defensible data plan has two lanes. Synthetic pretraining uses commercially permitted parametric assets, procedurally varied cameras, lighting, occlusion, hair, and sensor effects. Real calibration and final acceptance use consented subjects with independently licensed scan ground truth. Every asset record contains provenance, allowed purposes, attribution, retention, deletion, and biometric consent fields. Missing rights fail closed.

## 4. Architecture

1. Capture validation rejects blur, insufficient yaw coverage, occluded landmarks, inconsistent identity, and severe exposure problems.
2. Camera initialization predicts intrinsics/extrinsics, depth, point maps, and confidence; robust refinement minimizes landmarks, silhouette, and cross-view track residuals.
3. Coarse geometry fits shared neutral identity plus per-view pose/expression to a fixed head prior.
4. Canonical fusion lifts visible point-map and normal evidence into UV/vertex space with confidence and occlusion masks.
5. Fine optimization minimizes multi-view geometry, silhouette, landmark, normal, photometric, Laplacian, symmetry, and displacement-regularization terms in a staged schedule.
6. Texture fusion calibrates source colors, selects the strongest observation per texel neighborhood, blends seams, and fills only unobserved regions.
7. Export validates scale, topology, normals, UVs, materials, cameras, and optional expression assets before producing GLB/OBJ.

## 5. Quality benchmark and gates

The benchmark begins with at least 20 consented subjects spanning skin tone, age, sex presentation, hair coverage, face shape, eyewear, facial hair, and camera type. Each benchmark subject needs held-out photos and, for the gold subset, licensed high-quality scan geometry. Exact sample size grows after power analysis; 20 is a pilot floor, not a claim of population coverage.

Camera gates include landmark reprojection p95, focal plausibility, cheirality, and cross-view consistency. Geometry gates include scan point-to-surface distance, normal error, frontal and profile landmarks, silhouette IoU, ear/neck checks, and blinded human identity judgments. Texture gates include held-out-view LPIPS/SSIM, color error, seam energy, facial-region sharpness, and blind preference. Mesh gates require zero non-manifold edges, zero degenerate triangles, consistent orientation, valid UVs, and no visible cracks.

Initial numeric thresholds in the repository are engineering targets and will be calibrated on the licensed pilot set. A candidate passes only when every protected gate passes. The sequence is fixed: minimal structure test, offline mesh, clay profile/silhouette, textured profile, frontal regression, then complete multi-view reconstruction.

Direct automated comparison against newly generated KeenTools outputs requires written permission because of the current EULA. This does not block development: absolute scan ground truth and held-out photographs are the primary standard. If permission is later obtained, a blinded external comparison can be added without changing the architecture.

## 6. Delivery sequence

Milestone 0 establishes coordinate conventions, manifests, legal asset gates, and reproducible measurement. Milestone 1 delivers neutral coarse head reconstruction and camera recovery. Milestone 2 delivers fine identity geometry and full-head coverage. Milestone 3 delivers 4K multi-view texture fusion. Milestone 4 adds eyes, teeth, expression recovery, and ARKit-compatible blendshapes. Milestone 5 hardens the service, viewer, privacy workflow, and GPU deployment.

No milestone is described as KeenTools-quality until clay, texture, protected views, mesh health, and complete reconstruction all pass on the benchmark. Until then statuses are `UNVERIFIED`, `REJECT`, `PARTIAL_SUCCESS`, or `TECHNICAL_CHECK_PASSED`.

## 7. Immediate implementation decision

The first committed executable is a normalized-DLT camera baseline plus a fail-closed quality manifest evaluator. It intentionally does not create a pretty demo. It proves coordinate conventions and prevents future partial metrics from being called a successful reconstruction. The next appearance-changing experiment is commercial VGGT initialization on licensed or synthetic multi-view fixtures, with camera recovery as its only primary variable.

## 8. Milestone 1 camera slice status

The repository now has a fail-closed run manifest for input and model assets. Every input requires a verified file digest, provenance, allowed commercial purpose, retention/deletion terms, and explicit biometric consent. Capture validation requires 5–10 unique views, at least 1024 px on the shorter side, an upstream normalized clarity measurement of at least 0.5, and frontal/intermediate/profile yaw coverage on both sides. The clarity score is evidence produced by capture preprocessing; pixel decoding and metric calibration remain a separate implementation gate.

The VGGT adapter accepts only an asset record naming `facebook/VGGT-1B-Commercial` under `vggt-aup-license`, with a local digest and recorded acceptance/AUP review. It normalizes decoded outputs to NumPy arrays in the documented OpenCV camera-from-world convention. Camera gates require 3x4 extrinsics, 3x3 intrinsics, finite point maps and tracks, rigid rotations, plausible focal lengths/principal points, positive depth, stable normalized focal length across views, and cross-view track reprojection p95 no greater than 3 px.

The deterministic fixture is `TECHNICAL_CHECK_PASSED`. Real gated checkpoint inference, real-photo camera recovery, and all visual reconstruction quality remain `UNVERIFIED`; geometry and texture implementation stay blocked.

## Sources

See `claim-source-ledger.md` for the auditable mapping. Primary sources include KeenTools Cloud documentation and EULA; VGGT and its CVPR paper; VGGTFace and its AAAI paper; UVFaceFusion; Pixel3DMM; FLAME license documentation; FaceScape; Multiface; PyTorch3D; and the nvdiffrast license.
