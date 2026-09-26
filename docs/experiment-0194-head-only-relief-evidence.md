# Experiment 0194: local illumination test and visible head-only relief

Status: illumination execution, mesh guards and exact-camera neutral review
`TECHNICAL_CHECK_PASSED`; tested photometric lower-lip candidate `REJECT`;
physical shape, subject likeness and KeenTools parity `UNVERIFIED`.

Hair remains excluded. The current head and cameras are unchanged. This trial
tests a genuinely different observation from experiment 0171's color
association: linear sRGB luminance explained by current surface normals,
per-view order-2 spherical-harmonic illumination and shared point albedo.
All five independent/composited references and identity derivatives stay local.

## Observation and a corrected partition

589 unchanged vertices are spatially stratified (one per .035 world XY cell)
and z-buffer visible in front and both obliques. The dense mouth patch cannot
dominate by its vertex count. An initial world-Y predicate mistakenly selected
forehead/eye samples as the lower face in the OBJ's Y-down coordinates. Its
"lower-face" figures and claimed advantage over the spatial null are withdrawn.
No shape coefficient had been selected before this correction.

The corrected, explicitly checked lower-face holdout is native-front
`abs(x-634)<135, y>=760`: 119 samples at x499.266--768.030,
y760.169--914.643, world Y+.424--+.850. The other 470 samples fit illumination.
Front alone determines point albedo; both obliques are predicted. Sampled
irradiance is constrained positive and mean frontal train irradiance is one.

| Lower-face relative luminance error | Median | p95 |
| --- | ---: | ---: |
| Exposure only | 14.03% | 42.50% |
| Equal-degree-of-freedom spatial XY illumination | 10.14% | 31.50% |
| Current normals plus SH illumination | 11.29% | 34.00% |

The SH model does not beat the spatial null in the actual lower face. Moreover,
changing `(nx,ny,nz)` to `(-nx,-ny,nz)` changes only signs of SH basis columns;
the corresponding lighting coefficient signs yield exactly identical sampled
predictions. The observed maximum difference is zero. Unknown lighting cannot
establish convex versus concave anatomy this way. A synthetic Lambertian
positive check validates execution, not the reference-photo assumptions.

## One frozen-light lower-lip candidate

One coefficient was still tested without changing its predeclared family or
grid. It reuses experiment 0153's lower-lip Gaussian centered at native-front
(634,837), scales (105,23), with a smooth radial tail cut from 2.5 to 3 and
strictly unchanged vertices outside support. Only world Z changes. The 21
coefficients range from -.03 to +.03 in steps of .003. Illumination and photo
samples stay frozen; left30 alone selects from 88 eligible region samples.
Right30 is consulted only after selection, with no retuning after failure.

The selected coefficient is -.03. Left30 median relative error falls
18.46% to 16.75%, but right30 median rises 7.94% to 9.40% (its p95 falls
22.59% to 21.44%). Both leading facial contours worsen: left MAE
3.624 to 4.320 px, right 4.923 to 5.999 px. Minimum triangle area ratio is
.9119, no normal reverses, maximum displacement is .029979, and support-exterior
difference is zero. Safety does not rescue the failed transfer/shape checks.
The candidate is `REJECT`; no extra coefficient scan or candidate rendering
is used to reinterpret this failure. These references are not physical holdout
ground truth, and the metrics are limited diagnostics, not likeness scores.

## A clearer actual head result, not a geometry improvement

The Blender exact-camera diagnostic now has an opt-in `--relief-review` preset:
neutral clay, oblique camera-relative key light and weaker camera fill. The
existing blue-camera-fill default is preserved. Reports record the preset and
each light's position and rotation, plus the renderer hash. Comparisons must
use matching presets and actual light poses; geometry-derived lighting offsets cannot be assumed equal between
arbitrarily different meshes.

The unchanged CC0-eye/head OBJ was rendered at 1254 x 1254 in all five views.
Its hash matches the older hair-free source exactly. Blender import error is
5.96e-8; worst projection-replay maximum is .000116 px. An actual photo/clay
front-and-both-profiles contact sheet uses identical per-view crop and scale,
without separate alignment. The neutral view exposes stiff lip/chin relief
and rough central-face transitions more clearly; nose-to-chin exterior is
closer than interior anatomy, and the short cut neck remains. This is a more
inspectable baseline, not a prettier-render claim of shape improvement.

Private reproducible scripts, reports and rejected OBJ are under
`assets/private/subject-001/lambertian-normal-evidence-v1` and
`lambertian-relative-relief-v1`. Five exact neutral renders and a reopenable
scene are in `head-only-relief-review-v2`; the local contact sheet is
`head-only-neutral-review-v2/front-and-both-profiles.png`. Nothing biometric
was committed or uploaded. The package suite still passes 105 tests; actual
five-view rendering checks the new optional path separately.

Next gate: an anatomically structured lip/central-face representation with
reviewed native image-space boundaries and explicit tangent/normal continuity,
followed by the same real five-view white-mesh comparisons. Do not repeat the
failed one-mode photometric sweep or treat color boundaries as exact surface
turns. Until a genuinely more recognizable candidate survives review, keep
the current head experimental and unaccepted.
