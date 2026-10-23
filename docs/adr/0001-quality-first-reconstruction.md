# ADR 0001: quality-first clean-room reconstruction

## 2026-10-23:include full shape-derived normals and actual light coordinate frame

0345tests genuinely pose-coupled fixed-room radiometry,not independent viewSH
or brightness constancy. Normals must derive from ALLfree XYZwith their complete
derivatives;unknown albedo/light/exposure/principal point/pose cannot be fixed
to generating truth when claiming focal information. Do not rotate room light
with the head or omit the R*nchain accidentally. Exact identities and known
connectivity are ideal assumptions,not an image initializer.
This fixture adds a focal rank but conditional sigma(logf)16.33fails the fixed
.02screen despite passing analytic and negative controls. Stop the recipe,
not rescue it with stronger curvature/light/moreframes or quieter noise. Record
independent-light rank too;do not make unique causal claims. No camera/head/
medical/visual gate or default changes. Retain successful generic normal math,
retire one-off failed application after compact evidence/integrity checks.

## 2026-10-23:controlled matching precision does not ensure clinical support

0344full-image ALIKED/LightGlue trial yields22common source-face IDs versus
registered48,despite0343owned-pairp95.515px. Stop before camera/geometry;
neither infer clinical3Derror nor increase feature cap/crop/change frames to
rescue the fixed recipe. Counts/span policies are not physical observability
theorems;this rejection cannot establish that all22points/video are useless.
Retain compact full cohort and successful point fixture,retire candidate stack.
Before inference the audit also found0333source0was only a triangulation
residual:future conditional camera checks must independently leave out each
scored view.0344never ran that checker;source code/tests authored is not proof
they passed. No new actual head/medical or visual acceptance follows.

## 2026-10-23:source-domain physical scores keep undefined assignments visible

0343passes one ownedpair withp95.515px across all732sourcecueassignments,including
one unsupportedInf. Freeze truth/visibility independently before opening model
predictions;never use GTto erase inconvenient matches.Unmatched detections have
no endpoint:report recall/missing counts explicitly rather than silently imposing
95%detection repeatability throughInf. Scope-limited source masks and output
support policies are not segmentation/observability proofs. Positive controlled
precision does not waive actual material/camera/medical/whole-head/visual gates.
Keep immutable successful fixtures;separately register transfer before fitting.

## 2026-10-23:separate conservative cycle admission from physical failure

0338'sindependent visible affine-map witnesses show FB.75can reject1pxtrue
endpoints and accept16pxwrong ones. It is neither necessary nor sufficient for
physical endpoint3pxprecision;the metric3D/surface gate is separately required.
Keep historical operational entryREJECTs and immutable observations,not claims
of unmeasured physical failure. No replacement threshold or selection policy is
admitted by these counterexamples. Prospective new estimator validation must
establish its observation/noise/support and identifiable training graph with
independent truth/held evidence. Do not replay retired clinical data under weaker
filters,restore failed models,or fit a head on this audit alone. Actual camera
3px/fixed medical2mm/full-head/mesh/user visual gates and defaults stay unchanged.

## 2026-10-23:independent scoring controls must respect their numeric domain

0336'sfirst oracle-equality assertion stops before learned endpoint scoring:
float64(trueUV+40)-trueUVneed not be exactly40for nondyadic pixel coordinates.
Preserve the original stop and separate a dtype/input-magnitude-derived roundoff
bound from actual pixel/mmquality gates. Do not retrofit a model tolerance from
its just-observed error or rerun inference to hide failure. Only the unscored
evaluator control is repaired;all source/model/field/cohort/3pxchoices stay fixed.
Independent point precision on one owned pair does not prove camera calibration,
real-skin generalization or final reconstruction. Existing identifiability and
whole-head/medical/visual gates remain required. Successful phase receipts stay
immutable;new experiments write their own state/logs rather than overwrite them.

## 2026-10-23:freeze conditional direct-image capacity before domain transfer

0332fully passes one fixed owned3-view camera/depth control after a different
dense endpoint initializer. Retain the successful small image/truth/state fixture
and original physical evaluator;do not erase priorLKentry or sequentialDISID
failures. Passing a planar-patch/radiometric-model-exact context does not establish
curved/specular/deforming skin observations or real-video anatomical identity.
Before patient head fitting,require separately registered actual correspondence
and camera evidence,with independent held scoring and no scan geometry in the
estimator. Synthetic scene-unit error is not medicalmillimeters;all actual3px/
fixed-surface2mm/whole-head/visual gates and production defaults stay unchanged.

## 2026-10-22:validate information on the final training fold

0329shows one exact three-view common-point geometry has locally independent
focal information whereas two/repeated views do not. The unchanged source-query-
excluding one-held-target fold destroys that constraint. A full-observation
rank result cannot justify a solver protocol with a different training graph.
Check the actual training/held split before execution,without leaking held
pixels or discarding independent validation. This is not permission to sweep
view counts/angles or reduce camera/medical gates. Local information is not
global uniqueness,achieved accuracy or patient evidence.
Near a known exact null,central derivatives can create spurious tiny rank even
when relative derivative error is1e-10. Require an independent analytic/null
witness rather than tuning rank tolerance to the preferred outcome. Preserve
the original data/gauges and record both numerical and analytic results.

## 2026-10-22:calibration fixtures must identify the claimed unknowns

0328exposes a critical two-view equal-pivot-radius orbit:the true centered
rank-twoFhas an identically zero Demazure cubic under any positive focal
scale. A wrongf451and true1200both explain all exact image correspondences
with positive retriangulated depths. Known3Dprojection correctly rejects the
wrong physical camera,but this fixture cannot determine a solver's unique-f
recovery accuracy. Matrix validity,cheirality,inlier count,noncollinear motion
or zero reprojection alone must never substitute for identifiability.
Keep the numerical polynomial witness and a fixed radial-motion negative
control. A nonzero polynomial is not itself unique/stable calibration or a
noisy physical pass. Before another conditional calibration test,justify
genuinely sufficient information;do not merely swap solvers or tweak frozen
failed trajectories. This exact two-view result does not prove actual video
or earlier multiview runs unobservable;those need their own evidence. No
patient/head/medical gate,prior-as-truth restriction or production default changes.

## 2026-10-22:separate failed initialization entry from unmeasured direct accuracy

0321's fixed image-only full-track screen admits34of96queries,not its required48.
Stop before joint direct-patch optimization or known-camera physical scoring.
Do not call the unexecuted optimizer physically rejected or synthetic coverage
a patient result;do not lower entry support or tune LK/scene/angle/count to
salvage it. Correct residual math0320remains useful independently of the failed
application. Retire exclusive0321code/bulk with compact provenance before any
different architecture. TrueK/pose/scan may never seed image-only inference.

Status: accepted for implementation; final product quality remains `UNVERIFIED`.

## 2026-09-04 implementation amendment

All reconstruction runs must start from a versioned manifest that binds each file to SHA-256 and records provenance, allowed purpose, retention/deletion policy, and biometric consent. The VGGT adapter is restricted to the exact `facebook/VGGT-1B-Commercial` identity and its gated `vggt-aup-license`; neither missing records nor unavailable weights may trigger a fallback.

Status meanings are fixed: `TECHNICAL_CHECK_PASSED` is a bounded non-visual engineering check; `UNVERIFIED` means evidence has not been collected; `REJECT` means a required gate failed or is missing; `PARTIAL_SUCCESS` means numeric gates pass without complete licensed visual evidence; `ACCEPT` requires all protected gates plus licensed benchmark, held-out visual review, and complete reconstruction evidence.

## Decision

### 2026-10-21 allocation changes require output equivalence,not weaker inputs

0292 resource failure does not measure physical tracking precision. Preserve the
stop,retire exclusive assets before a different hypothesis,and do not alter
resolution,points,FP32,sequence or resource caps to call it passed.0293 permits
investigating independent-batch convex-upsample allocation only:NumPy algebra
passes,but CUDA/full-network equivalence and native capacity remain unproven.
Require those checks before another physical correspondence experiment. A
smaller symbolic temporary or passing software oracle is not camera/head quality.

0294subsequently passes fixed complete-network equality and native capacity;
0295still fails actual known-motion material/occlusion precision. Retire the
model-specific integration while keeping small independent software oracles.
PNG metadata is separate from model RGB identity:retain the initial hash stop
and explicit pre-inference record repair;missing historical pixels stay
unverified. No substantive physical threshold,cohort or input-error selection
is justified by a serialization repair. No second scored forward follows failure.

### 2026-10-21 model-output index contracts precede geometric interpretation

0270's pinned HF path passes strict learned-state loading but fails a known
planar correspondence gate. Preserve its failure and retire exclusive assets.
A deterministic interior coarse-match permutation exposes an upstream pair-order
contract hazard;do not silently reassociate predictions or label this as proof
that every release/architecture fails. Independently audit coarse identities,
fine-window axis/padding and floating pixel transforms before another bounded
trial. This is a supported source-correctness question,not permission to sweep
models/thresholds or waive physical camera,2mm,whole-head and visual acceptance.

### 2026-10-13 actual visible aperture and exported-mesh safety

Normal-facing transition edges are contour candidates, not visibility evidence;
first-hit rays must exclude hidden surfaces. Use actual skin/eyeball ownership
transitions for view-dependent eyelids rather than forcing fixed oblique sparse
eye corners to remain visible. Declare correspondence changes, preserve failed
bindings and keep exact final visibility checks. Their image residuals are not
common material tracks or physical camera acceptance. Enforce safety on the
finite exported mesh, not only its cage; never substitute convergence for guards.
Independent serialization/replay checks must preserve original faulty archives
and hash any corrected metadata without silently changing geometry.
Experiment0205's technically valid whole-head fit still fails nasal/lip profile
likeness. Keep its local evidence, leave defaults unchanged and inspect coherent
profile anatomy next. No hair/texture or visual/KeenTools gate is waived.

### 2026-10-13 full-head registration and contour support

Use a proper positive similarity to align a source head without independently
stretching its anatomical axes. Normalize rounded source attachment weights
explicitly for affine replay, and re-embed them on the finite exported surface
after geometric subdivision. A fixed semantic point can remain hidden even
when its2D projection resembles an observed contour. Experiment0204 rejects
static jaw/upper-lid support before fitting; do not relax visibility to make
that route run. Derive actual visible supports and recheck after deformation.
Pose convergence, added generic eyes and passing107 tests do not promote a
stock source head or establish physical camera/identity quality.

### 2026-10-13 inner-lip attachments do not define physical closure

Experiment0201 retains posterior source lip support and fixes a diagnosed corner
side-order reversal by welding contact laterally while preserving body X.
Official 68-point contour attachments and self-derived row numbering do not
establish a physical contact surface. Report changed lateral section relations;
do not claim complete section preservation when only Y/Z relations are retained.
This representation improvement does not promote the fitted donor, whose lower
roll samples become hidden and whose actual lip-to-skin form still fails review.
Experiment0202 rejects one depth-only rollback despite valid mesh checks.
Keep the source repair but inspect coupled lip and surrounding-skin anatomy
before more subject fitting. A pigment border is not proven to bound the whole
geometric lip volume. No camera, complete-head, hair or texture gate is waived.

### 2026-09-29 closure consistency precedes identity fitting

Experiment 0200 finds that closing a mean mesh while only averaging welded
basis entries leaves surrounding shape directions in the open-template space.
Apply the same frozen closure operator to both mean and variation; verify
neutral replay, finite-difference derivatives and retained section relations.
Reconstruct the original pre-weld graph, not a graph that omits intentionally
collapsed faces. RMS preservation is not a pointwise displacement guard;
enforce declared hard bounds without post-fit rescaling or relaxed thresholds.
Both actual constrained donor renders remain visually rejected after correction.
Recheck complete refined-curve visibility after shape changes: a once-visible
fixed material binding can become hidden. Correct implementation and a legal
shape prior do not establish natural closed-lip anatomy or subject likeness.
Stop tuning this rejected fit until the underlying contact-section and visible
support representation is justified. No head, camera, hair or texture promotion.

### 2026-09-29 a generic generated object is not an anatomical head prior

Experiment 0199 executes an explicitly MIT-released local initializer, but both
tested extraction precisions are visually rejected. Model availability, many
triangles and a watertight flag cannot override eyelid/nose/lip anatomy and
front/profile appearance checks. Report connected components and degenerate
incidences separately from the watertight boolean. Stop resolution/threshold
polishing of the rejected field; do not graft it into the current head.
An experimental asset lock records provenance; it is not itself enforced
production validation. Python assertions are unsuitable for mandatory rights
checks because optimized execution disables them. Local diagnostic success
does not change camera, consent, head-only or quality acceptance requirements.

### 2026-09-28 material curves are not automatically visible observations

Experiment 0198 rejects the tested free-XYZ native donor fit and its bilateral
follow-up. A welded zero gap is a topology check, not independent contact or
collision evidence. After subdivision, track inserted curve-edge vertices as
well as original attachments; verify nearest-surface visibility before treating
a projected material curve as a photo silhouette feature. Reduced binding
residuals and zero flipped faces do not override failed area/visual gates.
Do not graft or tune the rejected point-pulling branch into the subject head.

### 2026-09-27 coherent source versus coherent deformation

Experiment 0197 supplies a checked connected GNM closed-mouth exterior and
finite geometric refinement. A coherent source transferred as per-pixel depth
does not imply coherent destination anatomy: both actual candidates remain
visually rejected. Stop the tested transfer family's warp/depth/smoothing
sweeps. Next screen continuous 3D deformation with contact and skin-transition
checks before subject fitting/promotion. Existing pigment-rim depths and old
patch ownership are not anatomical truth; an expanded support must explicitly
declare and test its new protected exterior. No acceptance gate is relaxed.

### 2026-09-25 independent-reference and head-only scope

The user confirmed that the five locally authorized reference views were
generated or composited independently rather than captured from one rigid
subject or rendered from one fixed 3D scene. Rights/consent still permit
local validation, but image clarity and angle coverage do not imply shared
physical geometry. Prior cross-view camera residuals remain reproducible
image-group diagnostics, not measurements against a real camera truth or
proof that every discrepancy is pose error. A controlled same-subject capture
or known-camera, fixed-geometry synthetic set is required for physical
camera acceptance. Until then, use these views only for experimental visual
reference matching and label subject identity and full reconstruction
`UNVERIFIED`.

The user's current priority is the head mesh. Pause hair candidate work.
Compare front and both pure profiles under fixed experimental cameras and
change one head-anatomy factor per trial; require exact visual comparisons
and protected-face/mesh-safety checks before considering any promotion.
This prioritization does not waive the existing camera or visual gates.

### 2026-09-21 FLAME 2023 Open identity prior

The exact official `FLAME 2023 Open` model may be used as a neutral identity
prior under its published CC-BY-4.0 terms, including attribution, change
disclosure and prohibited-use review. This permission does not extend to
standard/older FLAME releases, registered scan data, landmark assets or the
separately licensed FLAME texture model. The official download and a safe local
conversion must each be hash locked. Adapter tests do not establish model-file
availability, subject fit, camera accuracy or visual acceptance.

The official asset was safely converted and hash locked on 2026-09-22. This
changes model availability to `TECHNICAL_CHECK_PASSED`, not identity quality:
experiment 0143 rejects the tested linear identity and topology-transfer
candidates. FLAME remains an optional standard topology/rig prior, never a
likeness or camera acceptance shortcut.

### 2026-09-12 independent Apache dense geometry

The exact `facebook/map-anything-apache` checkpoint may be loaded with its own
source/runtime/weight lock and offline, architecture-only DINO initialization.
It is a distinct experiment, never a fallback through the commercial VGGT
adapter. Actual experiment 0106 inference succeeds but camera and visual
promotion fail. No raw dense-surface fusion or texture is justified by model
availability. Any camera-conditioned follow-up must label its supplied cameras
as unaccepted, preserve independent held evidence and distinguish conditional
depth results from independently recovered calibration.

### 2026-09-08 user-authorized experimental geometry

The user explicitly authorized an **unaccepted experimental head** before the
camera gate passes. This supersedes the development sequencing restriction,
not any acceptance threshold. Experimental mesh exports and original-photo
comparisons may now proceed locally. They must state `UNVERIFIED`, preserve
camera failures, and distinguish observed surfaces from inferred/unseen regions.
Partial depth surfaces must not be described as a complete reconstructed head.
No texture or generated imagery may conceal geometry failures in comparisons.

### 2026-09-05 weight-independent development route

Following the user's direction to self-develop unavailable components, VGGT is
optional for future experiments rather than a prerequisite for all progress.
Its existing adapter remains locked to its commercial checkpoint. A separate
explicit weight-independent initializer may use our own geometric optimization
and consented anatomical annotations. It must still prove camera conventions,
physical validity, and held-out reprojection before advancing reconstruction.
This decision does not authorize substitution of research-only weights or imply
that the self-developed initializer is already implemented or validated.

### 2026-09-07 explicit matcher and camera alternatives

Separately identified free-commercial components may be tested with their own
source/checkpoint/runtime locks. LighterGlue uses the exact reviewed local
matcher bundle and Kornia 0.8.1; it does not load a fallback extractor or relax
the VGGT identity check. Consent remains limited to local validation.

Camera fitting must exclude every observation of the frozen held-out tracks.
Training consensus statistics cannot replace complete held-out reprojection.
The optional robust initializer rejects exact duplicate endpoints, invalid
intrinsic structure and a median triangulation angle below the default 1 degree.
These are necessary engineering safeguards, not calibrated accuracy guarantees
or evidence explaining this subject's failure. Experiment 0017's joint fit is
still `REJECT` at 7.5456 px held-out p95; no geometry or texture gate is unlocked.

The next candidate is specifically the officially Apache-2.0 `DA3-BASE` model,
with a separate asset review and camera-only evaluation. Its local execution
and result are not established by this decision; Large/Giant checkpoints are
not interchangeable fallbacks.

Experiment 0018 subsequently completed the separately locked DA3-BASE local
inference. It did not unlock the camera gate: after same-track joint refinement,
7.5485 px held-out p95 is effectively unchanged from 7.5456 px. The next experiment
must distinguish correspondence/localization limitations from camera fit, rather
than treat another starting model as demonstrated progress in visual accuracy.

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
- Pixel3DMM weights, FaceScape, Multiface, VHAP and standard/older FLAME releases: non-commercial restrictions. The separately named FLAME 2023 Open model is governed by the decision above.
- nvdiffrast: its published license is not suitable for this product. PyTorch3D is the selected differentiable renderer.
- Pure NeRF/Gaussian avatar output: does not provide the required stable fixed topology and editable mesh contract.
- Training a large end-to-end model first: delays falsification and hides camera, geometry, and texture failure modes.

## Data strategy

Experiment 0206 records a bounded exception for fitting local bilateral profile
envelopes against the five authorized AI-generated/composited references. Keep
camera and pose frozen, preserve the exact mesh guards, and audit support
visibility against the full exported head. Interleaved rows are diagnostics,
not a holdout: earlier candidates and cameras have already used these images.
Even a passing contour or ray check cannot promote the head. The first full
white-mesh comparison shows profile change but not recognizable likeness, so
the candidate is rejected and production defaults remain untouched. Continue
with coupled front/profile anatomy only; hair and texture stay outside scope.

Experiment 0196 permits only the already pinned Apache GNM neutral data as a
local anatomical donor hypothesis. Exact lip groups, exterior membership,
anterior contact closure and source hashes must be checked explicitly; neither
neutral pose nor broader region names prove closed anatomy. Discarding oral
rows is not an expression-capable full-head closure. Exact donor transfer and
rim continuity checks do not waive visual acceptance: both local candidates
are rejected. Stop fixed-rim section transfer; subsequent head-only work must
screen coherent lip-to-philtrum/chin support while protecting the rest of the
head, rather than tuning another additive amplitude.

Experiment 0194 adds a photometric boundary: fitting unknown per-view
illumination and shared albedo does not establish convex/concave anatomy.
Native image-space regions must be audited against the declared OBJ axes;
appearance-null controls and spatial holdouts precede shape fitting. Diagnostic
lighting must be reported and kept equal across candidate comparisons, never
counted as geometry improvement. The head-only scope excludes hair and does
not waive visual or camera acceptance.

Experiments 0114–0115 permit a separate local neutral-mouth topology proposal
after repeated fixed-topology closure failures. Exact boundary stitching and
unchanged retained exterior are required, but do not constitute anatomical
acceptance. Removing the old oral cavity sacrifices its representation; this
must not silently become an expression-capable product mesh. Metric-aware
surface interpolation is tested independently of visual quality. No camera,
texture or full-head gate is waived by these experiments.

Experiment 0058 extends the same reviewed graphical-data approach to four
whole-head shape controls. Apply deltas on original source topology before
neck clipping; new clip vertices must not receive guessed mappings. Generic
shape names are controls, not inferred demographic labels or identity evidence.

The 2026-09-10 experiment 0055 adds a bounded alternative to ad hoc geometry:
explicitly CC0, hash-pinned mouth/philtrum graphical displacement targets from
the existing base asset's revision. Use independently implemented data parsing,
not upstream application logic. These are generic authored shape controls,
not trained identity reconstruction. Verify frontal and bilateral effects;
their availability does not relax camera or visual acceptance gates.

Bootstrap with synthetic renders from commercially allowed parametric assets and our own procedural lighting/camera variation. Build the real benchmark from explicitly consented captures paired with licensed high-quality scans. Store identity/biometric consent, allowed uses, retention, and deletion state with each subject. No dataset enters training until its license is recorded in the asset manifest.

## Compute strategy

0241's isolated video-only model branch may export an explicitly unaccepted
safe OBJ under the existing experimental lane. Its generic learned semantic
observations,even with exact ray attachments and held detector residuals,are
not independent physical material correspondences. Recheck final visibility
without deleting failed supports. Keep scan registration/measurement in a
separate post-inference process with one recorded whole-output similarity and
no geometry/camera feedback. Numerical safety/replay must not promote a failed
video camera,regional error or complete-head visual result. Failed fixed
attachment assumptions require a bounded known-geometry test before refitting,
not another coefficient,focal,regularizer or point-subset sweep.

0244-0246 distinguish a failed prerequisite from an explicitly unaccepted
geometry diagnostic. A later diagnostic using valid observations must carry
every required missing/unstable held-view failure forward;it must not silently
turn a smaller available-view test into full acceptance. All original image,
3D,visibility,topology and visual gates still apply.0246 demonstrates that even
safe lower contour residuals can regress independently measured nose/mouth3D.
Reject that candidate,retain all evidence,and require a supported different
mechanism before more fitting. Global similarity/camera gauge must be diagnosed
without using a source-driven post-hoc alignment to manufacture improvement.

Experiment 0112 adds independently implemented Catmull-Clark finite refinement
as an explicit experimental geometry operation. A control cage, smooth shading
normals and an evaluated smooth surface are different representations. Fit
and validate the representation actually exported; old triangle attachments
must be re-established after subdivision. No automatic post-fit smoothing or
default promotion: the first real refined candidates regress a profile and
remain visually rejected. This requires no new trained asset or application
code reuse and does not change the camera/visual acceptance contract.

Camera investigation may optimize a temporary face patch as a nuisance variable,
but this does not authorize acceptance of head geometry or texture. Experiment
0009 keeps focal length and prior fixed, excludes validation from all fitting,
and remains REJECT. Detector self-consistency is not independent shape evidence.

The historical RTX3070 description is not current availability evidence:
2026-10-20 both local Python environments reportCPU-only and NVML fails.
0248/0249 must use explicitly timedCPU float32 execution;do not silently change
drivers,precision or resolution to rescue a benchmark. Future GPU sizing is a
profiling question,not a verified production requirement.

0248 separates checkpoint licensing from executed transitive code. An Apache
weight label cannot clear a nested NC module. Use only pinned reviewed
permissive code paths,retain upstream notices,block unsupported imports and
fail closed on missing/changed asset/source/runtime evidence. Strict full
parameter loading is necessary but not sufficient for accuracy.0249 uses the
unchanged known3D image-only camera/point screen before any real-video geometry
transfer;no confidence pruning,per-view realignment or production promotion.

0249 fails even with finite proper cameras and positive points. Internal point
composition consistency does not prove a pinhole camera explains the predicted
ray field,or that cameras agree with independent physical correspondences.
Require both checks;reject the current configuration without real-head fitting.
Some lower camera residuals do not establish a net benefit when joint geometry
regresses. Keep this bounded failure rather than relaxing the original gates.

## 2026-10-20 failed-route retention policy superseded by user cleanup request

Cleanup0250 keeps failure conclusions,source recovery refs and compact private
evidence,but removes exclusive failed-route code/tests,generated binaries,
weights/frameworks and environments before another route starts. Earlier
instructions to retain all failed candidates mean historical auditability,not
indefinite storage of every binary. Never remove original consented materials,
accepted baselines or shared safety/evaluation tests. Follow rootAGENTS.md.
Historical experiment commands may require Git recovery and reinstallation;
do not reactivate rejected configurations automatically.

## 2026-10-20 source frame identity and observable coverage

0252 proves backend seek-position labels can differ from actual decoded pixels.
Authoritative frame identity requires sequential ordinal plus RGB digest,not
merely a successful seek or matching backend counter. Preserve old artifact
identities;do not silently rewrite historical inputs. Container display matrices
and camera-sounding metadata tags are not physical calibration. Thumbnail review
can establish qualitative capture limits,not exact pose or metric head accuracy.
Only current footage is available;continue visible-face research but keep unseen
scalp/posterior completion explicitly unverified. No full-head gate is waived.

## 2026-10-20 silhouette capacity is conditional camera evidence

0254 permits a texture-free implicit-hull camera diagnostic,not a scan-conditioned
video reconstruction. Keep every depth interval across concave/holey silhouettes;
an outer min/max envelope can falsely declare coherence. Positive coherence is
not sufficient for accurate cameras:score all immutable known material points
independently,and retain proper matrices/cheirality/projection gates. Report
cost plateaus separately from optimizer tolerance and physical uncertainty.
Global similarity scale cannot be inferred from silhouette coherence alone.
Known rotations in a capacity test must not silently enter real inference.
No geometry fitting follows before unknown-pose and actual-video applicability
are independently validated. Original3px/2mm/full-head/visual gates stay intact.

0255's higher silhouette coherence accompanies worse independent projection in
every view and unsuccessful bounded termination. Do not transfer a known-pose
capacity result to unknown pose or interpret numerical improvement as physical
camera recovery. Preserve both successes and counterevidence with their actual
conditions. A demonstrably feasible true solution does not excuse a failed
initializer/solver,and one failed bounded solve does not prove all silhouette
methods impossible. Close the registered recipe without budget/seed/threshold
rescue. Failed camera outputs never initialize a purported accepted head.

0256's continuous explicit witnesses reduce distance loss to.129px RMS while
every independent camera still fails3px. Step-tolerance termination with large
reported optimality must not be sold as physical/global convergence. Count loss,
distance loss and latent feasible witnesses are different measurements;none
alone proves camera correctness or material correspondence. Close this attempted
silhouette-only unknown-pose numerical family after the registered second
mechanism fails;require independent information rather than another field,
weight,depth prior,solver or budget change. Preserve the known-motion fixture
without implying that the failed extension is production-ready.

0257 separates native material-feature observability from camera eligibility.
One feature in six frames is at most one physical identity candidate,not six
independent3D supports. A broad soft-tissue patch,unresolved cluster or neighboring
spot pair cannot silently become a precise rigid point. Record out-of-display
features separately from proven physical occlusion. Do not claim1px accuracy
from nearest-neighbor zoom or lower camera support requirements after inspection.
The bounded audit supports input identity,not calibrated correspondence or head
acceptance. Record its visual-review budget overrun and stop further expansion;
retain compact local hypotheses/evidence without starting a fit or changing any
production,3px,2mm,whole-head or actual-visual requirement.

0258 permits one separately locked Apache TAPNext++ recurrent observation model
because global image tokens/temporal learned state are distinct from retired
local trackers,not a tracker-threshold rescue. Its all-point planar precision
screen passes without filtering or post-hoc coordinate/bias correction. Preserve
that positive prerequisite but never transfer its result directly to3D:known
planar warps have neither true out-of-plane visibility nor skin rigidity. Require
independent3D motion/visibility and real applicability before camera/head fitting.
Model and checkpoint rights are reviewed separately,imports kept minimal in an
isolated runtime,and no human upload/training or production change is authorized.

0259 fails conditional3D material tracking and occlusion despite0258's planar
pass. Exact image returns,numerical replay and permissive assets cannot waive
physical correspondence. Score every true-visible initialized ID even when
the model calls it hidden;retain both visibility recalls and never initialize
unseen material IDs with hidden oracle3D. Do not attribute cross-fixture error
differences solely to rotation when appearance/query population also change.
Close this preregistered recipe without temporal-density,texture,query-count,
crop,resolution or threshold rescue. Retire its exclusive inference integration
and runtime while retaining successful small mathematical/2D evaluation evidence.
No camera/head fitting or relaxation of3px/2mm/full-head/actual visual gates follows.

0260 distinguishes model-family research,available artifacts,published grants,
and cleared runnable inference. NC releases cannot enter this commercial goal;
an unofficial D4RT implementation is neither the original model nor necessarily
unusable,but needs its own checkpoint/dependency/resource preflight. Do not
install a14GB artifact solely on a license badge or paper score. GeoCalib's
intrinsics/gravity are an optional cue,not complete head-relative extrinsics;
a same-K/gravity counterexample is retained as a shared safety regression.
No new model adoption,patient run or camera/head acceptance follows this screen.

0261 allows further bounded work on the published permissive OpenD4RT path but
does not clear runtime/accuracy. Require explicit strict full-state loading and
safe weights-only serialization;do not accept warning-only partial loads or
unsafe pickle fallback. File size,parameter payload and measured peak are
different resource facts. A documented mmap/meta/assign adapter may preserve
weights/FP32 while reducing duplication,but must restore deterministic
nonpersistent buffers and prove query-chunk invariance before reliance. Do not
silently quantize,change architecture or prune point populations to fit memory.
Published scene-camera quantities must not replace moving-head material/pose
evidence. Camera,2mm,whole-head and actual human visual gates remain unchanged.

0262 establishes loading/query invariants on a tiny deterministic fixture and
full empty meta architecture only. Preserve all tensors,precisions,queries and
strict keys;restore only the documented deterministic nonpersistent buffer.
Version-select a patched weights-only loader before trials,not unsafe pickle
fallback. Explicit local cache paths are ordinary environment repair,not a
model change. Report failed attempts as well as successful ones. A successful
small IO check and empty full graph do not establish actual released-checkpoint
compatibility,full memory/runtime or3D model accuracy. Require those separate
bounded gates before private real-video cameras or geometry;do not confuse
282.841MB test peak with the model's4.650GB parameter payload. No threshold,
head completeness,privacy or actual visual requirement changes.

0263 corrects a pre-valid Windows resource assumption:copy-on-write mappings
may charge commit for the entire file even when resident working set is small.
Do not treat the0262 small-file success or available physical RAM alone as
large-file mapping clearance. Before released-state execution,record a safety
amendment using the pinned Torch FakeTensorMode metadata path without full-file
mapping;prove its small-fixture invariants and retain the original protocol.
This is not model-value materialization or numerical rescue. Never silently
extend the registered transport deadline,relax strict matching,change the model
or use a writable shared mapping to avoid commit requirements. Actual model
inference still needs independent RAM/commit and physical3D accuracy evidence.

0264 separates a failed floating-point chunk-invariance precondition from
unmeasured3D reconstruction accuracy. Preserve the registered stop and do not
post-hoc tune tolerance/batch/precision. Conversely,do not classify a three-
component tensor delta as physical pixel/mm error or invent the failing head
when logs omit its name. Tiny-model invariance does not prove full-width FP32
batch invariance;the numerical control itself needs an independently justified
error budget. Source finite-byte/strict-load success and a partial forward are
not complete inference,physical correspondence or head acceptance. Seek one
explicit choice before treating still-untested public weights as disposable
failed assets or conducting a separate control-design audit;start no new route
while pending. Retain source recovery/compact evidence and protect originals.

0265 records the user's audit-only/temporary-retention choice. Distinguish exact
asset identity and finite/execution safety from numerical batching diagnostics
and physical quality. A blanket tensor tolerance across coordinate/logit/normal
heads needs an independently justified purpose/error budget;generic library
defaults or the just-observed mismatch are not such a derivation. Missing head
names/raw controls must be declared unknown,not silently reconstructed. Persist
future diagnostic evidence before a failure,if separately authorized to execute.

Do not change0264 or label its batch failure a harmless false positive. A future
trial may only use a prospectively approved fixed execution contract with all
physical gates intact;no arbitrary-batch equivalence claim follows. Audit-only
permission does not authorize that trial or indefinitely retain a rejected route.

0266 is separately authorized and prospectively registered. Record batch
consistency as a diagnostic without changing physical gates,then measure the
complete canonical schedule. The full run completes but fails0/31 physical
views,including bilateral point/visibility/localization gates. Reject and retire
this exact frozen recipe;do not reinterpret completed execution as a head or
rescue it with another preprocessing/checkpoint/budget sweep. Preserve exact
compact diagnostics and source recovery,not failed exclusive model infrastructure.

0280 adds no new product architecture. An affine metric upgrade is only an
initializer;positive definiteness,proper rotations,positive depth and optimizer
termination cannot stand in for independent unknown-pose perspective recovery.
Its software control fails,so patient estimation stops rather than fitting a head
or declaring the video's physical identities invalid. Keep original gates and
retire the fixed failed implementation;do not normalize a focal-bound solution
into success or start an unregistered reflection/threshold/iteration search.

0281 supplies explicit frozen-camera reflection evidence;0282 separately
registers the two discrete affine-depth alternatives and training-only objective
choice,not a parameter sweep. Its exact-data control recovers the true camera
without held selection,but actual training observations give an indefinite
metric. Do not clamp that metric or promote synthetic recovery to patient/head
success. Structural implementation repairs and actual-video applicability are
separate gates;preserve the original failures and clean failed exclusive code.

0283's control demonstrates that exact projective training reprojection does not
certify a valid metric upgrade. The analytic control camera family admits a
rank1 linear-quadric solution alongside rank3;never accept an arbitrary last
singular vector merely because its constraint residual is tiny. A separate
prospective rank-constrained alternative needs training-only selection and
independent held evaluation,not known focal/pose or medical geometry as an oracle.
0283 staysREJECT and is cleaned before such a different attempt.

0284 explicitly registers finite rank-three candidates,records every root and
selects by training-only pinhole error before untouched held scoring. Its frozen
prefix/new-upgrade control passes without known pose/focal/medical selection;
actual prefix hits its180s resource stop. Distinguish successful necessary math,
resource failure and unmeasured physical precision. Keep the small algebra
regression,not the failed application. Do not raise time limits or swap inputs
to hide the stop;any implementation acceleration first proves fixed-input
objective/gradient and pixel-replay equivalence under a separate bounded audit.

0285 supplies that fixed-input audit and3.49xconditional-kernel speedup without
changing original data/objective/iterations/budgets or quality gates. This is
not a promise of identical nonconvex optimizer trajectories;fresh held control
is still required and passes. Actual projective refinement/metric eligibility
fails,and frozen held-camera prediction also fails7.57px. Resource acceleration
does not upgrade head quality. Freeze this fixed pOSE+quadric recipe;no more
iteration,calibration-subspace or residual-based point/mask rescue. A new route
needs independently justified observation/rigidity or initialization evidence.
Keep only successful generic math and minimal private evidence,not failed apps.

0286 separates calibration-free local image consistency from global camera
initialization and physical geometry. Frozen held tracks increasingly fail the
predefined pair screen at longer separations,so global optimizer repair alone
cannot certify those observations. This association does not identify drift or
nonrigidity causally. A synthetic along-epipolar-line mismatch passes despite
40px error:passing the necessary constraint cannot certify identity/depth or
replace3pxcamera/2mmskin gates. Preserve complete pair failures/eligibility and
require independent observation evidence,not residual-based track selection or
another retired-solver replay. No actual head/visual acceptance follows.

0291's resource implementation moves a linear dot through bilinear sampling
without shrinking input/model/window/point capacity. Require whole-network
pixel-output controls,not a blanket raw tensor tolerance,then measured native
resources. Fixed smaller-control equality and algebra still cannot guarantee
all native nonlinear FP32outputs or actual material identities. Confidence
threshold comparisons are diagnostics,not calibrated physical acceptance or
permission to filter a cohort. A full native forward is only capacity evidence;
known3D/visibility,actual camera and independent medical/head gates remain.

0292shows that a successful fixed16-frame capacity control does not certify all
sequence/padding allocation patterns. Preserve an actual OOM as resourceREJECT
with unmeasured physical quality. A large batch-independent upsampling temporary
is evidence for a future exact-memory implementation audit,not permission to
change model/frames/precision,allocator flags or budget after failure. Retire
failed exclusive integration before a materially different,registered repair.

0298admits a narrow sparse detector/descriptor runtime,not a head route promotion.
Keep exact publisher asset IDs and pre-inference acquired-byte hashes,strict full
state and all parameter-byte checks. RootMIT does not erase third-party copied
utilities;use only the scoped cleared core/independent glue and retain notices.
Reference software equality and measured native capacity cannot establish
anatomical identity,visibility,3Dcamera recovery or2mmskin accuracy. Next test must
measure actual-image correspondence evidence under a prospectively fixed cohort,
with no medical geometry in the estimator and no head fitting before camera gates.

0299rejects a fixed raw sparse matching contract on real input,not model execution.
Preserve gross matches even when a percentile passes;numeric endpoint uniqueness
does not establish semantic/material identity. Distinguish count-ineligible pairs
from actual held residual failures. A training-RANSAC fit cannot certify untouched
putative held matches,but failure of this raw contract is also not a test of every
robust SfM association pipeline. Retire the failed exclusive integration before
new hypotheses;no post-error score/mask/pruning or camera/shape sweep to rescue it.

0300shows a structural interaction between independent holdout and incremental
PnP:three-view tracks leave only two training observations,so an initial stereo
point cannot attach another camera. Preserve this stop;do not leak the held view
or infer global unobservability. Retain successful coordinate-free graph controls
without calling cycles physical truth. Any different globally coupled initializer
must prove unknown-camera/scale recovery on the unchanged corrupted short-track
control before patient construction. No head/medical gate or default changes.

0301proves the different global bearing initializer on identical controlled
tracks/folds,not merely proper rotations or optimizer termination. Require full
bearing rank/positive scales and preserve the deficient-tree counterexample.
Its exact synthetic recovery supports a generic numerical backend,not every
observation graph. The fixed real cohort provides only a near-repeat F pair,
nonphysical focal boundary and no valid stereo baseline;stop before patient
geometry. Do not lower parallax/cheirality/hold-support or extend f to rescue it.
Keep successful standalone math/control while retiring the failed application.

0302tests partial triangle closure without altering pixels or camera math. Its
literal counterexample repairs an overly strict completeness assumption,but
does not establish physical identity. Actual association count increases while
the full eligible pose graph remains disconnected and focal hits a bound. Stop
and retire the fixed application;freeze further closure/score/forest/clustering
variants on this cached cohort. Do not promote a partial tree into complete
metric cameras or count growth into shape accuracy. New work needs genuinely
different justified source observations,not another solver/threshold sweep.

0303separates complete inference from failed fixed-anchor coverage. Missing330
cannot be replaced post-hoc,while its qualitatively judged domain also cannot
prove all784detections unusable. Future reuse requires a distinct explicit domain/
visibility protocol. Relative z/AR transforms/presence are not physical cameras,
material identity or independent truth.3px/2mm/head gates and defaults stay fixed.
# 0304:separate bounded optimization failure from physical impossibility

Anatomical VIDEO semantic observations are hypotheses,not fixed material truth.
The four-view solve has valid matrices/positive depth/nonbound focal,but misses
held3pxand one sample-count condition at a nonconverged300-evaluation limit.
Reject and clean the exact configuration without parameter/point/frame rescue;
do not infer a physical lower bound or quietly fit a head from these cameras.
Shared software controls do not replace medical or user-visual acceptance.

# 0307:admit a distinct observation mechanism,not a recurrent checkpoint rescue

0308follow-up:single actual-video trial failed at positive edge-scale camera
initialization before full BA/head/medical scoring. Runtime/checkpoint retired
under cleanup0308. Software admission is historical,not an accepted physical
tracker or camera. Actual0308peak memory UNVERIFIED because Windows venv parent
was monitored;generic descendant measurement/termination fixed without NNretry.

Noncausal TAPIR queries each frame globally before local temporal refinement;
it is not a reinstallation/threshold variant of rejected recurrent TAPNext++.
Publisher code/checkpoint grants,full weight/state identities,coordinate oracles
and bounded CPU smoke test pass. Keep one provisional runtime for an independently
registered real-video trial. No physical correspondence,head or medical acceptance
is inherited from software admission or model-family benchmark claims.

# 0310:require independent noisy physical camera evidence before another tracker

One unchanged procedural camera fit with deterministic sigma.5px/axis noise
passes conditional3px/matrix/depth checks yet has8.46%focal error and max300
nonconvergence. REJECT physical control;do not infer all real errors are caused
by the NN. No longer treat the exact-coordinate fixture as evidence of noisy
physical camera readiness. No production default/actual3px/2mmgate changed,
no current real-video rescue. See experiment0310for gauge/scoring caveats.
# 0311:do not infer optimizer fault from a weak-information physical fixture

Independent truth-linearization profile gives sigma(logf)=.0760183at sigma.5px
for0310geometry/folds. This is local/unbiased/Gaussian only. It changes the
priority from speculative solver replacement to genuinely additional information;
does not admit0310or excuse nonconvergence. No cached real-data retry/new model
installation is warranted merely by0310's8.46%error. Retain checked generic
read-only math;do not change actual camera/head/medical acceptance gates.

# 0315:strict software and domain-level calibration are different admissions

GeoCalib candidate is fully state-checked including persistent BNbuffers and
one bounded offline CPU forward. Do not use upstream flexible_load or replace
absent uncertainty with zero. Record continuous versus actual integer-pixel
crop/resize conventions. A software pass on an arbitrary procedural image has
no known physical focal target and grants no right to fit a patient head. Next
must test known-camera domain evidence,not reuse rejected0308camera outputs.

# 0316:do not turn a varying monocular focal prediction into a hard camera prior

Same1200pxcamera across generic head views yields2275/1213/1582pxpredictions;
all fail conditional native3pxray-error admission. Room also fails. Stop exact
candidate without selecting the near-correct side or changing renderer/seed/
focal/precision. This does not prove real photographic calibration impossible.
Retire exclusive source/weights/runtime and record the domain limitation before
a genuinely different information source. No actual-video/cached camera retry
is authorized merely by a software-pass or a plausible predicted number.
