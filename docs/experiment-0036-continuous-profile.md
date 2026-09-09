# Experiment 0036: continuous profile-edge constraints

Status: `UNVERIFIED` experimental geometry; not accepted camera or likeness.

## Controlled change

Replace the nearest-vertex/5-pixel-row association of 0035 with the actual outer
projected triangle-edge intersection at each unchanged profile-annotation row.
Convert image-space interpolation to perspective-correct 3D edge weights before
solving. The source template, fixed cameras, original photos, fitting curves,
regularization, six-ring locality policy and 0.06-template-unit movement bound
are unchanged. Frontal-ray displacement and triangle safety backtracking remain.
Historical outputs are preserved. This is one correspondence-discretization
experiment, not new calibration or a baseline promotion.

Implementation extends the existing sparse surface solver with weighted two-
vertex observations. The optional continuous mode leaves the previous default
unchanged. Horizontal edges, absent rows, invalid constraints and perspective
depth differences are explicitly handled/tested. The envelope is geometrical,
not semantic: it must not be mistaken for a face boundary when other objects
occlude the subject. No segmentation or physical point identity is inferred.

## Actual local result

Private output: `template-profile-v3/candidate.obj`, fit report and three-view
comparison under the consented subject directory. Five-view evidence and exact
edge/row audit: `template-profile-audit-v2/five-views.png`, `report.json`.
The private fit/audit scripts were executed; the five-view clay sheet inspected.
Input image consent/digests and registered baseline hash are checked before use.
No photos or identifiable mesh outputs are committed or uploaded.

| Fit-only measure | Unmodified template | Vertex constraint (0035) | Continuous edge |
|---|---:|---:|---:|
| left90 horizontal envelope MAE (px) | 8.236 | 6.184 | 3.642 |
| right90 horizontal envelope MAE (px) | 11.449 | 9.899 | 8.032 |

Both annotation sets are training inputs with 5–10 pixel estimated reading
uncertainty, not held-out truth. Some individual samples worsen; aggregate
reduction must not hide remaining right-side lip/chin mismatch. The unchanged
camera uncertainty can still be absorbed by geometry.

33/33 curve rows supplied constraints. The full step passes existing safety
checks: maximum displacement 0.056959 template units, no reversed triangle
normals, minimum face-area ratio 0.5798. Maximum all-vertex frontal projection
change is 3.22e-13 pixels. Physical scale, self-intersection freedom, shading,
occlusion order and perceptual frontal identity are not proven by these checks.

The actual model is still coarse and largely generic. Nose/lip/chin changes are
inspectable, but the result does not establish the user's requested likeness or
KeenTools-level quality. Eyes, cheeks, ears, neck, texture and export readiness
remain incomplete; no earlier camera failure is cleared.

## Verification and next gate

60 tests pass: known 3D edge reconstruction, perspective-correct interpolation,
horizontal edge/missing row behavior, invalid weights, and ray-constrained
continuous-step frontal invariance, plus the existing suite.

Next inspect the anatomical template/subject shape discrepancy beyond the
center profile, especially cheek/jaw and ear placement, with original-photo
observations rather than more unbounded repetition of the same curve fit.
Keep this candidate experimental and retain fixed-camera visual regression.
