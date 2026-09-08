# Experiment 0026: same-depth ray camera initialization

Status: camera `REJECT`; visual quality not accepted.

The local locked DA3-BASE runner now exposes `--ray-pose`, default false. This
selects the official model's alternative ray-based camera path using the same
reviewed checkpoint, source revision, CPU precision, seed, photos and resize.
No other model or checkpoint fallback was used. Actual inference took 18.154 s.
The five depth arrays are **exactly equal** to the previous prediction arrays;
the maximum depth difference is zero. Thus this is a camera initialization
experiment, not a changed learned depth result.

Private prediction: `da3-ray-v1/`, SHA-256
`cbb048c38efedcb30e3b33c1e3f02ed49e84467b8e2c9e77432c6a6f3d26f993`.
The consent-validating camera audit was parameterized to reuse the exact frozen
observations and held-out tracks, without fitting. Results in original pixels:

| Unrefined diagnostic | Previous p95 | Ray path p95 |
| --- | ---: | ---: |
| 18 manual third-view predictions | 48.5257 | 32.4658 |
| 33 held-track third-view predictions | 47.8225 | 25.7596 |
| 12 front-depth projections | 43.8307 | 22.9409 |

These lower errors do not pass the 3 px threshold or outperform the separately
optimized previous bundle result (~7.5485 px). They are not physical scan truth.
The shared gate passes matrices, conventions, finite values, rigid rotations,
focal plausibility/consistency and both cheirality checks, but rejects projection
p95 26.7100 px. Its mixed source/target population differs from the table above.

Experimental fusion uses the existing free-space/bilinear settings and original
image-space masks. Initial ray-fused-v1 bounds were contaminated by raster-edge
depth samples; this artifact is retained but not used as a comparator. For v2,
bounds instead transport the previous retained vertices' pixel/depth coordinates
through the new cameras. An exact depth-equality check protects that operation.
Camera-derived bounds and auto-fit display framing change; orbit previews must
not be presented as fixed-framing quantitative likeness comparisons.

Ray-fused-v2 extraction: 88,637 vertices / 172,400 triangles. No camera or depth
optimization, texture, hole filling, or anatomical template fitting was added.
50 existing tests pass, and both actual inference and the frozen real-data gate
ran successfully. The model remains local-only and the final head goal unmet.

The seven ray-fused-orbit-v2 views were inspected. Forehead and facial seams,
ear holes and cut neck/back surfaces remain obvious. The largest displayed
component contains 83,866 vertices / 164,342 triangles. It is still rejected as
a usable head; lower initialization errors are not a verified likeness gain.
Next use depth consistency explicitly during bounded camera refinement, rather
than assuming a better initializer alone will yield a satisfactory surface.
