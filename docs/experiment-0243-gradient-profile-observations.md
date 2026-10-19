# Experiment0243: view-dependent gradient-ridge profile observations

Date:2026-10-19. Pre-registered before fixture execution/video decoding.
Status:UNVERIFIED. No new camera/head fitting in this observation screen.

0242 falsifies the fixed semantic-material anchor assumption;0218 already
rejects absoluteR-B threshold crossings. Change observation definition to a
continuous **multichannel image-gradient ridge**,not a new threshold onR-B.
Reuse existing NumPy/SciPy/Pillow/OpenCV only. No model,training,scan or upload.

For each image row in the same0218 declared profile ROIs,use RGB horizontal
Gaussian derivative(sigma1px),its vector norm,and local gradient maxima. Require
ridge strength>=2 digital RGB units per pixel. A dynamic program retains every
row and minimizes -log(strength/row maximum)+.01*(dx)^2,with |dx|<=8px/row.
Parabolic3-sample peak interpolation supplies a subpixel coordinate. No data-fit
constants,anchors,smoothing of the output trace,outlier trimming or residual
weighting. Missing/clipped/infeasible rows fail closed. These engineering
assumptions can reject real edges; they are not a general skin segmentation model.

First run two deterministic mirrored analytical nose/lip/chin boundary fixtures
(213x190 pixels,seed243),subpixel pixel-area integration,blue gradient background,
warm face,dark-lip bands,isolated internal texture and2-unit RGB noise. Preserve
all known row coordinates. Test sigma.75/1/1.25 only as declared uncertainty,
not candidate selection. All six synthetic p95 errors must<=1px,max<=2px;
otherwise stop before opening actual video. Do not tune the fixture/parameters.

Only after that screen passes,copy the authorized case001 video-only manifest
subset and validate rights/hash. Fresh sequentially decode exact frames139/416,
not old seek PNGs. Fixed ROIs remain139:[400,630,590,843] direction+1 and
416:[120,630,320,843] direction-1. Every row remains scored. Nominal sigma1
is the only candidate; perturbations.75/1.25 measure all-row uncertainty.
Require per-view p95 shift<=2px,max<=4px,unclipped full-row ridge and actual
image review following the skin/background boundary rather than an internal lip
edge. No alternative ROI/threshold/scale/path penalty search. Stable but visibly
wrong traces are rejected. No identity,pose or focal optimization from failed data.

While sequentially decoding,save16 predeclared nominal coverage snapshots at
ordinals0,69,139,208,277,347,416,485,555,624,693,763,832,901,971,1040. These are
only a local qualitative coverage audit,not camera estimates or proof of physical
pose/360degree completeness. No case002 video,bone/skin STL or fitted output is
opened. Python open-audit blocks patient-pilot files except manifest metadata;
it is not a security sandbox. Generic fixture assets need no fabricated consent;
video-derived frames retain original explicit local-validation authorization.

Budget60s synthetic screen,60s authorized decode/measurement. Preserve every
fixture,failed trace,uncertainty alternative,RGB frame/hash,source/model-free
algorithm revision and actual overlay. Only code/tests/non-identifying summaries
enter Git. Passing this screen is observation readiness,not calibrated camera,
material correspondence,profile IoU,recognizable head or2mm reconstruction.

## Actual result: observation screen passed,not a new accepted head

All six mirrored known-boundary/scale fixtures pass: p95.0533-.0544px,
max.07535px,213/213 rows each. There is no parameter/fixture replacement.
The authorized exact-frame decode and real measurement finish in4.65s with
0 patient geometry/oracle read attempts. Original authorization restrictions,
video/frame hashes,all nominal/perturbed traces and selected strengths persist.

| Exact ordinal | Rows retained | Scale-uncertainty p95 px | Max px |
| --- | ---: | ---: | ---: |
| 139 | 213/213 | .1091 | .2785 |
| 416 | 213/213 | .2997 | 1.0043 |

Actual image overlays were inspected: nominal ridges follow the visible skin
profile through nasal bridge/tip,upper/lower lips and anterior chin,instead of
crossing the internal mouth-contact line. No worst rows were deleted or masks
changed. The fixed row ranges stop on anterior chin; they are not whole jaw,
neck,ear or complete-head outlines. The raw and scale-alternative lines remain
available. This supports bounded **observation readiness**,not independently
calibrated true boundary accuracy or an estimated camera. Small scale variation
cannot rule out a common systematic edge-location bias in real optical images.

Fresh sequential ordinals avoid the earlier seek ambiguity. These new PNGs
must not be silently substituted into0218's frozen experiment; a numerical
ratio versus its threshold sensitivity is not a same-input algorithm benchmark.
The new mechanism's known-pixel fixture and actual overlay are its evidence.

The16 sampled views show right/left profiles,frontals and raised/lowered head,
not posterior coverage. This qualitative sample does not prove no brief unseen
view exists in the entire video,but supplies no back-of-head observation.
Hair/cap also obscure cranial anatomy. Unobserved posterior/scalp must stay
explicitly prior-inferred until sufficient data exists; do not claim full-head
millimeter fidelity from successful face traces. No extra patient material or
case002 is opened to conceal this limitation.

Private output:`assets/private/gradient-profile-observations-0243/`,including
exactRGB frames and original-use manifest,fixture arrays,true curves,all-row
traces/uncertainties,`gradient-profile-review.png`,`video-coverage-review.png`,
`visual-review.json` and reproducible execution/test capsules. No patient files
enter Git;191 unit tests pass. Production defaults and0241 rejected geometry
remain unchanged. Execution/fixture/precision and bounded visual-trace checks
are `TECHNICAL_CHECK_PASSED`;physical cameras and final head remain `UNVERIFIED`.

Next real development step is to constrain one shared safe anatomical head with
these **view-dependent** contours and compare the frozen result to the source
scan. Use true projected visible envelopes,not fixed triangle attachments to
each image row. Reuse tested row-envelope/shape Jacobians and strict whole-mesh
guards; no local free patch or scan-fitted initialization. A bounded experiment
must preserve frontal/held-view evidence and all failed rows. Lower fitted
profile residuals alone cannot establish geometry improvement or acceptance.
