# Experiment 0023: narrow-band projective fusion

Status: `REJECT` as an improved head candidate. Final quality remains unverified.

The new NumPy fusion implementation averages signed projective depth distances
within a symmetric narrow band. Marching tetrahedra extracts the zero level set
only from cells whose eight corners are observed. Shared edge vertices prevent
tetrahedron cracks; triangle normals point toward positive distance. Unknown
space is not closed or filled. No model, camera, texture or retained input depth
was changed. This tests fusion, not corrected camera accuracy.

Private reproducible driver: `assets/private/subject-001/build_fused_surface.py`.
It rechecks local input consent and the pinned DA3 prediction SHA-256. Masks are
rasterized from experiment 0022's retained component triangles, not new semantic
ground truth. Grid: 96 cubed; band: 0.025 arbitrary DA3 units; equal view weights;
nearest-pixel depth samples. 154,505 grid nodes have observations, but only
48,766 have multiple-view observations. Changing support sets can introduce
discontinuities; this is not a complete calibrated TSDF reconstruction system.

Outputs are ignored local files under `fused-surface-v1/` and `fused-orbit-v1/`.
Full extraction: 135,016 vertices / 261,119 triangles. Largest component used for
the orbit: 129,190 vertices / 252,027 triangles. This component has 9,343 boundary
edges and zero edges with more than two incident triangles. It is not watertight;
that edge count does not exclude self-intersections or prove anatomical validity.

Seven clay orbit views were inspected. Prominent cracks, jagged/noisy surfaces,
and unreliable nose/lip detail remain. It cannot replace the previous experiment
or establish side-profile improvement. Display bounds are independently fitted,
so the orbit is not a fixed-framing quantitative baseline comparison.

The orbit report's old phrase "NOT fusion" describes the renderer's operation,
not the upstream mesh generation. The input here **was** fused. Future renderer
reports use source-neutral wording to avoid this ambiguity.

48 tests pass. New checks cover a known plane seen by two translated cameras,
positive-distance orientation, no surface in unknown space, invalid bounds,
and a closed synthetic sphere with exactly two triangles per mesh edge. These
checks establish bounded extraction behavior, not real-subject quality.

Next: resolve contradictory depth support/visibility before further fusion;
do not hide it with indiscriminate smoothing or texture.
