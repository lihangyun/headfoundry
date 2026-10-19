# Experiment0226: known-transform pixel precision before more camera fitting

Date:2026-10-19. Pre-registered before measurements. Status:`REJECT` for the16-case refinement gate.

## Question and single variable

0225 fails both frozen3D localization and pixel-only rigidity. It does not prove
the3D shape is the unique cause. Determine whether the existing descriptor
endpoints can satisfy a subpixel measurement budget even on controlled images,
then test one endpoint mechanism: descriptor-initialized forward/backward LK
refinement. No new features/weights, learned confidence, cameras,3D, masks on the
original images, scan fit or model training. Old LK chaining/direct-uninitialized
failures do not test descriptor-provided endpoint initialization.

Use only the unchanged case001 frames0,144,408,612 and original masks. Create
four deterministic target images per source with native720x1280 OpenCV bilinear
warps: identity; translation(+2.3,-1.7)px; rotation3deg/scale0.97 about(360,640)
then(+4.2,-3.1)px; projective matrix
`[[1,.015,0],[-.01,1,0],[.00008,-.00006,1]]`. Warp the existing mask by the same
matrix with nearest sampling to fix the measurement region, not to select
correct matches. This is a2D synthetic diagnostic, not actual3D view truth.

Use unchanged pinned XFeat4096/LighterGlue0.1 on source/target. Retain every
masked raw match for baseline evaluation. The candidate passes its raw descriptor
endpoint as LK's initial flow; source endpoint stays fixed. Reuse the original
21x21 window, pyramid3,30 iterations/0.01 epsilon, minEigen1e-4, forward/backward
error<=0.75px and forward patch-error<=15. Both tracking directions receive
their descriptor-provided approximate destination; no known warp or truth
coordinates enter the refiner. No temporal chaining or pose residual filtering.

Only after eligibility/refinement is computed, apply the known homography to
the source keypoint to evaluate endpoint errors. Save all raw matches, all
candidate outputs and all eligibility/error arrays, including failures. Report
baseline-all errors, candidate-eligible errors and baseline errors on the same
eligible cohort separately; filtering alone is not a paired precision gain.

Each of16 cases must retain>=30 candidate matches and>=50% of raw matches, with
candidate p95<=1px. The1px target is a measurement budget, not a replacement for
the3px camera gate. Require known-transform unit tests and an explicit LK
initial-flow argument check first. One run,180s. No window/pyramid/threshold or
transform-strength sweeps. Failure stops this candidate before real localization.

If all pass, a separately pre-registered real-video sentinel screen may reuse
the exact fixed refiner. It must still pass original camera/support gates on
every retained validation identity. Synthetic success is not anatomical truth,
millimeter scan accuracy, unseen-subject or complete head/visual acceptance.
All original/rejected outputs and production defaults remain unchanged; case002
is not used. Images/derived data remain private/local and are not used to train.

## Results and pre-registered read-only causal audit

The single10.925527s run passes14/16 cases. All identity controls are exactly0;
nonidentity raw-match p95 ranges3.546830-4.767000px. Translation refinement p95
is0.080809-0.135666px. All mild-affine tests pass at0.681430-0.943652px, but
projective source0/612 reach1.069723/1.230564px and fail the fixed1px budget.
Between99.15% and100% of raw matches remain eligible, so this gain is not obtained
by deleting nearly all difficult points. Actual projective before/after sheets
were inspected in front, both profiles and tilted front. No real camera/head
candidate is authorized by the partial synthetic result.

Next run one diagnostic on **only the two failed saved source0/612 projective
cases**: seed the identical LK routine at the known true endpoint instead of the
descriptor estimate. Keep every other setting and all saved observations fixed.
This unavailable-in-real-use oracle is not a candidate, input replacement or
accepted accuracy result. If its systematic error remains, changing coarse
initialization alone is not enough; do not tune LK windows/iterations to rescue
the result. If it vanishes, investigate the basin rather than changing geometry.
Report all endpoints/eligibility and paired errors, with exact target image
regeneration first. No new extraction/matching/model or camera solve.

Default-path replay against the previous committed helper on real pairs0/12,
144/156 and408/420 preserves all eligibility masks and all retained forward,
backward-error and patch-error arrays exactly. OpenCV's undefined patch errors
for rejected failed-status points are not required to be bit-identical; an
initial whole-array comparison failed on that invalid scratch output only.
Neither selection nor usable data changed.

The unavailable true-endpoint initialization audit reproduces the bias: same-ID
p95=1.069708/1.231038px for source0/612, while endpoint differences versus the
descriptor-seeded result have p95 only0.000520/0.000761px. Both saved target
images regenerate pixel-exactly. Thus a better coarse seed alone does not remove
these errors; the translation-only patch objective is insufficient for this
known projective image transformation. Do not adopt0226 for real localization
or tune its window/pyramid/iterations. A separately bounded affine-patch model
is a materially different follow-up, not a lowered precision target.
