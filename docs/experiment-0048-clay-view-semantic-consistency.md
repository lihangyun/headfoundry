# Experiment 0048: same-template cross-view landmark consistency

Status: anatomical detector mapping remains `UNVERIFIED`; a single frontal
clay detection is not accepted as fixed anatomical truth. No mesh, camera or
baseline changes. This isolates correspondence behavior from subject geometry.

The pinned local detector was run on actual 600px smooth renders of the exact
same source head in the original front/left30/right30 cameras. No photo upload,
generated image, training, new asset or lighting change. The existing private
runner now accepts a view/output argument while preserving its original defaults
and consent, model and mesh hash checks. Each view returns one detected face.

Exact continuous ray lifting returns 464 / 453 / 448 valid surface hits. The
right30 coarse raster-buffer probe had 447; continuous ray and pixel-center
counts are different and neither is silently substituted for the other.

For each semantic ID, lift its own-view detector pixel onto the shared unchanged
mesh. If these are reliable fixed anatomical correspondences, common visible
surface points should approximately agree in 3D. Actual pair distances in
template units (not meters):

| ID | Front-left | Front-right | Left-right |
| --- | ---: | ---: | ---: |
| 168, bridge | 0.0593 | 0.0532 | 0.0226 |
| 6, bridge | 0.0770 | 0.0600 | 0.0419 |
| 196 | 0.0425 | 0.1399 | 0.1385 |
| 399 | 0.1378 | 0.0323 | 0.1272 |
| 4, nose tip region | 0.0342 | 0.0238 | 0.0481 |
| 13, central lip | 0.0049 | 0.0179 | 0.0207 |
| 17, lower lip | 0.0052 | 0.0174 | 0.0187 |

All listed points intersect a surface in all three views. This alone does not
make every surface hit semantically valid: view occlusion can put a hidden
landmark prediction onto a different visible surface. In particular the large
opposite-view distances of 196/399 cannot be assumed to describe mesh defects.
Even the central bridge points drift while the actual head shape is unchanged.
The observed correspondence drift is comparable to or larger than the 0.03-unit
maximum geometry displacement in recent fits. It is therefore a material
confound, not negligible numerical rounding.

Inspected the three native clay overlays: green shows each view's detector,
red the frontal lifted point projected into that view. Differences are visible
around bridge/nose. These images are not real-subject likeness evidence. The
experiment does not fully separate synthetic-domain detector bias, occlusion
and ambiguous anatomy, nor establish a calibrated camera.

Private `clay-landmark-left30-v1`, `clay-landmark-right30-v1` retain native
renders/detections; `clay-view-consistency-v1` retains masks, triangle IDs,
3D points, original pixels, report hashes and inspected overlay. Runner:
`audit_clay_view_consistency.py`. Existing front probe remains unchanged.

Next use explicit surface/anatomical anchor review and common-visibility checks
before permitting central geometry changes. Do not average arbitrary rays from
occluded landmarks or deform the head to fit inconsistent synthetic semantics.
Anatomical eye completion and eventual texture/identity validation remain
unfinished. No public solver changed; 65 tests still pass.
