# Experiment 0172: explicit scalp and gathered hair trial

Status: local geometry and five-view exact-camera replay
`TECHNICAL_CHECK_PASSED`; both visible hair candidates and default promotion
`REJECT`.

The five consented photos, experiment-0132 cameras and 34,753-vertex head
remain unchanged. Only local experimental hair geometry was appended to the
OBJ. Variant 1 duplicates a thin upper-scalp surface, adds 318 fine guide
strands flowing rearward and the previously measured bun ellipsoid. Variant 2
raises the frontal/right crown and hairline, replaces exposed strands with a
tapering six-section gathered volume, and keeps the bun ellipsoid. Its cap has
461 vertices/844 faces; the appended hair has 2,604 faces. Both private OBJs,
reports, `.blend` files and five-view clay/photo renders are ignored locally.

The original source head coordinates and camera matrices were locked. The
Blender projection replay is below 0.0001 px p95 in all views for both
variants. This is a rendering correctness check, not camera acceptance.

Five-view visual inspection rejects variant 1: the cap reads as a helmet,
the exposed strands as a broom, and the bun as a separate ball. Variant 2
removes the broom but produces a hard polygonal hairline, a raised cap far
above the photographed left crown, and a visible cylindrical bun connector
on the right side. Both fail the required continuous swept hairstyle and
remain obviously generic in front and obliques. The bare face, incomplete
eyes and neck cut were not changed or solved. Neither variant is a subject
likeness improvement despite reaching some photographed hair pixels.

Stop hand-authoring scalar scalp offsets, cap thresholds and tube/ellipsoid
connectors as a route to an accepted head. The hairline and gathered flow
need photo-constrained correspondence and a coherent surface representation;
mask overlap or this same five-photo visual fit alone cannot prove a true
3D hair shape. Camera acceptance and whole-head visual quality remain
`UNVERIFIED`. No photos or derived biometric data were committed or uploaded.
