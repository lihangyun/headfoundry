# Experiment0233: pixel refinement on known nonplanar image motion

Date:2026-10-19. Pre-registered before endpoint measurements. Status:`REJECT`.

0231's nonplanar context fits the exact3D and most real contextual observations,
but untouched real raw endpoints still fail. Test one **image observation**
mechanism, not a new camera/shape solver: independently-contextualized epipolar
prealignment followed by unconstrained local pixel residuals.

Fit F only to contextual pairs using the exact0231 settings/gates. From its
inlier context, call uncalibrated stereo rectification. Disable that function's
additional algebraic outlier filter (threshold0) because context already passed
the3px geometric gate; do not add a matrix-scale-dependent second filter.
Combine transforms as H2^-1 H1 to map source coordinates to the target. This is
an appearance prewarp derived from general two-view geometry, **not** a planar-
face assertion or a recovered3D camera. Keep the original source image grid,
rectify only the target, and reuse unchanged21px/pyramid3/30-iteration seeded LK.
The source-grid cycle error remains in native pixels (<=0.75); patch MAE<=15.
Map the freely corrected endpoints back to original target pixels. Do not
replace them with either a homography projection or an epipolar-line projection.
A deliberately inconsistent-context unit test must prove they can depart from
the fitted F when the image evidence requires it.

Use exactly0232's five non-frontal views versus front. Geometry/visible material
points/cameras are frozen. Preselect common-visible points in0230's same fixed
box in both views, then require opaque alpha eroded11px in both images so the
21px patch has known foreground support. Report all exclusions before scoring.
This is an interior, mutually visible capability test; not occlusion robustness
or a raw learned-match test. Split immutable sample IDs: mod3==0 context, others
measurement. Context and measurement are never mixed.

Blender/projector coordinates use pixel centers at0.5; convert both source and
target truth to OpenCV array coordinates by subtracting0.5. Define coarse
target endpoints as true projections plus fixed iid Gaussian noise sigma1.5px,
seed233 (the full6x5000x2 array is saved once). This is a simulated coarse
observation distribution, not a calibrated statistical model of real XFeat
errors. Exact target truth enters **only the evaluator**, never the refiner.

Compare unchanged direct seeded LK against the single nonplanar-prealigned
candidate on the identical measurement IDs. Each of five cases must retain
>=30 measurements and>=50% of the fixed population, with candidate endpoint
p95<=1px. Report raw-all, candidate-all-eligible and paired-cohort baseline/
candidate errors; no truth/residual filtering. Require opaque-interior counts
and exact original image/geometry hashes. One180s run; no texture, noise, warp,
context, LK, confidence or threshold sweep. Failure stops this configuration
before real localization; a pass permits only a separately registered real test.

All scans/images/outputs remain private/local, with no training/upload. This
does not establish unpatterned-skin, real camera, scan-error, full-head or visual
acceptance. Case002 and all originals/defaults remain protected.

## First result and read-only validity audit

The single run rejects all five cases: only19.10%-30.31% measurements survive,
with corrected p95=28.33-73.55px, worse than the3.58-3.75px simulated coarse
inputs. Direct seeded LK also drifts badly. Do not promote this candidate or
tune its parameters. Actual before/after patterned-source sheets were inspected.

Before blaming a unique cause, audit the saved data without changing an
algorithm or point population. On every predeclared interior measurement, compare
bilinearly sampled source grayscale against its exact target-material projection,
and against the same target pixel location (zero-motion control). Report color
differences and correlations. Compare retained estimated flow magnitudes to true
flow, and report how much of each source measurement's coarsest21x21/pyramid3
support (native radius84px) lies outside opaque foreground. This distinguishes
invalid surface texture/coordinate assumptions from coarse-support contamination.
One diagnostic only,30s; no pixel-origin, texture, window/pyramid or threshold
search and no rerun of the rejected configuration.

The saved audit finds true-material correlation0.944-0.982 and MAE0.89-1.51
gray, while zero-motion correlations are near zero. The dataset contains a
stable material signal. Only0.42%-0.58% source coarse supports are fully opaque;
their conservative non-interior contributes median99.90%-99.92% of Scharr
gradient energy. This exposes a tracking-versus-local-measurement support
mismatch, not an error to repair by altering head shape.0234 tests that semantic
split separately; original default tracking and every rejected result remain.
