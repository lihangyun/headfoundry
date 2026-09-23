# Experiment 0170: experimental neck extension and side-view review

Status: boundary extraction, mesh construction and exact-camera render
`TECHNICAL_CHECK_PASSED`; neck shape and default promotion `REJECT`.

The unchanged experiment-0132 diagnostic OBJ has one 184-edge open boundary,
all at world Y=1.2. An experimental extension joins that ring to three
successive downward, mildly tapered rings and ends at Y=1.85, adding 552
vertices and 1,104 triangles. The original 34,753 vertices and 69,320 faces,
unaccepted cameras and five local photographs remain unchanged. The last
ring is deliberately open; neither the original nor the candidate is claimed
watertight. Exact-camera Blender source-coordinate and projection replay
checks pass, with all five p95 errors below 0.0001 px.

Real five-view overlays show the expected partial gain: the old floating
horizontal neck cut is no longer immediately below the jaw. The simple
extension also produces a long straight tube, visibly overlays skin/garment
incorrectly at the front and both obliques, and ends on an arbitrary diagonal
relative to the actual shirt/shoulder boundary in the profiles. It does not
model sternocleidomastoid, trapezius or shoulder connection and does not
improve the unchanged facial identity. The candidate is therefore `REJECT`,
not a promoted complete head.

The existing local MV-HRN side comparisons were re-inspected as a qualitative
reference. They show a severely incomplete/open side surface, while the
current HeadFoundry experimental head has a continuous facial exterior and
a closer visible nose-to-chin outline in its own exact-camera overlays.
Their render styles, camera registration, topology and support differ, so
this is **not** a controlled MV-HRN benchmark or general performance ranking.
No KeenTools private output or service was accessed. The next discriminating
identity work should target interior eyes/nose/lips and jaw relief with
independent view protections; another uniform neck extrusion will not make
the person recognizable.

The candidate OBJ, local source photos, MV-HRN artifacts and all five
diagnostic renders remain ignored under `assets/private/subject-001`.
