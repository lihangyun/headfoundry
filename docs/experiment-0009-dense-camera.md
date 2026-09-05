# Experiment 0009: held-out dense camera diagnostic

Status: REJECT. This is a camera-initialization experiment, not an accepted
head model or a comparison against KeenTools or MV-HRN.

The local detector's 468 frontal/intermediate-view correspondences constrain
alternating camera poses and a nuisance face surface. Intrinsics remain fixed
at an assumed 1800 px focal length with principal point (627, 627); frontal
pose and the frontal-derived prior remain fixed. Initial intermediate yaw is
-30/+30 degrees, independent of the previously fitted sparse cameras.
Boundary vertices are protected. Surface regularization remains 30.
Twelve iterations are fixed in advance; held-out observations never enter
surface fitting, pose fitting, stopping, or candidate selection.

Every thirteenth landmark is held out in each intermediate view, offset by six
indices in the second view. Boundary exclusions leave 60 validation points.
Frontal observations cannot be validation because they generated the prior.
The observations remain correlated detector estimates, not independent scans.
Full profiles are not silently treated as reliable detector ground truth.

Local subject-001 result, stored privately in dense-camera-v2:

- Training reprojection p95: 3.683767 px.
- Held-out reprojection p95: 10.437478 px (required <=3 px).
- Decision: REJECT; no camera acceptance or side-profile improvement claim.

The split and landmark population differ from experiment 0006, so their error
numbers are not a controlled before/after improvement comparison. Geometry
is optimized only as a diagnostic nuisance variable; this is not formal head
or texture implementation. Next gate remains reliable camera consistency and
independently checked correspondences before full-head reconstruction.

The deterministic test corrupts only held-out coordinates and verifies that
the fitted cameras and surface stay unchanged, while validation error rises.
Caller masks are preserved. The complete suite passed 32 tests.
