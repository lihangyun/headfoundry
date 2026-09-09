# Experiment 0040: cheek support versus oversized feature protection

Status: `UNVERIFIED` local geometry experiment. No accepted reconstruction.

The support audit predicted in 0039 was executed on the unchanged 0037 source
mesh and fixed cameras. Both edge endpoints for the two largest residuals in
each oblique view were frozen by the old image-rectangle protection. Their
frontal projections lie on the lateral cheek, not at the eight selected
feature anchors. This directly explains why those four fitting residuals were
constant in the previous run; it does not explain the remaining camera error.

## Single controlled change

Replace that oversized image rectangle with two topology rings around the
eight approximate anatomical anchors, plus the central image stripe, upper
face, lower neck and rear-half protection. Keep the same original-photo edge
observations from 0039, cameras, source mesh, six-ring local support,
regularization, movement bound and frontal-ray displacement parameterization.
No photos or annotations are adjusted after seeing the model. The feature-ring
mask is a bounded experimental policy, not complete semantic face segmentation.

## Actual result

Private artifacts: `assets/private/subject-001/oblique-jaw-v3/candidate.obj`,
`report.json`, `five-views.png`. Report includes each observation's source edge,
perspective weights, old/new protection state, frontal positions and feature
core vertex IDs. The five-view original/baseline/candidate clay sheet was
rendered and inspected. Exact pinned source hashes and local-only image consent
are checked by the runner; no biometric data enters Git or a remote service.

- Left oblique fitting MAE: 5.849 → 3.151 px.
- Right oblique fitting MAE: 5.944 → 2.394 px.
- Previously frozen upper residuals now change from approximately 11 px to
  approximately 4.7–4.8 px. Two chin-adjacent observations remain protected and
  unchanged; they were not dropped from the reported mean.
- Maximum displacement 0.037432 template units; all protected vertices exactly
  unchanged; all-vertex frontal projection change at most 3.22e-13 px.
- Existing central profile residual arrays are unchanged on both sides.

This is a meaningful local fitting result, not independent visual acceptance:
ten boundary observations are training inputs, initial cameras still have no
passed independent gate, and projected positions cannot certify shading,
self-intersections or identity. The face still looks largely generic and coarse;
eyes, ears and neck are not satisfactory. No default or accepted baseline is
replaced. Earlier rejected candidates are not used as input.

## Next gate

Retain this output only as an experimental branch. Establish coherent anatomical
neck/ear regions and inspect the remaining face/neck transition and shoulder
crop artifacts before treating the result as a usable full head. Geometry and
shading must remain separate variables; no texture should conceal shape errors.
Full identity, independent camera/visual gates, texture and export acceptance
remain incomplete.
