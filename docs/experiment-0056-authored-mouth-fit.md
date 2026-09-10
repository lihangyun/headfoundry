# Experiment 0056: real-photo fit of authored mouth volumes

Status: `UNVERIFIED`; no baseline promotion or likeness claim.

Use the six verified CC0 targets from 0055 as three signed controls for lower
lip, philtrum and upper lip volume. Each sign selects its authored increase or
decrease asset, with magnitude bounded to 0.5. Targets map through exact base
source IDs into the neck-clipped mesh; new cut vertices receive zero displacement.
Base/license/target hashes, matching revision and input consent are verified
before use. All cameras remain fixed. This replaces ad hoc ray displacement
modes; unlike those modes, the authored assets can alter frontal geometry.

The robust objective uses both local side-profile curves and six mouth points
in front/left30/right30, scaled by 5 pixels plus coefficient regularization.
All are fitting inputs with known uncertainties, not independent validation.
Mouth points use the existing lifted template correspondences; their semantics
are not assumed perfect simply because the new basis is authored anatomy.

Because increase/decrease pairs are not necessarily opposite vectors, the
control function has a branch at zero. Retain the initial signed solve, then
run all eight sign combinations with nonnegative magnitudes. All converge;
selection uses the same training objective, not evaluation/visual cherry-picking.

Best coefficients: lower lip effectively zero, philtrum -0.002547, upper lip
-0.362140. The lower-lip bound flag in the private branch-optimizer report denotes
zero magnitude within that sign branch, not reaching the global +/-0.5 limit.

| Fitting diagnostic | Source | Candidate |
| --- | ---: | ---: |
| Left local profile MAE px | 4.3040 | 4.2933 |
| Right local profile MAE px | 9.4491 | 8.7714 |
| Frontal mouth point mean px | 4.8665 | 4.8215 |
| Left30 mouth point mean px | 11.2925 | 11.2401 |
| Right30 mouth point mean px | 8.7840 | 8.7068 |

Maximum displacement 0.008368 template units; zero reversed face normals;
minimum triangle-area ratio 0.87820. These checks do not prove absence of
self-intersection or anatomical correctness. No decrease in camera error is
claimed because camera calibration was not estimated or accepted here.

Inspected actual five-view source/candidate clay renders with identical
lighting. The result avoids a large vertexwise lip protrusion but differences
are small and the head still looks generic. The remaining profile discrepancy
is not solved by these volume controls. Do not portray subpixel fitting gains
as a visually convincing reconstruction.

Private `authored-mouth-v1` retains the initial solve; `authored-mouth-v2`
contains the sign sweep, actual OBJ, full report, five-view rendering and final
surface audit. Runners `fit_authored_mouth.py` and the existing parameterized
renderer preserve the pre-dense source. No identifiable data is committed.
Public code unchanged; 71 tests pass.

Next determine whether authored lip height/position controls address the
remaining shape mismatch, reviewing additional assets individually before use.
Do not amplify volume controls that are already ineffective. Camera, complete
identity, eyes/texture and product acceptance remain unresolved.
