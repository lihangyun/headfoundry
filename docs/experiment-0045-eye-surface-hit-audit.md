# Experiment 0045: eye surface-hit ambiguity

Status: unrestricted clay-hit anatomical correspondence assumption `REJECT`;
bounded eye-rim proposal `UNVERIFIED`. No geometry or camera changes, no visual
head acceptance. This diagnostic changes the next action from stronger dense
deformation to correcting correspondence support.

## Evidence

Original-photo crops were overlaid with frozen template barycentric points,
before and after experiment 0044. Eight representative eye points have mean
error 11.55 / 32.04 / 31.24 px in front/left30/right30 before fitting, versus
9.32 / 30.42 / 29.04 after. These are all-point diagnostics, including points
occluded under the template; they are not the visibility-filtered training
metric from experiment 0044. Nose/mouth errors are smaller, and the conspicuous
eye displacement reverses horizontal direction between oblique views.

The exact ray-lifting implementation is geometrically correct but cannot tell
an eyelid from an internal orbital surface. At IDs 33,159,145,263,386, a 5px
radius neighborhood contains surfaces 0.19–0.32 template units in front of the
central hit. Inner canthi 133/362 show only 0.008/0.007 units of local depth
difference; lower eyelid 374 shows 0.003. The template has no separate eyeballs.
Several lifted eye points also become occluded when viewed obliquely.
Together this identifies wrong surface support as a major cause of eye-point
reprojection error, rather than sufficient evidence for deeper shape changes.
It does not establish the anatomical identity of every triangle or validate
the camera calibration.

## Explicit correspondence-only proposal

For those five audited points only, sample concentric frontal rays at 0.5px
increments, at most 5px from the original prediction. Select a ray in the first
ring with a hit at least 0.15 template units in front of the original internal
hit. Within that ring choose the nearest-depth candidate. This is a declared,
unaccepted eye-rim heuristic, not silent snapping or a general replacement for
`lift_pixels`. Original correspondences and all misses remain preserved.
No real-photo residual participates in selecting a proposal.

Actual frontal shifts are 3.5,1,1,0.5,2 pixels for IDs 33,159,145,263,386.
The 3D mesh and cameras are exactly the same in both evaluations.

| Point | Left30 error before / proposed | Right30 error before / proposed |
| --- | ---: | ---: |
| 33 | 30.63 / 3.89 | 38.08 / 5.37 |
| 159 | 57.50 / 7.30 | 54.02 / 5.85 |
| 145 | 55.43 / 4.22 | 58.50 / 7.10 |
| 263 | 39.14 / 8.61 | 22.66 / 15.75 |
| 386 | 57.86 / 8.16 | 50.30 / 7.64 |

Inspected the original-photo overlays. The proposed cyan eye points align much
closer to the observed eyelids in oblique views than the old red points, but
remaining errors are visible, particularly point 263. This is correspondence
evidence only: it does NOT mean the unchanged generic mesh now resembles the
subject, nor that the proposal is ground-truth anatomy. Front error at point
263 slightly worsens (13.22 to 13.28 px), retained in the private report.

## Artifacts and next gate

Local ignored outputs: `dense-feature-audit-v1/report.json`, `overlays.png`,
`eye-depth-audit.json`; `eye-rim-correspondence-v1/correspondences.npz`,
`report.json`, `overlays.png`. Private runners are `audit_dense_features.py`,
`audit_eye_lifting.py`, `propose_eye_rim_correspondences.py` and
`render_eye_rim_audit.py`. The feature report records source hashes. No photos,
identifiable outputs, external services or weights are added to Git.

Next audit the remaining dense eye-region support for depth discontinuity and
visibility, keep unsupported points explicit, and rerun bounded fitting only
after reviewing anatomical correspondence proposals. Recheck eye topology and
both profile curves before any promotion. Do not use the experiment 0044
candidate as an accepted seed. Camera and finished reconstruction gates remain
unmet. This turn changes no public solver; the existing 65-test suite passes.
