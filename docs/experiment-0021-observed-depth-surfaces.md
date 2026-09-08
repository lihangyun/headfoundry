# Experiment 0021: observed depth surfaces

Status: `UNVERIFIED` geometry; existing camera gate remains `REJECT`.

The user authorized experimental geometry before camera acceptance on 2026-09-08.
This experiment exposes DA3-BASE depth as actual triangles without another
camera optimization, smoothing, learned fallback, texture or hidden fusion.

Local source: subject-001/da3-base-v1/predictions.npz, SHA-256
`c32e7210c83135437b6e5e0fae7f71d5b623557447233259d36eeeb6aee76152`.
Input rights are checked again before processing. Consent remains local only.
Private script: `assets/private/subject-001/build_observed_surfaces.py`.
Private output: `assets/private/subject-001/observed-surfaces-v1/`.

Method: existing OpenCV unprojection, grid stride 3, approximate manually
specified image-space head polygons, maximum world edge length 0.025 (arbitrary
DA3 units, not metres). Triangles crossing excluded vertices or depth jumps are
removed, along with degenerate triangles. No unseen surface is filled.

| View | Vertices | Triangles |
| --- | ---: | ---: |
| front | 7547 | 14352 |
| left30 | 7362 | 13979 |
| left90 | 8336 | 15837 |
| right30 | 7564 | 14492 |
| right90 | 8960 | 17327 |

The five OBJ files are separate open surfaces, **not a fused or complete head**.
The original-photo/clay comparison uses each source camera without texture.
Same-view agreement is largely built into unprojection and is not independent
shape evidence. The approximate ROI is not a measured silhouette.

Visual inspection: facial features are visible, but banding, holes, cropped
contours and incomplete skull/neck remain conspicuous. No improvement over
MV-HRN or parity with KeenTools is established. No comparative competitor
outputs were accessed. A rotatable integrated experimental head is still pending.

Verification: 44 unit tests pass, including mesh index compaction, exclusion of
masked vertices, rejection of excessive edge lengths and invalid thresholds.
These are technical checks only. Next: inspect these surfaces in a shared
rotatable frame and test cross-view alignment before choosing a fusion method.
