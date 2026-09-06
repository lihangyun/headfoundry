# Experiment 0015: licensed learned local-feature entry point

Status: extraction UNVERIFIED; sparse track candidate REJECT. No camera or
head baseline is replaced, and no comparison proves KeenTools/MV-HRN quality.

The official [XFeat repository](https://github.com/verlab/accelerated_features)
publishes its implementation and bundled weights under its
[Apache-2.0 license](https://github.com/verlab/accelerated_features/blob/e92685f57f8318b18725c5c8c0bd28c7fe188d9a/LICENSE).
The reviewed revision is e92685f57f8318b18725c5c8c0bd28c7fe188d9a. The repository
license and upstream notices are retained locally. This is not permission to
reuse its training datasets; none were downloaded. LighterGlue is not loaded.

The new extraction entry point checks source/weight/license hashes and input
rights, consent and photo hashes BEFORE loading a model or reading image pixels.
It loads only the pinned local state dict with weights_only=True; it does not
use Torch Hub, fetch weights, upload photos, or run a cloud notebook. Text hashes
normalize CRLF to LF; checkpoint bytes are hashed exactly. The optional runtime
is isolated in the project environment: torch 2.8.0+cpu and tqdm 4.66.5.

## Local result

All five consented photos were extracted at native resolution, top_k=4096.
The three-view matching audit uses the same eroded detector-derived face mask
as experiment 0013. Detector predictions only locate the mask, not matches.
No camera or epipolar error filters the photometric candidates.

| Method | Front-left pairs | Front-right pairs | Left-right pairs | Three-view cycles |
| --- | --- | --- | --- | --- |
| Mutual L2 ratio 0.75 | 1 | 3 | 0 | 0 |
| Mutual cosine >0.82 | 401 | 496 | 115 | 16 |

The latter matches the upstream sparse matcher's default cosine threshold.
The two configurations were retained, not chosen by a held-out geometry score.
Face-mask feature counts are 1420 / 1143 / 1294. A crop contact sheet of the first
12 cycles was inspected: many candidates concentrate on eye/mouth structure,
some are near-duplicates, and anatomical ambiguity remains. Counts alone are
not camera evidence. Spatial separation of 8 px in every view leaves 14 cycles.

Against the already-rejected experiment 0012 cameras, all 16 cycles yield
237.64 px p95 third-view prediction error, with two especially gross conflicts.
This proves inconsistency with those cameras, not that all matches are wrong.
No track was dropped based on this score and no camera was fitted to these
tracks. The sparse candidate is not suitable for promotion.

## Installation / replay

Clone the official repository to ignored local asset storage and check out the
exact revision above. Preserve LICENSE. Install the pinned CPU torch runtime
and tqdm in the optional local environment. The asset lock records the exact
files required; any mismatch fails closed instead of substituting a checkpoint.

```powershell
.venv\Scripts\python.exe tools\extract_xfeat.py <local-run-manifest.json> <pinned-upstream-directory> <new-private-output-directory>
```

The core package still requires only NumPy. Tests do not require Torch or model
downloads: a small fixture checks consent rejection, exact checkpoint-byte
validation and cross-platform text-hash normalization. The full suite passes
35 tests. Private extraction and matching results remain outside Git.

Next safe investigation is the same checkpoint's coarse-to-fine matching path
or stricter correspondence ambiguity checks, retaining a genuine held-out camera
test. This is an initialization experiment, not formal head/texture development.
