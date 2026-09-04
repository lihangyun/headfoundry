# ADR 0001: quality-first clean-room reconstruction

Status: accepted for implementation; final product quality remains `UNVERIFIED`.

## 2026-09-04 implementation amendment

All reconstruction runs must start from a versioned manifest that binds each file to SHA-256 and records provenance, allowed purpose, retention/deletion policy, and biometric consent. Model loading is restricted to the exact `facebook/VGGT-1B-Commercial` identity and its gated `vggt-aup-license`; neither missing records nor unavailable weights may trigger a fallback.

Status meanings are fixed: `TECHNICAL_CHECK_PASSED` is a bounded non-visual engineering check; `UNVERIFIED` means evidence has not been collected; `REJECT` means a required gate failed or is missing; `PARTIAL_SUCCESS` means numeric gates pass without complete licensed visual evidence; `ACCEPT` requires all protected gates plus licensed benchmark, held-out visual review, and complete reconstruction evidence.

## Decision

Build an independent pipeline with four explicit stages:

1. Validate 5–10 neutral, sharp, well-covered input photographs.
2. Initialize intrinsics, extrinsics, depth, and point maps with the commercially licensed VGGT checkpoint, then refine cameras against landmarks and silhouettes.
3. Fit an open full-head prior with shared neutral identity and per-view pose/expression; lift observations into a canonical UV/vertex domain and perform confidence-weighted topology-aware optimization. Add high-frequency displacement only after the coarse head passes.
4. Project source pixels into UV space, solve per-view color/exposure, select by visibility/angle/sharpness, blend seams, and inpaint only genuinely unobserved regions.

GLB and OBJ are the first outputs. Eyes and teeth use our own licensed template assets. Expression and ARKit-compatible blendshapes are a later acceptance stage, not part of the first neutral-quality milestone.

## Why

The research evidence favors explicit multi-view geometry and canonical fusion over a single-image generator. Per-subject optimization accepts a slower 1–3 minute budget and avoids requiring a massive proprietary scan corpus before a truthful quality baseline exists.

## Rejected routes

- KeenTools service outputs or automated black-box measurements: incompatible with the service's competitive-use restrictions without written permission.
- Pixel3DMM weights, FaceScape, Multiface, VHAP, standard FLAME releases: non-commercial restrictions.
- nvdiffrast: its published license is not suitable for this product. PyTorch3D is the selected differentiable renderer.
- Pure NeRF/Gaussian avatar output: does not provide the required stable fixed topology and editable mesh contract.
- Training a large end-to-end model first: delays falsification and hides camera, geometry, and texture failure modes.

## Data strategy

Bootstrap with synthetic renders from commercially allowed parametric assets and our own procedural lighting/camera variation. Build the real benchmark from explicitly consented captures paired with licensed high-quality scans. Store identity/biometric consent, allowed uses, retention, and deletion state with each subject. No dataset enters training until its license is recorded in the asset manifest.

## Compute strategy

Development tests run on the local RTX 3070 8 GB. Production-quality learned initialization is isolated to a GPU worker sized after profiling; the current expectation is 24 GB or more for comfortable multi-view work, but this is a planning estimate, not a confirmed requirement. Optimization and export remain reproducible jobs with immutable input manifests.
