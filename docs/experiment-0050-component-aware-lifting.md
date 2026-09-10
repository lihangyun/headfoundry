# Experiment 0050: component-aware surface lifting

Status: occlusion-preserving component filter `TECHNICAL_CHECK_PASSED`;
anatomical correspondence and subject reconstruction `UNVERIFIED`.
No deformation, camera change or baseline promotion.

Adding eye geometry must not turn eyeball intersections into alleged eyelid
observations. `lift_pixels` now accepts an optional boolean mask over allowed
triangles. It first computes the nearest hit over the complete mesh and only
then rejects disallowed components. It never removes an occluder to select an
allowed surface behind it. Rejections retain the existing -1/NaN contract;
callers can retain the unfiltered result to distinguish misses from wrong
components. Default behavior remains unchanged. Mask shape and boolean type
are validated rather than converting integer labels implicitly.

The synthetic test places a disallowed near triangle in front of an allowed
far triangle: the result is a rejection, not the far triangle. It also covers
allowed nearest hits, all-disallowed masks and malformed masks. All 67 tests
pass.

## Actual combined-head audit

The local audit uses the actual combined eye-helper mesh from 0049, verifying
its digest and exact body vertex/triangle prefix. Component identity follows
the two explicitly appended eye triangle blocks. It intentionally freezes the
original 468 detector pixels from the empty-socket frontal render, isolating
the surface/component change from a new detector run.

- 446 nearest hits are on the body.
- 7 nearest hits are on the left eye helper, 11 on the right.
- 4 remain true ray misses.
- All 18 eye hits are rejected for body-only observations, without looking
  through them to internal orbital surfaces.
- Retained body triangle IDs and barycentric weights are exactly unchanged.

All five previously audited problematic eye IDs (33,159,145,263,386) now hit
eye components and are explicitly rejected as body/eyelid observations. Eye
hit IDs are retained in the private report and raw intersections remain in
the NPZ. This validates the component distinction, not the accuracy of the
generic helper eyes or of all 446 remaining body hits. Body membership alone
does not establish anatomical feature identity.

Private `component-lift-v1` contains raw IDs/weights, component IDs, body-only
IDs/weights, face-component mapping and report. Runner
`audit_component_lifting.py` checks photo consent and source mesh consistency.
Combined mesh SHA256:
`9f12b5e87bf0c4b853f95f81c64442c30def2d5027749020c83daf8165f52d45`.
No identifiable artifacts are committed. No new visual likeness claim is made
because geometry/rendering are unchanged from 0049.

Next use anatomically supported eyelid boundary anchors rather than relabeling
rejected eyeball hits or filling them with hidden body intersections. Central
nose semantics and the camera/identity/texture/product gates remain unresolved.
