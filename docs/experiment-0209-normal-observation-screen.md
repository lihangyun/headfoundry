# Experiment0209: licensed dense normal observation screen

Pre-registered2026-10-14 before predictor execution. Status: pending, no photo fit.
Question: can an untried permissively licensed generic predictor supply usable
facial surface normals, rather than adding more shape parameters? Counter-risk:
generic scene models may smooth nose/lips, mistake lighting for relief, or fail
on synthetic white-mesh imagery. A rendered-domain failure is not a universal
claim about photographs.

## Locked candidate and runtime decision

- MoGe-2 ViT-B normal, official `Ruicheng/moge-2-vitb-normal`, model revision
  `ca5f0e07ff01d3e5a364c1d954ed12ee1814b368`;419110160-byte `model.pt`, SHA256
  `16b8110e86d5dc5a849db120ca96ef3a223fd30b0c9146d1d81db504073da5f6`.
  Its own model card says MIT, not merely the source repository.
- Microsoft source revision `74fbce054ebed49800de42d0ad0e83495065719a`: MIT,
  vendored DINOv2 Apache-2.0. `pretrained=False` constructs the backbone; the
  complete locked checkpoint supplies weights. No extra model downloads.
- utils3d-moge revision `62f09d58509485564e24d5d9f6aac9ee9ebc0c37`, MIT.
  Existing CPU torch2.14.0 and dependencies; add only the required OpenCV headless
 4.10.0.84 in the repository's private environment. No service/UI/training stack.
- MoGe-3's official model card also declares MIT, but its sparse refinement
  requires a GPU/Triton/FlexGEMM chain. Current NVML initialization fails and
  existing torch is CPU-only. Do not spend this screen rebuilding GPU infrastructure;
  do not falsely label the earlier MoGe-2 variant as MoGe-3.

Sources: [official project](https://github.com/microsoft/MoGe),
[exact weight card](https://huggingface.co/Ruicheng/moge-2-vitb-normal/blob/ca5f0e07ff01d3e5a364c1d954ed12ee1814b368/README.md),
[source license](https://github.com/microsoft/MoGe/blob/74fbce054ebed49800de42d0ad0e83495065719a/LICENSE),
[normal training description](https://github.com/microsoft/MoGe/blob/74fbce054ebed49800de42d0ad0e83495065719a/docs/normal.md).
Normal labels are derived from training depth, not independent facial scans;
weights' declared licenses do not grant rights to their underlying datasets.
This screen does not approve redistribution of an entire binary environment.

## One variable, fixed gates and stop budget

Use the already known0208 synthetic cases00/06/11, views front/left30/right30.
These nine inputs are actual512px Blender white meshes with fixed cameras, not
independent unseen identities or user's photos. Freeze shape, lighting and cameras.
Main variable: the source of normal observations. Run one FP32 CPU pass per input,
1200 tokens, known FOV, no fine-tuning or photometric optimization. Compare with
exact mesh normals and report the optimistic first30 prior's material normals as
context. It is not fair to describe an oracle prior as a real detector baseline.

Before model execution, check its coordinate convention using the official
depth-to-normal helper on a constant-depth plane. Use that single fixed convention
for all images; no target-dependent sign/axis flipping. Evaluate first-hit surface
pixels, four-pixel-eroded foreground, excluding near-grazing normals. Report head,
nose, lips and chin separately; require at least20 samples per semantic region.

Screen requires all nine images to have >=95% predicted valid-pixel coverage on
the evaluation support; head median angular error<=12deg, head p90<=30deg, and
each nose/combined-lip/chin median<=15deg. Nonfinite/zero predicted normals count
as invalid, not silently dropped. No fitted target-dependent normal rotations.
These are prefilter limits, **not fine identity accuracy or visual acceptance**.

Budget: one15-minute inference run; at most one correction rerun for a concretely
identified implementation bug, not a quality miss. A failed region/coverage gate
stops this candidate for the screened domain: do not feed it to the subject fit,
increase model size/tokens, alter masks or retune thresholds. Show input/truth/
prediction/error comparisons even on failure. Keep current default heads and all
five authorized local-only reference images untouched. No uploads.

## Results and decision

One frozen run completed in71.142s after model loading; no correction inference
reruns, larger-model replacement, token sweep or threshold adjustment. All117
public tests pass. Independent recomputation from the nine saved raw predictions
reproduces every angular error and validity flag exactly (maximum difference0).
The driver hash still matches its run record. Per-input `inference_seconds` in
the raw report also includes map serialization/comparison writing; it must not
be advertised as a pure model-latency benchmark. CPU FP32 autocast warnings disable
unsupported autocast, not FP32 computation; no upstream source modification.

| Region | Mean of nine per-image median errors | Range of medians | Failed regional median gate |
|---|---:|---:|---:|
| Head | 10.27deg | 9.39–11.44deg | 0/9 |
| Nose | 17.52deg | 14.75–19.73deg | 8/9 |
| Combined lips | 14.85deg | 12.53–17.53deg | 5/9 |
| Chin | 14.54deg | 12.93–15.77deg | 3/9 |

Validity coverage is100% for all evaluated regions. **Every image fails at least
one protected region:0/9 joint passes.** Whole-head medians/p90 alone would have
hidden this. This rejects using the screened normal observations as sufficiently
accurate constraints for the current identity task. It is not an integration,
runtime or access failure, and not a claim that the weight license prohibits use.

The inspected case00-front and case06-left30 input/truth/prediction/error panels
show low-frequency head form but softened nose/lip relief and incorrect orbital
structure. The network also predicts content in the dark background; that is
not evaluated as face because support comes from the known first-hit mesh. The
optimistic dense3D first30 prior has approximately0.36–1.23deg head medians here;
normal replacement would introduce much larger errors than the small residual
we were trying to fix. That oracle is unavailable from photographs and is not a
fair claim that the production pipeline outperforms this network on real people.

- Execution/asset checks: `TECHNICAL_CHECK_PASSED`.
- This synthetic rendered-domain observation screen: `REJECT`.
- Actual photo-domain accuracy and any likeness result: `UNVERIFIED`.
- Subject/default promotion: `REJECT`; **no photograph inference or shape fitting**.

**Stop this fixed candidate.** Do not increase model size/tokens, smooth errors,
retune masks, or fit the user's head with these normals. Render-domain bias may
explain part of the miss; only separately cleared, representative geometric truth
could test that explanation. Model failure on white meshes does not prove all
learned normal or dense correspondence methods fail.

### Following investigation, not another same-family retune

The next discriminating source can be the **already licensed FLAME2023 Open**
geometry, as a structurally/topologically different target for GNM registration
and representation coverage. That is a3D-to-3D diagnostic, not another attempt to
replace the user's head with FLAME or claim success on photographs. Require
explicit rigid/scale alignment, protected facial regions, final-surface and
cross-view evidence before interpreting any fit.

A limited scan-source check also found that Digital Emily2's official page puts
noncommercial restrictions on reference imagery; it did not establish a clear
free-commercial grant for the complete scan package. **No Emily images, meshes
or textures were downloaded**, and no unofficial CC label was used to override
the originating terms. Existing FLAME Open clearance does not cover standard
FLAME, its texture model or registered scan datasets.
[Emily originating page](https://vgl.ict.usc.edu/Data/DigitalEmily2/),
[FLAME exact-model license distinctions](https://flame.is.tue.mpg.de/modellicense.html).

## Local evidence / reproduction

Ignored output `artifacts/experiment-0209/` contains the full report, nine raw
normal/depth/mask archives, evaluated pixel/material supports and nine4-column
input/truth/prediction/error comparisons. The independent review is recorded in
`visual-review.json`. These are synthetic surfaces, not the user's photographs.

With the exact source checkouts, model and runtime from
`examples/moge-2-normal-screen-lock.json` installed under the private research
directory, run on a fresh output directory:

```text
.venv-recon/Scripts/python.exe tools/experiment_0209.py
.venv/Scripts/python.exe -m unittest discover -s tests
```

The runner checks asset/source/runtime hashes before importing executable model
code, loads the local file only, sets offline flags, and refuses to overwrite its
first run. The official model-card text is retained beside the local checkpoint.
There is no downloader, unreviewed-model fallback, photo API or production default.
