# Experiment 0018: explicit DA3-BASE camera initialization

Inference: 2026-09-07. Frozen-split bundle check: 2026-09-08.
Result: `REJECT` for real-photo camera acceptance. No full-head implementation,
texture fusion, baseline replacement or visual-parity claim.

## Runnable local asset

The specifically named `depth-anything/DA3-BASE` checkpoint and official source
publish Apache-2.0. This is a separately identified initializer, not a substitute
checkpoint inside the VGGT adapter. Large/Giant/Nested variants are excluded.
`examples/da3-base-asset-lock.json` pins the model revision, checkpoint/config/card
digests, complete Python/YAML source-tree digest, source license and CPU runtime.
All five input digests, rights, local consent and capture records are checked
before model execution. Neither missing files nor failed checks trigger downloads.

The runner uses the core network and strict safetensors loading. The official
checkpoint deduplicates shared LayerNorm parameters: the standard safetensors
model loader restores actual aliases while checking all learned parameters.
It does not initialize missing learned weights randomly. No Hub API, web server,
Gaussian renderer, Open3D or cloud inference is used. Source/license attribution
is retained in the local upstream checkout and checkpoint model card.

The bounded runner currently accepts square photos only. It resizes to 504x504
with area sampling and applies the upstream ImageNet normalization, without crop
or padding. Five 1254x1254 photos ran locally in 12.55 seconds with CPU FP32,
four threads and the first image as reference. This is one measured run, not a
latency guarantee. Outputs contain five 3x4 world-to-camera matrices, five 3x3
processed-pixel intrinsics, and five 504x504 z-depth/confidence maps.

The NumPy adapter unprojects z-depth using OpenCV [R|t], preserves view/row/column
order, and maps intrinsics back through pure resize. Synthetic nonidentity-camera
roundtrips and malformed-input cases are tested. Same-view roundtrip accuracy
only verifies conventions; it cannot establish real geometry accuracy.

## Frozen observation checks

The five-view output is indexed by recorded view IDs, not assumed slot numbers.
Existing independent observations cover frontal and the two intermediate views;
the two profile cameras therefore still lack independent validation. No camera
or observation is adjusted in the raw-output check.

| Measurement | Result, original pixels | Meaning |
|---|---:|---|
| Six frozen visual-read anchors, all 18 third-view predictions, p95 | 48.5257 | REJECT; readings themselves have 4-6 px subjective uncertainty |
| Eleven frozen LighterGlue tracks, all 33 third-view predictions, p95 | 47.8225 | REJECT; matches are not scan ground truth |
| Frontal predicted depth projected to the two intermediate views, 12 errors, p95 | 43.8307 | Model depth consistency only |
| Shared three-view camera gate, source-pair triangulated anchors, p95 | 40.2589 | REJECT; includes source-pair fits, not all independent predictions |

All tested triangulated points have positive depth. Their median parallax is
about 32 degrees, so this particular failure is not explained by the newly
guarded low-parallax condition. Original-photo overlays were inspected: eye and
mouth predictions have visibly directional offsets. No photo is geometrically
warped to conceal them. Full-profile camera accuracy remains unverified.

## Same-track joint refinement

One subsequent solve uses the exact experiment-0017 split: 40 training tracks,
11 entire tracks excluded from all fitting. Only camera initialization changes:
DA3 supplies the starting poses and fixed per-view focal estimates. The first
camera is changed to the identity gauge, baseline is normalized, and training
points are triangulated from training observations. There is no depth/face prior.
The existing sparse soft-L1 solve retains its fixed 300-evaluation budget.

It converges after 41 evaluations. Training p95 becomes 3.6644 px; all 33 untouched
third-view predictions have p95 **7.5485 px**, with 100% positive depth. The earlier
fixed-1800-pixel initialization gave **7.5456 px on the same split**. Both fail
the unchanged 3 px gate. This experiment supplies no evidence that replacing
the starting model improves the final held-out alignment.

Next discriminating check: correspondence localization/rigidity under fixed
cameras, with independent image evidence and no residual-based cherry-picking.
Repeating model swaps alone is not supported by this result. Formal head/texture
work stays behind the existing camera gate; the requested final product is not done.

## Reproduction

Clone the official source into an ignored local asset directory and check out
revision `3d835ec1a5802d64a8b8b15f817a1ab54809bfe4`. Download only `model.safetensors`,
`config.json` and `README.md` from the model revision recorded in the lock.
Do not run the upstream all-extras installer. Use a dedicated Python 3.12 runtime
with the exact packages in the lock's `runtime` section (torch from its CPU index).
The installed local runtime is already configured; it does not need reinstalling.

```powershell
.venv/Scripts/python.exe tools/run_da3.py <consented-manifest.json> <source-directory> <model-directory> <new-output-directory>
C:/Python313/python.exe -m unittest discover -s tests -q
```

The full suite passes 43 tests. Shared camera checks additionally reject a
nonzero lower-triangular intrinsic entry and common tracks hidden behind cameras.
These safeguards do not claim to explain this subject's errors. Private reports
retain individual errors, split, matrices, source hashes and observed overlays;
identifiable inputs and outputs are not committed.
