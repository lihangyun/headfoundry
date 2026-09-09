# Experiment 0044: bounded dense anatomical template fit

Status: weighted triangle solver `TECHNICAL_CHECK_PASSED`; real reconstruction
`UNVERIFIED`. No accepted baseline replacement or KeenTools parity claim.

The single primary variable is shared mesh displacement under frozen cameras
and frozen clay-derived correspondences from experiment 0043. No new texture,
lighting, model weights, camera optimization or training is introduced.
The prior user authorization for unaccepted geometry experiments applies.

## Actual execution

The private local runner verifies photo consent and the source mesh digest.
Face-oval points are excluded because view-dependent contours are not fixed
anatomical correspondences. Interior points are lifted to exact triangle
barycentric coordinates. Source visibility is tested by nearest surface
intersection in front/left30/right30 and frozen before fitting. Every seventh
landmark ID is withheld in every view. This split uses the same detector and
is NOT independent ground truth; neighboring constraints are correlated.

979 visible training constraints drive one regularized displacement solve.
The existing weighted-edge solver now also supports three-vertex triangle
observations. Rear geometry, lower neck, central stripe and vertices outside
the local two-ring support remain exactly fixed. An initial 0.06-unit movement
bound is halved by the face-normal/area guard, leaving maximum displacement
0.03 template units and step 0.215057. Template units are not physical meters.

| Diagnostic, original photo pixels | Before | After |
| --- | ---: | ---: |
| Training point p95 | 29.6580 | 25.6864 |
| Withheld point p95, 176 observations | 26.5577 | 23.4861 |
| Frozen left-profile curve MAE | 3.6420 | 3.6570 |
| Frozen right-profile curve MAE | 8.0322 | 8.0135 |

Maximum sampled profile shifts are 0.547 / 0.522 px. Central-stripe protection
does not mathematically freeze the full silhouette: contributing contour
triangles can include unprotected vertices. The slight left regression is
retained, not rounded away as a pass. These profile curves were earlier fitting
inputs and have reading uncertainty; this is regression evidence only.

## Visual review and next decision

Inspected the actual five-view photo / prior clay / candidate clay sheet with
identical cameras and smooth shading. Changes are modest; the face still looks
generic, with missing eyeballs and insufficient subject-specific eye/nose/mouth
shape. The lower point error alone does not justify visual improvement or
production promotion. Keep the candidate experimental, not a new accepted prior.
Next discriminate feature-specific correspondence/camera bias from shape error
using enlarged anatomical overlays before increasing deformation strength.
Do not repeat progressively larger steps merely to lower detector residuals.

Private outputs: `dense-template-v1/candidate.obj`, `five-views.png`,
`report.json`, `profile-audit.json`; private runners `fit_dense_template.py`
and `audit_dense_template.py`. Photos and identifiable derivatives stay local
and outside Git. The audit records camera, correspondence, landmark, contour
and candidate hashes. Source mesh SHA256:
`1d9b0a35f29f504af50343e3f52a3efca4eeec29a4662cf668ebc5459901a6be`.
Candidate SHA256:
`6415ee3d9d785193e45dcd6c59f73dbba47482c9eb8805fd4f75010cfa016310`.

65 tests pass, including a two-camera triangle-interior constraint recovering
known synthetic displacement. Camera, identity, eyes/ears, UV/texture and final
product gates remain incomplete.
