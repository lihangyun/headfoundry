# Experiment 0092: surface-supported mesh sections

Status: `TECHNICAL_CHECK_PASSED` for section construction only; lip-rim anatomy
and reconstruction remain `UNVERIFIED`.

Implement `headfoundry.mesh_section.section_segments` to return plane/triangle
intersections with triangle IDs and endpoint barycentric weights. These retain
the relationship to the actual deformable mesh needed for curve constraints.
The function does not infer an anatomical rim or connect unrelated segments.

Reject coplanar faces explicitly because their intersection is not a unique
segment. Omit point-only tangencies and support empty intersections. On-plane
edges retain both triangle supports when shared; downstream curve construction
must account for duplicates. Validate finite vertices/plane and integer indices.

Replace the private one-off lip section calculation with this function. On the
hash-pinned real head it reproduces all 61 selected segment IDs and endpoints
within 1e-12 template units, adding endpoint support weights. No model changes.
Private `lip-section-v2` retains the resulting supported section and diagram.

Tests cover an ordinary crossing, support reconstruction after translation,
shared crossing endpoint, edge-on-plane, tangency, empty section and invalid
input/coplanarity. Full suite: 80 tests pass. This is a geometry operation test,
not visual likeness evidence. Next trace and review upper/lower rim curves
across multiple sections before applying a contact constraint.
