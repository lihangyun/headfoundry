# Experiment 0025: sampling versus cross-view disagreement

Status: `REJECT` as a usable head. Sampling alone does not solve visible seams.

The new optional `bilinear=True` samples four masked neighboring depth pixels;
all four must be supported. The original nearest mode remains the default for
reproduction. No smoothing, camera, voxel bounds, depth values, truncation,
free-space policy or texture changes were made. Boundary support consequently
shrinks slightly; this is part of the conservative interpolation policy.

Private driver: `build_fused_surface.py --free-space --bilinear --output
fused-surface-v3`, inside ignored subject-001. `compare_sampling.py` renders v2
and v3 with exactly the v2 display center/radius, identical cameras and lighting,
at orbit angles 0 and +60. `sampling-comparison-v1/comparison.png` has v2 above
v3. The two rows were visually inspected: fine noise changes slightly, but the
large forehead, eye and mouth discontinuities remain. No likeness gain claimed.

The v3 largest component has 84,761 vertices, 166,908 triangles and 3,952 boundary
edges (v2: 86,581 / 170,332 / 4,162). Neither mesh has edges incident to more than
two triangles; neither is an accepted anatomical mesh or watertight head.

An additional unchanged-input diagnostic, `audit_depth_conflict.py`, projects
source component vertices into the other masked depth maps with bilinear
sampling. A target depth farther than the projected source point by 0.025 means
the source surface contradicts the target's predicted foreground free space.
Negative differences are recorded separately: they can be ordinary occlusion
and must not be treated as equivalent errors. Examples among supported samples:

- front to left30: 38.33% foreground conflicts, 6,115 samples;
- front to right90: 42.90%, 4,345 samples;
- right30 to right90: 49.23%, 5,763 samples.

These are camera/depth consistency statistics at arbitrary scale, not physical
ground truth, calibrated likelihoods, or proof that either view is correct.
Masks are approximate; no causal attribution to camera versus depth is proven.

The pinned official DA3 source was checked: OutputProcessor only extracts the
depth/cameras in this path; API `_align_to_input_extrinsics_intrinsics` returns
unchanged when no input extrinsics are supplied. Metric alignment is a separate
nested branch, not a missing required step for this DA3-BASE invocation. This
check finds no omitted scale conversion; it does not prove the entire adapter
or model is error-free. No upstream implementation was modified or copied.

50 tests pass, including exact interpolation of affine depth and conservative
masked-border handling. Next prioritize camera/depth joint consistency rather
than further cosmetic sampler adjustments. Experimental geometry authorization
and all final quality gates remain unchanged.
