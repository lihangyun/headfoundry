# Experiment 0110: image-depth-guided central shape proposal

Status: `REJECT` after actual geometry and visual checks. The following
protocol was recorded before execution. Target: more faithful nose/lip depth in actual
side views of the existing head, without adding the exterior sheets from the
coarse observed surface. Counter-evidence: model depth and both sets of
cameras remain unaccepted; correspondence and template mouth opening cannot
be resolved just by moving points along frontal rays.

One primary variable: replace generic authored shape directions with one
bounded image-depth-derived direction. Source mesh/cameras are experiment
0079. Use only the raw model's frontal z depth (not its rejected cameras).
Fit a positive affine depth scale/offset against the existing template's
visible cheek/forehead raster support. This is gauge alignment to an
unaccepted prior, not calibration. A small fixed blur suppresses depth noise;
move only visible central nose/lip vertices along unchanged frontal rays,
feathering the region and bounding total displacement to 0.03 template units.

Prediction: actual profile shape improves without flipped triangles, lost
original visible landmark support, or worse bilateral profile means. Inspect
all five views and retain all original profile rows. Reject on structural or
visual failure; no texture, camera change, whole-track reclassification or
noncommercial model. Frontal projection is protected by construction but
cannot count as independent likeness validation. Do not claim mouth closure.

## Actual execution

The local Python 3.13 environment supplies the already installed SciPy needed
for the fixed sigma-2 depth filter and bilinear sampling. No package was added
to the separate model-inference environment. Model output bytes, source mesh
and source camera hashes are checked before use; all identity data stay private.

Affine alignment uses 4,452 visible prior pixels in the fixed forehead/cheek
bands, returning scale 1.84003649 and offset 0.89849112, with prior-depth
correlation 0.8723 and RMSE 0.02183 template units. This only describes agreement
with the existing unaccepted prior, not calibrated depth or valid anatomy.

The proposed direction affects 596 front-visible central vertices. Raw maximum
movement is 0.12731 and is first scaled to the fixed 0.03 cap. Structural step
selection then finds:

| Fraction of capped step | Reversed triangles | Minimum area ratio | Lost original visible supports |
| --- | ---: | ---: | ---: |
| 1 | 14 | 0.303 | 0 |
| 0.5 | 2 | 0.084 | 0 |
| 0.25 | 1 | 0.352 | 0 |
| 0.125 | 0 | 0.621 | 0 |

The last row is retained for inspection, with maximum movement 0.00375 units.
No profile observation participates in scale alignment or step selection.
Every original row is evaluated afterward: left profile MAE worsens from
**3.5891 to 3.8221 px** while right improves from **7.2493 to 6.9750 px**.
Thus bilateral protection fails. No baseline or camera is replaced.

Actual five-view photo/source/candidate renders were inspected. The retained
change is small and the face remains generic, with an open/angular mouth.
The structurally safe step does not deliver a recognizable improvement.
Camera gates stay failed; these fixed-camera profile observations are not a
new independent calibration benchmark. Visibility screening also does not
establish anatomical landmark correctness or collision freedom.

Private evidence: `image-depth-prior-v1/candidate.obj`, `cameras.npz`,
`comparison.png` and `report.json`. Report SHA-256:
`3c789710b0436b06d96152a0e2f73e78206a12011f49b120ff9e3e120a11f5b8`.
It records source, camera, depth, annotation and script hashes. Full public
suite rerun: **88 tests pass**. The experiment reused existing mesh/raster/
profile helpers rather than adding a public pipeline for a rejected method.

## Decision

Stop increasing this depth-derived ray direction. Positive depth correlation
with the prior did not make it a reliable bilateral facial-shape driver.
The fixed-front-ray family cannot close an incorrect frontal mouth opening.
Next address the neutral mouth surface/closure configuration explicitly,
preserving complete rim and outside anatomy, with actual frontal/oblique/
profile evidence before further identity fitting. Do not repeat the earlier
two-point attraction or claim depth filtering/template control count solves it.
