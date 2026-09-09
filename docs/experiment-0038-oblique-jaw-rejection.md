# Experiment 0038: oblique lower-oval trial rejected

Status: `REJECT` for adoption. No production path or quality gate changes.

The preceding 0037 commit is preserved. This local experiment used its
`jaw-width-v2` mesh, existing fixed cameras, and five far-side lower-oval
MediaPipe observations in each oblique view. Only local depth was fitted,
using the existing frontal-ray constraint, protected vertices and front-half
contour ROI. No new dependency, model, camera fit, or annotation adjustment.

The original-image annotation overlays and five-view before/after clay sheet
were rendered and inspected. The detector's far-side oval runs inside portions
of the visible face, rather than tracing its actual outer silhouette. Thus
its anatomical landmark meaning is not interchangeable with the outer-edge
constraint being optimized. Do not solve this mismatch by increasing motion
bounds or unfreezing protected features.

## Actual measurements (fitting only)

- left30 mean absolute horizontal error: 19.797 → 19.652 px.
- right30: 12.384 → 11.828 px.
- Maximum motion: 0.033232 template units.
- Protected vertices remain exact; frontal maximum pixel shift 2.54e-13.
- Existing central profile residual arrays are unchanged, including their
  known errors. These sparse checks do not prove unchanged full appearance.

Improvement is negligible, substantial residuals remain, and the observation
semantics are invalid for this silhouette objective. The result stays private
as a rejected diagnostic and must not seed the next reconstruction.

Private evidence: `assets/private/subject-001/oblique-jaw-v1/` contains the
candidate OBJ, numerical report, frozen observation indices/coordinates and
`five-views.png`. The local runner is `fit_oblique_jaw.py`. Source photo consent
and hashes are checked before processing; mesh and camera hashes are pinned:

- mesh: `08d38871837219ed86f60c5b2d3d633fbd1320e794d6febeef952f8dbbf79948`
- cameras: `83d9f1ee7499f8a3b1c8ea4e91337e2307b2a2adf0f10918e5a07b7c32927ef4`

No photos or derived biometric geometry were uploaded or added to Git.
The unchanged implementation's 60 tests still pass. They do not test the
semantic correctness of these real-image observations.

Next action: separate anatomical landmark correspondences from independently
read photo silhouettes. Establish actual face/neck/ear regions on the template
and photo boundary evidence before another oblique deformation. The existing
generic-head and camera limitations remain; full likeness is not achieved.
