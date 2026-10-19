# Experiment0230: rigid scan motion with exact visible material-point truth

Date:2026-10-19. Pre-registered before generation/measurement.
Upright diagnostic:`TECHNICAL_CHECK_PASSED`; tested planar precondition:`REJECT`.
Real camera/head acceptance remains `UNVERIFIED`.

0229's real contextual supports41/86 and21/68 fail. They do not distinguish
nonplanar motion capacity from unreliable image matches. Use the authorized
case001 skin STL as **diagnostic known geometry**, not as reconstructed output,
training data, final video-only geometry or test-case calibration.

Keep every original triangle/coordinate. Numerical conditioning is one recorded
isotropic similarity: center at the source bounding-box midpoint and divide by
half its largest extent; export its exact inverse and original-mm cameras.
Use declared720x1280 K with focal1083.257881738314 and center360/640, purely as
test-camera settings, not a claim about the real capture. Source axes were
initially assumed +Z front,-Y up; the visual-axis repair below establishes +Y up.
Place cameras at radius6 normalized units looking at the origin: front,
yaw-10,+10,-30,+30 and pitch+10 degrees. These are a fixed motion characterization,
not a parameter sweep used to select a passing reconstruction.

Sample5000 points area-uniformly across **all** source triangles, seed230, saving
triangle IDs and barycentrics. For each camera, use Blender BVH first hits and
0.01mm hit-position agreement to establish actual surface visibility, with
positive depth and image bounds. A two-layer occlusion self-check must pass.
Save every point/projection/visibility/gap, including occluded points. Do not
replace a hidden material point by a nearer surface. All vertices must remain
in front of all declared cameras. Independent Blender/OpenCV replay <=0.05px;
raw-mm versus normalized projection agreement <=1e-8px.

Compare front with each other camera on two predeclared populations: all shared
visible points (secondary) and shared points within fixed x[100,620),y[500,820)
in both images (primary, matching the old image-interior box). This synthetic
box is not an accepted anatomical scan region or real video alignment. Require
>=200 shared points and>=50px span per axis. Split immutable sample IDs by
parity: even fit context, all odd evaluate without residual deletion.

Fit the same global homography class/settings as0228 (MAGSAC3px/10000/0.999,
seed228), recording all context support even if below50%. Report context gate,
all odd reprojection p95 and fraction within3px. Also report analytic fundamental
geometry from declared cameras, and an eight-point F fit on even points, on all
odd points. F distances are not2D reprojection/camera acceptance. No source scan,
new head or real camera is optimized by this check.

Budget: one180s source-generation/render run and one30s analysis; source-only
clay views/true-point overlays must be inspected. Preserve failures; no new
camera distance, focal, ROI, sample or visibility-tolerance sweep. A successful
diagnostic is `TECHNICAL_CHECK_PASSED`, while product/camera/head acceptance is
still `UNVERIFIED`. Motion-class failure with perfect pairs can support a new
nonplanar observation hypothesis; success instead weakens that explanation for
the tested regime and redirects attention to image correspondence/noise.
Neither result uniquely diagnoses the actual real video.

No photos/meshes/outputs leave private local storage; no model training or paid
assets. Case002, bone scans, originals and production defaults stay protected.

## One visual-axis implementation repair

The first generated source-only sheet is upside down. Its OpenCV/Blender matrix
replays agree, but this does not validate anatomical up direction. Reject the
initial -Y-up assumption; the supplied case001 skin scan has +Y up. Preserve
that run's complete data, renders, results and exact producer source capsules.
Add an explicit test that a +Y source point projects above the frontal center.

Replay once into a separate upright directory with +Y-up and a consistently
signed pitch center. Reuse exactly the same5000 triangle IDs/barycentrics and
coordinates, K, radius6, yaw/pitch magnitudes, visibility tolerance, scopes and
all model-fit gates. Assert exact sample equality against the first archive.
This fixes a verified coordinate interpretation bug, not a geometry fit or a
search over cameras/ROIs to improve support. Do not draw a comparable-ROI or
physical-head conclusion from the original upside-down sheet.

## Read-only estimator-versus-capacity control

The upright run's fixed MAGSAC homographies fail the50% context gate on all five
motions, whereas declared-camera and fitted F geometries reproduce odd points
to numerical precision. Some RANSAC H extrapolation errors are extreme; do not
attribute their entire magnitude to an unavoidable minimum error of every H.

Before drawing the model-class conclusion, fit one non-robust all-even-point
homography (`cv2.findHomography(...,method=0)`) on each exact saved scope/pair.
All inputs are known correct, so this removes outlier-subset selection as a
confound. Evaluate **all the same odd IDs**, report context fraction within3px
and held p95, and preserve the original robust reports. This is one unavailable-
truth capacity control, not a replacement real matcher, threshold sweep or
promotion of a rejected warp. Budget30s; no focal, pose, ROI or point changes.

## Observed upright results

The original source file is unchanged. The repaired run reuses bit-identical
5000 sampled triangle IDs, barycentrics and conditioned positions. The first-hit
two-layer test passes. Raw-mm/normalized projection replay is below5.7e-13px;
independent Blender/OpenCV replay is below0.000112px across all views. Actual
upright source-only clay and true-point-versus-plane images were inspected.
These are supplied source meshes, not heads generated by HeadFoundry.

| Motion | Primary shared points | Robust H context support | All-point H odd p95 | F odd Sampson p95 |
| --- | --- | --- | --- | --- |
|yaw-10|1934|34.84%|15.030695px|0.00000414px|
|yaw+10|1948|35.26%|15.006003px|0.00000783px|
|yaw-30|1641|26.11%|43.599730px|0.00000334px|
|yaw+30|1691|25.41%|42.708202px|0.00000355px|
|pitch+10|1643|35.21%|13.333107px|0.00000228px|

The fixed robust planar context precondition fails all five even with perfect
material correspondences. A single all-context least-squares control still has
13.33-43.60px odd projection p95; the larger robust-fit extrapolation errors are
not an irreducible lower bound for every homography. The secondary all-visible
scope also fails. Analytic declared-camera epipolar error is below3.6e-13px.
The table's H reprojection and F line/Sampson errors are different-dimensional
quantities; do not call their ratio a camera or head-quality improvement.

This is evidence against that global-plane precondition in the tested rigid,
nonplanar head-motion regime. It is **not** a unique diagnosis of0229's actual
video, and does not certify raw image correspondences. Stop the planar rescue
branch; separately check independent nonplanar context and image measurements
before another3D solve. All data and source-only renders remain private/local.

An audit of0216's old positive-Z preview explains the misleading -Y impression:
its recorded Blender camera has an approximately180-degree roll (world matrix
diag(-1,-1,1)).0217 explicitly unrolls that preview and uses the actual matrix.
The0230 up-axis repair therefore does not overturn0217's failed correspondence
and visibility checks or retroactively validate those cameras. +Y-up here is
verified for this case001 scan, not inferred universally for all input scans.
