# Experiment 0058: whole-head authored shape scope

Status: `TECHNICAL_CHECK_PASSED` for verified preparation; identity and shape
quality remain `UNVERIFIED`. No accepted model or camera change.

Four CC0 graphical targets from the already pinned MakeHuman base revision
are locked in `examples/makehuman-head-shape-lock.json`: diamond, oval,
rectangular and round. Explicit target headers and the pinned base license
cover these data assets. No upstream application implementation is imported.
The existing preparation command now accepts an explicit `--lock`; its mouth
volume default and hash/license/revision checks remain unchanged.

Prepare locally:

```text
python -m tools.prepare_makehuman_targets assets/private/makehuman-base-v1 assets/private/makehuman-head-shapes-v1 assets/private/makehuman-head-basis-v1 --lock examples/makehuman-head-shape-lock.json
```

The independent parser maps 19158 source vertices into the original 4459-vertex
head topology. Affected counts are respectively 525, 1885, 460 and 1786.
The private scope probe verifies the original oblique-jaw-v3 mesh hash and
matching faces, applies each target separately at 0.5 strength, then clips
the neck at y=1.2. Deforming before clipping avoids assigning arbitrary zero
displacements to newly created neck-intersection vertices. Cameras, lighting
and source shape are fixed. This is a scope sweep, not subject fitting.

| Target | Maximum displacement, template units | Minimum triangle area ratio |
| --- | ---: | ---: |
| Diamond | 0.084524 | 0.775044 |
| Oval | 0.064848 | 0.407285 |
| Rectangular | 0.073015 | 0.806258 |
| Round | 0.060252 | 0.407285 |

All variants have zero reversed triangle normals relative to the preclip
source; all clipped outputs have 4352 vertices and 8610 faces. This is not a
self-intersection or anatomical validity proof. Actual front and bilateral
clay renders were inspected. The controls visibly change cranial height,
face width and jaw shape, with little change to the nose/lip profile. They
expand whole-head coverage but cannot alone resolve the central facial
profile defects observed in earlier experiments.

Private `makehuman-head-basis-v1` retains the prepared NPZ, scope report,
runner and actual three-view comparison sheet. No identifiable output is
committed. A synthetic CLI check verifies explicit lock selection, source-ID
mapping, coordinate signs and tamper rejection. The next experiment should
fit broader face/jaw observations with bounded controls and inspect five
views, while retaining independent central-profile checks. Do not promote
a generic shape preset or claim subject likeness from this scope probe.
