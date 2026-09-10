# Experiment 0061: anatomical anchor correspondence audit

Status: `UNVERIFIED` overall; three correspondences rejected for further
unqualified point fitting. No mesh, camera or original observation overwrite.

Trace the existing registration script: eight template anchors were selected
as nearby vertices around clicks in a frontal generic render. Six photo
targets in front/left30/right30 were replaced by manual visual readings;
profile targets and nose/chin targets still use detector estimates. A small
reprojection error therefore does not establish a common anatomical point.

The local audit verifies consent and locked source/camera hashes, projects
the eight current source vertices, and produces native-resolution paired
photo/clay crops with numbered markers and the original used/excluded mask.
Nearest-surface ray lifting independently measures whether each projected
source vertex is actually visible. This does not modify correspondence.

Concrete findings from inspected front, left30 and bilateral profile crops:

- Right90 nose target (anchor 6) visibly lies outside the nasal silhouette.
  Its original reprojection error is 22.69px. Reject using this detector
  coordinate as a measured surface point, rather than asking a camera or
  mesh fit to reproduce it.
- Left30 far mouth anchor 5 is behind the nearest template surface by
  0.063259 template units. Right30 far mouth anchor 4 is behind by 0.051779.
  Both were marked usable. Their low-ish 3.90/6.46px reprojection errors hide
  an occlusion/correspondence conflict. Reject these current pairs for
  further unqualified visible-point fitting.
- Near outer-eye anchor vertices are slightly recessed in the oblique and
  profile views (roughly 0.0053–0.0073 template units). This is consistent
  with an inset rim vertex selected from frontal clicks, but requires local
  topology inspection before correcting identities. Do not automatically
  snap to another surface point or declare those offsets measurement truth.
- Profile chin detector targets are not the lowest visible silhouette
  points. That alone does not make a fixed anatomical landmark wrong, but
  it makes treating them interchangeably with contour endpoints invalid.
  Cross-view anatomical correspondence remains uncertain.

Private `template-anchor-audit-v1` retains all five paired crops, per-anchor
projection/visibility gaps and explicit non-destructive `review.json`.
The original registration files remain untouched. The audit is specific to
the current fixed source: it does not prove the source anatomy correct or
provide corrected photo coordinates. All 72 existing tests pass.

This changes the next engineering action: future pose fits must not silently
reuse the rejected pairs. Establish visible anatomical support for nose,
chin and eyelid corners, with per-view validity, before repeating focal
optimization. Removing bad points can reduce pose observability; do not
relax the minimum support/rank requirements or fabricate replacements to
make a solve run. The product still lacks accepted calibration and likeness.
