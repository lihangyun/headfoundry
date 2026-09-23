# Experiment 0176: direction-dependent hairline and exact cap clipping

Status: fixed-input screening, mesh generation and rendering
`TECHNICAL_CHECK_PASSED`; scalp-coverage direction `PARTIAL_SUCCESS`;
complete hair geometry, visual likeness and default promotion `REJECT`.

The unchanged experiment-0132 head/cameras and existing private hair masks
were used. The prior gathered-hair-v2 cap left photographed hair regions
uncovered by visible hair geometry: 4,005 pixels in front, 20,318 in left90
and 21,837 in right90 at 512 px, even before counting hair outside the mesh.
The head normals were checked on top/front/rear/side samples and point
outward; an inverted-offset explanation was rejected. Removing an extra
front-Z eligibility limit generated an identical candidate hash, ruling out
that cutoff as the cause.

A three-parameter boundary offset varying with horizontal and rear position
was selected on front, left30, left90 and right30 *head-surface projections*.
The selected offset is `0.5*abs(x) + 0.8*max(z,0)` model units. On that
fixed-surface classification screen, mean selected-view F1 is 0.881 and
right90 F1 is 0.858, versus 0.611 for the old right90 boundary. This is
not a hair-silhouette score: the screen ignores surface thickness, outer
shape, bun and occlusion changes. Right90 was excluded from boundary
selection, but the pre-existing head, cameras and hand-built bun had already
used all five photos. It is not an independent reconstruction holdout.

The corresponding actual 3D candidate v3 improved full hair-mask IoU over
v2 in every view: front 0.485→0.690, left30 0.342→0.561, left90
0.370→0.600, right30 0.418→0.613 and right90 0.422→0.614. Yet the
renders show a jagged triangular hairline. The old generator discarded every
triangle crossing the boundary. Candidate v5 clips those triangles at the
zero level and tapers the cap to the original scalp there; its face areas are
positive. The visible sawtooth disappears. V5 IoU is 0.678/0.587/0.609/
0.640/0.626 in front/left30/left90/right30/right90. The front IoU drop
against v3 reflects extra dark coverage; larger area is not automatically
better.

Five-view visual review still rejects v5. The cap is an unnaturally uniform
black dome; its frontal line is too strongly peaked, the side transition
around the ear is incomplete, and the swept connector and ellipsoidal bun
read as separate primitive forms. The geometry is overlapping parts, not a
watertight continuous scalp-to-bun mesh. A per-pixel mask metric cannot
establish realistic gathered flow or identity. All photos, masks, candidate
OBJs, colors and renders stay ignored locally and were not uploaded.

Next replace the hand-built tube/ellipsoid junction with one connected
surface whose tangents flow from rear scalp into the bun, and test both
profile silhouettes and enlarged natural-image appearance. Do not spend
another round merely tuning the scalar hairline threshold.
