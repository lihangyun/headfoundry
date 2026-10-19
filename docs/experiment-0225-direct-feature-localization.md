# Experiment0225: frozen direct-feature model versus development sentinels

Date:2026-10-19. Pre-registered before target inference. Status:`REJECT`.

0224's independently detected/matched observations connect52 frames and one
mapping recovers1639 points at focal1083.257882px; training p95=2.618121px.
Freeze this whole model and its intrinsics. Test whether direct descriptor
associations to its existing3D points can localize the two already inspected
development sentinel frames. No LK, new triangulation,3D edits, intrinsic
refinement, source scan or other subject.

Preselect source612 for nearby624 and source0 for the later frontal1040, not
pose residuals or a best-of-reference search. These choices use already seen
view content; this is a development check, not fresh held-out validation.
Reload saved XFeat descriptors by exact feature index and independently verify
their pixel centers against every corresponding COLMAP image observation.
Extract held4096 features and filter using the original conservative ROI,
R-B>12, largest4-connected component and8 erode iterations with3x3 kernel.
Apply the same pinned LighterGlue configuration. Associate matches only to
already triangulated source features; disclose untriangulated matches separately.

All such point-ID matches enter the unchanged0222 pose/validation split and
gates: even IDs estimate fixed-K pose, odd IDs evaluate without residual
filtering; >=30 per split, >=30 pose inliers, >=50px validation span each axis,
proper rotation, positive entire-cloud depth and validation p95<=3px both frames.
No learned confidence or mask/reference change after results. One run,60s.
Hash frozen model files before/after and preserve actual overlays/arrays.

Even a pass cannot establish independent anatomy, source-scan millimeter error,
complete editable head, case002 generalization or visual likeness acceptance.

## One implementation repair before pose scores

The first run stops at its duplicate3D-ID guard before any pose fit or scored
report. COLMAP source images contain aliased observations: frame0 has233
observations/222 unique IDs, frame612 has183/180. Multiple2D feature entries can
refer to one triangulated point, so counting matched entries as independent
pose/validation support is unsafe. The initial producer, controls, failure and
target mask remain intact.

Before replay, define a residual-independent identity guard: for every3D ID
appearing more than once among matches, remove **all** its rows. Never choose a
copy by confidence, residual, closeness or pose. Count only remaining unique
identities at the unchanged gates. Save raw match indices, original triangulated
IDs and retained rows for audit. Replay the deterministic unchanged extraction
and matching once in a separate directory because the original interrupted run
did not export its in-memory matches. No pose score existed to optimize against.
No further rescue/tolerance/reference or matcher sweep is permitted.

## Read-only error decomposition after failed localization

The repaired replay still rejects:624 validation p95=7.829553px,1040 only20 pose
inliers. Before blaming shape, apply0222's unchanged even/odd essential-matrix
diagnostic to these saved descriptor matches and their **exact source feature
indices**, not reprojected3D positions. Do not remove odd-ID residuals or change
matching. One read-only audit; no new localization/camera/geometry solve.
If this pixel-only screen fails, a uniquely geometric causal explanation is not
supported. If it passes while frozen3D localization fails,3D/camera observability
is a plausible next hypothesis, still not proven by epipolar consistency alone.

## Observed results and stop

The repaired single replay preserves original model hashes. Exact source feature
index/pixel-center identity passes for both references. Independently recomputing
the foreground rule reproduces **52/52 original masks exactly**, with no mask
change inferred from target errors.

| Target | Raw matches | Triangulated matches | Alias rows removed | Unique pose / validation | Pose inliers | Validation p95 |
| --- | --- | --- | --- | --- | --- | --- |
|624|205|119|2|66 /51|38|7.829553px: REJECT|
|1040|143|75|4|40 /31|20|not scored: insufficient pose inliers|

624 passes proper rotation, entire-cloud positive depth and224x218.86px
validation spread, but fails the unchanged3px p95 gate.1040 stops at the
unchanged30-inlier gate. No odd-ID validation points are residual-filtered.
The actual two-photo point/residual overlays were inspected. This is not a
new white head, recognizable-identity gain or accepted camera pipeline.

Exact-index pixel-only essential fitting also rejects: untouched odd-ID line
p95=6.857389px at624 and3.764593px at1040. A camera/3D-only causal diagnosis is
therefore unsupported. These cohorts differ from0222, so9.66->7.83px is **not**
a controlled improvement percentage and cannot be marketed as one.

Stop this configuration and do not vary reference frames, confidence, focal or
mask thresholds. Before another reconstruction solve, measure the actual pixel
localization accuracy of the existing correspondences under known transformations
of these images. Such a diagnostic has exact2D truth without relying on cameras,
scan alignment or a learned geometry prior. Any subsequent subpixel observation
method must first pass that independent measurement screen; do not repair a head
to absorb unresolved pixel/camera/nonrigid errors. Case002 stays out of tuning.

Verification: all153 public tests pass in4.348s. New coverage includes true
chronological pair ordering, disconnected graphs, the unchanged foreground rule
and removal of every repeated identity copy. Full tests and exact binary/NPZ
replay are technical evidence only, not visual/physical acceptance.
