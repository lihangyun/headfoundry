# Experiment 0024: retain free-space evidence

Status: `REJECT` as a usable head; anatomical improvement remains `UNVERIFIED`.

Experiment 0023 discarded every observation outside a symmetric narrow band.
That omits rays' foreground empty-space evidence. A separate `free_space=True`
mode now retains positive projective distances, clipped at +1, while still
discarding samples farther than the truncation distance behind depth hits.
The old default is retained for reproducibility, not declared adequate.

This is a fusion-support experiment, not camera correction. Cameras, depth,
masks, 96-cubed grid, bounds, equal weights and 0.025 band remain unchanged.
The general volumetric integration context is described by the
[Open3D documentation](https://www.open3d.org/docs/latest/python_api/open3d.pipelines.integration.TSDFVolume.html).
No Open3D package or implementation was installed/copied.

Run the private consent-validating driver with `--free-space --output
fused-surface-v2`. Output is local and ignored. The original prediction hash
remains `c32e7210c83135437b6e5e0fae7f71d5b623557447233259d36eeeb6aee76152`.

Full extraction: 91,387 vertices / 178,250 triangles. Orbit largest component:
86,581 vertices / 170,332 triangles. Boundary edges: 4,162, versus 9,343 in v1;
both have zero edges incident to more than two triangles. Reduced counts do
not establish anatomical accuracy, watertightness, or lack of intersections.

Known grid nodes increase from 154,505 to 320,639; multi-view supported nodes
increase from 48,766 to 165,384. These counts now include foreground empty space
and are not counts of reliable reconstructed surface or independent validation.

49 tests pass, including positive saturated foreground evidence, exclusion of
hidden space behind hits, and exact reproduction of the old narrow-band mode.
Other plane/sphere extraction checks remain passing.

All seven `fused-orbit-v2/orbit.png` views were inspected. Large facial seams,
missing/stepped regions and noisy ear/hair surfaces persist. The result remains
unusable as the requested head despite reduced boundary counts. Both orbit
versions auto-fit display bounds; these are not fixed-scale accuracy comparisons.
No likeness improvement is claimed and no baseline is replaced.

Next investigate image-space depth sampling/support discontinuities and
cross-view depth disagreement separately. The fixed camera failures still
prevent a reliable independent reconstruction claim.
