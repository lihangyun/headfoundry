# Experiment0254: texture-free silhouette focal capacity,known-motion oracle

Date:2026-10-20. Pre-registered before new masks or coherence measurements.
Status:TECHNICAL_CHECK_PASSED for known-motion focal capacity only.
Unknown-pose/real-video camera and head acceptance:UNVERIFIED.
Previous0253 is progress:a fixed external-reference recipe
fails support,closes atd69d881,and its exclusive artifacts are cleaned.

Use ponytail/minimal existing NumPy/SciPy/OpenCV/Blender only. No new model,
training,service,dependency,real-video fit or head geometry. This tests CAMERA
observability,not appearance or source-scene anatomy. Full goal stays unchanged.

## Research basis and what is not established

[Hernandez,Schmitt,Cipolla2007,author draft](https://carlos-hernandez.org/papers/hernandez_pami07.pdf)
uses silhouette-ray/visual-hull coherence for circular-motion camera/focal
estimation. It accommodates truncated silhouettes,but explicitly states coherence
is necessary,not sufficient. Its circular-motion parameterization and precise
silhouette assumptions are not verified for this human video. Its reported
sculpture quality does not transfer to a living face or our implementation.

[Zhang,Wong2009,author institutional paper](https://hub.hku.hk/bitstream/10722/138033/1/Content.pdf?accept=1)
separates turntable image-invariant/rotation estimation from self-calibration;
it likewise relies on turntable geometry. Neither source supplies commercially
cleared code or a new patient-specific model here. Read principles only and
implement independently;do not attach fixed material IDs to sliding contours.

Inference:an implicit hull can avoid the failed skin/cap texture correspondences,
but weak perspective and limited views might make it unable to distinguish a
wrong focal/distance pair. Test that cheap favorable capacity first,not a full
multi-axis real-camera optimizer with still-unverified assumptions.

## Frozen diagnostic and one variable

Reuse successful0230 upright known-motion geometry/cameras/samples and exact
case001 authorized skin asset. Only known geometry for **evaluation/diagnostic**,
never video-only inference. No case002,bone or old AI image access. Validate only
the selected case001-skin manifest entry,original units/consent and0230 hashes.

Produce native720x1280 transparent white occupancy renders of that unchanged
mesh using the exact6 cameras(front,yaw+-10,+-30,pitch+10),K and recorded source
similarity. No smoothing,fill,mesh simplification,ROI selection or sample changes.
Reuse installed Blender5.2 and shared camera helper,check independent projection
replay<=.05px. Only render alpha/occupancy;no texture or new identity.

Threshold alpha>=128 for target masks. Source rays come from512 equally
arc-spaced samples over **all** contours of a3x3-square once-eroded mask (one
pixel axial margin,diagonal margin up to sqrt2). Use native pixel centers+0.5.
This is a predeclared raster-boundary tolerance,not an accepted physical camera
error or a knob to increase after failure. Keep holes/components;no convex hull,
largest-component selection,contour approximation or error-based point deletion.
These512 samples do not prove every pixel/surface is verified.

For each source sample,intersect its positive-depth ray with each other image's
entire polygon silhouette cone. Retain the **union of all depth intervals**,
not just the min/max envelope,then intersect unions across target cameras.
Record all per-ray feasibility. Coherence is the mean feasible fraction over
all6 views. Synthetic square/hole/disjoint/cheirality interval controls must pass;
an annulus must not become a filled convex hull. Confirm analytic projection
against independent OpenCV and original0230 point pixels.

Only primary variable:focal recovered by this silhouette-only coherence cost,
without photometric intensity,texture matching,semantic detector or prior fit.
Known rotations and translation directions are supplied as favorable oracle
conditions. Candidate common focal f is bounded[400,4000]px and all translations
are multiplied by f/f_truth,which uses the **unavailable true angular-scale
relation**. This isolates the weak-perspective focal/distance ambiguity,not a
general real-camera initializer. Truth geometry/visible material samples are
read only by evaluation after the cost;never by the silhouette objective.

First compute true-camera coherence;require>=.99 or stop before optimization.
Then one SciPy bounded scalar minimization of1-coherence (max32 evaluations,
xatol.1px). No grid,alternate start,offset/sampling/focal bound/algorithm sweep.
Save every evaluation,including flat plateaus and optimizer termination.
Score recovered cameras on **all originally visible** immutable0230 material
points,without fitting/filtering or realignment. Each view needs projection
p95<=3px,proper R,positive depth and successful optimizer termination. Independent
OpenCV projection must replay the reported errors. Do not select a view/solution
by the evaluation errors. A high coherence with failed projection rejects this
recipe;low raster-truth coherence instead rejects its implemented prerequisite.

Budget:one180s mask generation and one180s total coherence/optimization run,
external watchdog with process-handle polling. Refuse overwriting outputs.
Inspect actual masks/samples and final error review. No head/mesh fitting,real
calibration/2mm claim,case002 tuning or default promotion. Even a pass permits
only a separately registered unknown-pose camera capacity check,not real transfer.
If rejected,compact local reports/masks-review/controls suffice;remove exclusive
runner/raw masks/results after archive/Git source recovery and shared regression
checks under0250 policy. No original successful fixture is deleted or changed.

## Executed positive capacity result,not a video camera

Exact executed producer/pre-result protocol are recoverable at16217e6.
One Blender5.2.1LTS process exits0:16.473s wall including startup,5.588s measured
inside generation. All6 masks preserve the exact original mesh/transform/cameras;
camera replay passes. Each target has one outer contour in this fixture;the
synthetic annulus control separately verifies preservation of holes/intervals.

One36.404s cost/optimization run exits0. Truth coherence is1.0,all3072 source
rays feasible. The single bounded solve terminates after22 evaluations at
focal1064.4042px versus fixture1083.2579px (1.74046% relative difference).
Final coherence is1.0. No error-driven sample deletion,realignment or refit.

| Fixed view | All original visible points | Independent projection p95 px |
|---|---:|---:|
|front|2355|0.208176|
|yaw-10|2306|0.206189|
|yaw+10|2343|0.207620|
|yaw-30|2205|0.208252|
|yaw+30|2223|0.205960|
|pitch+10|2003|0.228074|

All rotations remain proper and every original sample has positive depth.
Independent OpenCV projection agrees within2.274e-13px. These13435 visible
sample-view evaluations are conditional on **known rotations**,not a held-out
real-video camera benchmark or new metric anatomy measurement.

The cost is not sharply identified:visited f1064.3550..1150.3372px all score1.
Those are observed trace extrema,not computed limits of the entire plateau.
The solver's.1px stopping tolerance is **not focal uncertainty**. Do not claim
unique/precise intrinsics from a perfect coherence score or choose another
plateau point using source-projection errors.

## Read-only global-scale audit and actual visual review

The protocol conservatively called the true angular-scale translation coupling
unavailable information. It indeed enters the evaluation camera gauge,but not
the coherence information:global translation scale multiplies every ray-depth
interval and cannot change their intersection feasibility. Check this without
refitting,using the already executed first f1775.0776px **non-perfect** trace
point:scale all camera translations by.125. All3072 feasibility flags remain
bit-identical;both scores are.9401041667 (one2.575s replay). This is global
similarity gauge invariance,not new pose knowledge or a recovered physical scale.
A future optimizer can fix unit radius rather than access this true radius.
Known relative rotations and the evaluation alignment still limit this oracle.

Actual6-view masks/source-ray sheet and fixed-output projection panels were
viewed. The panels show the **supplied scan**,not reconstructed output;green
points are true pixels and red arrows magnify residuals20x for diagnosis.
Every original visible point contributes to metrics;display points are sampled
by a fixed ordinal stride,not by error. No new mesh,likeness,2mm score or full
head acceptance follows. The real video's cap/neck rigidity and segmentation
are not validated by this clean synthetic source-only mask experiment.

Private bounded evidence is `assets/private/silhouette-focal-0254/`:render/input
hashes,execution logs,complete trace/per-point errors,mask/projection reviews and
scale replay. Retain this successful evaluation fixture and implementation;
there is no failed-route binary/model to accumulate or uninstall. No source,
case002,bone,production default or old intake artifact changes.

Four standalone interval controls pass. One shared regression additionally
checks true rigid-cube coherence,deliberately wrong-camera rejection and exact
global-scale replay. Full suite:131 tests pass in4.973s. These are numerical
controls,not real head acceptance.

## Next prerequisite

Test unknown relative rotations with the same fixed silhouette cost/populations
and an independently scored camera gate before any real-video transfer or
geometry fitting. Do not hide true rotations in a production initializer or
call the conditional focal result a solved camera pipeline. Only after that
is the source-video segmentation/rigidity applicability question actionable.
Do not return to rejected patch/SIFT/photometric settings or relax3px/2mm gates.

Runnable checks: `python tools/check_silhouette_focal_0254.py --self-check` and
`python -m unittest discover -s tests`. Full mask/solve commands intentionally
refuse existing private output;do not delete the successful fixture to rerun.
The pre-result source at16217e6 and recorded input hashes define this execution.
