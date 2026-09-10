# Experiment 0054: smooth local lip modes and bilateral tradeoff

Status: unconstrained candidate `REJECT` for left-view regression; constrained
candidate `UNVERIFIED` and effectively unchanged. No promotion.

Primary variable: replace vertexwise displacements with six compact polynomial
shape modes on the original neck-cut source. Mode centers are x +/-0.12 and
y 0.36/0.52/0.68, radii 0.4/0.22 template units. Cubic compact support and a
front-surface depth taper restrict influence; protected profile-support rows
remain fixed. Each mode displaces along the original frontal rays. Cameras,
targets and protected outside-profile regions remain unchanged. These manually
specified modes are not an anatomical or learned lip prior.

The robust six-parameter fit reduces right local MAE 9.4491 to 7.3693px, but
left increases 4.3040 to 5.0644px. Maximum movement is 0.03827 units, with one
coefficient at its 0.04 bound. Final mesh has zero reversed triangle normals,
minimum area ratio 0.81892, zero outside-profile shift and frontal reprojection
difference at most 3.41e-13px. The five-view actual clay render was inspected;
the mesh remains generic and the bilateral regression prevents adoption.

A second control explicitly constrains every left fitting sample's absolute
error not to increase (numerical tolerance 1e-6px) while optimizing right error
and coefficient regularization. The first unscaled SLSQP solve failed and was
not accepted. Normalized coefficients and residuals converge successfully.
This does not change the geometric bounds or hide a failed optimizer result.

The constrained result moves at most 5.12e-8 template units: left MAE 4.3040244,
right 9.4490858, compared with source 4.3040238 / 9.4490865. Maximum left increase
is 1.000015e-6px (floating-point agreement with the declared tolerance). It is
effectively the original model, not a successful improvement. No need to render
this negligible change as if it were a new visible result.

This establishes a limit of these six modes under the current cameras and
constraints, NOT mathematical impossibility of better reconstruction. There
are uncertainties in camera calibration, prior shape and approximate contour
observations. Do not remove the left-view guard or repeatedly enlarge these
same local modes merely to lower the right fitting error.

Private `smooth-lip-v1` retains the actual unconstrained candidate, fit report,
five-view render and final surface audit; `smooth-lip-constrained-v1` retains
the effectively unchanged constrained candidate and report. Runner
`fit_smooth_lip.py` verifies source consent/digest. Existing private renderer now
accepts a candidate directory while retaining its original default. Identifiable
artifacts remain local and outside Git. No public solver changed; 69 tests pass.

Next investigate a anatomically structured shape basis compatible with the
existing licensed template, verifying any additional asset rights before use,
instead of further ad hoc lip modes. This may require distinguishing what is
observable in the five photos from prior anatomy. No paid or noncommercial
fallback is authorized. Camera, identity, texture and product gates remain unmet.
