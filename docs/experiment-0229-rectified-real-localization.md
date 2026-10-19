# Experiment0229: independent-context measurements on real development sentinels

Date:2026-10-19. Pre-registered before real refinement. Status:`REJECT`.

0228 passes16/16 known2D transformations at the fixed1px precision and retention
gates. Freeze its context/rectification/LK implementation. Test those image
measurements on the **same** already inspected source612->624 and0->1040 pairs,
without a best-of-reference/matcher/intrinsic/geometry search. These are real
development diagnostics, not fresh independent test subjects.

Reuse0225's saved raw matches and exact feature indices/point-ID alias exclusions.
Context consists **only of source features with no triangulated3D ID**. Exclude
all triangulated source features, including aliases, from context fitting.
The unique triangulated matches are measurement points. Verify index/pixel and
3D ID joins explicitly; context and both pose/validation populations must be
disjoint. No new extraction/matching, weights, cameras, scan or3D optimization.

Apply0228's unchanged context homography and freely corrected image endpoints.
Eligible measurements are selected only by its original image/photometric/cycle
checks, before pose/geometry residuals. Keep original3D coordinates, intrinsic
matrix and point-ID parity split. Unchanged0222 gates still require>=30 even-ID
pose points,>=30 odd-ID validation points,>=30 pose inliers,>=50px validation
spread per axis, proper rotation, positive depth of the entire frozen cloud and
odd-ID validation p95<=3px in **both** frames. Never delete odd-ID residuals.

Also apply the unchanged point-disjoint essential-matrix diagnostic to these
exact source and corrected target pixels; report every retained odd ID. If
pixel rigidity passes but frozen3D localization fails, camera/3D consistency is
a distinct next hypothesis. If pixel rigidity/support fails, do not change3D
to compensate. Epipolar agreement alone is still not anatomical/camera truth.

Budget:one30s run. Preserve raw matches, context IDs, all corrected endpoints,
eligibility/warps, poses, residuals and actual photo overlays. Hash frozen model
files before/after. No context ratio, partition, reference, LK or focal sweep.
Any failure stops that configuration. No head/scan/likeness acceptance or model
training/upload; case002 and all original/default assets remain protected.

## Actual result and stop

Both pairs fail independent-context warp support before refining/scoring any
measurement or fitting a pose. Source612->624 has86 context pairs, of which41
(47.6744%) support the predeclared coarse model; source0->1040 has21/68
(30.8824%). Both are below the unchanged50% gate. Counts were independently
replayed from frozen arrays with identical seed/options for diagnosis only;
no rejected warp or point was promoted. Do not lower the first gate to47% or
change which points are context. Both retain0 camera measurements; the original
3D model/intrinsic/binary hashes remain unchanged. Actual photo sheets confirm
no accepted support markers, not a new reconstructed head.

This establishes that the synthetic planar-transform capability does not yet
transfer to these independently reserved context populations in real video.
It does not uniquely prove whether nonplanar motion, unreliable contextual
matches or other image/camera effects cause the failure. No new3D solve is
justified and no threshold/context/reference/warp-family rescue sweep follows.

Next use the authorized case001 skin STL as **diagnostic known3D geometry**,
with declared cameras and exact visible material-point projections, to separate
the motion-model capacity question from image-matching noise. This may include
source-only renders for review, but must not become the final reconstructed
head, model training or test-subject geometry fed into a video-only result.
Keep the video/scan target goal intact; case002 remains reserved.

Verification: all160 public tests pass in4.908s, including point-disjoint
context fitting and an image-residual test that corrects a deliberately biased
coarse warp. This proves the implemented behavior, not physical head accuracy.
