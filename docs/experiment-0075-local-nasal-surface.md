# Experiment 0075: local nasal vertex freedom

Status: `REJECT` for visual promotion. A real candidate was built and rendered;
lower fitting errors do not establish a natural-looking or accepted nose.

Following 0074, replace the four authored controls with local vertex freedom.
Reuse the existing sparse surface solver, neighbor displacement regularization
30, source cameras and the same twelve alar observations plus fourteen
original nasal silhouette rows. The editable region is the union of nonzero
support in the six nasal targets and two nasal-base targets: 486 vertices.
All other 3973 source vertices are exactly preserved. This is a bounded local
experiment, not a new learned model, new camera or production default.

At each iteration recompute profile edge support and solve using actual
barycentric alar observations. Test step sizes 1, 1/2, 1/4, 1/8, 1/16, 1/32;
require strictly lower combined pixel residual norm, total displacement at
most 0.03 template units, no reversed source triangles and minimum source
area ratio 0.5. Four steps are retained; the fifth is rejected by the area
condition. Its attempted lower error is not used as the final result.

| Diagnostic | Source | Retained candidate |
| --- | ---: | ---: |
| Combined residual norm px | 34.4429 | 25.6416 |
| Left nasal original-row MAE px | 2.8416 | 1.8297 |
| Right nasal original-row MAE px | 6.4675 | 4.6821 |
| Frontal alar mean px | 8.8148 | 6.3387 |
| Left-oblique alar mean px | 5.1659 | 3.8775 |
| Right-oblique alar mean px | 4.8562 | 2.4144 |

Maximum displacement 0.0252204; minimum triangle area ratio 0.515932;
zero reversed triangles. Exact ray-lift checks confirm all twelve eligible
alar supports remain visible. Far-side points remain excluded. These checks
do not establish anatomical correspondence, collision freedom or identity.

Actual photo/source/candidate five-view renders and enlarged nasal views
were inspected. Relative to the source, a conspicuous pinched/creased area
appears around the nasal tip in the frontal clay view. The subject's anatomy
is not established merely by matching these few points. Thus the locally
more expressive model reduces all listed fitting means but is still rejected.
The 486-vertex freedom is too weakly constrained by the current observations
and regularization to justify promotion; triangle orientation/area guards
alone do not protect natural curvature.

Next use smooth regional deformation or stronger shape-preserving constraints,
not more independent vertex motion or a weaker area guard. Keep the same
observations/cameras for that comparison and inspect enlarged clay views.
No texture should conceal the crease. Full head likeness and camera gate
remain unresolved.

Private `local-nasal-surface-v1` contains the candidate, iteration history,
source/camera hashes, final mesh audit and photo comparison. Its OBJ SHA256:
`a6ed5668cb5654eb51d23169bfff2480b7d8b2f6b9b747cfe043fdf8684b7b9c`.
`local-nasal-surface-v1-support-audit` contains actual enlarged views and
ray-visibility checks. All identity-bearing data stays local and Git-ignored.
Existing public suite: 77 tests pass; no public numerical API changed.
