# ADR 0001: quality-first clean-room reconstruction

Status: accepted for implementation; final product quality remains `UNVERIFIED`.

## 2026-09-04 implementation amendment

All reconstruction runs must start from a versioned manifest that binds each file to SHA-256 and records provenance, allowed purpose, retention/deletion policy, and biometric consent. The VGGT adapter is restricted to the exact `facebook/VGGT-1B-Commercial` identity and its gated `vggt-aup-license`; neither missing records nor unavailable weights may trigger a fallback.

Status meanings are fixed: `TECHNICAL_CHECK_PASSED` is a bounded non-visual engineering check; `UNVERIFIED` means evidence has not been collected; `REJECT` means a required gate failed or is missing; `PARTIAL_SUCCESS` means numeric gates pass without complete licensed visual evidence; `ACCEPT` requires all protected gates plus licensed benchmark, held-out visual review, and complete reconstruction evidence.

## Decision

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

Development tests run on the local RTX 3070 8 GB. Production-quality learned initialization is isolated to a GPU worker sized after profiling; the current expectation is 24 GB or more for comfortable multi-view work, but this is a planning estimate, not a confirmed requirement. Optimization and export remain reproducible jobs with immutable input manifests.
