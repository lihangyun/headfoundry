# Experiment 0049: explicit generic eye helper geometry

Status: asset preparation `TECHNICAL_CHECK_PASSED`; subject-specific eyes and
visual likeness `UNVERIFIED`. No default/baseline promotion. This experiment
adds eye component geometry only, without changing the source head, cameras,
lighting or correspondence mappings.

## Why this change

Recent experiments found rays entering empty orbital regions and returning
internal surfaces. The current clay head also visibly lacks eyeballs. Before
treating detector points as reliable anatomy, make that missing component
explicit. The already pinned CC0 graphical base asset contains `helper-l-eye`
and `helper-r-eye`; no application code, new weights, paid asset or external
service is needed. These are generic helper surfaces, not a reconstruction of
the photographed person's eyeballs, gaze, iris or cornea.

Both helpers contain 72 vertices and 140 triangles. Each has zero boundary and
zero nonmanifold edges. They are transformed with the same rigid coordinate
conversion/centering as the original template, without fitting to the photos.
The local combined experiment preserves every source head vertex exactly and
appends the two components. It does not fill or alter the intentionally open
neck. Interpenetration/contact correctness with subject-specific eyelids is
not established by the helpers' individual topology checks.

Actual five-view rendering finds 412 / 277 / 52 / 299 / 53 visible helper pixels
at 400px width in front/left30/left90/right30/right90. Inspected the identical-
shading before/after sheet: the eye openings now contain curved eye surfaces
instead of the previous interior geometry. The head remains generic and the
eyes have no iris detail. This is component completeness, not likeness or
KeenTools-level quality evidence.

## Reusable entry point

`tools/prepare_makehuman_head.py` now offers explicit `--include-eye-helpers`.
Default behavior still extracts body only. The flag includes only the two
named eye groups, never hair, lashes, joint markers or other helpers. Missing
required groups fail closed. Existing asset/license digest checks remain in
force, and the report explicitly records the option and generic-eye limitation.

Actual locked-asset invocation with the option exports 4603 vertices / 9146
triangles before later neck clipping. Unit coverage verifies default exclusion,
explicit inclusion, unrelated-helper exclusion and missing-eye failure. All
66 tests pass. The non-default option is not an accepted production path.

Private outputs: `makehuman-head-eyes-v1` contains the unfitted template export;
`subject-001/eye-helper-v1` contains the actual combined experimental mesh,
five-view comparison and geometry/visibility report. Private runner
`inspect_eye_helpers.py` verifies all pinned asset/license hashes and photo
consent. No photos or identifiable derived head are committed.

Next distinguish eyelid surface and eyeball surface when lifting anatomical
points. Adding an eyeball must not simply relabel eyeball hits as eyelid
correspondences. Keep mesh-component identity explicit before further fitting;
central nose correspondence uncertainty remains unresolved. Camera, identity,
texture and completed-product gates remain unmet.
