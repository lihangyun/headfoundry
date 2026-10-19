# Experiment0238: existing XFeat native learned fine localization

Date:2026-10-19. Pre-registered before implementation/inference. Status:`REJECT`.

0235 freezes photometric/context-patch precision;0236 freezes its raw direct
geometry configuration. Do not rescue either. Source inspection finds that the
already locked Apache XFeat checkpoint includes a native learned fine matcher
which earlier sparse XFeat/LighterGlue runs did not execute. Test its actual
trained dense-grid localization, not a new photometric window/confidence sweep.

Primary variable: **activate the native learned fine head** on its intended
dense coarse descriptors. Baseline is the same raw mutual-nearest dense matches,
not0226's different sparse points. Keep exact existing checkpoint/source/runtime,
4096 requested features, upstream default dual scales(.6,1.3), native mutual
matching with no cosine threshold, temperature3 and confidence>.25. No LighterGlue,
LK/ECC, epipolar/context warp, pose fit, fine-threshold/scale/feature-count sweep
or asset substitution. Four threads, CPU Torch2.8.0+cpu, seed219, OpenCV four
threads. One180s process budget for all16 cases; preserve failures.

Reuse exactly0226's frames0,144,408,612, original image/mask bytes, four transforms
and saved warped images. Re-generate each warp/mask and assert the saved target
pixels match exactly. Original face masks filter coarse features **before**
mutual matching, as in earlier measurement. No ROI change or truth filtering.

Native fine matching changes its first image's coordinates only. Therefore call
it with transformed image first and original reference second: refined target
pixels remain paired with **unchanged reference grid anchors**. Preserve native
dense indices, scales, raw MNN rows and confidence for all candidates. Native
confidence must select the same ordered rows as the public `refine_matches`
output, with its second endpoints exactly equal to those reference anchors.
Feature dictionaries must remain bit-identical after matching/refinement.

Remove every row in an exact duplicate coarse source or target coordinate group,
not the best residual copy; record these as rejected rather than independent
observations. After native confidence, require finite target points in image and
the same generated target face mask. Do not use transform error to retain a point.
The raw-MNN population remains the retention denominator, so pruning cannot hide
low support. IDs are scale-aware native extraction IDs, not old sparse3D IDs;
this does not establish consistent multi-view tracks without a later check.

Only after eligibility is fixed, compute target truth H*reference_anchor. Reuse
0226's exact evaluator: every case needs>=30 retained,>=50% original MNN retention
and p95<=1 original pixel. Require **all16** cases to pass, no per-view recipe or
best threshold. Save full coarse/refined/eligible arrays, identities, confidence,
known errors and actual projective before/after panels. Unit-check ordering,
immutable anchors/inputs, rejected aliases and malformed/empty cases.

Any failed case rejects this complete native recipe and stops it without
post-hoc defaults/threshold/scale/offset corrections or real camera/head fitting.
A complete2D pass only permits a separately predeclared known nonplanar3D
observation test; it is not real-camera or recognizable-head acceptance. Existing
source regions, full-head/scan/profile/visual gates and case002 reservation stay
unchanged. No training/upload, production-default or original-material changes.

## Single frozen result

All16 cases fail the unchanged1px p95 requirement. The complete run takes7.46s;
all179 regression tests pass. All native confidence row-order, fixed reference
anchor, feature immutability and exact target-image regeneration checks pass.
Coverage is not the limiting factor: retained fractions are86.51%-98.39%.

| Frame | identity p95 px | translation p95 px | affine p95 px | projective p95 px |
| --- | --- | --- | --- | --- |
| 0 | 2.890858 | 3.494972 | 4.112157 | 3.670082 |
| 144 | 2.934876 | 3.562372 | 3.749382 | 3.994122 |
| 408 | 2.595445 | 2.741583 | 4.239813 | 3.459518 |
| 612 | 2.888405 | 3.338086 | 3.678011 | 3.760888 |

In every identity case the same raw dense MNN coordinates have exactly0px error,
yet the native fine head moves them to2.60-2.93px retained p95 despite high native
confidence. This direct fixed-anchor counterexample is not a camera, head-shape,
truth-seed or point-ID problem. Some nonidentity coarse errors improve, but the
native fine outputs are not calibrated subpixel measurements under this recipe.
Actual projective panels retain visible local offsets; no median-only promotion.

Stop this native fine recipe. No identity-bias subtraction, pose rescue, confidence
change, single/dual-scale comparison, subpixel temperature or coordinate-offset
correction is run. Its scale-aware native IDs cannot be joined to the old sparse
COLMAP IDs. No nonplanar/real localization or head fitting follows from this fail.
Private arrays retain all raw rows, confidence/eligibility, immutable native
anchor identities, features, transforms and exact pre-result registration.

The next distinct route should not require treating automatic local feature
positions as independent subpixel truth. Before a global model-based image fit,
one bounded **anatomical-prior capacity** diagnostic on the newly available real
skin scan can determine whether the existing licensed whole-head representation
can describe the target face at all. Any scan-fit result is an oracle only,
never a video-derived candidate or a camera waiver;0143's old AI-reference fits
and frozen free-patch schemes remain rejected. This requires a fresh bounded
protocol and actual whole-head/source-region review, not a parameter rescue here.
