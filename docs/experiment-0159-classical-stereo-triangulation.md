# Experiment 0159: classical stereo triangulation and unused-profile check

Status: execution `TECHNICAL_CHECK_PASSED`; fused subject geometry `REJECT`.

The hypothesis from experiment 0158 was that disparities passing bidirectional
left/right matching could provide shared 3D face evidence under the unchanged
experiment-0132 cameras. The only experimental change is stereo validation and
triangulation; cameras, photographs and the current head stay fixed. The five
authorized photographs and all derived point clouds remain in ignored local
storage.

OpenCV's disparity-to-3D matrix was applied to each front/30-degree pair.
Rectified points were converted to the same world frame, required to have
positive depth in both source cameras, and sampled on a fixed 3-pixel grid.
Bidirectional 2-pixel disparity consistency retains 24.6%/25.4% of masked
front-face pixels. The two resulting clouds contain 2,908/3,368 samples;
their median nearest-neighbor separation is 0.215/0.178 model units. A
predeclared 0.03-unit cross-pair agreement threshold retains only 443 fused
points, below the 1,000-point technical support requirement.

Projection of that fused cloud into the unused left/right pure-profile photos
covers only 7/17 and 7/16 reviewed contour rows, respectively. The covered-row
absolute errors are 34.21 and 21.41 px. Private photo overlays confirm that
the cloud is patchy around the nose/eye and lacks the mouth/chin surface needed
for a recognizable side profile. These errors are a diagnostic of sparse cloud
support, **not** a mesh silhouette score; omitted rows are failures of coverage,
not zero-error observations.

The world-coordinate bounds overlap the current head scale, so a trivial unit
conversion does not explain the result. The two pair clouds may sample
different visible patches as well as contain correspondence/calibration error;
this test does not attribute the entire mismatch to one cause. The hypothesis
that this classical stereo configuration can drive a subject head is `REJECT`.
Do not fuse or fit the 443 points into the accepted geometry and do not infer
KeenTools-level quality from experiment 0158's central disparity medians.

Next gate: use the pure-profile photographs as direct subject-shape evidence,
with fixed cameras and explicit held rows, and seek a surface representation
that can improve both sides visibly. Any candidate still requires five-view
Blender overlays, protected eye/nose evidence and mesh-safety checks before
promotion.

Follow-up: [experiment 0160](experiment-0160-visible-profile-boundary.md)
measures the actual rendered boundary and finds that the existing brow-to-chin
profile samples already track the photo within about 4--5 px mean. The remaining
visible deficit is not resolved by refitting those same sparse outer rows.
