# Experiment 0098: bounded pair/profile relinearization

Status: `UNVERIFIED`; no baseline or camera promotion.

Apply up to five source-referenced solves with updated apparent profile-edge
support after each retained step. Keep 0097's thirteen half-gap pairs, sixteen
profile rows, cameras, protected region and regularization. Accept only tested
fractions satisfying total source-relative movement <=0.03, area ratio >=0.5,
no reversed triangles and both whole-profile means <=source+1e-6 px.
This protects source means, not every row or monotonic per-iteration error.

Five steps are retained at fractions 0.25,0.5,0.5,0.25,0.25. Final maximum
movement is 0.028292 template units and minimum area ratio 0.598009, verified
again on the exported OBJ; 4173 protected vertices stay unchanged. All thirteen
pair distances decrease. Whole-profile means change from 3.589129/7.249347 to
3.539336/6.521262 px. Intermediate left-profile means fluctuate; do not claim
monotonic descent. A final unused proposal is computed after the fifth retained
step but is not exported or included in these measurements.

Actual photo/source/candidate five-view renders were inspected. Mouth changes
remain small at head scale, and generic facial proportions and lip anatomy
persist. Both mean reductions are fitting evidence, not recognizable identity
or independent visual acceptance. Contact is still a soft relative constraint;
collision freedom and visible-seam correspondence remain unverified.

Private `rim-pair-bounded-v1` retains the actual mesh, cameras, five-step history,
gap measurements and inspected comparison. No personal data is committed.
Public production code is unchanged; checks were real bounded iteration,
recomputed silhouettes, protected vertices and exported triangle/render checks.
Next verify the final candidate's local contact and visible seam rather than
repeating iterations solely to improve the same mean profile measurements.
