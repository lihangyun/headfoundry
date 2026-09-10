# Experiment 0067: visible alar support and nasal fitting

Status: `REJECT` for shape promotion. No original camera or mesh replacement.

Inspect eight detector-indexed nasal support points on photo/clay crops in
front/left30/right30. Use the correct neck-cut mesh topology for the stored
triangle IDs and barycentric weights. The first diagnostic run mistakenly
used preclip triangle numbering and produced absurd 80–295px errors; discard
its v1 evidence. Corrected v2 uses the verified neck-cut source and support
hashes. This was a diagnostic runner indexing error, not a detector finding.

Actual v2 crops show front bilateral alar candidates 98/327, 129/358 and
64/294 near corresponding nasal regions. In each oblique view, the far-side
three mesh points are occluded, with 0.178–0.261 template-unit nearest-surface
gaps. Their occasionally low 2–11px projection errors do not make them visible.
Keep six front observations and only the near three per oblique view; exclude
the far triples and do not add nasal apex 4 to this fit. The photo targets
are detector estimates, visually reviewed but not anatomical ground truth.

Map the six support triangles through the neck-cut original-vertex map back
to the preclip topology used by authored targets; reject new cut IDs. Add
these twelve visible 2D alar observations to the existing bilateral nasal
profile objective in 0066, retaining the same fixed cameras, shape source,
three paired controls, frontal-projection prior, bounds and eight sign runs.
Only the observation set changes. All branches converge.

Best tip/depth/width coefficients: 0.024240, -0.014780, -0.044850. Maximum
movement 0.002066 template units; maximum frontal shift 0.767755px. No
reversed triangle normals, minimum area ratio 0.957893. Those checks are not
anatomy or collision validation.

| Fitting diagnostic px | Source | Candidate |
| --- | ---: | ---: |
| Front alar mean | 8.8148 | 8.8813 |
| Left30 near alar mean | 5.1659 | 4.9156 |
| Right30 near alar mean | 4.8562 | 4.8291 |
| Left nasal profile MAE | 2.8416 | 3.0856 |
| Right nasal profile MAE | 6.4675 | 6.3071 |

Same-camera five-view actual renders were inspected. Geometry changes remain
tiny, frontal alar alignment and left profile regress, and recognizable
subject likeness is not established. Do not amplify this rejected update.
The frontal alar support projects roughly 7–10px above its target readings;
the current three controls do not directly model alar-base vertical position.
That is a specific next shape/support question, not evidence for unrestricted
vertex displacement or a calibrated camera.

Private `nasal-support-audit-v2` and `authored-nose-alar-v1` retain corrected
crops, visibility records, candidate OBJ, masks, full fit reports and final
surface audit. v1 diagnostic data remain retained but explicitly invalid.
All 72 tests pass. Photos and identifiable artifacts remain outside Git.
