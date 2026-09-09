# Experiment 0037: lower-face outline and neck-confound correction

Status: first trial `REJECT`; corrected local trial `UNVERIFIED`. No accepted
likeness, no camera gate change, and no production default replacement.

## Scope

Primary variable: lower cheek/jaw geometry on the experimental 0036 mesh.
Use the same fixed five cameras and 12 existing frontal MediaPipe oval points
(six per side, approximately rows 707–900). These detector estimates are fitting
inputs, not held-out evidence. Original photo overlays were inspected; the
readings broadly follow the visible lower face but are not exact ground truth.

This intentionally changes the lower frontal outline, superseding the previous
experiment's whole-frontal-projection freeze only for this local trial. The
eyes/nose/mouth core, central stripe, upper face and lower neck remain fixed.
Existing six-ring displacement smoothing, finite step bound and triangle checks
are retained. No camera or texture changes.

## First trial: wrong surface association

`jaw-width-v1` reduced aggregate outline error but introduced an unnatural
side-view lower-jaw/neck protrusion. It is rejected and retained only as evidence.
The support audit identifies a concrete confound: the last two rows on each
side selected rear-neck edges, not the facial outline. Those support points
have template z approximately +0.37/+0.52 and frontal camera depth 6.23/6.38,
whereas upper facial supports are z -0.30 to -0.56 and depth 5.29–5.53.
The whole-object envelope is therefore not interchangeable with a face boundary.
The audit is in `jaw-width-v1/support-audit.json`.

## Corrected bounded trial

The shared fitter now accepts an explicit contour-face mask and protected
vertices. For this one known template, the private runner restricts contour
support to triangles entirely in template z<0 and freezes all rear-half vertices.
This coarse front-half ROI is disclosed and not claimed as universal anatomical
segmentation. All topology remains present in the exported mesh and render;
the mask changes observations, not which triangles are displayed.

Private output: `assets/private/subject-001/jaw-width-v2/candidate.obj`,
`report.json`, `five-views.png`. The five-view photo/before/after sheet was
inspected. The visible v1 rear-neck distortion is avoided, but the face remains
coarse and largely generic. Eye, ear and neck fidelity is still inadequate.

- Frontal face-ROI envelope fitting MAE: left 9.929 → 4.689 px;
  right 13.848 → 7.693 px. The same ROI is used before and after; these cannot
  be compared directly to v1's whole-object-envelope scores.
- All explicitly protected vertices: exactly zero displacement.
- Existing complete-object central profile residual arrays: unchanged on both
  sides (MAE 3.642 / 8.032 px). This is a bounded curve regression check, not
  proof of unchanged cheek/neck appearance or independent quality acceptance.
- Maximum displacement: 0.054638 template units; no physical scale inferred.

Source mesh hash:
`f1fb1814b8427c7d3849f7f71b2bbb4dbb37f11bb1238d018d424611c82d3549`.
Registered camera bundle hash remains as recorded in 0034–0036. The private
runner validates both hashes and source-photo rights/digests. Observations,
ROI policy and indices are recorded in its private report. No biometric assets
or photos are uploaded or added to Git.

## Checks and next gate

60 tests pass, with additional assertions for exact protected-vertex retention,
invalid protected IDs, and exclusion of all contour faces without altering the
mesh. Both vertex and continuous modes honor the contour mask; defaults remain
backward-compatible.

Next establish actual anatomical face/neck/ear regions and improve coarse
surface fitting across oblique views. Do not iterate against a whole-object
silhouette as if it were an anatomical jaw. Independent cameras, complete
identity geometry, eyes/ears/neck, textures and export acceptance remain unmet.
